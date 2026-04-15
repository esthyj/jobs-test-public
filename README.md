# job-test-public

직업 분류 챗봇 평가를 위한 질문 데이터셋 생성 결과물 저장소.

고객이 자신의 일·상황을 자연어로 설명하면 보험 설계사가 "(고객 설명) 하시는 분은 직업이 뭔가요?" 형태로 묻고, 챗봇이 해당 `job_code`를 맞히는 시스템의 성능 평가용 데이터셋이다.

## 폴더 구조

```
job-test-public/
├── README.md
├── gitignore
└── result/
    ├── similar_job_dictionary.json    # job_code 앞 4자리가 동일한 유사 직업군 딕셔너리
    ├── classify_now/
    │   ├── A_job_classify_now/        # A: 실제 본사 데이터
    │   ├── B_job_classify_now/        # B: 직업코드 기반 단일 직업 질문 
    │   └── C_job_classify_now/        # C: 복수직업설명 문장
    └── compare_llm_models/            # LLM 모델 비교 (LMArena Elo 기준 6개 모델)
```

## 작업 개요

### 1. `similar_job_dictionary.json`
- `jobs.csv`의 `job_code` 앞 4자리(`job_code[0:4]`)를 key로 묶은 유사 직업군 딕셔너리.
- 같은 prefix에 2개 이상 `job_code`가 있는 경우만 포함.
- 구조: `{ "1110": ["11102", "11103", "11104"], ... }`

### 2. `classify_now/A` — 본사 실제 데이터 테스트 결과
- 실제 본사에서 수집된 직업 설명 데이터를 입력으로 직업 분류 챗봇을 돌린 평가 결과.
- 입력 데이터에 대한 오분류 케이스를 `eval_result_*.txt`에 기록.

### 3. `classify_now/B` — 단일 직업 질문 데이터셋
- `jobs.csv`의 각 직업에 대해 설계사가 직업을 확인하는 질문 1개씩 생성.
- similar_job_dictionary.jsonl에 직업코드가 없는 경우, 한 개의 직업 설명을 보고 질의를 생성
- similar_job_dictioanry.jsonl에 직업코드가 있는 경우, 각 직업군에 있는 모든 직업을 한 프롬프트에 넣고, 직업군 내 다른 직업코드와 구별되는 질의 생성 (similar_job_dictioanry.jsonl의 각 직업군 내 유사한 직업코드가 있어, 질의를 잘 분류하기 위함)
- 생성 모델: `claude-sonnet-4-6`
- 임베딩 검증으로 `job_code`가 다르게 분류된 행 제거: dense + BM25 hybrid + rerank → `B_final_question_rerank.jsonl` (최종)
  - **Dense 임베딩**: OpenAI `text-embedding-3-large`
  - **BM25 형태소 분석기**: `kiwipiepy` (Kiwi) + `rank_bm25`의 `BM25Okapi` (하이브리드 가중치 embed 0.7 / BM25 0.3)
  - **Reranker**: `dragonkue/bge-reranker-v2-m3-ko` (hybrid top-10 후보를 재정렬)

### 4. `classify_now/C` — 복수직업 설명 문장 데이터셋
- 유사 직업군(prefix 1개)당 직업 쌍 1개를 선택해 "낮에는 X, 밤에는 Y" 형태로 한 사람이 두 직업을 가진 상황의 설명 문장을 생성.
- 쌍 선택 우선순위: `risk_grade` 1등급 차이 → `risk_grade` 상이 → 동일.
- 후처리: `risk_grade`가 다르면 더 높은(E에 가까운) `job_code`만 남기고, 같으면 2개 모두 유지.
- 임베딩 검증으로 `job_code`가 다르게 분류된 행 제거: dense + BM25 hybrid + rerank → `C_final_question.jsonl` (최종)
  - **Dense 임베딩**: OpenAI `text-embedding-3-large`
  - **BM25 형태소 분석기**: `kiwipiepy` (Kiwi) + `rank_bm25`의 `BM25Okapi` (하이브리드 가중치 embed 0.7 / BM25 0.3)
  - **Reranker**: `dragonkue/bge-reranker-v2-m3-ko` (hybrid top-10 후보를 재정렬, GPU 가능 시 fp16)

### 5. `eval_result_*.txt` / `verify_result_*.txt` 해석 방법

#### `eval_result_*.txt` — 분류 성능 평가
각 `*_job_classify_now/` 폴더에 위치. 데이터셋을 직업 분류 챗봇에 통과시킨 결과.

**헤더 — 전체 지표**
```
데이터: A_final_question.jsonl (165/165건, 에러 0건)
소요 시간: 86.3s
  Top-1 Precision : 68/165 = 41.21%   # 1순위 예측이 정답인 비율
  Top-10 Recall   : 143/165 = 86.67%  # 정답이 상위 10개 안에 있는 비율
  MRR@10          : 0.5691            # Mean Reciprocal Rank — 정답 순위의 역수 평균 (1에 가까울수록 좋음)
```

**오분류 상세**
```
# 12 GT=87315(자가용특수차운전자) → Pred=87327 (top4) | 피보험자 본인은 차량 3.5톤이하 ...
```
- `#`: 데이터셋 내 행 번호
- `GT`: Ground Truth (정답 `job_code`·직업명)
- `Pred`: top-1 예측값
- `(topN)`: 정답이 top-10 중 N번째에 있음. `(miss)`면 top-10에 정답 없음.
- `|` 뒤는 입력 질문 원문

#### `verify_result_*.txt` — 오분류 재검증 (B 전용)
오분류로 판정된 케이스를 GPT-5.4에게 재판단시켜 GT/Pred 중 어느 쪽이 실제로 맞는지 검증.

```
  # 54 GT=25300(유치원 교사) Pred=24720(보육 교사) → GT
```
- 각 행 끝의 `→ GT` / `→ Pred`가 재판정 결과.
- `→ Pred`가 많으면 GT 라벨 자체에 노이즈가 있다는 뜻 (데이터셋 품질 이슈).

### 6. `compare_llm_models/` — LLM 성능 비교
- 동일 프롬프트(복수직업 설명 문장 생성)로 6개 모델 비교.
- 비교 대상: `gpt-5.4`, `gpt-5-mini`, `sonnet-4.6`, `opus-4.6`, `gemini-3.0-flash`, `gemini-3.1-pro`
- 선정 결과: **`sonnet-4.6`** — 사람 같은 말투를 유지하면서 가장 간결. 비용 고려하여 `gemini-3.0-flash`도 병행 사용 예정.
- 상세 결과는 `compare_llm_models/README.md` 참고.

