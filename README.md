# 📦job-test-public

직업 분류 챗봇 평가용 데이터셋과 실험 결과를 정리한 공개 저장소입니다.

이 저장소는 결과물 아카이브에 가깝습니다.
실제 데이터셋 JSONL, 평가 로그 TXT, 모델 비교 메모가 모두 `result/` 아래에 정리되어 있습니다.

## 📖Task 정의

Task는 2가지입니다.

1. `ask_slots`

직업 분류 전에 추가 질문이 필요한 케이스를 골라내고, 상황에 맞는 추가 질의 slot을 제시합니다.

2. `classify_now`

고객이 자연어로 설명한 직업/상황을 보고 적절한 `job_code`를 바로 분류하는 성능을 평가합니다.

## 📄결과 요약

### `ask_slots`

| 세트 | 폴더명 | 실험 설명 | 대표 점수 |
|---|---|---|---|
| A | `A_ask_slots` | 본사 데이터 | 90.4% (`conditional slot accuracy`) |
| B | `B_ask_slots` | 본사 데이터 few-shot 기반 유사 데이터 생성 | 69.6% (`conditional slot accuracy`, Claude 기준) |

### `classify_now`

| 세트 | 폴더명 | 실험 설명 | 대표 점수 |
|---|---|---|---|
| A | `A_job_classify_now` | 본사 데이터 | 92.73% (`Recall@3`) |
| B | `B_job_classify_now` | 직업코드 설명 기반 데이터 생성 | 99.12% (`Recall@3`) |
| C | `C_job_classify_now` | 직업코드 설명 기반 복수직업 데이터 생성 | 100.0% (`Recall@10`) |
| D | `D_job_classify_now` | 본사 데이터 few-shot 기반 유사 데이터 생성 | 74.94% (재검증 반영 최종 점수) |

## 📁저장소 구조

```text
job-test-public/
├── README.md
└── result/
    ├── ask_slots/
    │   ├── A_ask_slots/                         # 본사 데이터
    │   │   ├── questions.jsonl
    │   │   ├── eval_results.jsonl
    │   │   └── eval_results.txt
    │   └── B_ask_slots/                        # 본사 데이터 few-shot 기반 유사 데이터 생성
    │       ├── claude/
    │       │   ├── questions.jsonl
    │       │   ├── eval_results.jsonl
    │       │   └── eval_results.txt
    │       └── gemini/
    │           ├── questions.jsonl
    │           ├── eval_results.jsonl
    │           └── eval_results.txt
    ├── classify_now/
    │   ├── A_job_classify_now/                 # 본사 데이터
    │   │   ├── questions.jsonl
    │   │   └── eval_results_20260415_181654.txt
    │   ├── B_job_classify_now/                 # 직업코드 설명 기반 생성 데이터
    │   │   ├── questions.jsonl
    │   │   ├── eval_results_20260416_104110.txt
    │   │   └── verify_results_20260416_110116.txt
    │   ├── C_job_classify_now/                 # 복수 직업 질의 생성 데이터
    │   │   ├── questions.jsonl
    │   │   └── eval_results_20260414_152833.txt
    │   └── D_job_classify_now/                 # few-shot 기반 유사 데이터 생성
    │       ├── questions.jsonl
    │       ├── eval_results_20260416_092643.txt
    │       └── verify_results_20260416_102607.txt
    └── compare_llm_models/
        ├── README.md                           # 모델별 결과 비교
        └── google_models_limit.png             # Google 계열 모델 비교 이미지
```

## 🚀모델 비교 자료

`result/compare_llm_models/README.md`에는 6개의 LLM으로 질문을 생성하고 품질을 비교한 예시가 정리되어 있습니다.

- 비교 대상: `gpt-5.4`, `gpt-5-mini`, `sonnet-4.6`, `opus-4.6`, `gemini-3.0-flash`, `gemini-3.1-pro`
- 결론 요약: 사람과 가장 유사한 품질을 보여준 `sonnet-4.6`을 우선 선택했고, 일부 task에서는 `gemini-3.0-flash`도 병행 사용했습니다.

## 🧠핵심 산출물 상세

