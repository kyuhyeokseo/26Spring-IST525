#!/usr/bin/env python3
"""
Collect a control group of GitHub PRs that do not explicitly reference AI tools in
GH Archive issue comments, then enrich them with GitHub REST API metadata.

Usage example:
python collect_control_github.py \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --limit-prs 500 \
  --output-dir data_control_refs
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

import pandas as pd
from google.cloud import bigquery

from collect_ai_reference_github import (
    AI_REGEX,
    CandidateComment,
    GitHubAPI,
    add_derived_columns,
    compute_stats,
    ensure_env,
    get_bigquery_client,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--limit-prs",
        type=int,
        default=500,
        help="Max number of non-AI PRs to seed from BigQuery",
    )
    parser.add_argument(
        "--max-prs",
        type=int,
        default=None,
        help="Max unique PRs to enrich via GitHub API (defaults to --limit-prs)",
    )
    parser.add_argument(
        "--output-dir",
        default="data_control_refs",
        help="Directory to save CSV/JSON outputs",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=0,
        help="Only keep repos with at least this many stars (GitHub API stage)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Sleep between GitHub API calls",
    )
    return parser.parse_args()


def build_bq_query() -> str:
    ai_pattern = AI_REGEX.pattern.replace("\\", "\\\\")
    return f"""
    DECLARE start_date DATE DEFAULT @start_date;
    DECLARE end_date DATE DEFAULT @end_date;

    WITH comment_events AS (
      SELECT
        repo.name AS repo_name,
        CAST(JSON_VALUE(payload, '$.issue.number') AS INT64) AS issue_number,
        JSON_VALUE(payload, '$.comment.id') AS comment_id,
        actor.login AS actor_login,
        created_at,
        JSON_VALUE(payload, '$.comment.body') AS comment_body,
        JSON_VALUE(payload, '$.issue.pull_request.url') AS pr_url
      FROM `githubarchive.month.*`
      WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m', start_date)
                              AND FORMAT_DATE('%Y%m', end_date)
        AND type = 'IssueCommentEvent'
    ),
    ai_prs AS (
      SELECT DISTINCT repo_name, issue_number
      FROM comment_events
      WHERE pr_url IS NOT NULL
        AND DATE(created_at) BETWEEN start_date AND end_date
        AND comment_body IS NOT NULL
        AND REGEXP_CONTAINS(LOWER(comment_body), r'{ai_pattern}')
    ),
    control_comments AS (
      SELECT
        repo_name,
        issue_number AS pr_number,
        comment_id,
        actor_login,
        CAST(created_at AS STRING) AS created_at,
        comment_body,
        ROW_NUMBER() OVER (
          PARTITION BY repo_name, issue_number
          ORDER BY created_at DESC, comment_id DESC
        ) AS row_num
      FROM comment_events
      WHERE pr_url IS NOT NULL
        AND DATE(created_at) BETWEEN start_date AND end_date
        AND comment_body IS NOT NULL
        AND NOT REGEXP_CONTAINS(LOWER(comment_body), r'{ai_pattern}')
        AND NOT EXISTS (
          SELECT 1
          FROM ai_prs
          WHERE ai_prs.repo_name = comment_events.repo_name
            AND ai_prs.issue_number = comment_events.issue_number
        )
    )
    SELECT
      repo_name,
      pr_number,
      comment_id,
      actor_login,
      created_at,
      comment_body
    FROM control_comments
    WHERE row_num = 1
    ORDER BY created_at DESC
    LIMIT @limit_prs
    """


def query_control_candidates(
    client: bigquery.Client,
    start_date: str,
    end_date: str,
    limit_prs: int,
) -> List[CandidateComment]:
    query = build_bq_query()
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            bigquery.ScalarQueryParameter("limit_prs", "INT64", limit_prs),
        ]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    records: List[CandidateComment] = []
    for row in df.to_dict(orient="records"):
        records.append(
            CandidateComment(
                repo_name=row["repo_name"],
                pr_number=int(row["pr_number"]),
                comment_id=row.get("comment_id"),
                actor_login=row.get("actor_login"),
                created_at=row["created_at"],
                comment_body=row.get("comment_body") or "",
                matched_keyword=None,
            )
        )
    return records


def enrich_prs(
    github: GitHubAPI,
    candidate_comments: List[CandidateComment],
    max_prs: int,
    min_stars: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from collect_ai_reference_github import enrich_prs as enrich_ai_prs

    return enrich_ai_prs(
        github=github,
        candidate_comments=candidate_comments,
        max_prs=max_prs,
        min_stars=min_stars,
    )


def filter_strict_control(
    pr_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    ai_comment_prs = set()
    ai_review_prs = set()

    if not comments_df.empty and "contains_ai_reference" in comments_df.columns:
        ai_comment_prs = {
            (row.repo_name, int(row.pr_number))
            for row in comments_df.loc[
                comments_df["contains_ai_reference"].fillna(False).astype(bool),
                ["repo_name", "pr_number"],
            ].itertuples(index=False)
        }

    if not reviews_df.empty and "contains_ai_reference" in reviews_df.columns:
        ai_review_prs = {
            (row.repo_name, int(row.pr_number))
            for row in reviews_df.loc[
                reviews_df["contains_ai_reference"].fillna(False).astype(bool),
                ["repo_name", "pr_number"],
            ].itertuples(index=False)
        }

    contaminated_prs = ai_comment_prs | ai_review_prs
    strict_keep_mask = [
        (row.repo_name, int(row.pr_number)) not in contaminated_prs
        for row in pr_df[["repo_name", "pr_number"]].itertuples(index=False)
    ]
    strict_pr_df = pr_df.loc[strict_keep_mask].copy()

    if strict_pr_df.empty:
        strict_comments_df = comments_df.iloc[0:0].copy()
        strict_reviews_df = reviews_df.iloc[0:0].copy()
    else:
        keep_keys = {(row.repo_name, int(row.pr_number)) for row in strict_pr_df[["repo_name", "pr_number"]].itertuples(index=False)}
        strict_comments_df = comments_df.loc[
            [
                (row.repo_name, int(row.pr_number)) in keep_keys
                for row in comments_df[["repo_name", "pr_number"]].itertuples(index=False)
            ]
        ].copy()
        strict_reviews_df = reviews_df.loc[
            [
                (row.repo_name, int(row.pr_number)) in keep_keys
                for row in reviews_df[["repo_name", "pr_number"]].itertuples(index=False)
            ]
        ].copy()

    filter_stats = {
        "n_prs_before_strict_filter": int(len(pr_df)),
        "n_prs_removed_for_ai_reference_in_enriched_data": int(len(contaminated_prs)),
        "n_prs_after_strict_filter": int(len(strict_pr_df)),
    }
    return strict_pr_df, strict_comments_df, strict_reviews_df, filter_stats


def save_outputs(
    output_dir: Path,
    candidate_comments: List[CandidateComment],
    pr_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
    stats: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    candidate_df = pd.DataFrame([asdict(item) for item in candidate_comments])
    candidate_df.to_csv(output_dir / "candidate_control_prs_from_bq.csv", index=False)
    pr_df.to_csv(output_dir / "pull_requests.csv", index=False)
    comments_df.to_csv(output_dir / "comments.csv", index=False)
    reviews_df.to_csv(output_dir / "reviews.csv", index=False)

    with open(output_dir / "summary_stats.json", "w", encoding="utf-8") as file_obj:
        json.dump(stats, file_obj, ensure_ascii=False, indent=2)

    lines = [
        "# Control Group Summary",
        f"- PRs: {stats.get('n_prs', 0)}",
        f"- Repos: {stats.get('n_repos', 0)}",
        f"- Comments: {stats.get('n_comments', 0)}",
        f"- Reviews: {stats.get('n_reviews', 0)}",
        f"- Merged rate: {stats.get('merged_rate')}",
        f"- Median time to merge (hours): {stats.get('median_time_to_merge_hours')}",
        "",
        "## Top repos by PR count",
    ]
    for key, value in (stats.get("top_repos_by_pr_count") or {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## AI keyword counts in comments")
    for key, value in (stats.get("ai_keyword_counts_in_comments") or {}).items():
        lines.append(f"- {key}: {value}")

    with open(output_dir / "summary_report.md", "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines))


def main() -> None:
    args = parse_args()
    github_token, gcp_project = ensure_env()

    output_dir = Path(args.output_dir)
    max_prs = args.max_prs if args.max_prs is not None else args.limit_prs

    print("[1/4] Querying non-AI control PRs from BigQuery...")
    bq_client = get_bigquery_client(gcp_project)
    candidate_comments = query_control_candidates(
        client=bq_client,
        start_date=args.start,
        end_date=args.end,
        limit_prs=args.limit_prs,
    )
    print(f"Found {len(candidate_comments)} control PR seeds from GH Archive.")

    print("[2/4] Enriching PRs with GitHub API...")
    github = GitHubAPI(token=github_token, sleep=args.sleep)
    pr_df, comments_df, reviews_df = enrich_prs(
        github=github,
        candidate_comments=candidate_comments,
        max_prs=max_prs,
        min_stars=args.min_stars,
    )

    print("[3/4] Deriving metrics...")
    pr_df, comments_df, reviews_df, filter_stats = filter_strict_control(pr_df, comments_df, reviews_df)
    pr_df = add_derived_columns(pr_df, comments_df, reviews_df)
    stats = compute_stats(pr_df, comments_df, reviews_df)
    stats["dataset_type"] = "control_non_ai_reference_strict"
    stats["n_candidate_prs_from_bq"] = len(candidate_comments)
    stats.update(filter_stats)

    print("[4/4] Saving outputs...")
    save_outputs(output_dir, candidate_comments, pr_df, comments_df, reviews_df, stats)

    print("\nDone.")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
