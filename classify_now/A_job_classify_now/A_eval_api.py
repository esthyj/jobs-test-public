"""
A_final_question.jsonl(정답 문서)의 질문을 API에 보내
Top-1 Accuracy(Precision), Top-10 Recall, MRR@10 을 측정하는 스크립트.

사용법:
    python A_eval_api.py                    # 전체
    python A_eval_api.py --n 50             # 앞 50건만
    python A_eval_api.py --workers 10       # 동시 요청 10개
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
JSONL_PATH = BASE_DIR / "A_final_question.jsonl"
API_URL = "http://3.35.12.44:5031/api/infer"


def _normalize_code(code: str) -> str:
    """GT 코드의 첫 글자가 알파벳이면 제거하여 비교용 코드 반환."""
    if code and code[0].isalpha():
        return code[1:]
    return code


def call_api(query: str) -> dict:
    resp = requests.post(
        API_URL,
        json={"query": query, "additional_info": ""},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def load_jsonl(path: Path) -> list[dict]:
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            questions.append({
                "question": row["question"].strip(),
                "job_code": row["truth_job_code"].strip(),
                "job_name": row.get("truth_job_name", "").strip(),
            })
    return questions


def evaluate(questions: list[dict], workers: int, *, out=sys.stdout) -> None:
    total = len(questions)
    top1_hit = 0
    top10_hit = 0
    rr_sum = 0.0
    errors = []
    mismatches = []

    print(f"평가 시작: {total}건, 동시 요청 {workers}개\n", file=sys.stderr)
    start = time.time()

    def task(idx: int, q: dict):
        return idx, q, call_api(q["question"])

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(task, i, q): i for i, q in enumerate(questions)}
        done = 0
        for future in as_completed(futures):
            done += 1
            try:
                idx, q, result = future.result()
            except Exception as e:
                i = futures[future]
                errors.append((i, str(e)))
                print(f"  [{done}/{total}] #{i} 에러: {e}", file=sys.stderr)
                continue

            gt_code = q["job_code"]
            gt_norm = _normalize_code(gt_code)
            pred_code = result.get("top1_code", "")
            candidates = result.get("candidates", [])
            candidate_codes = [c["job_code"] for c in candidates]

            # Top-1
            hit1 = pred_code == gt_norm

            # Top-10 Recall & RR
            hit10 = False
            rr = 0.0
            for rank, code in enumerate(candidate_codes, start=1):
                if code == gt_norm:
                    hit10 = True
                    rr = 1.0 / rank
                    break

            if hit1:
                top1_hit += 1
            if hit10:
                top10_hit += 1
            rr_sum += rr

            if not hit1:
                mismatches.append({
                    "idx": idx,
                    "gt_code": gt_code,
                    "gt_name": q["job_name"],
                    "pred_code": pred_code,
                    "top10_codes": candidate_codes,
                    "hit_at": candidate_codes.index(gt_norm) + 1 if gt_norm in candidate_codes else None,
                    "question": q["question"][:80],
                })

            if done % 50 == 0 or done == total:
                elapsed = time.time() - start
                print(f"  [{done}/{total}] {elapsed:.1f}s 경과", file=sys.stderr)

    elapsed = time.time() - start
    evaluated = total - len(errors)

    # ── 결과 출력 ──
    print("\n" + "=" * 60, file=out)
    print(f"데이터: {JSONL_PATH.name} ({evaluated}/{total}건, 에러 {len(errors)}건)", file=out)
    print(f"소요 시간: {elapsed:.1f}s", file=out)
    print("=" * 60, file=out)
    print(f"  Top-1 Precision : {top1_hit}/{evaluated} = {top1_hit/evaluated*100:.2f}%", file=out)
    print(f"  Top-10 Recall   : {top10_hit}/{evaluated} = {top10_hit/evaluated*100:.2f}%", file=out)
    print(f"  MRR@10          : {rr_sum/evaluated:.4f}", file=out)
    print("=" * 60, file=out)

    # 틀린 건 상세
    if mismatches:
        print(f"\n오분류 상세 ({len(mismatches)}건):", file=out)
        mismatches.sort(key=lambda m: m["idx"])
        for m in mismatches:
            hit_str = f"top{m['hit_at']}" if m["hit_at"] else "miss"
            print(f"  #{m['idx']:>3d} GT={m['gt_code']}({m['gt_name']}) → Pred={m['pred_code']} ({hit_str}) | {m['question']}", file=out)


def main():
    parser = argparse.ArgumentParser(description="A_final_question.jsonl API 정확도 평가")
    parser.add_argument("--n", type=int, default=0, help="평가할 질문 수 (0=전체)")
    parser.add_argument("--workers", type=int, default=5, help="동시 요청 수 (기본 5)")
    args = parser.parse_args()

    questions = load_jsonl(JSONL_PATH)

    if args.n > 0:
        questions = questions[: args.n]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = BASE_DIR / f"eval_result_{timestamp}.txt"

    with open(result_path, "w", encoding="utf-8") as result_file:
        evaluate(questions, args.workers, out=result_file)

    print(f"\n결과 저장: {result_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
