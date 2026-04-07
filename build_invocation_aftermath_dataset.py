#!/usr/bin/env python3
"""
Build an invocation aftermath dataset for uptake analysis.

For each human Suggestion-Invocation mention, collect:
- the invocation itself
- next 3 human utterances in the same PR thread
- latency to next human / next bot / next any comment
- merge outcome and time-to-merge after invocation

Outputs:
- invocation_aftermath_dataset.csv
- invocation_aftermath_summary.json

Usage:
python build_invocation_aftermath_dataset.py \
  --base-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --refinement-csv analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv \
  --comments-csv data_ai_refs/comments.csv \
  --prs-csv data_ai_refs/pull_requests.csv \
  --output-dir analysis_ai_refs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


BOT_PATTERN = r"\[bot\]|Copilot|Claude|coderabbit|CLAassistant|cr-gpt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-csv", default="analysis_ai_refs/llm_labeling_human_mentions.csv")
    parser.add_argument(
        "--refinement-csv",
        default="analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv",
    )
    parser.add_argument("--comments-csv", default="data_ai_refs/comments.csv")
    parser.add_argument("--prs-csv", default="data_ai_refs/pull_requests.csv")
    parser.add_argument("--output-dir", default="analysis_ai_refs")
    return parser.parse_args()


def hours_between(later: pd.Timestamp | None, earlier: pd.Timestamp | None) -> float | None:
    if later is None or earlier is None or pd.isna(later) or pd.isna(earlier):
        return None
    return round((later - earlier).total_seconds() / 3600.0, 3)


def normalize_text(text: Any) -> str:
    if pd.isna(text):
        return ""
    return " ".join(str(text).split())


def first_match_after(df: pd.DataFrame, ts: pd.Timestamp, mask: pd.Series) -> pd.Series | None:
    sub = df.loc[(df["created_at_dt"] > ts) & mask].sort_values("created_at_dt")
    if sub.empty:
        return None
    return sub.iloc[0]


def build_dataset(
    base_df: pd.DataFrame,
    refinement_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    pr_df: pd.DataFrame,
) -> pd.DataFrame:
    mentions = base_df.merge(refinement_df, on="mention_uid", how="inner", suffixes=("", "_refined"))
    mentions = mentions.loc[mentions["suggestion_subtype"] == "Suggestion-Invocation"].copy()
    mentions["mention_time_dt"] = pd.to_datetime(mentions["mention_time"], utc=True, errors="coerce")

    comments = comments_df.copy()
    comments["created_at_dt"] = pd.to_datetime(comments["created_at"], utc=True, errors="coerce")
    comments["is_bot_like"] = comments["user_login"].astype(str).str.contains(BOT_PATTERN, case=False, regex=True)
    comments["comment_uid"] = comments.apply(
        lambda row: f"{row['repo_name']}#{int(row['pr_number'])}:{row['comment_type']}:{int(row['comment_id'])}",
        axis=1,
    )

    prs = pr_df.copy()
    prs["merged_at_dt"] = pd.to_datetime(prs["merged_at"], utc=True, errors="coerce")

    rows: list[dict[str, Any]] = []
    for _, mention in mentions.iterrows():
        repo_name = mention["repo_name"]
        pr_number = int(mention["pr_number"])
        mention_uid = mention["mention_uid"]
        mention_ts = mention["mention_time_dt"]

        pr_comments = comments.loc[
            (comments["repo_name"] == repo_name) & (comments["pr_number"] == pr_number)
        ].sort_values("created_at_dt")

        next_any = pr_comments.loc[pr_comments["created_at_dt"] > mention_ts].head(1)
        next_human = pr_comments.loc[
            (pr_comments["created_at_dt"] > mention_ts) & (~pr_comments["is_bot_like"])
        ].head(1)
        next_bot = pr_comments.loc[
            (pr_comments["created_at_dt"] > mention_ts) & (pr_comments["is_bot_like"])
        ].head(1)
        next_three_human = pr_comments.loc[
            (pr_comments["created_at_dt"] > mention_ts) & (~pr_comments["is_bot_like"])
        ].head(3)

        pr_row = prs.loc[(prs["repo_name"] == repo_name) & (prs["pr_number"] == pr_number)]
        pr_row = pr_row.iloc[0] if not pr_row.empty else None

        human_rows = list(next_three_human.itertuples(index=False))
        row: dict[str, Any] = {
            "mention_uid": mention_uid,
            "repo_name": repo_name,
            "pr_number": pr_number,
            "invocation_user_login": mention["user_login"],
            "invocation_speaker_role": mention["speaker_role"],
            "invocation_location": mention["mention_location"],
            "invocation_timing_phase": mention["timing_phase"],
            "invocation_order_label": mention["mention_order_label"],
            "invocation_body": normalize_text(mention["mention_body"]),
            "invocation_addressing_mode": mention["addressing_mode"],
            "invocation_time": mention["mention_time"],
            "has_next_any_comment": bool(not next_any.empty),
            "has_next_human_comment": bool(not next_human.empty),
            "has_next_bot_comment": bool(not next_bot.empty),
            "latency_to_next_any_comment_hours": (
                hours_between(next_any.iloc[0]["created_at_dt"], mention_ts) if not next_any.empty else None
            ),
            "latency_to_next_human_comment_hours": (
                hours_between(next_human.iloc[0]["created_at_dt"], mention_ts) if not next_human.empty else None
            ),
            "latency_to_next_bot_comment_hours": (
                hours_between(next_bot.iloc[0]["created_at_dt"], mention_ts) if not next_bot.empty else None
            ),
            "n_human_followups_captured": len(human_rows),
            "merged": bool(pr_row["merged"]) if pr_row is not None and not pd.isna(pr_row["merged"]) else False,
            "pr_state": pr_row["pr_state"] if pr_row is not None else "",
            "invocation_before_merge": (
                bool(pr_row["merged"])
                and not pd.isna(pr_row["merged_at_dt"])
                and not pd.isna(mention_ts)
                and mention_ts <= pr_row["merged_at_dt"]
                if pr_row is not None
                else False
            ),
            "time_to_merge_after_invocation_hours": (
                hours_between(pr_row["merged_at_dt"], mention_ts)
                if pr_row is not None and bool(pr_row["merged"]) and not pd.isna(pr_row["merged_at_dt"])
                else None
            ),
            "time_to_close_after_invocation_hours": (
                round(float(pr_row["time_to_close_hours"]) - float((mention_ts - pd.to_datetime(pr_row["created_at"], utc=True)).total_seconds() / 3600.0), 3)
                if pr_row is not None and not pd.isna(pr_row.get("time_to_close_hours")) and not pd.isna(mention_ts)
                else None
            ),
            "pr_total_comments": int(pr_row["total_comment_count_all_comments"]) if pr_row is not None and not pd.isna(pr_row["total_comment_count_all_comments"]) else None,
            "pr_ai_comments": int(pr_row["ai_reference_comment_count_all_comments"]) if pr_row is not None and not pd.isna(pr_row["ai_reference_comment_count_all_comments"]) else None,
            "pr_title": pr_row["pr_title"] if pr_row is not None else "",
            "pr_language": pr_row["repo_language"] if pr_row is not None else "",
            "uptake_label": "",
            "uptake_secondary_label": "",
            "uptake_notes": "",
        }

        for idx in range(3):
            if idx < len(human_rows):
                item = human_rows[idx]
                row[f"next_human_{idx+1}_user_login"] = item.user_login
                row[f"next_human_{idx+1}_comment_type"] = item.comment_type
                row[f"next_human_{idx+1}_created_at"] = item.created_at
                row[f"next_human_{idx+1}_contains_ai_reference"] = bool(item.contains_ai_reference)
                row[f"next_human_{idx+1}_body"] = normalize_text(item.body)
                row[f"next_human_{idx+1}_latency_hours"] = hours_between(item.created_at_dt, mention_ts)
            else:
                row[f"next_human_{idx+1}_user_login"] = ""
                row[f"next_human_{idx+1}_comment_type"] = ""
                row[f"next_human_{idx+1}_created_at"] = ""
                row[f"next_human_{idx+1}_contains_ai_reference"] = ""
                row[f"next_human_{idx+1}_body"] = ""
                row[f"next_human_{idx+1}_latency_hours"] = ""

        rows.append(row)

    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    valid_merge_after = df.loc[df["invocation_before_merge"] == True].copy()
    result: dict[str, Any] = {
        "n_invocations": int(len(df)),
        "has_next_human_comment_rate_pct": round(df["has_next_human_comment"].mean() * 100, 2) if len(df) else 0.0,
        "has_next_bot_comment_rate_pct": round(df["has_next_bot_comment"].mean() * 100, 2) if len(df) else 0.0,
        "merged_rate_pct": round(df["merged"].mean() * 100, 2) if len(df) else 0.0,
        "n_invocations_before_merge": int(len(valid_merge_after)),
        "invocation_before_merge_rate_pct": round(df["invocation_before_merge"].mean() * 100, 2) if len(df) else 0.0,
    }
    for col in [
        "latency_to_next_any_comment_hours",
        "latency_to_next_human_comment_hours",
        "latency_to_next_bot_comment_hours",
        "time_to_merge_after_invocation_hours",
    ]:
        series = pd.to_numeric(df[col], errors="coerce")
        result[f"median_{col}"] = round(float(series.dropna().median()), 3) if series.dropna().size else None
        result[f"mean_{col}"] = round(float(series.dropna().mean()), 3) if series.dropna().size else None

    merge_series = pd.to_numeric(valid_merge_after["time_to_merge_after_invocation_hours"], errors="coerce")
    result["median_time_to_merge_after_invocation_hours_valid"] = (
        round(float(merge_series.dropna().median()), 3) if merge_series.dropna().size else None
    )
    result["mean_time_to_merge_after_invocation_hours_valid"] = (
        round(float(merge_series.dropna().mean()), 3) if merge_series.dropna().size else None
    )

    if "invocation_speaker_role" in df.columns:
        role_counts = df["invocation_speaker_role"].value_counts().to_dict()
        result["invocations_by_role"] = {k: int(v) for k, v in role_counts.items()}
    if "invocation_timing_phase" in df.columns:
        timing_counts = df["invocation_timing_phase"].value_counts().to_dict()
        result["invocations_by_timing"] = {k: int(v) for k, v in timing_counts.items()}
    return result


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_df = pd.read_csv(args.base_csv)
    refinement_df = pd.read_csv(args.refinement_csv)
    comments_df = pd.read_csv(args.comments_csv)
    pr_df = pd.read_csv(args.prs_csv)

    dataset = build_dataset(base_df, refinement_df, comments_df, pr_df)
    summary = summarize(dataset)

    dataset_path = output_dir / "invocation_aftermath_dataset.csv"
    summary_path = output_dir / "invocation_aftermath_summary.json"
    dataset.to_csv(dataset_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"dataset": str(dataset_path), "summary": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
