#!/usr/bin/env python3
"""
Build a 100-row stratified uptake coding sample from invocation aftermath data.

Stratification keys:
- merged
- invocation_speaker_role
- invocation_timing_phase

Each non-empty stratum gets at least one row if possible, and the remaining rows
are allocated proportionally by stratum size.

Usage:
python build_invocation_uptake_stratified_sample.py \
  --input-csv analysis_ai_refs/invocation_aftermath_dataset.csv \
  --output-csv analysis_ai_refs/invocation_uptake_stratified_100.csv \
  --sample-size 100
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


STRATA = ["merged", "invocation_speaker_role", "invocation_timing_phase"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default="analysis_ai_refs/invocation_aftermath_dataset.csv")
    parser.add_argument("--output-csv", default="analysis_ai_refs/invocation_uptake_stratified_100.csv")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def allocate_sample_sizes(group_sizes: pd.Series, sample_size: int) -> dict[tuple, int]:
    nonempty = group_sizes[group_sizes > 0]
    n_groups = len(nonempty)
    if n_groups == 0:
        return {}

    # start with one per non-empty stratum if possible
    allocations = {idx: 1 for idx in nonempty.index}
    remaining = sample_size - n_groups

    if remaining < 0:
        # fallback: allocate to largest groups only
        top_groups = nonempty.sort_values(ascending=False).head(sample_size)
        return {idx: 1 for idx in top_groups.index}

    weights = nonempty / nonempty.sum()
    raw_extra = weights * remaining
    extra_floor = raw_extra.astype(int)
    remainders = (raw_extra - extra_floor).sort_values(ascending=False)

    for idx, value in extra_floor.items():
        allocations[idx] += int(value)

    still_needed = sample_size - sum(allocations.values())
    if still_needed > 0:
        for idx in remainders.index[:still_needed]:
            allocations[idx] += 1

    # do not exceed available rows in a stratum
    overflow = 0
    for idx in list(allocations.keys()):
        available = int(nonempty.loc[idx])
        if allocations[idx] > available:
            overflow += allocations[idx] - available
            allocations[idx] = available

    if overflow > 0:
        spare = {
            idx: int(nonempty.loc[idx]) - allocations[idx]
            for idx in allocations
            if int(nonempty.loc[idx]) - allocations[idx] > 0
        }
        for idx, _ in sorted(spare.items(), key=lambda kv: kv[1], reverse=True):
            if overflow <= 0:
                break
            take = min(spare[idx], overflow)
            allocations[idx] += take
            overflow -= take

    return allocations


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input_csv)

    group_sizes = df.groupby(STRATA).size()
    allocations = allocate_sample_sizes(group_sizes, args.sample_size)

    sampled_parts = []
    for stratum, n in allocations.items():
        if n <= 0:
            continue
        merged, role, timing = stratum
        sub = df[
            (df["merged"] == merged)
            & (df["invocation_speaker_role"] == role)
            & (df["invocation_timing_phase"] == timing)
        ]
        sampled_parts.append(sub.sample(n=n, random_state=args.random_state, replace=False))

    sample = pd.concat(sampled_parts, ignore_index=True)
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

    summary = (
        sample.groupby(STRATA)
        .size()
        .reset_index(name="n")
        .sort_values(["merged", "invocation_speaker_role", "invocation_timing_phase"])
    )
    print(f"Saved {len(sample)} rows to {args.output_csv}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
