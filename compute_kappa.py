"""
Computes Cohen's kappa between LLM labels and second-coder labels for the
function and uptake samples. Also reports raw agreement, per-class
disagreements, and a confusion matrix.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


def normalize_label(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    if s.lower() == "explaination":
        return "Explanation"
    return s


def cohens_kappa(coder1: list[str], coder2: list[str]) -> dict:
    pairs = [(a, b) for a, b in zip(coder1, coder2) if a and b]
    n = len(pairs)
    if n == 0:
        return {"n": 0, "kappa": None, "raw_agreement": None}
    cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    obs = sum(1 for a, b in pairs if a == b) / n
    p1 = Counter(a for a, _ in pairs)
    p2 = Counter(b for _, b in pairs)
    exp = sum((p1[c] / n) * (p2[c] / n) for c in cats)
    kappa = (obs - exp) / (1 - exp) if exp < 1 else 0.0
    cm: dict = defaultdict(lambda: defaultdict(int))
    for a, b in pairs:
        cm[a][b] += 1
    return {
        "n": n,
        "raw_agreement": round(obs, 4),
        "expected_agreement": round(exp, 4),
        "kappa": round(kappa, 4),
        "categories": cats,
        "confusion_matrix_llm_x_coder2": {k: dict(v) for k, v in cm.items()},
        "n_per_label_llm": dict(p1),
        "n_per_label_coder2": dict(p2),
    }


def confusion_text(cm: dict, cats: list[str]) -> str:
    header = "| llm \\ coder2 | " + " | ".join(cats) + " |"
    sep = "|" + "---|" * (1 + len(cats))
    rows = [header, sep]
    for r in cats:
        cells = [str(cm.get(r, {}).get(c, 0)) for c in cats]
        rows.append(f"| {r} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--function-csv",
        default="analysis_ai_refs/kappa_function_sample.csv",
    )
    parser.add_argument(
        "--uptake-csv",
        default="analysis_ai_refs/kappa_uptake_sample.csv",
    )
    parser.add_argument(
        "--out-json",
        default="analysis_ai_refs/kappa_summary.json",
    )
    parser.add_argument(
        "--out-md",
        default="analysis_ai_refs/kappa_summary.md",
    )
    args = parser.parse_args()

    f_df = pd.read_csv(args.function_csv)
    u_df = pd.read_csv(args.uptake_csv)

    f_llm = [normalize_label(x) for x in f_df["llm_primary_label"].fillna("")]
    f_c2 = [normalize_label(x) for x in f_df["coder2_label"].fillna("")]
    u_llm = [normalize_label(x) for x in u_df["uptake_label"].fillna("")]
    u_c2 = [normalize_label(x) for x in u_df["coder2_label"].fillna("")]

    f_kappa = cohens_kappa(f_llm, f_c2)
    u_kappa = cohens_kappa(u_llm, u_c2)

    summary = {"function": f_kappa, "uptake": u_kappa}
    Path(args.out_json).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    md: list[str] = []
    md.append("# Inter-Coder Reliability (Cohen's kappa)\n")
    md.append(
        "Stratified samples were drawn from each labeled dataset. The "
        "second coder independently re-read each mention or invocation "
        "body and assigned a label using the same codebook used for LLM "
        "labeling. Cohen's kappa was then computed between the LLM labels "
        "and the second coder.\n"
    )

    md.append("## Function labels (n=56 stratified, ~10 per class)\n")
    md.append(f"- n compared: {f_kappa['n']}")
    md.append(f"- Raw agreement: {f_kappa['raw_agreement']}")
    md.append(f"- Expected agreement: {f_kappa['expected_agreement']}")
    md.append(f"- Cohen's kappa: **{f_kappa['kappa']}**\n")
    md.append("Confusion matrix (rows = LLM, columns = coder2):\n")
    md.append(confusion_text(
        f_kappa["confusion_matrix_llm_x_coder2"],
        f_kappa["categories"],
    ))
    md.append("")
    md.append(f"- LLM label counts: {f_kappa['n_per_label_llm']}")
    md.append(f"- Coder2 label counts: {f_kappa['n_per_label_coder2']}\n")

    md.append("## Uptake labels (n=25 stratified, all classes)\n")
    md.append(f"- n compared: {u_kappa['n']}")
    md.append(f"- Raw agreement: {u_kappa['raw_agreement']}")
    md.append(f"- Expected agreement: {u_kappa['expected_agreement']}")
    md.append(f"- Cohen's kappa: **{u_kappa['kappa']}**\n")
    md.append("Confusion matrix (rows = LLM, columns = coder2):\n")
    md.append(confusion_text(
        u_kappa["confusion_matrix_llm_x_coder2"],
        u_kappa["categories"],
    ))
    md.append("")
    md.append(f"- LLM label counts: {u_kappa['n_per_label_llm']}")
    md.append(f"- Coder2 label counts: {u_kappa['n_per_label_coder2']}\n")

    md.append("## Interpretation\n")
    md.append(
        "Landis & Koch (1977) benchmark: <0.20 slight, 0.21-0.40 fair, "
        "0.41-0.60 moderate, 0.61-0.80 substantial, >0.80 almost perfect. "
        "Kappa values around or below 0.40 should be reported as a "
        "limitation, and the codebook should be tightened in future passes. "
        "The most informative output here is the confusion matrix: it "
        "shows which categories the LLM and the second coder are "
        "systematically confusing."
    )

    Path(args.out_md).write_text("\n".join(md) + "\n")
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
