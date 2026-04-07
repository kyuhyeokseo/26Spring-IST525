#!/usr/bin/env python3
"""
Build suggestion-only refinement inputs from the first-pass human labeling results.

Outputs:
- suggestion_refinement_human_mentions.csv
- suggestion_refinement_prompt.md
- suggestion_refinement_schema.json

Usage:
python build_suggestion_refinement_inputs.py \
  --base-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --labels-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --output-dir analysis_ai_refs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REFINEMENT_LABELS = [
    "Suggestion-Invocation",
    "Suggestion-Recommendation",
    "Suggestion-TaskDelegation",
    "Suggestion-StepInstruction",
]

ADDRESSING_LABELS = [
    "Talking-to-AI",
    "Talking-about-AI",
    "Mixed",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-csv", default="analysis_ai_refs/llm_labeling_human_mentions.csv")
    parser.add_argument("--labels-csv", default="analysis_ai_refs/llm_labeling_human_mentions_labeled.csv")
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def build_prompt() -> str:
    return "\n".join(
        [
            "# Suggestion Refinement Prompt",
            "",
            "Task:",
            "You are doing a second-pass refinement for GitHub PR mentions that were already labeled as Suggestion.",
            "Refine each mention along two dimensions:",
            "1. suggestion_subtype",
            "2. addressing_mode",
            "",
            "Suggestion subtype labels:",
            "- Suggestion-Invocation: directly invokes an AI agent/tool with an address like @copilot, @claude, or a short imperative call.",
            "- Suggestion-Recommendation: recommends using AI, or suggests AI as an option, without directly tasking it.",
            "- Suggestion-TaskDelegation: assigns a concrete piece of work to AI, often larger than a single edit, such as fixing tests, implementing a feature, or addressing PR feedback.",
            "- Suggestion-StepInstruction: directs AI through phased or sequential steps, e.g. implement phase 1, continue to next step, do X then Y.",
            "",
            "Addressing mode labels:",
            "- Talking-to-AI: the text is addressed to the AI system/agent as an interaction partner.",
            "- Talking-about-AI: the text discusses AI or AI usage without addressing it directly.",
            "- Mixed: both are meaningfully present.",
            "",
            "Notes:",
            "- A mention can be both Invocation and TaskDelegation in spirit, but choose the single best suggestion_subtype.",
            "- If the utterance is directly addressed to AI, prefer Talking-to-AI.",
            "- Very short agent calls like '@copilot' or '@claude review' are usually Suggestion-Invocation and Talking-to-AI.",
            "- If the mention says content was generated with AI, that is usually Talking-about-AI rather than Talking-to-AI.",
            "",
            "Return JSON only with this shape:",
            '{"mention_uid":"...", "suggestion_subtype":"...", "addressing_mode":"...", "confidence":"high", "rationale":"..."}',
        ]
    )


def write_schema(output_dir: Path) -> None:
    schema = {
        "output_format": "json",
        "fields": {
            "mention_uid": "string, must exactly match the input mention_uid",
            "suggestion_subtype": REFINEMENT_LABELS,
            "addressing_mode": ADDRESSING_LABELS,
            "confidence": ["low", "medium", "high"],
            "rationale": "short explanation, 1 sentence preferred",
        },
    }
    (output_dir / "suggestion_refinement_schema.json").write_text(
        json.dumps(schema, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    base_df = pd.read_csv(args.base_csv)
    labels_df = pd.read_csv(args.labels_csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merged = base_df.merge(
        labels_df[["mention_uid", "llm_primary_label"]],
        on="mention_uid",
        how="inner",
        suffixes=("", "_labeled"),
    )
    primary = merged["llm_primary_label_labeled"].replace({"Explaination": "Explanation"})
    suggestions = merged.loc[primary == "Suggestion"].copy()

    suggestions["suggestion_subtype"] = ""
    suggestions["addressing_mode"] = ""
    suggestions["refinement_confidence"] = ""
    suggestions["refinement_rationale"] = ""

    cols = [
        "mention_uid",
        "repo_name",
        "pr_number",
        "mention_id",
        "user_login",
        "speaker_role",
        "mention_location",
        "mention_time",
        "timing_phase",
        "mention_order_label",
        "mention_body",
        "suggestion_subtype",
        "addressing_mode",
        "refinement_confidence",
        "refinement_rationale",
    ]
    suggestions[cols].to_csv(output_dir / "suggestion_refinement_human_mentions.csv", index=False)
    (output_dir / "suggestion_refinement_prompt.md").write_text(build_prompt(), encoding="utf-8")
    write_schema(output_dir)

    print(
        json.dumps(
            {
                "n_suggestion_mentions": int(len(suggestions)),
                "output_csv": str(output_dir / "suggestion_refinement_human_mentions.csv"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
