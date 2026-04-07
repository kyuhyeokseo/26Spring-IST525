#!/usr/bin/env python3
"""
Run Ollama-based second-pass refinement over suggestion-only mentions.

Usage:
python run_ollama_suggestion_refinement.py \
  --input-csv analysis_ai_refs/suggestion_refinement_human_mentions.csv \
  --output-csv analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv \
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


SYSTEM_PROMPT = """You refine GitHub PR AI mentions that were already labeled as Suggestion.
Return valid JSON only.

Suggestion subtype labels:
- Suggestion-Invocation: directly invokes an AI agent/tool with an address like @copilot or @claude.
- Suggestion-Recommendation: recommends using AI without directly addressing it.
- Suggestion-TaskDelegation: assigns a concrete piece of work to AI, such as fixing tests, implementing a feature, or addressing feedback.
- Suggestion-StepInstruction: directs AI through explicit sequential or phased steps.

Addressing mode labels:
- Talking-to-AI: text is addressed to AI as an interaction partner.
- Talking-about-AI: text discusses AI without addressing it directly.
- Mixed: both are meaningfully present.
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
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--tail-chars", type=int, default=250)
    parser.add_argument("--no-rationale", action="store_true")
    return parser.parse_args()


def truncate_text(text: Any, max_chars: int, tail_chars: int) -> str:
    value = "" if pd.isna(text) else str(text)
    if len(value) <= max_chars:
        return value
    marker = "\n...[TRUNCATED]...\n"
    head_chars = max_chars - tail_chars - len(marker)
    if head_chars < 150:
        head_chars = max_chars // 2
        tail_chars = max_chars - head_chars - len(marker)
    return value[:head_chars] + marker + value[-tail_chars:]


def build_user_prompt(row: pd.Series, max_chars: int, tail_chars: int, no_rationale: bool) -> str:
    payload = {
        "mention_uid": row["mention_uid"],
        "speaker_role": row.get("speaker_role", ""),
        "mention_location": row.get("mention_location", ""),
        "timing_phase": row.get("timing_phase", ""),
        "mention_order_label": row.get("mention_order_label", ""),
        "mention_body": truncate_text(row.get("mention_body", ""), max_chars=max_chars, tail_chars=tail_chars),
    }
    rationale_line = "Omit rationale." if no_rationale else "Include a short rationale."
    return (
        "Refine this Suggestion mention.\n"
        "Return JSON only with keys: mention_uid, suggestion_subtype, addressing_mode, confidence, rationale. "
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
        prompt = build_user_prompt(
            row,
            max_chars=args.max_chars,
            tail_chars=args.tail_chars,
            no_rationale=args.no_rationale,
        )
        text = call_ollama(args.base_url, args.model, prompt, args.timeout)
        parsed = parse_json_text(text)
        rows.append(
            {
                "mention_uid": mention_uid,
                "suggestion_subtype": parsed.get("suggestion_subtype", ""),
                "addressing_mode": parsed.get("addressing_mode", ""),
                "refinement_confidence": parsed.get("confidence", ""),
                "refinement_rationale": parsed.get("rationale", ""),
            }
        )
        completed_uids.add(mention_uid)
        processed_in_run += 1
        pd.DataFrame(rows).to_csv(output_path, index=False)
        if args.sleep > 0:
            time.sleep(args.sleep)
        if processed_in_run % 25 == 0:
            print(f"Processed {processed_in_run} new rows...")

    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Saved {len(rows)} labeled rows to {output_path}")


if __name__ == "__main__":
    main()
