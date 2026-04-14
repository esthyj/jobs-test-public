import argparse
import asyncio
import csv
import json
import os
import random
import re
import sys
from itertools import combinations
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / ".env")

CSV_PATH = ROOT_DIR / "jobs.csv"
SIMILAR_DICT_PATH = ROOT_DIR / "classify_now" / "C_job_classify_now" / "similar_job_dictionary.json"
OUTPUT_DIR = BASE_DIR / "results"

MODELS = {
    "gpt-5.4": {"provider": "openai", "model": "gpt-5.4"},
    "gpt-5-mini": {"provider": "openai", "model": "gpt-5-mini"},
    "sonnet-4.6": {"provider": "anthropic", "model": "claude-sonnet-4-6"},
    "opus-4.6": {"provider": "anthropic", "model": "claude-opus-4-6"},
    "gemini-3.0-flash": {"provider": "google", "model": "gemini-3-flash-preview"},
    "gemini-3.1-pro": {"provider": "google", "model": "gemini-3.1-pro-preview"},
}

RISK_GRADE_ORDER = ["A", "B", "C", "D", "E"]

PROMPT_TEMPLATE = """복수직업을 가진 사람이 자신이 하는 일에 대해서 설명하는 문장을 생성합니다.

## 목표
아래 2개의 직업은 서로 비슷하지만 구분되어야 하는 유사 직업군에 속합니다.
한 사람이 이 2개의 직업을 동시에 갖고 있을 때, 자신이 하는 일을 설명하는 문장 1개를 생성하세요.

## 직업 쌍 (군 prefix: {prefix})

### 직업 1
- job_code: {job_code_1}
- 직업명: {job_name_1}
- 직업 설명: {description_1}
{examples_line_1}

### 직업 2
- job_code: {job_code_2}
- 직업명: {job_name_2}
- 직업 설명: {description_2}
{examples_line_2}

## 생성 규칙
1. 위 2개의 직업을 동시에 갖고 있는 고객이 자신의 일을 설명하는 **문장 1개**를 생성한다.
2. 고객은 자신의 직업명을 직접적으로 말하지 않고, 설명을 참고하여 자신이 하는 일이나 상황을 우회적으로 설명한다. 두루뭉실하지 않도록, 직업명·설명·예시에 맞도록 구체적이고 명확하게 설명한다.
   - 각 직업만의 고유한 업무·작업 환경·사용 장비·취급 대상·결과물 등 식별 가능한 디테일을 최소 1~2개 포함하여, 같은 군의 다른 직업과 명확히 구분되도록 한다.
   - 최대한 짧게 자신의 직업을 설명하되, 직업 설명이 반드시 직업 코드로 분류될 수 있어야 한다.
3. 아래와 같이 자신이 하는 일을 표현한다. 직업 2개가 X,Y라고 가정할때 다음과 같이 문장을 생성한다.
   - "낮에는 X일, 밤에는 Y일 해"
   - "X,Y 이런 일 해"
   - "X일도 하면서 Y일도 해"
   - 존댓말과 반말을 자연스럽게 섞어 다양하게 생성한다.


## 출력 형식
아래 JSON 객체 **하나**만 출력한다. 설명·주석·마크다운 코드펜스 금지.
{{"job_code": ["{job_code_1}", "{job_code_2}"], "question": "<문장>"}}"""


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_jobs_index() -> dict[str, dict]:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        index = {}
        for row in reader:
            code = (row.get("job_code") or "").strip()
            if not code:
                continue
            index[code] = {
                "job_code": code,
                "job_name": (row.get("job_name") or "").strip(),
                "description": (row.get("description") or "").strip(),
                "examples": (row.get("examples") or "").strip(),
                "risk_grade": (row.get("risk_grade") or "").strip(),
            }
    return index


def load_similar_dict() -> dict[str, list[str]]:
    with SIMILAR_DICT_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def pick_pairs(n: int, seed: int = 42) -> list[tuple[str, dict, dict]]:
    rng = random.Random(seed)
    jobs_index = load_jobs_index()
    similar_dict = load_similar_dict()

    tasks = []
    for prefix, codes in similar_dict.items():
        valid = [jobs_index[c] for c in codes if c in jobs_index and jobs_index[c]["description"]]
        if len(valid) < 2:
            continue
        pairs = list(combinations(valid, 2))
        a, b = rng.choice(pairs)
        tasks.append((prefix, a, b))
        if n and len(tasks) >= n:
            break
    return tasks


def build_prompt(prefix: str, r1: dict, r2: dict) -> str:
    ex1 = f"- 해당 직업 예시: {r1['examples']}" if r1["examples"] else ""
    ex2 = f"- 해당 직업 예시: {r2['examples']}" if r2["examples"] else ""
    return PROMPT_TEMPLATE.format(
        prefix=prefix,
        job_code_1=r1["job_code"], job_name_1=r1["job_name"],
        description_1=r1["description"], examples_line_1=ex1,
        job_code_2=r2["job_code"], job_name_2=r2["job_name"],
        description_2=r2["description"], examples_line_2=ex2,
    )


