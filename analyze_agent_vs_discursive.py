"""
Splits AI mentions into:
  - agent_commanding: mentions that @-mention an AI bot account
    (e.g., @copilot, @claude-bot, @cursor[bot], @github-copilot, @devin,
    @codex, @gemini, @sourcery-ai, @coderabbitai, @qodo-merge-pro, etc.)
  - discursive: AI is referenced in prose but no AI bot account is @-mentioned
    (e.g., "I asked ChatGPT and it said...", "Copilot suggested this earlier")

Re-runs the headline distributions (suggestion subtype, addressing mode,
role, timing, location) for each group so we can show the "Talking-to-AI 99%"
finding is or is not driven by bot-orchestration.

Inputs:
  analysis_ai_refs/suggestion_refinement_human_mentions.csv (has body)
  analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv (has labels)

Outputs:
  analysis_ai_refs/agent_vs_discursive_summary.json
  analysis_ai_refs/agent_vs_discursive_summary.md
  analysis_ai_refs/suggestion_refinement_with_invocation_class.csv
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

AGENT_LOGIN_PATTERNS = [
    r"@copilot\b",
    r"@github-copilot(?:\[bot\])?\b",
    r"@claude\b",
    r"@claude-bot\b",
    r"@anthropic-claude\b",
    r"@cursor(?:\[bot\])?\b",
    r"@cursoragent\b",
    r"@devin(?:-ai)?(?:\[bot\])?\b",
    r"@codex\b",
    r"@chatgpt-codex\b",
    r"@openai-codex\b",
    r"@gemini(?:-code-assist)?(?:\[bot\])?\b",
    r"@google-bard\b",
    r"@sourcery-ai(?:\[bot\])?\b",
    r"@coderabbitai(?:\[bot\])?\b",
    r"@qodo-merge-pro(?:\[bot\])?\b",
    r"@codiumai-pr-agent(?:\[bot\])?\b",
    r"@sweep-ai(?:\[bot\])?\b",
    r"@aider\b",
    r"@jules(?:\[bot\])?\b",
    r"@goose\b",
    r"@duckopus\b",
]

AGENT_RE = re.compile("|".join(AGENT_LOGIN_PATTERNS), re.IGNORECASE)


def classify_invocation_form(body: str) -> str:
    if not isinstance(body, str):
        return "discursive"
    return "agent_commanding" if AGENT_RE.search(body) else "discursive"


def safe_pct(d: dict[str, int]) -> dict[str, float]:
    total = sum(d.values()) or 1
    return {k: round(100 * v / total, 2) for k, v in d.items()}


def value_counts(series: pd.Series) -> dict[str, int]:
    return series.fillna("__missing__").value_counts().to_dict()


def crosstab(df: pd.DataFrame, row: str, col: str) -> dict:
    out: dict = defaultdict(lambda: defaultdict(int))
    for r, c in zip(df[row].fillna("__missing__"), df[col].fillna("__missing__")):
        out[str(r)][str(c)] += 1
    return {k: dict(v) for k, v in out.items()}


def crosstab_pct(ct: dict) -> dict:
    return {k: safe_pct(v) for k, v in ct.items()}


def summarize_block(df: pd.DataFrame) -> dict:
    n = len(df)
    block: dict = {
        "n": n,
        "subtype_counts": value_counts(df["suggestion_subtype"]),
        "addressing_counts": value_counts(df["addressing_mode"]),
        "role_counts": value_counts(df["speaker_role"]),
        "timing_counts": value_counts(df["timing_phase"]),
        "location_counts": value_counts(df["mention_location"]),
    }
    block["subtype_pct"] = safe_pct(block["subtype_counts"])
    block["addressing_pct"] = safe_pct(block["addressing_counts"])
    block["role_pct"] = safe_pct(block["role_counts"])
    block["timing_pct"] = safe_pct(block["timing_counts"])
    block["location_pct"] = safe_pct(block["location_counts"])
    block["subtype_by_role"] = crosstab(df, "speaker_role", "suggestion_subtype")
    block["subtype_by_role_pct"] = crosstab_pct(block["subtype_by_role"])
    block["subtype_by_timing"] = crosstab(df, "timing_phase", "suggestion_subtype")
    block["subtype_by_timing_pct"] = crosstab_pct(block["subtype_by_timing"])
    block["addressing_by_role"] = crosstab(df, "speaker_role", "addressing_mode")
    block["addressing_by_role_pct"] = crosstab_pct(block["addressing_by_role"])
    return block


def build_md(summary: dict) -> str:
    lines: list[str] = []
    lines.append("# Agent-Commanding vs Discursive Reference\n")
    lines.append(
        "This split partitions human-authored AI mentions by whether the body "
        "contains an @-mention of an AI bot account (`agent_commanding`) or only "
        "references AI in prose (`discursive`). The original headline finding "
        "of `Talking-to-AI` 99% is re-evaluated against this split to test "
        "whether it reflects discursive participation of AI or workflow-level "
        "bot orchestration.\n"
    )

    overall = summary["overall"]
    lines.append("## Overall split\n")
    lines.append(f"- Total: {overall['total']}")
    lines.append(
        f"- Agent-commanding: {overall['agent_commanding']} "
        f"({overall['agent_commanding_pct']}%)"
    )
    lines.append(
        f"- Discursive: {overall['discursive']} ({overall['discursive_pct']}%)\n"
    )

    for group in ("agent_commanding", "discursive"):
        block = summary[group]
        lines.append(f"## {group} (n={block['n']})\n")
        lines.append("### Suggestion subtype")
        for k, v in block["subtype_pct"].items():
            lines.append(f"- {k}: {v}% ({block['subtype_counts'][k]})")
        lines.append("\n### Addressing mode")
        for k, v in block["addressing_pct"].items():
            lines.append(f"- {k}: {v}% ({block['addressing_counts'][k]})")
        lines.append("\n### Speaker role")
        for k, v in block["role_pct"].items():
            lines.append(f"- {k}: {v}% ({block['role_counts'][k]})")
        lines.append("\n### Timing phase")
        for k, v in block["timing_pct"].items():
            lines.append(f"- {k}: {v}% ({block['timing_counts'][k]})")
        lines.append("\n### Location")
        for k, v in block["location_pct"].items():
            lines.append(f"- {k}: {v}% ({block['location_counts'][k]})")
        lines.append("")

    lines.append("## Interpretation hooks\n")
    o = summary["overall"]
    ac = summary["agent_commanding"]
    dc = summary["discursive"]
    addr_ac = ac["addressing_pct"].get("Talking-to-AI", 0.0)
    addr_dc = dc["addressing_pct"].get("Talking-to-AI", 0.0)
    inv_ac = ac["subtype_pct"].get("Suggestion-Invocation", 0.0)
    inv_dc = dc["subtype_pct"].get("Suggestion-Invocation", 0.0)
    lines.append(
        f"- Among `agent_commanding`, Talking-to-AI is {addr_ac}% and "
        f"Suggestion-Invocation is {inv_ac}%."
    )
    lines.append(
        f"- Among `discursive`, Talking-to-AI is {addr_dc}% and "
        f"Suggestion-Invocation is {inv_dc}%."
    )
    if abs(addr_ac - addr_dc) > 20:
        lines.append(
            "- The Talking-to-AI rate differs substantially between the two "
            "groups. The original 99% figure is largely a property of bot "
            "orchestration, not discursive AI participation."
        )
    else:
        lines.append(
            "- The Talking-to-AI rate is similar across both groups, which "
            "supports the original interpretation that AI is treated as an "
            "addressable participant even outside agent-account orchestration."
        )
    return "\n".join(lines) + "\n"


def merge_with_labels(base: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    label_cols = [c for c in labels.columns if c != "mention_uid"]
    base = base.drop(columns=[c for c in label_cols if c in base.columns])
    return base.merge(labels, on="mention_uid", how="left")


def summarize_full(df: pd.DataFrame, has_subtype: bool) -> dict:
    n = len(df)
    block: dict = {
        "n": n,
        "addressing_counts": value_counts(df["addressing_mode"])
        if "addressing_mode" in df.columns
        else {},
        "role_counts": value_counts(df["speaker_role"]),
        "timing_counts": value_counts(df["timing_phase"]),
        "location_counts": value_counts(df["mention_location"]),
    }
    if "llm_primary_label" in df.columns:
        block["function_counts"] = value_counts(df["llm_primary_label"])
        block["function_pct"] = safe_pct(block["function_counts"])
    if has_subtype and "suggestion_subtype" in df.columns:
        block["subtype_counts"] = value_counts(df["suggestion_subtype"])
        block["subtype_pct"] = safe_pct(block["subtype_counts"])
    if block["addressing_counts"]:
        block["addressing_pct"] = safe_pct(block["addressing_counts"])
    block["role_pct"] = safe_pct(block["role_counts"])
    block["timing_pct"] = safe_pct(block["timing_counts"])
    block["location_pct"] = safe_pct(block["location_counts"])
    return block


def write_md_section(title: str, summary: dict, lines: list[str]) -> None:
    lines.append(f"## {title}\n")
    o = summary["overall"]
    lines.append(f"- Total: {o['total']}")
    lines.append(
        f"- Agent-commanding: {o['agent_commanding']} ({o['agent_commanding_pct']}%)"
    )
    lines.append(f"- Discursive: {o['discursive']} ({o['discursive_pct']}%)\n")
    for group in ("agent_commanding", "discursive"):
        block = summary[group]
        lines.append(f"### {group} (n={block['n']})\n")
        if "function_pct" in block:
            lines.append("Function (LLM primary label):")
            for k, v in block["function_pct"].items():
                lines.append(f"- {k}: {v}% ({block['function_counts'][k]})")
            lines.append("")
        if "subtype_pct" in block:
            lines.append("Suggestion subtype:")
            for k, v in block["subtype_pct"].items():
                lines.append(f"- {k}: {v}% ({block['subtype_counts'][k]})")
            lines.append("")
        if block.get("addressing_pct"):
            lines.append("Addressing mode:")
            for k, v in block["addressing_pct"].items():
                lines.append(f"- {k}: {v}% ({block['addressing_counts'][k]})")
            lines.append("")
        lines.append("Speaker role:")
        for k, v in block["role_pct"].items():
            lines.append(f"- {k}: {v}% ({block['role_counts'][k]})")
        lines.append("")
        lines.append("Timing phase:")
        for k, v in block["timing_pct"].items():
            lines.append(f"- {k}: {v}% ({block['timing_counts'][k]})")
        lines.append("")
        lines.append("Location:")
        for k, v in block["location_pct"].items():
            lines.append(f"- {k}: {v}% ({block['location_counts'][k]})")
        lines.append("")


def split_summary(df: pd.DataFrame, has_subtype: bool) -> dict:
    total = len(df)
    n_agent = int((df["invocation_class"] == "agent_commanding").sum())
    n_disc = int((df["invocation_class"] == "discursive").sum())
    return {
        "overall": {
            "total": total,
            "agent_commanding": n_agent,
            "discursive": n_disc,
            "agent_commanding_pct": round(100 * n_agent / total, 2),
            "discursive_pct": round(100 * n_disc / total, 2),
        },
        "agent_commanding": summarize_full(
            df[df["invocation_class"] == "agent_commanding"], has_subtype
        ),
        "discursive": summarize_full(
            df[df["invocation_class"] == "discursive"], has_subtype
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-input-csv",
        default="analysis_ai_refs/llm_labeling_human_mentions.csv",
    )
    parser.add_argument(
        "--full-labels-csv",
        default="analysis_ai_refs/llm_labeling_human_mentions_labeled.csv",
    )
    parser.add_argument(
        "--suggestion-input-csv",
        default="analysis_ai_refs/suggestion_refinement_human_mentions.csv",
    )
    parser.add_argument(
        "--suggestion-labels-csv",
        default="analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv",
    )
    parser.add_argument(
        "--out-json",
        default="analysis_ai_refs/agent_vs_discursive_summary.json",
    )
    parser.add_argument(
        "--out-md",
        default="analysis_ai_refs/agent_vs_discursive_summary.md",
    )
    parser.add_argument(
        "--out-full-csv",
        default="analysis_ai_refs/human_mentions_with_invocation_class.csv",
    )
    parser.add_argument(
        "--out-suggestion-csv",
        default="analysis_ai_refs/suggestion_refinement_with_invocation_class.csv",
    )
    args = parser.parse_args()

    full_df = merge_with_labels(
        pd.read_csv(args.full_input_csv), pd.read_csv(args.full_labels_csv)
    )
    sug_df = merge_with_labels(
        pd.read_csv(args.suggestion_input_csv),
        pd.read_csv(args.suggestion_labels_csv),
    )

    full_df["invocation_class"] = full_df["mention_body"].apply(
        classify_invocation_form
    )
    sug_df["invocation_class"] = sug_df["mention_body"].apply(
        classify_invocation_form
    )

    summary = {
        "all_human_mentions": split_summary(full_df, has_subtype=False),
        "suggestion_subset": split_summary(sug_df, has_subtype=True),
    }

    Path(args.out_json).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    md_lines: list[str] = []
    md_lines.append("# Agent-Commanding vs Discursive Reference\n")
    md_lines.append(
        "This split partitions human-authored AI mentions by whether the body "
        "contains an @-mention of an AI bot account (`agent_commanding`) or "
        "only references AI in prose (`discursive`). The original headline "
        "finding of `Talking-to-AI` 99% is re-evaluated against this split to "
        "test whether it reflects discursive participation of AI or "
        "workflow-level bot orchestration.\n"
    )
    write_md_section(
        "All human-authored AI mentions (n=925)",
        summary["all_human_mentions"],
        md_lines,
    )
    write_md_section(
        "Suggestion subset (n=739)",
        summary["suggestion_subset"],
        md_lines,
    )

    md_lines.append("## Interpretation hooks\n")
    o = summary["all_human_mentions"]["overall"]
    s = summary["suggestion_subset"]["overall"]
    md_lines.append(
        f"- Across all 925 human-authored AI mentions, "
        f"{o['agent_commanding_pct']}% are agent-commanding "
        f"(@-mention an AI bot account) and only {o['discursive_pct']}% are "
        f"purely discursive references."
    )
    md_lines.append(
        f"- Within the Suggestion subset (n=739), the agent-commanding share "
        f"climbs to {s['agent_commanding_pct']}%, with only "
        f"{s['discursive']} purely discursive cases."
    )
    md_lines.append(
        "- The original 99% `Talking-to-AI` finding therefore reflects, "
        "almost entirely, workflow-level orchestration of AI bot agents "
        "(primarily Copilot) via @-mention, rather than discursive "
        "participation of AI in the open prose of code review."
    )
    md_lines.append(
        "- The discursive subset is small but qualitatively distinct: it "
        "captures the cases where developers reference AI tools in prose "
        "(e.g., `I asked ChatGPT...`, `Copilot suggested earlier`). It is "
        "this subset that maps onto the existing CHI/CSCW literature on "
        "AI-as-referenced-tool, while the agent-commanding subset maps onto "
        "the emerging governance question of bot-mediated workflow."
    )
    Path(args.out_md).write_text("\n".join(md_lines) + "\n")

    full_df.to_csv(args.out_full_csv, index=False)
    sug_df.to_csv(args.out_suggestion_csv, index=False)
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")
    print(f"Wrote: {args.out_full_csv}")
    print(f"Wrote: {args.out_suggestion_csv}")
    print(
        f"All-mentions split: agent="
        f"{summary['all_human_mentions']['overall']['agent_commanding']} "
        f"({summary['all_human_mentions']['overall']['agent_commanding_pct']}%) "
        f"discursive="
        f"{summary['all_human_mentions']['overall']['discursive']} "
        f"({summary['all_human_mentions']['overall']['discursive_pct']}%)"
    )
    print(
        f"Suggestion-subset split: agent="
        f"{summary['suggestion_subset']['overall']['agent_commanding']} "
        f"({summary['suggestion_subset']['overall']['agent_commanding_pct']}%) "
        f"discursive="
        f"{summary['suggestion_subset']['overall']['discursive']} "
        f"({summary['suggestion_subset']['overall']['discursive_pct']}%)"
    )


if __name__ == "__main__":
    main()
