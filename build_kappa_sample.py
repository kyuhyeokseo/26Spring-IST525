"""
Builds two stratified inter-coder reliability samples:
  - 50 mentions stratified across LLM function labels (Suggestion / Critique /
    Explanation / Justification / Meta discussion / Other)
  - 30 invocation cases stratified across uptake labels (positive_uptake /
    corrective_critique / continued_delegation / no_clear_uptake)

Outputs CSVs ready for a second coder. The second coder fills in
`coder2_label`. The companion script `compute_kappa.py` computes Cohen's
kappa between the LLM label and the second coder.

Inputs:
  analysis_ai_refs/llm_labeling_human_mentions.csv (body + heuristic info)
  analysis_ai_refs/llm_labeling_human_mentions_labeled.csv (LLM labels)
  analysis_ai_refs/invocation_uptake_stratified_100.csv (body + context)
  analysis_ai_refs/invocation_uptake_stratified_100_labeled.csv (uptake labels)
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

random.seed(42)


def stratified_sample(
    df: pd.DataFrame, label_col: str, per_class: int, seed: int = 42
) -> pd.DataFrame:
    rng = random.Random(seed)
    parts: list[pd.DataFrame] = []
    for label, group in df.groupby(label_col):
        n = min(per_class, len(group))
        idx = rng.sample(list(group.index), n)
        parts.append(group.loc[idx])
    return pd.concat(parts).sort_values(label_col)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--function-input",
        default="analysis_ai_refs/llm_labeling_human_mentions.csv",
    )
    parser.add_argument(
        "--function-labels",
        default="analysis_ai_refs/llm_labeling_human_mentions_labeled.csv",
    )
    parser.add_argument(
        "--uptake-input",
        default="analysis_ai_refs/invocation_uptake_stratified_100.csv",
    )
    parser.add_argument(
        "--uptake-labels",
        default="analysis_ai_refs/invocation_uptake_stratified_100_labeled.csv",
    )
    parser.add_argument("--per-class-function", type=int, default=10)
    parser.add_argument("--per-class-uptake", type=int, default=10)
    parser.add_argument(
        "--out-function",
        default="analysis_ai_refs/kappa_function_sample.csv",
    )
    parser.add_argument(
        "--out-uptake",
        default="analysis_ai_refs/kappa_uptake_sample.csv",
    )
    args = parser.parse_args()

    f_in = pd.read_csv(args.function_input)
    f_lbl = pd.read_csv(args.function_labels)
    overlap = [c for c in f_lbl.columns if c != "mention_uid" and c in f_in.columns]
    f_in = f_in.drop(columns=overlap)
    f = f_in.merge(f_lbl, on="mention_uid", how="left")
    f = f.dropna(subset=["llm_primary_label"]).copy()
    fs = stratified_sample(
        f, "llm_primary_label", per_class=args.per_class_function
    )
    fs_out = fs[
        [
            "mention_uid",
            "repo_name",
            "pr_number",
            "speaker_role",
            "timing_phase",
            "mention_location",
            "mention_body",
            "llm_primary_label",
        ]
    ].copy()
    fs_out["coder2_label"] = ""
    fs_out["coder2_notes"] = ""
    fs_out.to_csv(args.out_function, index=False)
    print(
        f"Function sample: {len(fs_out)} rows, "
        f"by class:\n{fs_out['llm_primary_label'].value_counts().to_dict()}"
    )

    u_in = pd.read_csv(args.uptake_input)
    u_lbl = pd.read_csv(args.uptake_labels)
    overlap = [c for c in u_lbl.columns if c != "mention_uid" and c in u_in.columns]
    u_in = u_in.drop(columns=overlap)
    u = u_in.merge(u_lbl, on="mention_uid", how="left")
    u = u.dropna(subset=["uptake_label"]).copy()
    us = stratified_sample(u, "uptake_label", per_class=args.per_class_uptake)
    keep_cols = [
        "mention_uid",
        "invocation_user_login",
        "invocation_speaker_role",
        "invocation_timing_phase",
        "invocation_body",
        "next_human_1_body",
        "next_human_2_body",
        "next_human_3_body",
        "uptake_label",
    ]
    keep_cols = [c for c in keep_cols if c in us.columns]
    us_out = us[keep_cols].copy()
    us_out["coder2_label"] = ""
    us_out["coder2_notes"] = ""
    us_out.to_csv(args.out_uptake, index=False)
    print(
        f"Uptake sample: {len(us_out)} rows, "
        f"by class:\n{us_out['uptake_label'].value_counts().to_dict()}"
    )

    print(f"Wrote {args.out_function}")
    print(f"Wrote {args.out_uptake}")


if __name__ == "__main__":
    main()
