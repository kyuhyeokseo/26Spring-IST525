"""
Applies the author-accountability codebook to the 46 author-authored
discursive AI mentions (invocation_class == 'discursive' AND
speaker_role == 'author').

The labels below were assigned by close reading of each body against
the codebook in `analysis_ai_refs/author_accountability_codebook.md`.
A second coder (the first author) is expected to spot-check the 15
cases listed in `author_accountability_phase_b_template.csv` for
inter-coder reliability.

Outputs:
  analysis_ai_refs/author_accountability_coded.csv
  analysis_ai_refs/author_accountability_summary.{md,json}
  analysis_ai_refs/author_accountability_phase_b_template.csv
"""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pandas as pd

random.seed(42)

# idx -> (label, rationale)
LABELS: dict[int, tuple[str, str]] = {
    0: ("other", "AI is product of repo (implementing Claude model support), not the tool used"),
    1: ("provenance_only", "'Posted by Claude on behalf of @gmr' tag + routine status"),
    2: ("provenance_only", "same template: posted-by-Claude prefix + status"),
    3: ("other", "PR description for Hebrew translation; AI is product context"),
    4: ("provenance_only", "brief Hebrew note disclosing Copilot was used"),
    5: ("provenance_only", "'Generated with Claude Code' tag on routine review"),
    6: ("provenance_only", "same template as #5, different PR"),
    7: ("provenance_only", "heads-up disclosure of Copilot use; commits to add to commit msg"),
    8: ("other", "false positive: 'LLM' appears only in qwen3_moe filename"),
    9: ("process_documentation", "describes how each of 5 Copilot review comments was processed"),
    10: ("process_documentation", "itemized response to Copilot/Claude review in claude-coded repo"),
    11: ("other", "resolution note; AI appears only in filename path"),
    12: ("other", "resolution note; AI appears only in filename path"),
    13: ("other", "resolution note; AI appears only in filename path"),
    14: ("other", "resolution note; AI appears only in filename path"),
    15: ("other", "resolution note; AI appears only in filename path"),
    16: ("other", "body consists mainly of quoted Copilot review text"),
    17: ("process_documentation", "describes .claude-flow/ workflow orchestration files and their purpose"),
    18: ("provenance_only", "[AI-assisted - Claude] tag on PR closure explanation"),
    19: ("provenance_only", "[AI-assisted - Claude] tag on short status update"),
    20: ("provenance_only", "[AI-assisted - Claude] tag on detailed fix writeup"),
    21: ("provenance_only", "[AI-assisted - Claude] tag on CI debugging report"),
    22: ("provenance_only", "[AI-assisted - Claude] tag on review-response argument"),
    23: ("provenance_only", "[AI-assisted - Claude] tag on follow-up issue filing"),
    24: ("process_documentation", "structured 'Review Comments Processed' + Co-Authored-By: Claude"),
    25: ("provenance_only", "'Co-Authored-By: Claude' tag dominates; technical content incidental"),
    26: ("provenance_only", "'Generated with Claude Code' tag on code review"),
    27: ("fault_to_ai", "'ignore the one it said about AGENTS.md' — Copilot got a comment wrong"),
    28: ("other", "Graphite stack comment; AI keyword only in repo name 'claude-extras'"),
    29: ("other", "merge activity notification; AI keyword only in repo name"),
    30: ("other", "Graphite stack comment; AI keyword only in repo name"),
    31: ("other", "merge activity notification; AI keyword only in repo name"),
    32: ("defensive_justification", "'Intentionally Not Changed' section defending decisions against AI reviewer critique"),
    33: ("other", "describes product feature description that mentions Claude/Gemini models"),
    34: ("other", "describes code fix in file that interacts with Claude/Gemini models"),
    35: ("other", "philosophical defense of AI autonomy as product design, not accountability for this PR"),
    36: ("provenance_only", "AI-generated 'Solution Draft Log' posting on author's behalf"),
    37: ("other", "philosophical comparison of AI vs human programmers; product advocacy"),
    38: ("provenance_only", "AI-generated 'Solution Draft Log' posting on author's behalf"),
    39: ("other", "defends a color decision by citing CLAUDE.md rules; AI aspect incidental"),
    40: ("process_documentation", "itemized fixes in response to claude-review comments"),
    41: ("other", "defends product behavior (exit code 3) as intentional; AI is product context"),
    42: ("process_documentation", "commits to address each Gemini review comment with planned fixes"),
    43: ("process_documentation", "itemized changes made in response to Gemini Code Assist review"),
    44: ("process_documentation", "itemized fixes promised in response to Gemini review"),
    45: ("process_documentation", "explains that Claude Code usage over months revealed parameter needs"),
}


