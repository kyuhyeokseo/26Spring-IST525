#!/usr/bin/env python3
"""
Analyze discussion structure and persuasion-oriented timing around AI mentions.

Outputs:
- ai_discussion_persuasion_analysis.json
- ai_discussion_persuasion_analysis.md

Usage example:
python analyze_ai_discussion_and_persuasion.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from analyze_ai_reference_patterns import assign_roles, assign_timing, build_ai_mentions, load_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data_ai_refs")
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def build_discussion_summary(pr_df: pd.DataFrame, comments_df: pd.DataFrame, reviews_df: pd.DataFrame) -> Dict[str, Any]:
    participants_comments = comments_df[["repo_name", "pr_number", "user_login"]].dropna().drop_duplicates()
    participants_reviews = reviews_df[["repo_name", "pr_number", "user_login"]].dropna().drop_duplicates()
    participants = pd.concat([participants_comments, participants_reviews], ignore_index=True).drop_duplicates()
    participant_counts = (
        participants.groupby(["repo_name", "pr_number"]).size().reset_index(name="n_participants")
    )

    base = pr_df[
        [
            "repo_name",
            "pr_number",
            "total_comment_count_all_comments",
            "reviews_count_api",
            "review_comments_count_api",
            "ai_reference_comment_count_all_comments",
            "merged",
        ]
    ].copy()
    base = base.merge(participant_counts, on=["repo_name", "pr_number"], how="left")
    base["n_participants"] = base["n_participants"].fillna(0)
    base["merged_num"] = pd.to_numeric(base["merged"], errors="coerce").fillna(0)

    ai_prs = base.loc[base["ai_reference_comment_count_all_comments"].fillna(0) > 0].copy()
    ai_prs["reviews_count_api"] = pd.to_numeric(ai_prs["reviews_count_api"], errors="coerce").fillna(0)
    ai_prs["review_comments_count_api"] = pd.to_numeric(ai_prs["review_comments_count_api"], errors="coerce").fillna(0)
    ai_prs["total_comment_count_all_comments"] = pd.to_numeric(
        ai_prs["total_comment_count_all_comments"], errors="coerce"
    ).fillna(0)

    return {
        "median_participants_per_ai_pr": round(float(ai_prs["n_participants"].median()), 2),
        "mean_participants_per_ai_pr": round(float(ai_prs["n_participants"].mean()), 2),
        "median_comments_per_ai_pr": round(float(ai_prs["total_comment_count_all_comments"].median()), 2),
        "median_reviews_per_ai_pr": round(float(ai_prs["reviews_count_api"].median()), 2),
        "median_review_comments_per_ai_pr": round(float(ai_prs["review_comments_count_api"].median()), 2),
        "corr_ai_mentions_vs_participants": round(
            float(
                pd.to_numeric(ai_prs["ai_reference_comment_count_all_comments"], errors="coerce").fillna(0).corr(
                    ai_prs["n_participants"]
                )
            ),
            3,
        ),
    }


def build_persuasion_summary(
    pr_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> Dict[str, Any]:
    mentions = build_ai_mentions(pr_df, comments_df, reviews_df)
    mentions = assign_roles(mentions, comments_df, reviews_df)
    mentions = assign_timing(mentions)
    mentions = mentions.sort_values(["repo_name", "pr_number", "mention_time_dt", "mention_id"]).copy()

    reviews_df = reviews_df.copy()
    reviews_df["submitted_at_dt"] = pd.to_datetime(reviews_df["submitted_at"], errors="coerce", utc=True)
    pr_df = pr_df.copy()
    pr_df["merged_at_dt"] = pd.to_datetime(pr_df["merged_at"], errors="coerce", utc=True)

    first_mentions = (
        mentions.groupby(["repo_name", "pr_number"])["mention_time_dt"]
        .min()
        .reset_index(name="first_ai_mention_dt")
    )
    persuasion_df = pr_df.merge(first_mentions, on=["repo_name", "pr_number"], how="left")
    persuasion_df["has_ai_mention"] = persuasion_df["first_ai_mention_dt"].notna()

    reviews_joined = reviews_df.merge(first_mentions, on=["repo_name", "pr_number"], how="inner")
    reviews_after_ai = reviews_joined.loc[
        reviews_joined["submitted_at_dt"] >= reviews_joined["first_ai_mention_dt"]
    ].copy()

    approvals_after_ai = reviews_after_ai.loc[reviews_after_ai["state"] == "APPROVED"].copy()
    changes_requested_after_ai = reviews_after_ai.loc[reviews_after_ai["state"] == "CHANGES_REQUESTED"].copy()

    prs_with_approval_after_ai = approvals_after_ai[["repo_name", "pr_number"]].drop_duplicates()
    prs_with_changes_after_ai = changes_requested_after_ai[["repo_name", "pr_number"]].drop_duplicates()

    merged_after_ai = persuasion_df.loc[
        persuasion_df["has_ai_mention"] & persuasion_df["merged_at_dt"].notna()
    ].copy()
    if not merged_after_ai.empty:
        merged_after_ai["hours_from_first_ai_mention_to_merge"] = (
            merged_after_ai["merged_at_dt"] - merged_after_ai["first_ai_mention_dt"]
        ).dt.total_seconds() / 3600.0
    else:
        merged_after_ai["hours_from_first_ai_mention_to_merge"] = pd.Series(dtype=float)

    ai_pr_count = int(persuasion_df["has_ai_mention"].sum())

    return {
        "n_ai_prs": ai_pr_count,
        "prs_with_approval_after_first_ai_mention": int(len(prs_with_approval_after_ai)),
        "prs_with_changes_requested_after_first_ai_mention": int(len(prs_with_changes_after_ai)),
        "approval_after_ai_rate_pct": round(
            len(prs_with_approval_after_ai) / ai_pr_count * 100, 2
        )
        if ai_pr_count
        else 0.0,
        "changes_requested_after_ai_rate_pct": round(
            len(prs_with_changes_after_ai) / ai_pr_count * 100, 2
        )
        if ai_pr_count
        else 0.0,
        "median_hours_from_first_ai_mention_to_merge": round(
            float(merged_after_ai["hours_from_first_ai_mention_to_merge"].dropna().median()), 3
        )
        if merged_after_ai["hours_from_first_ai_mention_to_merge"].notna().any()
        else None,
        "mean_hours_from_first_ai_mention_to_merge": round(
            float(merged_after_ai["hours_from_first_ai_mention_to_merge"].dropna().mean()), 3
        )
        if merged_after_ai["hours_from_first_ai_mention_to_merge"].notna().any()
        else None,
    }


def build_report(results: Dict[str, Any]) -> str:
    discussion = results["discussion_structure"]
    persuasion = results["persuasion_proxy"]
    lines = [
        "# AI Discussion and Persuasion Analysis",
        "",
        "## Discussion Structure",
        f"- Median participants per AI PR: {discussion['median_participants_per_ai_pr']}",
        f"- Mean participants per AI PR: {discussion['mean_participants_per_ai_pr']}",
        f"- Median comments per AI PR: {discussion['median_comments_per_ai_pr']}",
        f"- Median reviews per AI PR: {discussion['median_reviews_per_ai_pr']}",
        f"- Median review comments per AI PR: {discussion['median_review_comments_per_ai_pr']}",
        f"- Corr(AI mentions, participants): {discussion['corr_ai_mentions_vs_participants']}",
        "",
        "## Persuasion Proxy",
        f"- AI PRs: {persuasion['n_ai_prs']}",
        f"- PRs with approval after first AI mention: {persuasion['prs_with_approval_after_first_ai_mention']}",
        f"- Approval-after-AI rate: {persuasion['approval_after_ai_rate_pct']}%",
        f"- PRs with changes requested after first AI mention: {persuasion['prs_with_changes_requested_after_first_ai_mention']}",
        f"- Changes-requested-after-AI rate: {persuasion['changes_requested_after_ai_rate_pct']}%",
        f"- Median hours from first AI mention to merge: {persuasion['median_hours_from_first_ai_mention_to_merge']}",
        f"- Mean hours from first AI mention to merge: {persuasion['mean_hours_from_first_ai_mention_to_merge']}",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pr_df, comments_df, reviews_df = load_data(input_dir)
    results = {
        "discussion_structure": build_discussion_summary(pr_df, comments_df, reviews_df),
        "persuasion_proxy": build_persuasion_summary(pr_df, comments_df, reviews_df),
    }

    (output_dir / "ai_discussion_persuasion_analysis.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "ai_discussion_persuasion_analysis.md").write_text(
        build_report(results),
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
