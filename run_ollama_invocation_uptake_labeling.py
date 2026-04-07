#!/usr/bin/env python3
"""
Run Ollama-based uptake labeling over invocation aftermath rows.

Usage:
python run_ollama_invocation_uptake_labeling.py \
  --input-csv analysis_ai_refs/invocation_uptake_coding_sample.csv \
  --output-csv analysis_ai_refs/invocation_uptake_coding_sample_labeled.csv \
  --model llama3.1
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests


SYSTEM_PROMPT = """You classify uptake after an AI invocation in a GitHub PR discussion.
Return valid JSON only.

Available uptake labels:
- positive_uptake: the subsequent human response accepts, confirms, resolves, or clearly builds on the invocation toward completion.
- corrective_critique: the subsequent response indicates the AI output was wrong, incomplete, failed, or requires correction.
- continued_delegation: the subsequent response mainly continues to assign more work or next steps to AI without clear acceptance or resolution.
- no_clear_uptake: no clear evidence of acceptance, correction, or continued delegation is visible in the captured follow-ups.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--model", default="llama3.1")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--max-chars", type=int, default=1500)
    parser.add_argument("--no-rationale", action="store_true")
    return parser.parse_args()


def clip(text: Any, max_chars: int) -> str:
    if pd.isna(text):
        return ""
    value = " ".join(str(text).split())
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + " ..."


def build_user_prompt(row: pd.Series, max_chars: int, no_rationale: bool) -> str:
    payload = {
        "mention_uid": row["mention_uid"],
        "invocation_body": clip(row.get("invocation_body", ""), max_chars),
        "next_human_1_body": clip(row.get("next_human_1_body", ""), max_chars),
        "next_human_2_body": clip(row.get("next_human_2_body", ""), max_chars),
        "next_human_3_body": clip(row.get("next_human_3_body", ""), max_chars),
        "merged": bool(row.get("merged", False)),
        "time_to_merge_after_invocation_hours": row.get("time_to_merge_after_invocation_hours", ""),
    }
    rationale_line = "Omit rationale." if no_rationale else "Include a short rationale."
    return (
        "Classify the uptake pattern after this AI invocation.\n"
        "Return JSON only with keys: mention_uid, uptake_label, uptake_secondary_label, confidence, rationale. "
        f"{rationale_line}\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def parse_json_text(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def call_ollama(base_url: str, model: str, prompt: str, timeout: float) -> str:
    resp = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_csv)
    output_path = Path(args.output_csv)

    if output_path.exists() and not args.overwrite and not args.resume:
        raise RuntimeError(f"{output_path} already exists. Use --overwrite to replace it.")

    df = pd.read_csv(input_path)
    if args.limit is not None:
        df = df.head(args.limit).copy()

    existing_rows: list[dict[str, Any]] = []
    completed_uids: set[str] = set()
    if output_path.exists() and args.resume:
        existing_df = pd.read_csv(output_path)
        existing_rows = existing_df.to_dict(orient="records")
        completed_uids = set(existing_df["mention_uid"].astype(str).tolist())
        print(f"Resuming with {len(completed_uids)} completed rows.")

    rows: list[dict[str, Any]] = list(existing_rows)
    processed_in_run = 0
    for _, row in df.iterrows():
        mention_uid = str(row["mention_uid"])
        if mention_uid in completed_uids:
            continue
        prompt = build_user_prompt(row, args.max_chars, args.no_rationale)
        text = call_ollama(args.base_url, args.model, prompt, args.timeout)
        parsed = parse_json_text(text)
        rows.append(
            {
                "mention_uid": mention_uid,
                "uptake_label": parsed.get("uptake_label", ""),
                "uptake_secondary_label": parsed.get("uptake_secondary_label", ""),
                "uptake_confidence": parsed.get("confidence", ""),
                "uptake_rationale": parsed.get("rationale", ""),
            }
        )
        completed_uids.add(mention_uid)
        processed_in_run += 1
        pd.DataFrame(rows).to_csv(output_path, index=False)
        if args.sleep > 0:
            time.sleep(args.sleep)
        if processed_in_run % 10 == 0:
            print(f"Processed {processed_in_run} new rows...")

    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Saved {len(rows)} labeled rows to {output_path}")


if __name__ == "__main__":
    main()
