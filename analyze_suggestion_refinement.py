#!/usr/bin/env python3
"""
Aggregate suggestion refinement results.

Usage:
python analyze_suggestion_refinement.py \
  --base-csv analysis_ai_refs/suggestion_refinement_human_mentions.csv \
  --labels-csv analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv \
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
    parser.add_argument("--base-csv", required=True)
    parser.add_argument("--labels-csv", required=True)
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def counts_table(df: pd.DataFrame, index: str, column: str) -> dict[str, Any]:
    return (
        df.pivot_table(index=index, columns=column, values="mention_uid", aggfunc="count", fill_value=0)
        .to_dict(orient="index")
    )


def main() -> None:
    args = parse_args()
    base_df = pd.read_csv(args.base_csv)
    labels_df = pd.read_csv(args.labels_csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = base_df.merge(labels_df, on="mention_uid", how="left", suffixes=("", "_labeled"))
    subtype = df["suggestion_subtype_labeled"].fillna("").replace("", pd.NA)
    addressing = df["addressing_mode_labeled"].fillna("").replace("", pd.NA)
    df["refined_subtype"] = subtype
    df["refined_addressing"] = addressing

    results: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "n_labeled_rows": int(subtype.notna().sum()),
        "suggestion_subtype_counts": subtype.value_counts(dropna=True).to_dict(),
        "suggestion_subtype_pct": (subtype.value_counts(normalize=True, dropna=True) * 100).round(2).to_dict(),
        "addressing_mode_counts": addressing.value_counts(dropna=True).to_dict(),
        "addressing_mode_pct": (addressing.value_counts(normalize=True, dropna=True) * 100).round(2).to_dict(),
    }

    labeled = df.loc[subtype.notna()].copy()
    if "speaker_role" in labeled.columns:
        results["subtype_by_role"] = counts_table(labeled, "speaker_role", "refined_subtype")
        results["addressing_by_role"] = counts_table(labeled, "speaker_role", "refined_addressing")
    if "timing_phase" in labeled.columns:
        results["subtype_by_timing"] = counts_table(labeled, "timing_phase", "refined_subtype")
        results["addressing_by_timing"] = counts_table(labeled, "timing_phase", "refined_addressing")
    if "mention_location" in labeled.columns:
        results["subtype_by_location"] = counts_table(labeled, "mention_location", "refined_subtype")
        results["addressing_by_location"] = counts_table(labeled, "mention_location", "refined_addressing")

    (output_dir / "suggestion_refinement_summary.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