def parse_json_answer(text: str) -> dict:
    s = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.DOTALL)
    if m:
        s = m.group(1).strip()
    return json.loads(s)


async def call_openai(model: str, prompt: str) -> str:
    key = os.environ["OPENAI_API_KEY"]
    async with httpx.AsyncClient(verify=False, timeout=120) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_openai_responses(model: str, prompt: str) -> str:
    key = os.environ["OPENAI_API_KEY"]
    async with httpx.AsyncClient(verify=False, timeout=300) as client:
        resp = await client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "input": prompt},
        )
        resp.raise_for_status()
        data = resp.json()
        texts = []
        for item in data.get("output", []):
            for c in item.get("content", []) or []:
                if c.get("type") in ("output_text", "text") and c.get("text"):
                    texts.append(c["text"])
        return "".join(texts)


async def call_anthropic(model: str, prompt: str) -> str:
    key = os.environ["ANTHROPIC_API_KEY"]
    async with httpx.AsyncClient(verify=False, timeout=120) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(b["text"] for b in data["content"] if b.get("type") == "text")


async def call_google(model: str, prompt: str) -> str:
    key = os.environ["GOOGLE_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    async with httpx.AsyncClient(verify=False, timeout=120) as client:
        resp = await client.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        resp.raise_for_status()
        data = resp.json()
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)


async def call_model(label: str, spec: dict, prompt: str) -> str:
    if spec["provider"] == "openai":
        return await call_openai(spec["model"], prompt)
    if spec["provider"] == "openai_responses":
        return await call_openai_responses(spec["model"], prompt)
    if spec["provider"] == "anthropic":
        return await call_anthropic(spec["model"], prompt)
    if spec["provider"] == "google":
        return await call_google(spec["model"], prompt)
    raise ValueError(f"unknown provider for {label}")


async def call_one(label: str, spec: dict, prompt: str) -> dict:
    entry = {"model_id": spec["model"]}
    try:
        text = await call_model(label, spec, prompt)
        entry["raw"] = text
        try:
            entry["parsed"] = parse_json_answer(text)
        except Exception as e:
            entry["parse_error"] = str(e)
    except Exception as e:
        entry["error"] = f"{type(e).__name__}: {e}"
        log(f"[{label}] FAIL: {entry['error']}")
    return entry


async def run_pair(prefix: str, r1: dict, r2: dict, labels: list[str]) -> dict:
    prompt = build_prompt(prefix, r1, r2)
    results = await asyncio.gather(
        *(call_one(label, MODELS[label], prompt) for label in labels)
    )
    record = {
        "prefix": prefix,
        "pair": [r1["job_code"], r2["job_code"]],
        "job_names": [r1["job_name"], r2["job_name"]],
        "prompt": prompt,
        "models": {label: entry for label, entry in zip(labels, results)},
    }
    log(f"done prefix={prefix}")
    return record


def format_readable(record: dict) -> str:
    lines = []
    lines.append("---")
    lines.append("")
    lines.append(f"## 🏷️ prefix `{record['prefix']}`")
    lines.append("")
    lines.append("| # | job_code | 직업명 |")
    lines.append("|---|---|---|")
    lines.append(f"| 1 | `{record['pair'][0]}` | {record['job_names'][0]} |")
    lines.append(f"| 2 | `{record['pair'][1]}` | {record['job_names'][1]} |")
    lines.append("")
    lines.append("| 모델 | 생성 문장 |")
    lines.append("|---|---|")
    for label, entry in record["models"].items():
        q = (
            entry.get("parsed", {}).get("question")
            or entry.get("error")
            or entry.get("parse_error")
            or entry.get("raw", "")
        )
        q = str(q).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| **{label}** | {q} |")
    lines.append("")
    return "\n".join(lines)


async def main_async(n: int, only: list[str] | None, out_path: Path) -> None:
    tasks = pick_pairs(n)
    log(f"selected {len(tasks)} pair(s)")
    labels = only or list(MODELS.keys())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    readable_path = out_path.with_suffix(".md")
    with out_path.open("w", encoding="utf-8") as f, readable_path.open("w", encoding="utf-8") as rf:
        for prefix, r1, r2 in tasks:
            record = await run_pair(prefix, r1, r2, labels)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            rf.write(format_readable(record) + "\n")
            rf.flush()
    log(f"saved jsonl to {out_path}")
    log(f"saved readable to {readable_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=1, help="number of pairs to test")
    p.add_argument("--models", nargs="*", default=None, help="subset of model labels")
    p.add_argument("--output", type=Path, default=OUTPUT_DIR / "compare.jsonl", help="output jsonl path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(main_async(args.n, args.models, args.output))


if __name__ == "__main__":
    main()
