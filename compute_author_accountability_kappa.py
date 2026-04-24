"""
Computes Cohen's kappa between the primary LLM-assisted author
accountability labels (in `author_accountability_phase_b_template.csv`,
column `accountability_label`) and the second coder's labels (column
`coder2_label`).

Run this after a second coder (the first author) fills in
`coder2_label` for the 14 stratified cases. If fewer than 10 cases are
labeled, kappa is not reported.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


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
        "confusion_matrix_c1_x_c2": {k: dict(v) for k, v in cm.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        default="analysis_ai_refs/author_accountability_phase_b_template.csv",
    )
    parser.add_argument(
        "--out-json",
        default="analysis_ai_refs/author_accountability_kappa.json",
    )
    parser.add_argument(
        "--out-md",
        default="analysis_ai_refs/author_accountability_kappa.md",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    filled = df[df["coder2_label"].fillna("").str.strip() != ""]
    print(f"Found {len(filled)}/{len(df)} rows with coder2 labels.")
    if len(filled) < 10:
        print(
            "Fewer than 10 second-coder labels; fill more rows before "
            "computing kappa. Writing a skeleton output."
        )
        skel = {"n": int(len(filled)), "note": "insufficient labels"}
        Path(args.out_json).write_text(json.dumps(skel, indent=2))
        Path(args.out_md).write_text(
            f"# Author Accountability Kappa\n\nOnly {len(filled)}/14 "
            "second-coder labels present. Add more before running.\n"
        )
        return

    k = cohens_kappa(
        filled["accountability_label"].tolist(),
        filled["coder2_label"].tolist(),
    )
    Path(args.out_json).write_text(json.dumps(k, indent=2, ensure_ascii=False))

    md: list[str] = []
    md.append("# Author Accountability Inter-Coder Reliability\n")
    md.append(f"- n compared: {k['n']}/{len(df)}")
    md.append(f"- Raw agreement: {k['raw_agreement']}")
    md.append(f"- Expected agreement: {k['expected_agreement']}")
    md.append(f"- Cohen's kappa: **{k['kappa']}**\n")
    md.append("Confusion matrix (rows = primary coder, columns = second coder):\n")
    cats = k["categories"]
    header = "| primary \\ coder2 | " + " | ".join(cats) + " |"
    sep = "|" + "---|" * (1 + len(cats))
    md.append(header)
    md.append(sep)
    for r in cats:
        cells = [str(k["confusion_matrix_c1_x_c2"].get(r, {}).get(c, 0))
                 for c in cats]
        md.append(f"| {r} | " + " | ".join(cells) + " |")
    md.append("")
    md.append("## Interpretation\n")
    md.append(
        "Landis & Koch (1977) benchmarks: <0.20 slight, 0.21-0.40 fair, "
        "0.41-0.60 moderate, 0.61-0.80 substantial, >0.80 almost perfect. "
        "For a six-category codebook with a 14-case sample, values around "
        "0.50 are expected and reportable as moderate agreement."
    )
    Path(args.out_md).write_text("\n".join(md) + "\n")
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")
    print(json.dumps(k, indent=2))


if __name__ == "__main__":
    main()
