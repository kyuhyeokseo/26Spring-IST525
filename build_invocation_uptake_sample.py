#!/usr/bin/env python3
"""
Build a representative manual-coding sample for invocation uptake analysis.

The sample mixes:
- fast merged cases
- slow merged cases
- no-next-human cases
- multi-followup cases
- non-merged cases

Usage:
python build_invocation_uptake_sample.py \
  --input-csv analysis_ai_refs/invocation_aftermath_dataset.csv \
  --output-csv analysis_ai_refs/invocation_uptake_coding_sample.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default="analysis_ai_refs/invocation_aftermath_dataset.csv")
    parser.add_argument("--output-csv", default="analysis_ai_refs/invocation_uptake_coding_sample.csv")
    return parser.parse_args()


def take(df: pd.DataFrame, n: int, sort_cols: list[str], ascending: list[bool]) -> pd.DataFrame:
    if df.empty:
        return df.head(0)
    return df.sort_values(sort_cols, ascending=ascending).head(n)


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input_csv)

    sample_parts = [
        take(
            df[(df["merged"] == True) & (df["invocation_before_merge"] == True)],
            8,
            ["time_to_merge_after_invocation_hours"],
            [True],
        ),
        take(
            df[(df["merged"] == True) & (df["invocation_before_merge"] == True)],
            8,
            ["time_to_merge_after_invocation_hours"],
            [False],
        ),
        take(
            df[df["has_next_human_comment"] == False],
            6,
            ["invocation_time"],
            [True],
        ),
        take(
            df[df["n_human_followups_captured"] >= 3],
            8,
            ["pr_ai_comments", "pr_total_comments"],
            [False, False],
        ),
        take(
            df[df["merged"] == False],
            8,
            ["pr_ai_comments", "pr_total_comments"],
            [False, False],
        ),
    ]

    sample = pd.concat(sample_parts, ignore_index=True)
    sample = sample.drop_duplicates(subset=["mention_uid"]).reset_index(drop=True)

    sample["manual_uptake_label"] = ""
    sample["manual_uptake_secondary"] = ""
    sample["manual_uptake_notes"] = ""

    output_cols = [
        "mention_uid",
        "repo_name",
        "pr_number",
        "invocation_user_login",
        "invocation_speaker_role",
        "invocation_timing_phase",
        "invocation_body",
        "has_next_human_comment",
        "has_next_bot_comment",
        "latency_to_next_human_comment_hours",
        "n_human_followups_captured",
        "merged",
        "invocation_before_merge",
        "time_to_merge_after_invocation_hours",
        "pr_title",
        "next_human_1_user_login",
        "next_human_1_body",
        "next_human_2_user_login",
        "next_human_2_body",
        "next_human_3_user_login",
        "next_human_3_body",
        "manual_uptake_label",
        "manual_uptake_secondary",
        "manual_uptake_notes",
    ]
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    sample[output_cols].to_csv(args.output_csv, index=False)
    print(f"Saved {len(sample)} rows to {args.output_csv}")


if __name__ == "__main__":
    main()
