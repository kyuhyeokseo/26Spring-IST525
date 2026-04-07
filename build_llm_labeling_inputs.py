#!/usr/bin/env python3
"""
Build full-input CSVs for LLM-based function labeling of AI-reference mentions.

Outputs:
- llm_labeling_all_mentions.csv
- llm_labeling_human_mentions.csv
- llm_labeling_bot_mentions.csv
- llm_labeling_schema.json
- llm_labeling_prompt_human.md
- llm_labeling_prompt_bot.md

Usage example:
python build_llm_labeling_inputs.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from analyze_ai_reference_patterns import assign_roles, assign_timing, build_ai_mentions, load_data
from build_ai_function_coding_sample import bot_flag, heuristic_label, normalize_text


LABELS = [
    "Justification",
    "Explanation",
    "Suggestion",
    "Critique",
    "Meta discussion",
    "Other",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data_ai_refs")
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def build_mentions_table(input_dir: Path) -> pd.DataFrame:
    pr_df, comments_df, reviews_df = load_data(input_dir)
    mentions = build_ai_mentions(pr_df, comments_df, reviews_df)
    mentions = assign_roles(mentions, comments_df, reviews_df)
    mentions = assign_timing(mentions)
    mentions = mentions.copy()
    mentions["mention_body"] = mentions["mention_body"].map(normalize_text)
    mentions["is_bot_like"] = mentions["user_login"].map(bot_flag)
    mentions["heuristic_function_label"] = mentions["mention_body"].map(heuristic_label)
    mentions["mention_uid"] = mentions.apply(
        lambda row: f"{row['repo_name']}#{int(row['pr_number'])}:{row['mention_location']}:{row['mention_id']}",
        axis=1,
    )
    mentions["llm_primary_label"] = ""
    mentions["llm_secondary_label"] = ""
    mentions["llm_confidence"] = ""
    mentions["llm_rationale"] = ""
    mentions["llm_contains_multiple_functions"] = ""
    return mentions


def write_schema(output_dir: Path) -> None:
    schema = {
        "output_format": "json",
        "fields": {
            "mention_uid": "string, must exactly match the input mention_uid",
            "primary_label": LABELS,
            "secondary_label": LABELS + [""],
            "confidence": ["low", "medium", "high"],
            "contains_multiple_functions": ["true", "false"],
            "rationale": "short explanation, 1-2 sentences",
        },
    }
    (output_dir / "llm_labeling_schema.json").write_text(
        json.dumps(schema, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_prompt(audience: str) -> str:
    audience_line = (
        "Focus on human-authored collaboration language."
        if audience == "human"
        else "Focus on bot-like or tool-generated collaboration language."
    )
    return "\n".join(
        [
            f"# LLM Labeling Prompt ({audience})",
            "",
            "Task:",
            "Classify the social function of an AI-reference mention in a GitHub PR discussion.",
            audience_line,
            "",
            "Available labels:",
            "- Justification: Uses AI mention to defend, justify, or legitimize a code/design choice.",
            "- Explanation: Uses AI mention to disclose provenance, explain where content came from, or document process.",
            "- Suggestion: Recommends using an AI tool or directly asks an AI tool/agent to do something.",
            "- Critique: Challenges the quality, correctness, or appropriateness of AI-generated output.",
            "- Meta discussion: Talks about policy, norms, trust, or philosophy of AI use.",
            "- Other: AI mention is present but the main function does not fit the labels above.",
            "",
            "Instructions:",
            "- Choose exactly one `primary_label`.",
            "- Optionally choose one `secondary_label` if a second function is clearly present.",
            "- Return `contains_multiple_functions=true` only when two functions are meaningfully present.",
            "- Base the label on the function of the mention in context, not just the keyword itself.",
            "- If uncertain, prefer `Other` over overclaiming.",
            "",
            "Return JSON only with this shape:",
            '{"mention_uid":"...", "primary_label":"...", "secondary_label":"...", "confidence":"high", "contains_multiple_functions":"false", "rationale":"..."}',
        ]
    )


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mentions = build_mentions_table(input_dir)

    cols = [
        "mention_uid",
        "repo_name",
        "pr_number",
        "mention_id",
        "user_login",
        "is_bot_like",
        "speaker_role",
        "mention_location",
        "mention_time",
        "timing_phase",
        "mention_order_label",
        "heuristic_function_label",
        "mention_body",
        "llm_primary_label",
        "llm_secondary_label",
        "llm_confidence",
        "llm_contains_multiple_functions",
        "llm_rationale",
    ]

    mentions[cols].to_csv(output_dir / "llm_labeling_all_mentions.csv", index=False)
    mentions.loc[mentions["is_bot_like"] == False, cols].to_csv(
        output_dir / "llm_labeling_human_mentions.csv", index=False
    )
    mentions.loc[mentions["is_bot_like"] == True, cols].to_csv(
        output_dir / "llm_labeling_bot_mentions.csv", index=False
    )

    write_schema(output_dir)
    (output_dir / "llm_labeling_prompt_human.md").write_text(build_prompt("human"), encoding="utf-8")
    (output_dir / "llm_labeling_prompt_bot.md").write_text(build_prompt("bot"), encoding="utf-8")

    print(
        json.dumps(
            {
                "all_mentions": int(len(mentions)),
                "human_mentions": int((mentions["is_bot_like"] == False).sum()),
                "bot_mentions": int((mentions["is_bot_like"] == True).sum()),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
