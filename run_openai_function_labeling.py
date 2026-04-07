#!/usr/bin/env python3
"""
Run OpenAI-based function labeling over prepared mention CSV rows.

Expected environment variable:
- OPENAI_API_KEY

Usage example:
python run_openai_function_labeling.py \
  --input-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --model gpt-5-mini \
  --limit 100
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
from openai import OpenAI


SYSTEM_PROMPT = """You classify the social function of AI-reference mentions in GitHub PR discussions.
Return valid JSON only.

Available labels:
- Justification: Uses AI mention to defend, justify, or legitimize a code/design choice.
- Explanation: Uses AI mention to disclose provenance, explain where content came from, or document process.
- Suggestion: Recommends using an AI tool or directly asks an AI tool/agent to do something.
- Critique: Challenges the quality, correctness, or appropriateness of AI-generated output.
- Meta discussion: Talks about policy, norms, trust, or philosophy of AI use.
- Other: AI mention is present but the main function does not fit the labels above.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def ensure_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required.")
    return api_key


def build_user_prompt(row: pd.Series) -> str:
    payload = {
        "mention_uid": row["mention_uid"],
        "speaker_role": row.get("speaker_role", ""),
        "mention_location": row.get("mention_location", ""),
        "timing_phase": row.get("timing_phase", ""),
        "mention_order_label": row.get("mention_order_label", ""),
        "is_bot_like": bool(row.get("is_bot_like", False)),
        "heuristic_function_label": row.get("heuristic_function_label", ""),
        "mention_body": row.get("mention_body", ""),
    }
    return (
        "Classify the social function of this AI-reference mention.\n"
        "Return JSON only with keys: mention_uid, primary_label, secondary_label, "
        "confidence, contains_multiple_functions, rationale.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def extract_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    texts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", "") == "output_text":
                texts.append(getattr(content, "text", ""))
    return "\n".join(texts).strip()


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


def main() -> None:
    args = parse_args()
    api_key = ensure_api_key()

    input_path = Path(args.input_csv)
    output_path = Path(args.output_csv)

    df = pd.read_csv(input_path)
    if args.limit is not None:
        df = df.head(args.limit).copy()

    if output_path.exists() and not args.overwrite:
        raise RuntimeError(f"{output_path} already exists. Use --overwrite to replace it.")

    client = OpenAI(api_key=api_key)
    rows: list[dict[str, Any]] = []

    for index, row in df.iterrows():
        prompt = build_user_prompt(row)
        response = client.responses.create(
            model=args.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        text = extract_text(response)
        parsed = parse_json_text(text)
        rows.append(
            {
                "mention_uid": row["mention_uid"],
                "llm_primary_label": parsed.get("primary_label", ""),
                "llm_secondary_label": parsed.get("secondary_label", ""),
                "llm_confidence": parsed.get("confidence", ""),
                "llm_contains_multiple_functions": parsed.get("contains_multiple_functions", ""),
                "llm_rationale": parsed.get("rationale", ""),
            }
        )
        if args.sleep > 0:
            time.sleep(args.sleep)
        if (index + 1) % 25 == 0:
            print(f"Processed {index + 1} rows...")

    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Saved {len(rows)} labeled rows to {output_path}")


if __name__ == "__main__":
    main()
