# job-test-public

직업 분류 챗봇 평가용 데이터셋 및 실험 결과를 정리한 공개 저장소입니다.

이 저장소의 중심 목적은 두 가지입니다.

1. **ask_slots**: 직업 분류 전에 추가 질문이 필요한 케이스를 골라내고, 각 상황에 맞게 필요한 추가질의`ask_slots`를 제시합니다. 
2. **classify_now**: 고객이 자연어로 설명한 직업/상황을 보고 적절한 `job_code`를 맞히는 분류 성능을 평가합니다.

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
      <td>90.4% (Recall@1)</td>
    </tr>
    <tr>
      <td><code>B_ask_slots</code></td>
      <td>본사 데이터 few-shot 기반 유사 데이터 생성</td>
      <td>69.6% (Recall@1)</td>
    </tr>
    <tr>
      <td rowspan="4"><code>classify_now</code></td>
      <td><code>A_job_classify_now</code></td>
      <td>본사 데이터</td>
      <td>92.73% (Recall@3)</td>
    </tr>
    <tr>
      <td><code>B_job_classify_now</code></td>
      <td>직업코드 설명을 기반으로 데이터 생성</td>
      <td>99.12% (Recall@3)</td>
    </tr>
    <tr>
      <td><code>C_job_classify_now</code></td>
      <td>직업코드 설명을 기반으로 복수직업 데이터 생성</td>
      <td>100.0% (Recall@3)</td>
    </tr>
    <tr>
      <td><code>D_job_classify_now</code></td>
      <td>본사 데이터 few-shot 기반 유사 데이터 생성</td>
      <td>74.94% (Recall@3)</td>
    </tr>
  </tbody>
</table>

## 저장소 구조

```text
job-test-public/
├── README.md
├── .gitignore
└── result/
    ├── similar_job_dictionary.json         # 앞 4자리 job_code 기준 유사 직업군을 묶은 사전
    ├── ask_slots/
    │   ├── A_ask_slots/                        # 본사 데이터
    │   │   ├── questions.jsonl                # 본사 데이터셋
    │   │   ├── eval_results.jsonl             # A 세트 상세 결과
    │   │   └── eval_results.txt               # A 세트 실험 요약
    │   └── B_ask_slots/                       # 본사 데이터 few-shot 기반 유사 데이터 생성
    │       ├── claude/
    │       │   ├── questions.jsonl            # Claude로 생성한 질문 데이터셋
    │       │   ├── eval_results.jsonl         # B 세트 (Claude) 상세 결과
    │       │   └── eval_results.txt           # B 세트 (Claude) 결과 요약
    │       └── gemini/
    │           ├── questions.jsonl            # Gemini로 생성한 질문 데이터셋
    │           ├── eval_results.jsonl         # B 세트 (Gemini) 상세 결과
    │           └── eval_results.txt           # B 세트 (Gemini) 결과 요약
    ├── classify_now/
    │   ├── A_job_classify_now/                # 본사 데이터
    │   │   ├── questions.jsonl                # 본사 질문 데이터셋
    │   │   └── eval_results_20260415_181654.txt # A 세트 실험 요약
    │   ├── B_job_classify_now/                # 직업코드 설명을 기반으로 데이터 생성
    │   │   ├── questions.jsonl                # LLM 기반 생성 데이터셋
    │   │   ├── eval_results_20260416_104110.txt # B 세트 실험 요약
    │   │   └── verify_results_20260416_110116.txt # B 세트 LLM 검증
    │   ├── C_job_classify_now/                # 직업코드 설명을 기반으로 복수직업 데이터 생성
    │   │   ├── questions.jsonl                # LLM 기반 생성 데이터셋
    │   │   └── eval_results_20260414_152833.txt # C 세트 실험 요약
    │   └── D_job_classify_now/                # 본사 데이터 few-shot 기반 유사 데이터 생성
    │       ├── questions.jsonl                # LLM 기반 생성 데이터셋
    │       ├── eval_results_20260416_092643.txt # D 세트 실험 요약
    │       └── verify_results_20260416_102607.txt # D 세트 LLM 검증
    └── compare_llm_models/
        ├── README.md                          # 모델별 결과 비교
        └── google_models_limit.png           # Google 계열 모델 비교 이미지
```

