#!/usr/bin/env python3
"""
Analyze AI-reference PR patterns using already collected CSV outputs.

Focus areas:
- Who mentions AI? (author / reviewer / other commenter)
- When is AI mentioned? (early / middle / late in PR lifecycle)
- Where is AI mentioned? (issue comments / review comments / review bodies)
- How does AI mention intensity relate to PR outcomes?
- What repo / project traits are common?
- How does PR complexity relate to AI mention intensity?

Usage example:
python analyze_ai_reference_patterns.py \
  --input-dir data_ai_refs \
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
    parser.add_argument("--input-dir", default="data_ai_refs", help="Directory with collected AI CSV outputs")
    parser.add_argument("--output-dir", default="analysis_ai_refs", help="Directory to save analysis outputs")
    return parser.parse_args()


def load_data(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pr_df = pd.read_csv(input_dir / "pull_requests.csv")
    comments_df = pd.read_csv(input_dir / "comments.csv")
    reviews_df = pd.read_csv(input_dir / "reviews.csv")
    return pr_df, comments_df, reviews_df


def build_ai_mentions(pr_df: pd.DataFrame, comments_df: pd.DataFrame, reviews_df: pd.DataFrame) -> pd.DataFrame:
    pr_meta = pr_df[
        [
            "repo_name",
            "pr_number",
            "pr_user",
            "created_at",
            "closed_at",
            "merged_at",
            "updated_at",
            "merged",
            "repo_language",
            "repo_stars",
            "commits",
            "additions",
            "deletions",
            "changed_files",
            "total_comment_count_all_comments",
            "ai_reference_comment_count_all_comments",
            "time_to_merge_hours",
        ]
    ].copy()

    comments_ai = comments_df.loc[comments_df["contains_ai_reference"].fillna(False).astype(bool)].copy()
    comments_ai["mention_location"] = comments_ai["comment_type"]
    comments_ai["mention_time"] = comments_ai["created_at"]
    comments_ai["mention_id"] = comments_ai["comment_id"]
    comments_ai["mention_body"] = comments_ai["body"]
    comments_ai = comments_ai[
        ["repo_name", "pr_number", "user_login", "mention_location", "mention_time", "mention_id", "mention_body"]
    ]

    reviews_ai = reviews_df.loc[reviews_df["contains_ai_reference"].fillna(False).astype(bool)].copy()
    reviews_ai["mention_location"] = "review"
    reviews_ai["mention_time"] = reviews_ai["submitted_at"]
    reviews_ai["mention_id"] = reviews_ai["review_id"]
    reviews_ai["mention_body"] = reviews_ai["body"]
    reviews_ai = reviews_ai[
        ["repo_name", "pr_number", "user_login", "mention_location", "mention_time", "mention_id", "mention_body"]
    ]

    mentions = pd.concat([comments_ai, reviews_ai], ignore_index=True)
    mentions = mentions.merge(pr_meta, on=["repo_name", "pr_number"], how="left")
    mentions["mention_time_dt"] = pd.to_datetime(mentions["mention_time"], errors="coerce", utc=True)
    mentions["pr_created_at_dt"] = pd.to_datetime(mentions["created_at"], errors="coerce", utc=True)
    mentions["pr_closed_at_dt"] = pd.to_datetime(mentions["closed_at"], errors="coerce", utc=True)
    mentions["pr_merged_at_dt"] = pd.to_datetime(mentions["merged_at"], errors="coerce", utc=True)
    mentions["pr_updated_at_dt"] = pd.to_datetime(mentions["updated_at"], errors="coerce", utc=True)
    mentions["pr_end_dt"] = (
        mentions["pr_merged_at_dt"]
        .combine_first(mentions["pr_closed_at_dt"])
        .combine_first(mentions["pr_updated_at_dt"])
    )
    return mentions


def assign_roles(mentions: pd.DataFrame, comments_df: pd.DataFrame, reviews_df: pd.DataFrame) -> pd.DataFrame:
    review_comment_users = (
        comments_df.loc[comments_df["comment_type"] == "review_comment", ["repo_name", "pr_number", "user_login"]]
        .dropna()
        .drop_duplicates()
    )
    review_users = reviews_df[["repo_name", "pr_number", "user_login"]].dropna().drop_duplicates()
    reviewer_users = pd.concat([review_comment_users, review_users], ignore_index=True).drop_duplicates()
    reviewer_sets = reviewer_users.groupby(["repo_name", "pr_number"])["user_login"].agg(lambda s: set(s)).to_dict()

    def role_for_row(row: pd.Series) -> str:
        if pd.notna(row["user_login"]) and row["user_login"] == row["pr_user"]:
            return "author"
        reviewers = reviewer_sets.get((row["repo_name"], row["pr_number"]), set())
        if pd.notna(row["user_login"]) and row["user_login"] in reviewers:
            return "reviewer"
        return "other_commenter"

    mentions = mentions.copy()
    mentions["speaker_role"] = mentions.apply(role_for_row, axis=1)
    return mentions


def assign_timing(mentions: pd.DataFrame) -> pd.DataFrame:
    mentions = mentions.copy()
    lifecycle_seconds = (mentions["pr_end_dt"] - mentions["pr_created_at_dt"]).dt.total_seconds()
    elapsed_seconds = (mentions["mention_time_dt"] - mentions["pr_created_at_dt"]).dt.total_seconds()
    normalized = elapsed_seconds / lifecycle_seconds.where(lifecycle_seconds > 0)
    normalized = normalized.fillna(0).clip(lower=0, upper=1)
    mentions["lifecycle_progress"] = normalized

    def phase(value: float) -> str:
        if value <= 1 / 3:
            return "early"
        if value <= 2 / 3:
            return "middle"
        return "late"

    mentions["timing_phase"] = mentions["lifecycle_progress"].map(phase)
    mentions = mentions.sort_values(["repo_name", "pr_number", "mention_time_dt", "mention_id"]).copy()
    mentions["mention_order_in_pr"] = mentions.groupby(["repo_name", "pr_number"]).cumcount() + 1
    mention_counts = mentions.groupby(["repo_name", "pr_number"]).size().rename("n_ai_mentions_total")
    mentions = mentions.merge(mention_counts, on=["repo_name", "pr_number"], how="left")

    def order_label(row: pd.Series) -> str:
        if row["n_ai_mentions_total"] == 1:
            return "single"
        if row["mention_order_in_pr"] == 1:
            return "first"
        if row["mention_order_in_pr"] == row["n_ai_mentions_total"]:
            return "last"
        return "middle"

    mentions["mention_order_label"] = mentions.apply(order_label, axis=1)
    return mentions


def summarize_role_location_timing(mentions: pd.DataFrame) -> Dict[str, Any]:
    pr_role = (
        mentions.groupby("speaker_role")[["repo_name", "pr_number"]]
        .apply(lambda df: len(df.drop_duplicates()))
        .to_dict()
    )
    role_counts = mentions["speaker_role"].value_counts().to_dict()
    role_pct = (mentions["speaker_role"].value_counts(normalize=True) * 100).round(2).to_dict()

    location_counts = mentions["mention_location"].value_counts().to_dict()
    location_pct = (mentions["mention_location"].value_counts(normalize=True) * 100).round(2).to_dict()

    timing_counts = mentions["timing_phase"].value_counts().to_dict()
    timing_pct = (mentions["timing_phase"].value_counts(normalize=True) * 100).round(2).to_dict()

    order_counts = mentions["mention_order_label"].value_counts().to_dict()
    order_pct = (mentions["mention_order_label"].value_counts(normalize=True) * 100).round(2).to_dict()

    return {
        "n_ai_mentions": int(len(mentions)),
        "speaker_role_counts": role_counts,
        "speaker_role_pct": role_pct,
        "prs_with_ai_mentions_by_role": {k: int(v) for k, v in pr_role.items()},
        "mention_location_counts": location_counts,
        "mention_location_pct": location_pct,
        "timing_phase_counts": timing_counts,
        "timing_phase_pct": timing_pct,
        "mention_order_counts": order_counts,
        "mention_order_pct": order_pct,
    }


def summarize_intensity_vs_outcomes(pr_df: pd.DataFrame) -> Dict[str, Any]:
    analysis_df = pr_df.copy()
    analysis_df["merged_num"] = pd.to_numeric(analysis_df["merged"], errors="coerce").fillna(0)
    analysis_df["ai_count"] = pd.to_numeric(
        analysis_df["ai_reference_comment_count_all_comments"], errors="coerce"
    ).fillna(0)
    analysis_df["time_to_merge_hours_num"] = pd.to_numeric(
        analysis_df["time_to_merge_hours"], errors="coerce"
    )

    def intensity_bin(value: float) -> str:
        if value == 0:
            return "0"
        if value == 1:
            return "1"
        if value <= 3:
            return "2-3"
        if value <= 5:
            return "4-5"
        if value <= 10:
            return "6-10"
        return "11+"

    analysis_df["ai_intensity_bin"] = analysis_df["ai_count"].map(intensity_bin)
    grouped = analysis_df.groupby("ai_intensity_bin")
    bin_summary = {}
    for name, group in grouped:
        bin_summary[name] = {
            "n_prs": int(len(group)),
            "merge_rate_pct": round(float(group["merged_num"].mean() * 100), 2),
            "median_time_to_merge_hours": (
                round(float(group["time_to_merge_hours_num"].dropna().median()), 3)
                if group["time_to_merge_hours_num"].notna().any()
                else None
            ),
            "median_total_comments_per_pr": round(
                float(pd.to_numeric(group["total_comment_count_all_comments"], errors="coerce").fillna(0).median()), 2
            ),
        }

    return {
        "correlation_ai_mentions_vs_total_comments": round(
            float(
                analysis_df["ai_count"].corr(
                    pd.to_numeric(analysis_df["total_comment_count_all_comments"], errors="coerce").fillna(0)
                )
            ),
            3,
        ),
        "correlation_ai_mentions_vs_changed_files": round(
            float(analysis_df["ai_count"].corr(pd.to_numeric(analysis_df["changed_files"], errors="coerce").fillna(0))),
            3,
        ),
        "correlation_ai_mentions_vs_additions": round(
            float(analysis_df["ai_count"].corr(pd.to_numeric(analysis_df["additions"], errors="coerce").fillna(0))),
            3,
        ),
        "merge_rate_by_ai_intensity_bin": bin_summary,
    }


def summarize_repo_traits(pr_df: pd.DataFrame) -> Dict[str, Any]:
    df = pr_df.copy()
    df["repo_stars_num"] = pd.to_numeric(df["repo_stars"], errors="coerce").fillna(0)
    df["ai_count"] = pd.to_numeric(df["ai_reference_comment_count_all_comments"], errors="coerce").fillna(0)

    def stars_bin(value: float) -> str:
        if value == 0:
            return "0"
        if value <= 10:
            return "1-10"
        if value <= 100:
            return "11-100"
        if value <= 1000:
            return "101-1000"
        return "1000+"

    df["repo_stars_bin"] = df["repo_stars_num"].map(stars_bin)
    stars_summary = (
        df.groupby("repo_stars_bin")
        .agg(
            n_prs=("pr_number", "count"),
            median_ai_mentions=("ai_count", "median"),
            median_comments=("total_comment_count_all_comments", "median"),
        )
        .round(2)
        .to_dict(orient="index")
    )

    language_summary = (
        df.groupby("repo_language")
        .agg(
            n_prs=("pr_number", "count"),
            median_ai_mentions=("ai_count", "median"),
            merge_rate=("merged", lambda s: pd.to_numeric(s, errors="coerce").fillna(0).mean() * 100),
        )
        .sort_values("n_prs", ascending=False)
        .head(15)
        .round(2)
        .to_dict(orient="index")
    )

    return {
        "top_languages_with_ai_prs": language_summary,
        "repo_stars_distribution": stars_summary,
        "median_repo_stars": round(float(df["repo_stars_num"].median()), 2),
        "mean_repo_stars": round(float(df["repo_stars_num"].mean()), 2),
    }


def summarize_complexity(pr_df: pd.DataFrame) -> Dict[str, Any]:
    df = pr_df.copy()
    df["ai_count"] = pd.to_numeric(df["ai_reference_comment_count_all_comments"], errors="coerce").fillna(0)
    for col in ["commits", "additions", "deletions", "changed_files"]:
        df[f"{col}_num"] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    def complexity_bin(value: float) -> str:
        if value <= 1:
            return "0-1"
        if value <= 5:
            return "2-5"
        if value <= 10:
            return "6-10"
        if value <= 20:
            return "11-20"
        return "21+"

    df["changed_files_bin"] = df["changed_files_num"].map(complexity_bin)
    by_changed_files = (
        df.groupby("changed_files_bin")
        .agg(
            n_prs=("pr_number", "count"),
            median_ai_mentions=("ai_count", "median"),
            mean_ai_mentions=("ai_count", "mean"),
            merge_rate=("merged", lambda s: pd.to_numeric(s, errors="coerce").fillna(0).mean() * 100),
        )
        .round(2)
        .to_dict(orient="index")
    )

    return {
        "median_changed_files": round(float(df["changed_files_num"].median()), 2),
        "median_additions": round(float(df["additions_num"].median()), 2),
        "median_deletions": round(float(df["deletions_num"].median()), 2),
        "median_commits": round(float(df["commits_num"].median()), 2),
        "changed_files_bins": by_changed_files,
    }


def build_report(results: Dict[str, Any]) -> str:
    role = results["role_timing_location"]
    intensity = results["intensity_vs_outcomes"]
    repo = results["repo_traits"]
    complexity = results["complexity"]

    lines = [
        "# AI Reference Pattern Analysis",
        "",
        "## Who mentions AI?",
        f"- Total AI mention events: {role['n_ai_mentions']}",
    ]
    for key, value in role["speaker_role_counts"].items():
        pct = role["speaker_role_pct"].get(key, 0)
        lines.append(f"- {key}: {value} mentions ({pct}%)")

    lines.extend(
        [
            "",
            "## When is AI mentioned?",
        ]
    )
    for key, value in role["timing_phase_counts"].items():
        pct = role["timing_phase_pct"].get(key, 0)
        lines.append(f"- {key}: {value} mentions ({pct}%)")

    lines.extend(
        [
            "",
            "## Where is AI mentioned?",
        ]
    )
    for key, value in role["mention_location_counts"].items():
        pct = role["mention_location_pct"].get(key, 0)
        lines.append(f"- {key}: {value} mentions ({pct}%)")

    lines.extend(
        [
            "",
            "## Intensity vs Outcomes",
            f"- Corr(AI mentions, total comments): {intensity['correlation_ai_mentions_vs_total_comments']}",
            f"- Corr(AI mentions, changed files): {intensity['correlation_ai_mentions_vs_changed_files']}",
            f"- Corr(AI mentions, additions): {intensity['correlation_ai_mentions_vs_additions']}",
            "",
            "### Merge rate by AI intensity",
        ]
    )
    for key, value in intensity["merge_rate_by_ai_intensity_bin"].items():
        lines.append(
            f"- {key}: n={value['n_prs']}, merge_rate={value['merge_rate_pct']}%, "
            f"median_merge_hours={value['median_time_to_merge_hours']}, "
            f"median_comments={value['median_total_comments_per_pr']}"
        )

    lines.extend(
        [
            "",
            "## Repo Traits",
            f"- Median repo stars: {repo['median_repo_stars']}",
            f"- Mean repo stars: {repo['mean_repo_stars']}",
            "",
            "## PR Complexity",
            f"- Median changed files: {complexity['median_changed_files']}",
            f"- Median additions: {complexity['median_additions']}",
            f"- Median deletions: {complexity['median_deletions']}",
            f"- Median commits: {complexity['median_commits']}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pr_df, comments_df, reviews_df = load_data(input_dir)
    mentions = build_ai_mentions(pr_df, comments_df, reviews_df)
    mentions = assign_roles(mentions, comments_df, reviews_df)
    mentions = assign_timing(mentions)

    results = {
        "role_timing_location": summarize_role_location_timing(mentions),
        "intensity_vs_outcomes": summarize_intensity_vs_outcomes(pr_df),
        "repo_traits": summarize_repo_traits(pr_df),
        "complexity": summarize_complexity(pr_df),
    }

    (output_dir / "ai_reference_pattern_analysis.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "ai_reference_pattern_analysis.md").write_text(build_report(results), encoding="utf-8")

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
