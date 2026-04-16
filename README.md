# job-test-public

직업 분류 챗봇 평가용 데이터셋 및 실험 결과를 정리한 공개 저장소입니다.

이 저장소의 중심 목적은 두 가지입니다.

1. 직업 분류 전에 추가 질문이 필요한 케이스를 골라내고, 각 상황에 맞게 필요한 추가질의`ask_slots`를 제시합니다. (ask_slots)
2. 고객이 자연어로 설명한 직업/상황을 보고 적절한 `job_code`를 맞히는 분류 성능을 평가합니다. (classify_now)

결과물 아카이브이며, 실제 데이터셋 JSONL, 평가 로그 TXT, 모델 비교 메모가 `result/` 아래에 정리되어 있습니다.

## 결과 요약

<table>
  <thead>
    <tr>
      <th>테스크</th>
      <th>폴더명</th>
      <th>실험 설명</th>
      <th>점수</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2"><code>ask_slots</code></td>
      <td><code>A_ask_slots</code></td>
      <td>본사 데이터</td>
      <td>90.4%</td>
    </tr>
    <tr>
      <td><code>B_ask_slots</code></td>
      <td>본사 데이터 few-shot 기반 유사 데이터 생성</td>
      <td>69.6%</td>
    </tr>
    <tr>
      <td rowspan="4"><code>classify_now</code></td>
      <td><code>A_job_classify_now</code></td>
      <td>본사 데이터</td>
      <td>92.73%</td>
    </tr>
    <tr>
      <td><code>B_job_classify_now</code></td>
      <td>직업코드 설명을 기반으로 데이터 생성</td>
      <td>99.12%</td>
    </tr>
    <tr>
      <td><code>C_job_classify_now</code></td>
      <td>직업코드 설명을 기반으로 복수직업 데이터 생성</td>
      <td>100%</td>
    </tr>
    <tr>
      <td><code>D_job_classify_now</code></td>
      <td>본사 데이터 few-shot 기반 유사 데이터 생성</td>
      <td>74.94%</td>
    </tr>
  </tbody>
</table>

## 저장소 구조

```text
job-test-public/
├── README.md
├── gitignore
└── result/
    ├── similar_job_dictionary.json
    ├── ask_slots/
    │   ├── job_code_classifier_ask_slots_only.jsonl
    │   ├── A_ask_slots/
    │   │   ├── ask_slot_question.jsonl
    │   │   ├── eval_results.jsonl
    │   │   └── eval_results.txt
    │   └── B_ask_slots/
    │       ├── claude/
    │       │   ├── B_fq_final_question_claude.jsonl
    │       │   ├── eval_results_claude.jsonl
    │       │   └── eval_results_claude.txt
    │       └── gemini/
    │           ├── A_fq_final_question_gemini.jsonl
    │           ├── eval_result_gemini.jsonl
    │           └── eval_result_gemini.txt
    ├── classify_now/
    │   ├── questions.jsonl
    │   ├── A_job_classify_now/
    │   │   ├── A_final_question.jsonl
    │   │   └── eval_result_20260415_181654.txt
    │   ├── B_job_classify_now/
    │   │   ├── B_final_question.jsonl
    │   │   ├── eval_result_20260416_104110.txt
    │   │   └── verify_result_20260416_110116.txt
    │   ├── C_job_classify_now/
    │   │   ├── C_final_question.jsonl
    │   │   └── eval_result_20260414_152833.txt
    │   └── D_job_classify_now/
    │       ├── D_final_question.jsonl
    │       ├── eval_result_20260416_092643.txt
    │       └── verify_result_20260416_102607.txt
    └── compare_llm_models/
        ├── README.md
        └── google_models_limit.png
```

## 핵심 산출물 요약

### 1. `result/similar_job_dictionary.json`

- `job_code` 앞 4자리가 같은 유사 직업군을 묶은 사전입니다.
- 같은 prefix에 2개 이상 직업 코드가 있는 경우만 포함합니다.
- 예시:

```json
{
  "1110": ["11102", "11103", "11104"]
}
```

이 파일은 유사한 직업끼리 헷갈리지 않는 질문을 만들 때 기준 데이터로 사용된 것으로 보입니다.

### 2. `result/classify_now/`

직업 분류 챗봇 자체의 성능을 검증하는 데이터셋과 평가 결과입니다.

주요 파일 수:

- `questions.jsonl`: 165건
- `A_final_question.jsonl`: 165건
- `B_final_question.jsonl`: 680건
- `C_final_question.jsonl`: 85건
- `D_final_question.jsonl`: 495건

각 세트의 의미는 다음과 같습니다.