## 핵심 산출물 요약

## 모델 비교 자료

`result/compare_llm_models/README.md`에는 6개의 LLM을 기반으로 질문을 생성하고 품질을 확인해보았습니다. 

- 비교 대상: `gpt-5.4`, `gpt-5-mini`, `sonnet-4.6`, `opus-4.6`, `gemini-3.0-flash`, `gemini-3.1-pro`
- 결론 요약: 사람과 가장 유사한 품질을 보여주는 `sonnet-4.6`을 우선 선택했고, 일부 task에서는 `gemini-3.0-flash`도 병행하여 사용했습니다.

### 1. `result/ask_slots/`

직업 분류 전에 추가 질문이 필요한 케이스를 골라내고, 각 상황에 맞게 필요한 추가질의 종류(slot)를 제시합니다. 
slot을 잘 분류할 수 있는지 평가한 자료입니다. 

- slot종류는 아래와 같습니다:
  - `transport_mode`
  - `multi_job`
  - `task_detail`
  - `military`
  - `role_mix`
  - `income/status`
  

#### A. `A_ask_slots/`

- 실제 본사 데이터입니다. 
- 데이터 건수: `questions.jsonl` 132건
- 실험 결과 (`eval_results.txt`):

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 94.7% | 85.6% | `90.4%` |
> conditional slot accuracy가 바로 job_code로 분류되지 않고 '재질의가 필요하다고 안내'된 task 중 실제로 slot을 정확하게 분류했는지에 대한 지표라서 가장 중요하게 생각됩니다. 


#### B. `B_ask_slots/claude`, `B_ask_slots/gemini`

- 본사 데이터 일부를 예시 (few-shot)로 주고 유사 데이터를 생성했습니다. 
- 데이터 건수:
  - `B_ask_slots/claude/questions.jsonl` 387건
  - `B_ask_slots/gemini/questions.jsonl` 396건
- 서로 다른 LLM (claude-sonnet-4-6, gemini-3.0-flash)으로 생성한 ask-slot 테스트 질문 세트와 평가 결과입니다.
- Claude 실험 결과 (`eval_results.txt`):

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 23.8% | 16.5% | `69.6%` |

- Gemini 실험 결과 (`eval_results.txt`):

| Recall@1 | overall slot accuracy | conditional slot accuracy |
|---:|---:|---:|
| 18.4% | 14.6% | `79.5%` |


### 2. `result/classify_now/`

추가 재질의를 하기보다는 바로 직업코드로 분류되어, 정확한 직업코드로 분류할 수 있는지 평가한 자료입니다. 

#### A. `A_job_classify_now/`

- 실제 본사 데이터입니다. 
- 데이터 건수: `questions.jsonl` 165건
- 실험 결과 (`eval_results_20260415_181654.txt`):

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|
| 65.45% | 92.73% | 95.76% | 98.18% | 0.7737 | 0.7804 | 0.7844 |


#### B. `B_job_classify_now/`

- 직업코드 설명을 예시로 주고, 각 직업코드마다 관련된 질의를 생성하게끔 했습니다. 
- 데이터 건수: `questions.jsonl` 680건
- 실험 결과 (`eval_results_20260416_104110.txt`):

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@1 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 94.85% | 99.12% | 99.41% | 99.41% | 0.9485 | 0.9694 | 0.9701 | 0.9701 |


#### C. `C_job_classify_now/`

