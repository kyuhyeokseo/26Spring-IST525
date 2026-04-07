#!/usr/bin/env python3
"""
Aggregate and summarize LLM-labeled AI mention functions.

Expected input CSV columns:
- mention_uid
- llm_primary_label
- llm_secondary_label
- llm_confidence
- llm_contains_multiple_functions
- llm_rationale

Usage example:
python analyze_llm_labeled_functions.py \
  --labels-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --base-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-dir analysis_ai_refs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-csv", required=True, help="CSV after LLM labeling")
    parser.add_argument("--base-csv", required=True, help="Original labeling input CSV")
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labels_df = pd.read_csv(args.labels_csv)
    base_df = pd.read_csv(args.base_csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = base_df.merge(
        labels_df[
            [
                "mention_uid",
                "llm_primary_label",
                "llm_secondary_label",
                "llm_confidence",
                "llm_contains_multiple_functions",
                "llm_rationale",
            ]
        ],
        on="mention_uid",
        how="left",
        suffixes=("", "_labeled"),
    )

    primary = df["llm_primary_label_labeled"].fillna("").replace("", pd.NA)
    confidence = df["llm_confidence_labeled"].fillna("").replace("", pd.NA)

    results: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "n_labeled_rows": int(primary.notna().sum()),
        "primary_label_counts": primary.value_counts(dropna=True).to_dict(),
        "primary_label_pct": (primary.value_counts(normalize=True, dropna=True) * 100).round(2).to_dict(),
        "confidence_counts": confidence.value_counts(dropna=True).to_dict(),
    }

    if "speaker_role" in df.columns:
        role_breakdown = (
            df.loc[primary.notna()]
            .pivot_table(index="speaker_role", columns="llm_primary_label_labeled", values="mention_uid", aggfunc="count", fill_value=0)
            .to_dict(orient="index")
        )
        results["primary_label_by_role"] = role_breakdown

    if "mention_location" in df.columns:
        location_breakdown = (
            df.loc[primary.notna()]
            .pivot_table(index="mention_location", columns="llm_primary_label_labeled", values="mention_uid", aggfunc="count", fill_value=0)
            .to_dict(orient="index")
        )
        results["primary_label_by_location"] = location_breakdown

    if "timing_phase" in df.columns:
        timing_breakdown = (
            df.loc[primary.notna()]
            .pivot_table(index="timing_phase", columns="llm_primary_label_labeled", values="mention_uid", aggfunc="count", fill_value=0)
            .to_dict(orient="index")
        )
        results["primary_label_by_timing"] = timing_breakdown

    (output_dir / "llm_labeled_function_summary.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
