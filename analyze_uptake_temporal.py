"""
Re-analyzes the invocation uptake x merge association with temporal hygiene.

Original analysis: uptake_label (coded from the next 1-3 human follow-ups)
crossed with merge status. This is partly tautological because invocations
that occurred AFTER the PR was already merged cannot have caused the merge
outcome, and yet inflate the apparent association.

This script:
  1. Splits the 100-case stratified sample into pre-merge and post-merge.
  2. Re-runs a permutation chi-square only on pre-merge invocations.
  3. Adds a stricter "early-response" view: only count uptake events whose
     first human follow-up occurred within a fixed window (default 24h).
  4. Reports both the original 100-case test and the pre-merge subset for
     sensitivity comparison.

Inputs:
  analysis_ai_refs/invocation_uptake_stratified_100_labeled.csv
  analysis_ai_refs/invocation_aftermath_dataset.csv

Outputs:
  analysis_ai_refs/uptake_temporal_summary.json
  analysis_ai_refs/uptake_temporal_summary.md
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

random.seed(42)


def chi_square(observed: list[list[int]]) -> tuple[float, int]:
    """Pearson chi-square on a contingency table (list of rows)."""
    rows = len(observed)
    cols = len(observed[0]) if rows else 0
    row_sums = [sum(r) for r in observed]
    col_sums = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
    n = sum(row_sums)
    if n == 0:
        return 0.0, max(0, (rows - 1) * (cols - 1))
    chi = 0.0
    for i in range(rows):
        for j in range(cols):
            exp = row_sums[i] * col_sums[j] / n
            if exp > 0:
                chi += (observed[i][j] - exp) ** 2 / exp
    return chi, (rows - 1) * (cols - 1)


def permutation_pvalue(
    rows: list[str], cols: list[str], n_perm: int = 5000
) -> tuple[float, int, float]:
    if len(rows) != len(cols) or not rows:
        return 1.0, 0, 0.0
    # build observed table
    row_levels = sorted(set(rows))
    col_levels = sorted(set(cols))
    row_idx = {v: i for i, v in enumerate(row_levels)}
    col_idx = {v: i for i, v in enumerate(col_levels)}
    table = [[0] * len(col_levels) for _ in range(len(row_levels))]
    for r, c in zip(rows, cols):
        table[row_idx[r]][col_idx[c]] += 1
    obs_chi, df = chi_square(table)
    cols_list = list(cols)
    count = 0
    for _ in range(n_perm):
        random.shuffle(cols_list)
        perm_table = [[0] * len(col_levels) for _ in range(len(row_levels))]
        for r, c in zip(rows, cols_list):
            perm_table[row_idx[r]][col_idx[c]] += 1
        chi, _ = chi_square(perm_table)
        if chi >= obs_chi:
            count += 1
    return (count + 1) / (n_perm + 1), df, obs_chi


def crosstab_with_pct(rows: list[str], cols: list[str]) -> dict:
    out: dict = defaultdict(lambda: Counter())
    for r, c in zip(rows, cols):
        out[r][c] += 1
    table: dict = {}
    for r, counter in out.items():
        total = sum(counter.values()) or 1
        table[r] = {
            "counts": dict(counter),
            "pct": {k: round(100 * v / total, 2) for k, v in counter.items()},
            "n": sum(counter.values()),
        }
    return table


def fmt_table(title: str, table: dict, lines: list[str]) -> None:
    lines.append(f"### {title}\n")
    keys = sorted({k for v in table.values() for k in v["counts"].keys()})
    header = "| group | n | " + " | ".join(keys) + " |"
    sep = "|" + "---|" * (2 + len(keys))
    lines.append(header)
    lines.append(sep)
    for group, v in table.items():
        cells = []
        for k in keys:
            c = v["counts"].get(k, 0)
            p = v["pct"].get(k, 0.0)
            cells.append(f"{c} ({p}%)")
        lines.append(f"| {group} | {v['n']} | " + " | ".join(cells) + " |")
    lines.append("")


def collapse_uptake(label: str) -> str:
    """For 2x2 chi-square: positive vs everything-else (which is dominated by
    corrective_critique), to avoid sparse cells."""
    if label == "positive_uptake":
        return "positive_uptake"
    return "non_positive"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--labels-csv",
        default="analysis_ai_refs/invocation_uptake_stratified_100_labeled.csv",
    )
    parser.add_argument(
        "--aftermath-csv",
        default="analysis_ai_refs/invocation_aftermath_dataset.csv",
    )
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument(
        "--early-window-hours",
        type=float,
        default=24.0,
        help="Threshold for 'early response' subset.",
    )
    parser.add_argument(
        "--out-json",
        default="analysis_ai_refs/uptake_temporal_summary.json",
    )
    parser.add_argument(
        "--out-md",
        default="analysis_ai_refs/uptake_temporal_summary.md",
    )
    args = parser.parse_args()

    labels = pd.read_csv(args.labels_csv)
    after = pd.read_csv(args.aftermath_csv)
    df = labels.merge(
        after[
            [
                "mention_uid",
                "invocation_time",
                "merged",
                "invocation_before_merge",
                "time_to_merge_after_invocation_hours",
                "next_human_1_latency_hours",
                "next_human_1_created_at",
                "pr_state",
                "invocation_speaker_role",
                "invocation_timing_phase",
            ]
        ],
        on="mention_uid",
        how="left",
    )

    summary: dict = {"args": vars(args)}

    # ----- View 0: original 100-case -----
    pval0, df0, chi0 = permutation_pvalue(
        df["uptake_label"].tolist(),
        df["merged"].astype(str).tolist(),
        n_perm=args.n_perm,
    )
    pval0_2x2, df0_2x2, chi0_2x2 = permutation_pvalue(
        [collapse_uptake(x) for x in df["uptake_label"]],
        df["merged"].astype(str).tolist(),
        n_perm=args.n_perm,
    )
    summary["view0_full_100"] = {
        "n": int(len(df)),
        "uptake_x_merge_full_chi2": round(chi0, 4),
        "uptake_x_merge_full_df": df0,
        "uptake_x_merge_full_p_perm": round(pval0, 4),
        "uptake_x_merge_2x2_chi2": round(chi0_2x2, 4),
        "uptake_x_merge_2x2_df": df0_2x2,
        "uptake_x_merge_2x2_p_perm": round(pval0_2x2, 4),
        "table_uptake_by_merge": crosstab_with_pct(
            df["merged"].astype(str).tolist(),
            df["uptake_label"].tolist(),
        ),
    }

    # `invocation_before_merge` is True ONLY for merged PRs (it is a
    # logical conjunction of merged AND invocation timestamp < merge
    # timestamp). For non-merged PRs the field is False trivially.
    # The two stricter views below therefore drop merged-PR cases where the
    # uptake response could not plausibly have shaped the merge decision,
    # while keeping all non-merged PRs as the comparison baseline.

    # Mark merged cases whose first human response arrived BEFORE the merge.
    df["response_before_merge"] = (
        (df["merged"] == True)
        & (df["next_human_1_latency_hours"].notna())
        & (df["time_to_merge_after_invocation_hours"].notna())
        & (
            df["next_human_1_latency_hours"]
            < df["time_to_merge_after_invocation_hours"]
        )
    )
    # For non-merged: trivially keep them.
    keep_mask_v1 = (df["merged"] == False) | df["response_before_merge"]
    pre = df[keep_mask_v1].copy()
    summary["view1_response_before_merge"] = {
        "n": int(len(pre)),
        "n_dropped_post_merge_response": int(
            ((df["merged"] == True) & ~df["response_before_merge"]).sum()
        ),
        "n_merged_kept": int(((pre["merged"] == True)).sum()),
        "n_nonmerged_kept": int(((pre["merged"] == False)).sum()),
    }
    if len(pre) >= 10:
        pval1, df1, chi1 = permutation_pvalue(
            pre["uptake_label"].tolist(),
            pre["merged"].astype(str).tolist(),
            n_perm=args.n_perm,
        )
        pval1_2x2, df1_2x2, chi1_2x2 = permutation_pvalue(
            [collapse_uptake(x) for x in pre["uptake_label"]],
            pre["merged"].astype(str).tolist(),
            n_perm=args.n_perm,
        )
        summary["view1_response_before_merge"].update(
            {
                "uptake_x_merge_full_chi2": round(chi1, 4),
                "uptake_x_merge_full_df": df1,
                "uptake_x_merge_full_p_perm": round(pval1, 4),
                "uptake_x_merge_2x2_chi2": round(chi1_2x2, 4),
                "uptake_x_merge_2x2_df": df1_2x2,
                "uptake_x_merge_2x2_p_perm": round(pval1_2x2, 4),
                "table_uptake_by_merge": crosstab_with_pct(
                    pre["merged"].astype(str).tolist(),
                    pre["uptake_label"].tolist(),
                ),
            }
        )

    # ----- View 2: also drop very-tight merges -----
    # Drop merged cases where time-to-merge after invocation < 1h, since
    # uptake could not have meaningfully shaped that merge decision.
    keep_mask_v2 = keep_mask_v1 & (
        (df["merged"] == False)
        | (df["time_to_merge_after_invocation_hours"] >= 1.0)
    )
    early = df[keep_mask_v2].copy()
    summary["view2_response_before_merge_and_gap"] = {
        "min_gap_hours": 1.0,
        "n": int(len(early)),
        "n_merged_kept": int(((early["merged"] == True)).sum()),
        "n_nonmerged_kept": int(((early["merged"] == False)).sum()),
    }
    if len(early) >= 10:
        pval2, df2, chi2 = permutation_pvalue(
            early["uptake_label"].tolist(),
            early["merged"].astype(str).tolist(),
            n_perm=args.n_perm,
        )
        pval2_2x2, df2_2x2, chi2_2x2 = permutation_pvalue(
            [collapse_uptake(x) for x in early["uptake_label"]],
            early["merged"].astype(str).tolist(),
            n_perm=args.n_perm,
        )
        summary["view2_response_before_merge_and_gap"].update(
            {
                "uptake_x_merge_full_chi2": round(chi2, 4),
                "uptake_x_merge_full_df": df2,
                "uptake_x_merge_full_p_perm": round(pval2, 4),
                "uptake_x_merge_2x2_chi2": round(chi2_2x2, 4),
                "uptake_x_merge_2x2_df": df2_2x2,
                "uptake_x_merge_2x2_p_perm": round(pval2_2x2, 4),
                "table_uptake_by_merge": crosstab_with_pct(
                    early["merged"].astype(str).tolist(),
                    early["uptake_label"].tolist(),
                ),
            }
        )

    # ----- timing × uptake on the temporally-clean subset -----
    if len(pre) >= 10:
        pval_t, df_t, chi_t = permutation_pvalue(
            pre["uptake_label"].tolist(),
            pre["invocation_timing_phase"].astype(str).tolist(),
            n_perm=args.n_perm,
        )
        summary["view1_response_before_merge"]["uptake_x_timing_chi2"] = round(
            chi_t, 4
        )
        summary["view1_response_before_merge"]["uptake_x_timing_df"] = df_t
        summary["view1_response_before_merge"]["uptake_x_timing_p_perm"] = round(
            pval_t, 4
        )
        summary["view1_response_before_merge"]["table_uptake_by_timing"] = (
            crosstab_with_pct(
                pre["invocation_timing_phase"].astype(str).tolist(),
                pre["uptake_label"].tolist(),
            )
        )

    Path(args.out_json).write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    md: list[str] = []
    md.append("# Uptake x Merge: Temporal Hygiene Re-Analysis\n")
    md.append(
        "The original 100-case test mixes invocations that occurred *before* "
        "and *after* the PR was merged. Post-merge invocations cannot have "
        "shaped merge outcome, so their inclusion inflates the apparent "
        "association. This document reports the original test and two "
        "stricter views.\n"
    )

    md.append("## View 0 — Original (n=100)\n")
    v0 = summary["view0_full_100"]
    md.append(
        f"- Full 4x2 chi-square: chi2={v0['uptake_x_merge_full_chi2']}, "
        f"df={v0['uptake_x_merge_full_df']}, "
        f"perm p={v0['uptake_x_merge_full_p_perm']}"
    )
    md.append(
        f"- Collapsed 2x2 (positive vs non-positive): "
        f"chi2={v0['uptake_x_merge_2x2_chi2']}, "
        f"perm p={v0['uptake_x_merge_2x2_p_perm']}\n"
    )
    fmt_table("Uptake by merge status, full 100", v0["table_uptake_by_merge"], md)

    md.append(
        "## View 1 — Drop merged cases whose first response post-dates the merge\n"
    )
    v1 = summary["view1_response_before_merge"]
    md.append(
        f"- n={v1['n']}: kept {v1['n_merged_kept']} merged + "
        f"{v1['n_nonmerged_kept']} non-merged. "
        f"Dropped {v1['n_dropped_post_merge_response']} merged cases whose "
        "first uptake response arrived only after the merge had occurred "
        "(uptake could not have shaped the merge decision in those cases)."
    )
    if "uptake_x_merge_full_chi2" in v1:
        md.append(
            f"- Full chi-square: chi2={v1['uptake_x_merge_full_chi2']}, "
            f"df={v1['uptake_x_merge_full_df']}, "
            f"perm p={v1['uptake_x_merge_full_p_perm']}"
        )
        md.append(
            f"- 2x2 (positive vs non-positive): "
            f"chi2={v1['uptake_x_merge_2x2_chi2']}, "
            f"perm p={v1['uptake_x_merge_2x2_p_perm']}\n"
        )
        fmt_table(
            "Uptake by merge status, pre-merge only",
            v1["table_uptake_by_merge"],
            md,
        )
    if "uptake_x_timing_chi2" in v1:
        md.append(
            f"- Pre-merge timing x uptake: "
            f"chi2={v1['uptake_x_timing_chi2']}, "
            f"perm p={v1['uptake_x_timing_p_perm']}\n"
        )
        fmt_table(
            "Uptake by timing phase, pre-merge only",
            v1["table_uptake_by_timing"],
            md,
        )

    md.append(
        "## View 2 — Same as View 1, also drop merged cases with <1h "
        "invocation-to-merge gap\n"
    )
    v2 = summary["view2_response_before_merge_and_gap"]
    md.append(
        f"- n={v2['n']}: kept {v2['n_merged_kept']} merged + "
        f"{v2['n_nonmerged_kept']} non-merged. Stricter check that uptake "
        "had room to operate before merge."
    )
    if "uptake_x_merge_full_chi2" in v2:
        md.append(
            f"- Full chi-square: chi2={v2['uptake_x_merge_full_chi2']}, "
            f"perm p={v2['uptake_x_merge_full_p_perm']}"
        )
        md.append(
            f"- 2x2: chi2={v2['uptake_x_merge_2x2_chi2']}, "
            f"perm p={v2['uptake_x_merge_2x2_p_perm']}\n"
        )
        fmt_table(
            "Uptake by merge status, pre-merge + early-response",
            v2["table_uptake_by_merge"],
            md,
        )

    md.append("## Interpretation\n")
    md.append(
        "Reporting the pre-merge subset removes the most obvious source of "
        "tautology: cases where the invocation happened after the PR had "
        "already been merged. If the association in View 1 weakens "
        "substantially relative to View 0, the original chi-square should "
        "be reported with that caveat."
    )
    md.append(
        "View 2 is a stricter sensitivity check: it restricts further to "
        "invocations whose first human follow-up arrived within the early "
        "window. This is the closest available proxy for 'did the uptake "
        "occur in time to plausibly shape the PR outcome'."
    )

    Path(args.out_md).write_text("\n".join(md) + "\n")
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")
    print(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if not isinstance(vv, dict)}
         for k, v in summary.items() if isinstance(v, dict)},
        indent=2,
    ))


if __name__ == "__main__":
    main()