### 1. `result/ask_slots/`

직업 분류 전에 추가 질문이 필요한 케이스를 골라내고,
각 상황에 맞는 추가 질의 종류(slot)를 제시합니다.

즉, "바로 분류할 수 있는가"가 아니라
"추가 질문이 필요한가, 필요하다면 어떤 slot인가"를 평가한 자료입니다.

slot 종류는 아래와 같습니다.

- `transport_mode`
- `multi_job`
- `task_detail`
- `military`
- `role_mix`
- `income/status`

### A. `A_ask_slots/`

- 실제 본사 데이터입니다.
- 데이터 건수: `questions.jsonl` 132건
- 실험 결과 파일: `eval_results.txt`

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 94.7% | 85.6% | `90.4%` |

`conditional slot accuracy`는
"바로 job_code로 분류되지 않고, 재질의가 필요하다고 안내된 케이스 중
실제 slot까지 정확히 맞췄는가"를 보는 지표라서
가장 중요하게 해석했습니다.

### B. `B_ask_slots/claude`, `B_ask_slots/gemini`

- 본사 데이터 일부를 예시로 주고, 유사 데이터를 생성했습니다.
- 질의 생성 모델: `claude-sonnet-4-6`, `gemini-3.0-flash`

데이터 건수는 아래와 같습니다.

- `B_ask_slots/claude/questions.jsonl`: 387건
- `B_ask_slots/gemini/questions.jsonl`: 396건

Claude 실험 결과:

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 23.8% | 16.5% | `69.6%` |

Gemini 실험 결과:

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 18.4% | 14.6% | `79.5%` |

## 2. `result/classify_now/`

추가 재질의 없이 바로 직업코드로 분류할 수 있는지를 평가한 자료입니다.
즉, 고객 발화를 보고 적절한 `job_code`를 후보 상위권에 얼마나 잘 올리는지를 확인합니다.

### A. `A_job_classify_now/`

- 실제 본사 데이터입니다.
- 데이터 건수: `questions.jsonl` 165건
- 실험 결과 파일: `eval_results_20260415_181654.txt`

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|
| 65.45% | 92.73% | 95.76% | 98.18% | 0.7737 | 0.7804 | 0.7844 |

### B. `B_job_classify_now/`

- 직업코드 설명을 예시로 주고, 각 직업코드에 대응하는 질의를 생성했습니다.
- 질의 생성 모델: `claude-sonnet-4-6`
- 데이터 건수: `questions.jsonl` 680건
- 임의 RAG를 사용하여 질문과 가장 유사한 직업코드가 Ground Truth가 맞는지 검증했습니다.
- 실험 결과 파일: `eval_results_20260416_104110.txt`
- 실험 후, 오답에 대해서 `gpt-5.4`를 사용해 Groud Truth와
  예측값(직업급수서비스) 중 무엇이 더 정답에 가까운지 검증했습니다.
- 전부 GT를 제시한 것으로 보아, 난이도는 낮지만 정확도는 높은
  LLM 데이터셋으로 해석했습니다.

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@1 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 94.85% | 99.12% | 99.41% | 99.41% | 0.9485 | 0.9694 | 0.9701 | 0.9701 |

### C. `C_job_classify_now/`

- 직업코드 설명 2개를 예시로 주고, 복수 직업을 가진 사람의 질의를 생성했습니다.
- 질의 생성 모델: `claude-sonnet-4-6`
- 데이터 건수: `questions.jsonl` 85건
- `job_code`는 문자열 하나일 수도 있고 배열일 수도 있습니다.
- 직업 등급이 다른 경우에는 등급이 낮은 문자열 하나를 사용했고, 직업 등급이 같은 경우에는 배열에 직업코드를 모두 포함시켰습니다.
- 임의 RAG를 사용하여 질문과 가장 유사한 직업코드가 Ground Truth가 맞는지 검증했습니다.
- 실험 결과 파일: `eval_results_20260414_152833.txt`

| Recall@1 | Recall@10 | MRR@10 |
|---:|---:|---:|
| 70.59% | 100.00% | 0.8529 |

### D. `D_job_classify_now/`

