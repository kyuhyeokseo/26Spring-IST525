#!/usr/bin/env python3
"""
Compare summary metrics between the AI-reference dataset and the control dataset.

Usage example:
python compare_ai_vs_control.py \
  --ai-dir data_ai_refs \
  --control-dir data_control_refs \
  --output comparison_ai_vs_control.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai-dir", default="data_ai_refs", help="AI-reference dataset directory")
    parser.add_argument(
        "--control-dir",
        default="data_control_refs",
        help="Control dataset directory",
    )
    parser.add_argument(
        "--output",
        default="comparison_ai_vs_control.json",
        help="Path to save comparison JSON",
    )
    return parser.parse_args()


def load_dataset(base_dir: Path) -> Dict[str, pd.DataFrame]:
    return {
        "pull_requests": pd.read_csv(base_dir / "pull_requests.csv"),
        "comments": pd.read_csv(base_dir / "comments.csv"),
        "reviews": pd.read_csv(base_dir / "reviews.csv"),
    }


def summarize_dataset(label: str, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    pr_df = data["pull_requests"]
    comments_df = data["comments"]
    reviews_df = data["reviews"]

    merged = pd.to_numeric(pr_df["merged"], errors="coerce").fillna(0)
    time_to_merge = pd.to_numeric(pr_df["time_to_merge_hours"], errors="coerce")
    total_comments = pd.to_numeric(pr_df["total_comment_count_all_comments"], errors="coerce").fillna(0)
    ai_comments = pd.to_numeric(
        pr_df["ai_reference_comment_count_all_comments"], errors="coerce"
    ).fillna(0)

    return {
        "label": label,
        "n_prs": int(len(pr_df)),
        "n_repos": int(pr_df["repo_name"].nunique()) if not pr_df.empty else 0,
        "merged_rate_pct": round(float(merged.mean() * 100), 2) if not pr_df.empty else 0.0,
        "median_time_to_merge_hours": (
            round(float(time_to_merge.dropna().median()), 3) if time_to_merge.notna().any() else None
        ),
        "median_total_comments_per_pr": round(float(total_comments.median()), 2),
        "median_ai_reference_comments_per_pr": round(float(ai_comments.median()), 2),
        "mean_total_comments_per_pr": round(float(total_comments.mean()), 2),
        "mean_ai_reference_comments_per_pr": round(float(ai_comments.mean()), 2),
        "comment_ai_reference_rate_pct": round(
            float(comments_df["contains_ai_reference"].fillna(False).astype(bool).mean() * 100), 2
        )
        if not comments_df.empty
        else 0.0,
        "review_ai_reference_rate_pct": round(
            float(reviews_df["contains_ai_reference"].fillna(False).astype(bool).mean() * 100), 2
        )
        if not reviews_df.empty
        else 0.0,
        "top_languages": pr_df["repo_language"].fillna("Unknown").value_counts().head(10).to_dict(),
    }


def compute_comparison(ai_summary: Dict[str, Any], control_summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ai_reference_dataset": ai_summary,
        "control_dataset": control_summary,
        "differences": {
            "n_prs": ai_summary["n_prs"] - control_summary["n_prs"],
            "merged_rate_pct_points": round(
                ai_summary["merged_rate_pct"] - control_summary["merged_rate_pct"], 2
            ),
            "median_time_to_merge_hours": (
                None
                if ai_summary["median_time_to_merge_hours"] is None
                or control_summary["median_time_to_merge_hours"] is None
                else round(
                    ai_summary["median_time_to_merge_hours"]
                    - control_summary["median_time_to_merge_hours"],
                    3,
                )
            ),
            "median_total_comments_per_pr": round(
                ai_summary["median_total_comments_per_pr"]
                - control_summary["median_total_comments_per_pr"],
                2,
            ),
            "median_ai_reference_comments_per_pr": round(
                ai_summary["median_ai_reference_comments_per_pr"]
                - control_summary["median_ai_reference_comments_per_pr"],
                2,
            ),
            "comment_ai_reference_rate_pct_points": round(
                ai_summary["comment_ai_reference_rate_pct"]
                - control_summary["comment_ai_reference_rate_pct"],
                2,
            ),
            "review_ai_reference_rate_pct_points": round(
                ai_summary["review_ai_reference_rate_pct"]
                - control_summary["review_ai_reference_rate_pct"],
                2,
            ),
        },
    }


def main() -> None:
    args = parse_args()
    ai_dir = Path(args.ai_dir)
    control_dir = Path(args.control_dir)

    ai_data = load_dataset(ai_dir)
    control_data = load_dataset(control_dir)

    ai_summary = summarize_dataset("ai_reference", ai_data)
    control_summary = summarize_dataset("control", control_data)
    comparison = compute_comparison(ai_summary, control_summary)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
