#!/usr/bin/env python3
"""
Aggregate uptake labels for invocation aftermath coding results.

Usage:
python analyze_invocation_uptake.py \
  --base-csv analysis_ai_refs/invocation_uptake_coding_sample.csv \
  --labels-csv analysis_ai_refs/invocation_uptake_coding_sample_labeled.csv \
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


def main() -> None:
    args = parse_args()
    base_df = pd.read_csv(args.base_csv)
    labels_df = pd.read_csv(args.labels_csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = base_df.merge(labels_df, on="mention_uid", how="left", suffixes=("", "_labeled"))
    uptake = df["uptake_label"].fillna("").replace("", pd.NA)

    results: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "n_labeled_rows": int(uptake.notna().sum()),
        "uptake_label_counts": uptake.value_counts(dropna=True).to_dict(),
        "uptake_label_pct": (uptake.value_counts(normalize=True, dropna=True) * 100).round(2).to_dict(),
    }

    labeled = df.loc[uptake.notna()].copy()
    for group_col, out_name in [
        ("invocation_speaker_role", "uptake_by_role"),
        ("invocation_timing_phase", "uptake_by_timing"),
        ("merged", "uptake_by_merged"),
    ]:
        if group_col in labeled.columns:
            results[out_name] = (
                labeled.pivot_table(
                    index=group_col,
                    columns="uptake_label",
                    values="mention_uid",
                    aggfunc="count",
                    fill_value=0,
                ).to_dict(orient="index")
            )

    (output_dir / "invocation_uptake_summary.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
