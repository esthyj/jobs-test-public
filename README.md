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

### 1. `result/ask_slots/`

직업 분류 전에 추가 질문이 필요한 케이스를 골라내고, 각 상황에 맞게 필요한 추가질의 종류(slot)를 제시합니다. 
slot을 잘 분류할 수 있는지 평가한 자료입니다. 

- slot은 아래와 같습니다:
  - `transport_mode`
  - `multi_job`
  - `task_detail`
  - `military`
  - `role_mix`
  - `income/status`

| 세트 | 데이터 파일 | 건수 | 모델/출처 | Recall@1 | overall slot accuracy | conditional slot accuracy |
|---|---|---:|---|---:|---:|---:|
| A | `A_ask_slots/questions.jsonl` | 132 | 본사 데이터 | 94.7% | 85.6% | 90.4% |
| B-Claude | `B_ask_slots/claude/questions.jsonl` | 387 | `claude-sonnet-4-6` 생성 | 23.8% | 16.5% | 69.6% |
| B-Gemini | `B_ask_slots/gemini/questions.jsonl` | 396 | `gemini-3.0-flash` 생성 | 18.4% | 14.6% | 79.5% |

#### A. `A_ask_slots/`

- 실제 본사 데이터입니다. 
- 데이터 건수: `questions.jsonl` 132건
- 실험 결과 (`eval_results.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 94.7% |
| overall slot accuracy | 85.6% |
| conditional slot accuracy | 90.4% |


#### B. `B_ask_slots/claude`, `B_ask_slots/gemini`

- 데이터 건수:
  - `B_ask_slots/claude/questions.jsonl` 387건
  - `B_ask_slots/gemini/questions.jsonl` 396건
- 서로 다른 LLM (claude-sonnet-4-6, gemini-3.0-flash)으로 생성한 ask-slot 테스트 질문 세트와 평가 결과입니다.
- Claude 실험 결과 (`eval_results.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 23.8% |
| overall slot accuracy | 16.5% |
| conditional slot accuracy | 69.6% |

- Gemini 실험 결과 (`eval_results.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 18.4% |
| overall slot accuracy | 14.6% |
| conditional slot accuracy | 79.5% |


### 2. `result/classify_now/`

직업 분류 챗봇 자체의 성능을 검증하는 데이터셋과 평가 결과입니다.

각 세트의 의미는 다음과 같습니다.

#### A. `A_job_classify_now/`

- 데이터 건수: `questions.jsonl` 165건
- 실제 상담/현업형 질문 데이터를 정답 라벨과 함께 정리한 평가셋입니다.
- `A_job_classify_now/questions.jsonl`은 실제 상담형 질문에 정답 `truth_job_code`, `truth_job_name`까지 포함한 기준 평가셋입니다.
- 실험 결과 (`eval_results_20260415_181654.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 65.45% |
| Recall@3 | 92.73% |
| Recall@5 | 95.76% |
| Recall@10 | 98.18% |
| MRR@3 | 0.7737 |
| MRR@5 | 0.7804 |
| MRR@10 | 0.7844 |
- 예시:

```json
{"question": "남자인데 집에서 살림을 해. 그럼 직업은 뭘로 하지?", "truth_job_code": "B3200", "truth_job_name": "전업주부"}
```

#### B. `B_job_classify_now/`

- 데이터 건수: `questions.jsonl` 680건
- 단일 직업을 비교적 명확하게 지칭하는 질문 데이터셋입니다.
- 각 레코드는 `job_code`와 질문 한 쌍으로 구성됩니다.
- 실험 결과 (`eval_results_20260416_104110.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 94.85% |
| Recall@3 | 99.12% |
| Recall@5 | 99.41% |
| Recall@10 | 99.41% |
| MRR@1 | 0.9485 |
| MRR@3 | 0.9694 |
| MRR@5 | 0.9701 |
| MRR@10 | 0.9701 |
- 예시:

```json
{"job_code": "13121", "question": "대학교나 대학원 같은 교육기관에서 총장이나 학장 직책으로 학교 전체 운영을 기획하고 교직원들을 지휘·조정하는 분, 직업이 뭔가요?"}
```

- `verify_results_*.txt`는 오분류로 보인 케이스를 별도 LLM으로 다시 확인한 검증 로그입니다.

#### C. `C_job_classify_now/`

- 데이터 건수: `questions.jsonl` 85건
- 유사 직업군 또는 복합 역할을 한 문장에 담은 데이터셋입니다.
- `job_code`가 문자열 하나일 수도 있고, 배열일 수도 있어 다중 라벨/후처리 결과가 함께 들어 있습니다.
- 실험 결과 (`eval_results_20260414_152833.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 70.59% |
| Recall@10 | 100.00% |
| MRR@10 | 0.8529 |
- 예시:

```json
{"job_code": ["11103", "11104"], "2_code": ["11103", "11104"], "question": "평소엔 사무실에서 예산이나 정책 기획 문서 작업하다가, 현장 나가서 건축이나 토목 시설 직접 점검·감독하는 일도 해요."}
```

#### D. `D_job_classify_now/`

- 데이터 건수: `questions.jsonl` 495건
- 실제 현업에서 자주 나오는 짧은 판정형 질문 모음으로 보입니다.
- A/B/C보다 질문이 짧고, "어떻게 분류하나요?" 형태가 많습니다.
- 실험 결과 (`eval_results_20260416_092643.txt`):

| 지표 | 값 |
|---|---|
| Recall@1 | 43.23% |
| Recall@3 | 66.06% |
| Recall@5 | 75.15% |
| Recall@10 | 81.41% |
| MRR@3 | 0.5350 |
| MRR@5 | 0.5558 |
| MRR@10 | 0.5650 |
- 예시:

```json
{"question": "자영업자가 직접 배달까지 하는 경우 어떻게 분류하나요?", "job_code": "87394"}
```

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

- `Recall@1`: 1순위 예측이 정답인 비율
- `Recall@3`, `Recall@5`, `Recall@10`: 정답이 상위 N개 후보 안에 포함된 비율
- `MRR@N`: 정답 순위의 역수 평균. 1에 가까울수록 좋습니다.
- 일부 파일에는 오분류 상세가 이어서 기록됩니다.

### `classify_now/*/verify_results_*.txt`

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

- 로그의 `ask_followup rate (recall)`은 문서에서 `Recall@1`로 통일해 표기했습니다.
- `Recall@1`: 추가 질문이 필요한 케이스를 놓치지 않고 잡아낸 비율
- `slot accuracy (overall)`: 전체 데이터 기준 슬롯 예측 정확도
- `slot accuracy | ask_followup`: 추가 질문이 필요하다고 판단한 케이스 중 슬롯 종류까지 맞춘 비율
- 하단 `per-task` 표에서 task별 성능을 따로 확인할 수 있습니다.

## 모델 비교 자료

`result/compare_llm_models/README.md`에는 6개의 LLM을 기반으로 질문을 생성하고 품질을 확인해보았습니다. 

- 비교 대상: `gpt-5.4`, `gpt-5-mini`, `sonnet-4.6`, `opus-4.6`, `gemini-3.0-flash`, `gemini-3.1-pro`
- 결론 요약: 사람과 가장 유사한 품질을 보여주는 `sonnet-4.6`을 우선 선택했고, 일부 task에서는 `gemini-3.0-flash`도 병행하여 사용했습니다.