#### A. `A_job_classify_now/`

- 실제 상담/현업형 질문 데이터를 정답 라벨과 함께 정리한 평가셋입니다.
- `questions.jsonl`은 질문만 있고, `A_final_question.jsonl`은 정답 `truth_job_code`, `truth_job_name`까지 포함합니다.
- 예시:

```json
{"question": "남자인데 집에서 살림을 해. 그럼 직업은 뭘로 하지?", "truth_job_code": "B3200", "truth_job_name": "전업주부"}
```

#### B. `B_job_classify_now/`

- 단일 직업을 비교적 명확하게 지칭하는 질문 데이터셋입니다.
- 각 레코드는 `job_code`와 질문 한 쌍으로 구성됩니다.
- 예시:

```json
{"job_code": "13121", "question": "대학교나 대학원 같은 교육기관에서 총장이나 학장 직책으로 학교 전체 운영을 기획하고 교직원들을 지휘·조정하는 분, 직업이 뭔가요?"}
```

- `verify_result_*.txt`는 오분류로 보인 케이스를 별도 LLM으로 다시 확인한 검증 로그입니다.

#### C. `C_job_classify_now/`

- 유사 직업군 또는 복합 역할을 한 문장에 담은 데이터셋입니다.
- `job_code`가 문자열 하나일 수도 있고, 배열일 수도 있어 다중 라벨/후처리 결과가 함께 들어 있습니다.
- 예시:

```json
{"job_code": ["11103", "11104"], "2_code": ["11103", "11104"], "question": "평소엔 사무실에서 예산이나 정책 기획 문서 작업하다가, 현장 나가서 건축이나 토목 시설 직접 점검·감독하는 일도 해요."}
```

#### D. `D_job_classify_now/`

- 실제 현업에서 자주 나오는 짧은 판정형 질문 모음으로 보입니다.
- A/B/C보다 질문이 짧고, "어떻게 분류하나요?" 형태가 많습니다.
- 예시:

```json
{"question": "자영업자가 직접 배달까지 하는 경우 어떻게 분류하나요?", "job_code": "87394"}
```

### 3. `result/ask_slots/`

분류 전에 추가 질문이 필요한지 판정하는 실험 결과입니다.

주요 파일 수:

- `A_ask_slots/ask_slot_question.jsonl`: 132건
- `B_ask_slots/claude/B_fq_final_question_claude.jsonl`: 387건
- `B_ask_slots/gemini/A_fq_final_question_gemini.jsonl`: 396건

구성은 다음과 같습니다.

#### 공통 입력 사전: `job_code_classifier_ask_slots_only.jsonl`

- 슬롯별 대표 질문 목록을 묶어둔 파일입니다.
- 확인된 task 종류:
  - `transport_mode`
  - `multi_job`
  - `task_detail`
  - `military`
  - `role_mix`
  - `income/status`

예를 들어 `transport_mode`에는 "직접 운전하는지", "어떤 차량인지"를 더 물어봐야 하는 질문들이 들어 있습니다.

#### A. `A_ask_slots/`

- 수작업 또는 기준셋 성격의 ask-slot 평가 데이터로 보입니다.
- `ask_slot_question.jsonl`은 각 질문에 대해 필요한 슬롯 task를 라벨링해 둔 입력셋입니다.
- `eval_results.jsonl`은 모델 추론 결과, `eval_results.txt`는 요약 성능입니다.
- 예시:

```json
{"idx": 1, "task": "transport_mode", "question": "치킨집 사장인 경우 음식도 만들고 이륜차로 배달도 하는데 이런 경우에는 직업을 주방장 또는 배달업 중 무엇으로 적용해야 하나요?", "pred_decision": "ask_followup", "followup_slot": "transport_mode"}
```

#### B. `B_ask_slots/claude`, `B_ask_slots/gemini`

- 서로 다른 LLM으로 생성한 ask-slot 테스트 질문 세트와 평가 결과입니다.
- 각 모델별 질문 생성 결과와 성능 로그가 분리되어 있습니다.
- 예시:

```json
{"task": "transport_mode", "question": "오토바이로 꽃배달 하시는 분 직업코드는 어떻게 되나요?"}
```

## 성능 로그 해석

### `classify_now/*/eval_result_*.txt`

직업 분류 성능 요약입니다. 파일마다 지표 이름이 약간 다르지만 의미는 같습니다.

예시:

```text
평가 완료: 680/680건 (에러 0건)
Recall@1       : 645/680 = 94.85%
Recall@3       : 674/680 = 99.12%
Recall@5       : 676/680 = 99.41%
Recall@10      : 676/680 = 99.41%
MRR@5          : 0.9701
```