- 본사 데이터 일부를 예시로 주고, few-shot 방식으로 유사 데이터를 생성했습니다.
- 질의 생성 모델: `gemini-3.0-flash`
- Ground Truth `job_code`는 임의 RAG 기반으로 생성되어 일부 부정확한 데이터가 포함되었을 가능성이 있습니다.
- 데이터 건수: `questions.jsonl` 495건
- 실험 결과 파일: `eval_results_20260416_092643.txt`

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|
| 43.23% | 66.06% | 75.15% | 81.41% | 0.5350 | 0.5558 | 0.5650 |

`verify_results_20260416_102607.txt`를 기준으로 재검증하면 다음과 같습니다.

- GT가 맞다고 판단: 124건
- Pred가 맞다고 판단: 157건

따라서 전체 데이터셋 495건 중 GT가 틀린 것으로 보이는 124건을 제외하면, 최종 점수는 `(495 - 124) / 495 = 74.94%`로 해석할 수 있습니다.

## 📊성능 로그 해석

### `classify_now/*/eval_results_*.txt`

직업 분류 실험 요약 파일입니다. 파일마다 지표 이름이 조금씩 다를 수 있지만 의미는 같습니다.

예시:

```text
평가 완료: 680/680건 (에러 0건)
Recall@1       : 645/680 = 94.85%
Recall@3       : 674/680 = 99.12%
Recall@5       : 676/680 = 99.41%
Recall@10      : 676/680 = 99.41%
MRR@5          : 0.9701
```

- `Recall@1`: 1순위 예측이 정답인 비율
- `Recall@N`: 정답이 상위 N개 후보 안에 포함된 비율
- `MRR@N`: 정답 순위의 역수 평균으로, 1에 가까울수록 좋습니다.
- 일부 파일에는 오분류 상세 내역이 이어서 기록됩니다.

### `classify_now/*/verify_results_*.txt`

오분류처럼 보인 케이스를 다시 검증하기 위해,
LLM에게 GT와 Pred 중 어느 직업코드가 더 타당한지 질의한 결과입니다.

- 사용 모델: `gpt-5.4`

예시:

```text
# 54 GT=25300(유치원 교사) Pred=24720(보육 교사) → GT
```

- `GT`: LLM 생성 데이터의 정답값
- `Pred`: 직업급수서비스가 예측한 값
- `→ GT`: LLM 생성 데이터 쪽이 더 타당하다고 재판정
- `→ Pred`: 직업급수서비스 예측값이 더 타당하다고 재판정

### `ask_slots/*/eval_results.txt`

추가 질문 필요 여부와 slot 분류 정확도를 요약한 파일입니다.

예시:

```text
total: 132
ask_followup rate (recall): 125/132 = 0.947
slot accuracy (overall):    113/132 = 0.856
slot accuracy | ask_followup: 113/125 = 0.904
```

- 로그의 `ask_followup rate (recall)`은 이 README에서 `Recall@1`로 통일해 표기했습니다.
- `Recall@1`: 추가 질문이 필요한 케이스를 놓치지 않고 잡아낸 비율
- `slot accuracy (overall)`: 전체 데이터 기준 slot 예측 정확도
- `slot accuracy | ask_followup`: 추가 질문이 필요하다고 판단한 케이스 중 slot 종류까지 맞춘 비율
- 이 문서에서는 `slot accuracy | ask_followup`, 즉 `conditional slot accuracy`를 가장 중요한 지표로 해석했습니다.

## ⚙️임의 RAG

Ground Truth `job_code`를 빠르게 추정하거나 생성 데이터를 1차 검증할 때,
아래와 같은 임의 RAG 파이프라인을 사용했습니다.

- 검색 방식: hybrid embedding (`dense 0.7 + sparse 0.3`)
- 1차 후보 추출: hybrid 검색으로 상위 10개 후보 추출
- 2차 정렬: reranker로 최종 순위 재정렬
- dense embedding 모델: `text-embedding-3-large`
- sparse embedding 방식: `Kiwi` 형태소 분석 기반 BM25
- reranker 모델: `dragonkue/bge-reranker-v2-m3-ko`