def main() -> None:
    df = pd.read_csv(
        "analysis_ai_refs/human_mentions_with_invocation_class.csv"
    )
    sub = df[
        (df["invocation_class"] == "discursive")
        & (df["speaker_role"] == "author")
    ].reset_index(drop=True)
    assert len(sub) == 46, f"expected 46 rows, got {len(sub)}"

    sub["accountability_label"] = sub.index.map(lambda i: LABELS[i][0])
    sub["accountability_rationale"] = sub.index.map(lambda i: LABELS[i][1])
    keep = [
        "mention_uid",
        "repo_name",
        "pr_number",
        "user_login",
        "timing_phase",
        "mention_location",
        "mention_body",
        "llm_primary_label",
        "accountability_label",
        "accountability_rationale",
    ]
    sub[keep].to_csv(
        "analysis_ai_refs/author_accountability_coded.csv", index=False
    )

    # Summary
    counts = Counter(sub["accountability_label"])
    total = len(sub)
    pct = {k: round(100 * v / total, 2) for k, v in counts.items()}
    # Excluding "other" subset
    non_other_total = total - counts.get("other", 0)
    non_other_pct = {
        k: round(100 * v / non_other_total, 2)
        for k, v in counts.items()
        if k != "other" and non_other_total > 0
    }

    summary = {
        "n_total": total,
        "counts": dict(counts),
        "pct": pct,
        "n_excluding_other": non_other_total,
        "pct_excluding_other": non_other_pct,
        "cross_with_timing": {},
        "cross_with_llm_function": {},
    }

    # Cross with timing
    for timing in sub["timing_phase"].dropna().unique():
        s = sub[sub["timing_phase"] == timing]
        summary["cross_with_timing"][str(timing)] = dict(
            Counter(s["accountability_label"])
        )

    # Cross with original LLM function label
    for llm in sub["llm_primary_label"].fillna("__missing__").unique():
        s = sub[sub["llm_primary_label"].fillna("__missing__") == llm]
        summary["cross_with_llm_function"][str(llm)] = dict(
            Counter(s["accountability_label"])
        )

    Path("analysis_ai_refs/author_accountability_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    # Markdown summary
    md: list[str] = []
    md.append("# Author Accountability Modes: Coded Distribution\n")
    md.append(
        "Second-pass coding of the 46 author-authored discursive AI "
        "mentions. Codebook: "
        "`author_accountability_codebook.md`. Labels assigned by close "
        "reading of each body against the 6-category scheme; a 15-case "
        "stratified subsample is reserved for inter-coder reliability in "
        "`author_accountability_phase_b_template.csv`.\n"
    )
    md.append(f"## Distribution (n={total})\n")
    for k in ["provenance_only", "process_documentation",
              "defensive_justification", "credit_partition",
              "fault_to_ai", "other"]:
        c = counts.get(k, 0)
        md.append(f"- `{k}`: {c} ({pct.get(k, 0.0)}%)")
    md.append("")

    md.append(
        f"## Distribution excluding `other` "
        f"(n={non_other_total} genuine AI-accountability cases)\n"
    )
    for k in ["provenance_only", "process_documentation",
              "defensive_justification", "credit_partition",
              "fault_to_ai"]:
        c = counts.get(k, 0)
        md.append(f"- `{k}`: {c} ({non_other_pct.get(k, 0.0)}%)")
    md.append("")

    md.append("## Representative quotes by category\n")
    for label in ["provenance_only", "process_documentation",
                  "defensive_justification", "fault_to_ai"]:
        matching = sub[sub["accountability_label"] == label]
        if matching.empty:
            continue
        md.append(f"### `{label}` examples\n")
        for _, r in matching.head(3).iterrows():
            snip = str(r["mention_body"])[:400].replace("\n", " ")
            md.append(f"- **{r['repo_name']}#{r['pr_number']}** (`{r['user_login']}`)")
            md.append(f"  > {snip}")
        md.append("")

    md.append("## Interpretation\n")
    md.append(
        "Of the 46 author-authored discursive AI mentions, 19 (41.3%) "
        "were `other` — primarily false positives where an AI keyword "
        "appears in a filename, product description, or repo name "
        "without doing accountability work. Restricting to the 27 "
        "genuine AI-accountability cases:\n"
    )
    md.append(
        f"- `provenance_only` dominates at {non_other_pct.get('provenance_only', 0.0)}% — "
        "authors overwhelmingly use bare disclosure markers ('🤖 Generated "
        "with Claude Code', '[AI-assisted - Claude]', 'Co-Authored-By: "
        "Claude') with no accompanying defense or partition."
    )
    md.append(
        f"- `process_documentation` is the second most common mode "
        f"({non_other_pct.get('process_documentation', 0.0)}%) — "
        "authors describe how they processed AI-generated review feedback "
        "or AI-assisted tooling, typically as structured 'addressed' lists."
    )
    md.append(
        f"- `defensive_justification` ({non_other_pct.get('defensive_justification', 0.0)}%) "
        f"and `fault_to_ai` ({non_other_pct.get('fault_to_ai', 0.0)}%) "
        "are rare. `credit_partition` does not appear at all in this "
        "sample."
    )
    md.append("")
    md.append(
        "This is a stronger and more conservative finding than the "
        "initial 'author attribution regime' hypothesis. Authors are "
        "*not* performing elaborate accountability theater. They are "
        "doing **minimal, routinized disclosure** — a provenance tag at "
        "the end of a comment, or a 'here is how I processed AI review' "
        "checklist. Credit partition and fault attribution to AI, which "
        "would require more agonistic framing, are essentially absent. "
        "This aligns with the Tier-3 finding that explicit normative "
        "challenge is rare: AI participation is being absorbed through "
        "lightweight, template-like conventions rather than contested in "
        "prose."
    )
    md.append("")
    md.append(
        "For the paper, this supports the revised framing: the "
        "discursive subset is the layer where AI is made visible, but "
        "the mode of visibility is **disclosure-and-proceed**, not "
        "active accountability negotiation. Two results sections follow "
        "naturally from this: a quantitative distribution, and a short "
        "qualitative note on the near-absence of credit partition and "
        "defensive argumentation (which is itself a CSCW finding about "
        "how OSS communities handle AI)."
    )

    Path("analysis_ai_refs/author_accountability_summary.md").write_text(
        "\n".join(md) + "\n"
    )

    # Phase B template: 15-case stratified subsample
    rng = random.Random(42)
    phase_b_rows: list[pd.Series] = []
    # Sample proportionally: take up to 4 from each non-singleton class, else all
    for label, group in sub.groupby("accountability_label"):
        n_target = min(len(group), 4)
        idx_list = list(group.index)
        rng.shuffle(idx_list)
        phase_b_rows.extend(sub.loc[idx_list[:n_target]].to_dict("records"))
    # Trim or expand to 15
    phase_b_df = pd.DataFrame(phase_b_rows)
    if len(phase_b_df) > 15:
        phase_b_df = phase_b_df.sample(n=15, random_state=42)
    phase_b_df = phase_b_df.reset_index(drop=True)
    phase_b_df["coder2_label"] = ""
    phase_b_df["coder2_notes"] = ""
    phase_b_df[
        [
            "mention_uid",
            "repo_name",
            "pr_number",
            "user_login",
            "timing_phase",
            "mention_location",
            "mention_body",
            "accountability_label",
            "accountability_rationale",
            "coder2_label",
            "coder2_notes",
        ]
    ].to_csv(
        "analysis_ai_refs/author_accountability_phase_b_template.csv",
        index=False,
    )

    print(f"Coded 46 cases. Distribution: {dict(counts)}")
    print(f"Phase B template: {len(phase_b_df)} cases, stratified")
    print("Outputs:")
    print("  analysis_ai_refs/author_accountability_coded.csv")
    print("  analysis_ai_refs/author_accountability_summary.{md,json}")
    print("  analysis_ai_refs/author_accountability_phase_b_template.csv")


if __name__ == "__main__":
    main()