- `Recall@1` 또는 `Top-1 Accuracy/Precision`: 1순위 예측이 정답인 비율
- `Recall@3`, `Recall@5`, `Recall@10`: 정답이 상위 N개 후보 안에 포함된 비율
- `MRR@N`: 정답 순위의 역수 평균. 1에 가까울수록 좋습니다.
- 일부 파일에는 오분류 상세가 이어서 기록됩니다.

### `classify_now/*/verify_result_*.txt`

오분류처럼 보인 케이스를 재판정한 결과입니다.

예시:

```text
# 54 GT=25300(유치원 교사) Pred=24720(보육 교사) → GT
```

- `GT`: 기존 정답 라벨
- `Pred`: 분류기가 낸 예측값
- `→ GT`: 기존 라벨이 맞다고 재판정
- `→ Pred`: 예측값 쪽이 더 타당하다고 재판정

### `ask_slots/*/eval_results.txt`

추가 질문 필요 여부를 얼마나 잘 맞췄는지 요약한 파일입니다.

예시:

```text
total: 132
ask_followup rate (recall): 125/132 = 0.947
slot accuracy (overall):    113/132 = 0.856
slot accuracy | ask_followup: 113/125 = 0.904
```

- `ask_followup rate (recall)`: 추가 질문이 필요한 케이스를 놓치지 않고 잡아낸 비율
- `slot accuracy (overall)`: 전체 데이터 기준 슬롯 예측 정확도
- `slot accuracy | ask_followup`: 추가 질문이 필요하다고 판단한 케이스 중 슬롯 종류까지 맞춘 비율
- 하단 `per-task` 표에서 task별 성능을 따로 확인할 수 있습니다.

## 현재 저장된 대표 결과

확인 시점 기준 주요 수치는 다음과 같습니다.

### classify_now

| 세트 | 건수 | 대표 지표 |
|---|---:|---|
| A | 165 | Top-1 Precision 65.45%, Top-10 Recall 98.18%, MRR@10 0.7844 |
| B | 680 | Recall@1 94.85%, Recall@10 99.41%, MRR@5 0.9701 |
| C | 85 | 세부 로그 파일 존재 (`eval_result_20260414_152833.txt`) |
| D | 495 | Top-1 Accuracy 43.23%, Top-10 Recall 81.41%, MRR@10 0.5650 |

### ask_slots

| 세트 | 건수 | 대표 지표 |
|---|---:|---|
| A | 132 | ask_followup recall 94.7%, overall slot accuracy 85.6% |
| B-Claude | 387 | ask_followup recall 23.8%, overall slot accuracy 16.5% |
| B-Gemini | 396 | ask_followup recall 18.4%, overall slot accuracy 14.6% |

해석하면, 현재 저장소에 있는 결과만 기준으로는:

- `classify_now/B`는 매우 높은 분류 성능을 보입니다.
- `classify_now/D`는 실제 현업형 짧은 질문에 가까워 보여 성능이 상대적으로 낮습니다.
- `ask_slots/A`는 기준셋에서 안정적이지만, LLM 생성 질문셋인 `B_ask_slots`에서는 성능이 많이 떨어집니다.

## 모델 비교 자료

`result/compare_llm_models/README.md`에는 질문 생성용 LLM 비교 메모가 정리되어 있습니다.

- 비교 대상: `gpt-5.4`, `gpt-5-mini`, `sonnet-4.6`, `opus-4.6`, `gemini-3.0-flash`, `gemini-3.1-pro`
- 기록 기준일: 2026년 4월 10일
- 결론 요약: 질문 생성 품질 기준으로 `sonnet-4.6`을 우선 선택했고, 비용 측면에서 `gemini-3.0-flash` 병행 사용도 검토한 것으로 정리되어 있습니다.

## 빠르게 훑어보기

가장 먼저 보면 좋은 파일은 아래 순서입니다.

1. `result/classify_now/A_job_classify_now/A_final_question.jsonl`
2. `result/classify_now/B_job_classify_now/B_final_question.jsonl`
3. `result/ask_slots/A_ask_slots/eval_results.txt`
4. `result/classify_now/B_job_classify_now/eval_result_20260416_104110.txt`
5. `result/compare_llm_models/README.md`

## 참고

- 이 저장소에는 실행 스크립트나 모델 서버 코드보다 데이터셋과 평가 산출물이 중심으로 들어 있습니다.
- 따라서 "어떻게 실행하나"보다는 "어떤 테스트셋이 있고 결과를 어떻게 읽나"에 초점을 두고 문서를 작성했습니다.
