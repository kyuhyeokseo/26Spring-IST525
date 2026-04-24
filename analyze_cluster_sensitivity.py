"""
Cluster sensitivity analysis for the uptake-by-merge chi-square test.

The original 100-case stratified sample contains 56 unique PRs (some PRs
contribute up to 6 invocations each). The original chi-square assumes
independent observations, which is violated by within-PR clustering.

This script:
  1. Repeatedly samples one invocation per PR (n=56 each draw).
  2. Computes the chi-square statistic for each draw.
  3. Reports the distribution of chi-square values and the proportion of
     draws in which the association reaches p < 0.05 by permutation.

Outputs:
  analysis_ai_refs/cluster_sensitivity_summary.json
  analysis_ai_refs/cluster_sensitivity_summary.md
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

import pandas as pd

random.seed(42)


def chi_square(table: list[list[int]]) -> tuple[float, int]:
    rows = len(table)
    cols = len(table[0]) if rows else 0
    row_sums = [sum(r) for r in table]
    col_sums = [sum(table[i][j] for i in range(rows)) for j in range(cols)]
    n = sum(row_sums)
    if n == 0:
        return 0.0, max(0, (rows - 1) * (cols - 1))
    chi = 0.0
    for i in range(rows):
        for j in range(cols):
            exp = row_sums[i] * col_sums[j] / n
            if exp > 0:
                chi += (table[i][j] - exp) ** 2 / exp
    return chi, (rows - 1) * (cols - 1)


def build_table(rows: list[str], cols: list[str]) -> tuple[list[list[int]], list[str], list[str]]:
    row_levels = sorted(set(rows))
    col_levels = sorted(set(cols))
    row_idx = {v: i for i, v in enumerate(row_levels)}
    col_idx = {v: i for i, v in enumerate(col_levels)}
    table = [[0] * len(col_levels) for _ in range(len(row_levels))]
    for r, c in zip(rows, cols):
        table[row_idx[r]][col_idx[c]] += 1
    return table, row_levels, col_levels


def perm_p(rows: list[str], cols: list[str], n_perm: int = 2000, seed: int = 42) -> float:
    obs_table, _, _ = build_table(rows, cols)
    obs_chi, _ = chi_square(obs_table)
    rng = random.Random(seed)
    cols_list = list(cols)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(cols_list)
        table, _, _ = build_table(rows, cols_list)
        chi, _ = chi_square(table)
        if chi >= obs_chi:
            count += 1
    return (count + 1) / (n_perm + 1)


def collapse_uptake(label: str) -> str:
    return "positive_uptake" if label == "positive_uptake" else "non_positive"


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
    parser.add_argument("--n-iter", type=int, default=1000)
    parser.add_argument("--n-perm-per-iter", type=int, default=500)
    parser.add_argument(
        "--out-json",
        default="analysis_ai_refs/cluster_sensitivity_summary.json",
    )
    parser.add_argument(
        "--out-md",
        default="analysis_ai_refs/cluster_sensitivity_summary.md",
    )
    args = parser.parse_args()

    labels = pd.read_csv(args.labels_csv)
    after = pd.read_csv(args.aftermath_csv)
    df = labels.merge(
        after[["mention_uid", "repo_name", "pr_number", "merged"]],
        on="mention_uid",
        how="left",
    )
    df["pr_id"] = df["repo_name"] + "#" + df["pr_number"].astype(str)

    n_unique_pr = df["pr_id"].nunique()
    n_unique_repo = df["repo_name"].nunique()
    pr_counts = df["pr_id"].value_counts()
    summary: dict = {
        "n_total": int(len(df)),
        "n_unique_pr": int(n_unique_pr),
        "n_unique_repo": int(n_unique_repo),
        "max_per_pr": int(pr_counts.max()),
        "mean_per_pr": round(float(pr_counts.mean()), 3),
        "n_iter": args.n_iter,
        "n_perm_per_iter": args.n_perm_per_iter,
    }

    rng = random.Random(42)
    chi_full_vals: list[float] = []
    chi_2x2_vals: list[float] = []
    p_full_vals: list[float] = []
    p_2x2_vals: list[float] = []
    n_sig_full = 0
    n_sig_2x2 = 0

    grouped = df.groupby("pr_id").indices
    pr_ids = list(grouped.keys())

    for it in range(args.n_iter):
        chosen_idx = [rng.choice(list(grouped[pr])) for pr in pr_ids]
        sub = df.iloc[chosen_idx]
        full_chi, _ = chi_square(
            build_table(sub["uptake_label"].tolist(),
                        sub["merged"].astype(str).tolist())[0]
        )
        chi_full_vals.append(full_chi)
        coll = [collapse_uptake(x) for x in sub["uptake_label"]]
        c2x2_chi, _ = chi_square(
            build_table(coll, sub["merged"].astype(str).tolist())[0]
        )
        chi_2x2_vals.append(c2x2_chi)

        p_full = perm_p(
            sub["uptake_label"].tolist(),
            sub["merged"].astype(str).tolist(),
            n_perm=args.n_perm_per_iter,
            seed=12345 + it,
        )
        p_2x2 = perm_p(
            coll,
            sub["merged"].astype(str).tolist(),
            n_perm=args.n_perm_per_iter,
            seed=22345 + it,
        )
        p_full_vals.append(p_full)
        p_2x2_vals.append(p_2x2)
        if p_full < 0.05:
            n_sig_full += 1
        if p_2x2 < 0.05:
            n_sig_2x2 += 1

    def stats_block(vals: list[float]) -> dict:
        sv = sorted(vals)
        n = len(sv)
        return {
            "mean": round(statistics.mean(sv), 4),
            "median": round(statistics.median(sv), 4),
            "p05": round(sv[max(0, int(n * 0.05) - 1)], 4),
            "p95": round(sv[min(n - 1, int(n * 0.95))], 4),
            "min": round(sv[0], 4),
            "max": round(sv[-1], 4),
        }

    summary["chi_full"] = stats_block(chi_full_vals)
    summary["chi_2x2"] = stats_block(chi_2x2_vals)
    summary["p_full"] = stats_block(p_full_vals)
    summary["p_2x2"] = stats_block(p_2x2_vals)
    summary["pct_sig_full_p_lt_0.05"] = round(100 * n_sig_full / args.n_iter, 2)
    summary["pct_sig_2x2_p_lt_0.05"] = round(100 * n_sig_2x2 / args.n_iter, 2)

    Path(args.out_json).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    md: list[str] = []
    md.append("# Cluster Sensitivity for Uptake x Merge Chi-Square\n")
    md.append(
        f"The 100-case stratified uptake sample contains "
        f"{summary['n_unique_pr']} unique PRs across "
        f"{summary['n_unique_repo']} repositories. Up to "
        f"{summary['max_per_pr']} invocations come from the same PR "
        f"(mean {summary['mean_per_pr']}). The original chi-square "
        "assumes independent observations, which is violated by "
        "within-PR clustering. This script repeats the test "
        f"{summary['n_iter']:,} times, each time sampling one invocation "
        "per PR, and reports the resulting distribution.\n"
    )
    md.append("## Per-iteration distributions\n")
    md.append(f"- Full 4x2 chi-square: {summary['chi_full']}")
    md.append(f"- Collapsed 2x2 chi-square: {summary['chi_2x2']}")
    md.append(f"- Full p (perm): {summary['p_full']}")
    md.append(f"- Collapsed 2x2 p (perm): {summary['p_2x2']}\n")
    md.append("## Significance rates across draws\n")
    md.append(
        f"- Full table p < 0.05 in {summary['pct_sig_full_p_lt_0.05']}% of draws"
    )
    md.append(
        f"- Collapsed 2x2 p < 0.05 in {summary['pct_sig_2x2_p_lt_0.05']}% of draws\n"
    )
    md.append("## Interpretation\n")
    sig_pct = summary["pct_sig_2x2_p_lt_0.05"]
    if sig_pct >= 80:
        md.append(
            "The association is robust to within-PR clustering: the "
            "majority of one-per-PR resamples still reach p < 0.05. The "
            "original chi-square is a defensible summary."
        )
    elif sig_pct >= 50:
        md.append(
            "The association partially survives within-PR clustering. "
            "About half of the one-per-PR resamples still reach p < 0.05, "
            "so the original chi-square should be reported alongside this "
            "sensitivity check, not as the sole evidence."
        )
    else:
        md.append(
            "The association is fragile to within-PR clustering. Only a "
            "minority of one-per-PR resamples reach p < 0.05, which "
            "suggests the original chi-square overstates the strength of "
            "the merge x uptake association."
        )
    Path(args.out_md).write_text("\n".join(md) + "\n")
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