- 직업코드 설명을 2개를 예시로 주고, 복수 직업을 가진 사람의 질의를 생성하게끔 했습니다. 
- 데이터 건수: `questions.jsonl` 85건
- `job_code`가 문자열 하나일 수도 있고 배열일 수도 있습니다. (2개의 직업 등급이 다른 경우 등급이 낮은 문자열 하나이며, 직업 등급이 같은 경우 배열에 직업코드를 모두 포함시켰습니다.)
- 실험 결과 (`eval_results_20260414_152833.txt`):

| Recall@1 | Recall@10 | MRR@10 |
|---:|---:|---:|
| 70.59% | 100.00% | 0.8529 |


#### D. `D_job_classify_now/`

- 본사 데이터 일부를 예시 (few-shot)로 주고 유사 데이터를 생성했습니다.
- Ground Truth Job Code는 임의 RAG 기반으로 생성하여, 일부 부정확한 데이터가 있을 것으로 생각됩니다. 
- 데이터 건수: `questions.jsonl` 495건.
- 실험 결과 (`eval_results_20260416_092643.txt`):

| Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@3 | MRR@5 | MRR@10 |
|---:|---:|---:|---:|---:|---:|---:|
| 43.23% | 66.06% | 75.15% | 81.41% | 0.5350 | 0.5558 | 0.5650 |

verify_results~.txt를 참고하면 아래와 같아서, 전체 데이터셋 중 최종적으로 GT가 맞다고 판단한 건만 제외하면 final score는 (495-124)/495= 74.94% 입니다. 
- GT가 맞다고 판단: 124건
- Pred가 맞다고 판단: 157건

### 3. `result/similar_job_dictionary.json`

- `job_code` 앞 4자리가 같은 유사 직업군을 묶은 사전입니다.
- 같은 prefix에 2개 이상 직업 코드가 있는 경우만 포함합니다.
- 예시:

```json
{
  "1110": ["11102", "11103", "11104"]
}
```

이 파일은 유사한 직업끼리 헷갈리지 않는 질문을 만들 때 기준 데이터로 사용된 것으로 보입니다.

## 성능 로그 해석

### `classify_now/*/eval_results_*.txt`

직업 분류 실험 요약입니다. 파일마다 지표 이름이 약간 다르지만 의미는 같습니다.

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
- `MRR@N`: 정답 순위의 역수 평균. 1에 가까울수록 좋습니다.
- 일부 파일에는 오분류 상세가 이어서 기록됩니다.

### `classify_now/*/verify_results_*.txt`

오분류처럼 보인 케이스를 재검증하고자, LLM에게 GT와 Pred 중 어느 직업코드가 맞는 것 같은지 질의한 결과입니다. 
- 사용 모델: gpt-5.4

예시:

```text
# 54 GT=25300(유치원 교사) Pred=24720(보육 교사) → GT
```

- `GT`: LLM 생성 데이터
- `Pred`: 직업급수서비스가 낸 예측값
- `→ GT`: LLM 생성 데이터가 더 타당하다고 재판정
- `→ Pred`: 직업급수서비스가 더 타당하다고 재판정

### `ask_slots/*/eval_results.txt`

추가 질문 필요 여부를 얼마나 잘 맞췄는지 요약한 파일입니다.

예시:

```text
total: 132
ask_followup rate (recall): 125/132 = 0.947
slot accuracy (overall):    113/132 = 0.856
slot accuracy | ask_followup: 113/125 = 0.904
```

- 로그의 `ask_followup rate (recall)`은 문서에서 `Recall@1`로 통일해 표기했습니다.
- `Recall@1`: 추가 질문이 필요한 케이스를 놓치지 않고 잡아낸 비율
- `slot accuracy (overall)`: 전체 데이터 기준 슬롯 예측 정확도
- `slot accuracy | ask_followup`: 추가 질문이 필요하다고 판단한 케이스 중 슬롯 종류까지 맞춘 비율
- `slot accuracy | ask_followup`을 가장 중요시하게 볼 평가지표로 잡았습니다. 
