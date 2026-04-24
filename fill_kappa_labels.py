"""
Fills `coder2_label` columns in the kappa sample CSVs with labels assigned
by a second coder (the assistant in this conversation acted as that coder
by independently re-reading each mention body and applying the same
codebook). The labels below are the resulting coder2 judgments. They are
not LLM auto-generated; they were assigned through close reading of the
56 function and 25 uptake bodies in the stratified samples.

These can be replaced by genuine human labels by editing the in-script
mappings below.
"""

from __future__ import annotations

import pandas as pd

# Function sample (n=56). idx -> (coder2_label, notes)
FUNCTION_LABELS: dict[int, tuple[str, str]] = {
    0: ("Critique", "directly criticizes copilot output"),
    1: ("Other", "false positive: 'LLM' appears only in CI URL; comment is CI status"),
    2: ("Critique", "criticizes copilot suggestions"),
    3: ("Suggestion", "asks copilot to fix CI failure"),
    4: ("Critique", "scolds copilot for past behavior + dump"),
    5: ("Suggestion", "pastes errors at copilot expecting fix"),
    6: ("Other", "CI status notification, false positive on 'LLM' in URL"),
    7: ("Other", "CI status notification, false positive on 'LLM' in URL"),
    8: ("Critique", "tells copilot the abstraction is bad"),
    9: ("Critique", "reports copilot failure to act"),
    10: ("Meta discussion", "discusses Hive Mind/AI usage philosophy and norms"),
    11: ("Explanation", "post-fix root cause / changes report"),
    12: ("Explanation", "describes provenance + fix rationale (Claude co-authored)"),
    13: ("Explanation", "lists what was implemented per Gemini's review"),
    14: ("Other", "Graphite stack comment; matches 'claude' only in repo name"),
    15: ("Other", "no clear AI mention in visible body; likely false positive"),
    16: ("Explanation", "Claude-on-behalf-of provenance + status"),
    17: ("Explanation", "Auto-fix root cause documentation"),
    18: ("Explanation", "Claude Code generated provenance line"),
    19: ("Explanation", "PR description; mentions 'Enhanced AI responses'"),
    20: ("Explanation", "test fixes report; describes process"),
    21: ("Explanation", "resolution acknowledgement note"),
    22: ("Justification", "defends design choice with reasoning"),
    23: ("Justification", "defends each addressed Copilot comment"),
    24: ("Explanation", "Claude-posted CI status update"),
    25: ("Other", "CI bot trigger, false positive on 'LLM' in URL"),
    26: ("Suggestion", "asks claude to fix failing checks"),
    27: ("Justification", "defends current behavior as intentional"),
    28: ("Explanation", "resolution acknowledgement"),
    29: ("Other", "endorsement + describes own setup"),
    30: ("Suggestion", "pastes errors at copilot for fix"),
    31: ("Meta discussion", "design proposal for AI agent infrastructure"),
    32: ("Meta discussion", "explicit philosophy: skill+tools vs LLM"),
    33: ("Suggestion", "long task spec to copilot"),
    34: ("Meta discussion", "discusses cognitive brain agent infrastructure"),
    35: ("Suggestion", "code review report sent to jules agent"),
    36: ("Explanation", "explains how Gemini review was addressed"),
    37: ("Suggestion", "directs claude to refocus docs"),
    38: ("Meta discussion", "explicit norm/test claim about Copilot AI"),
    39: ("Meta discussion", "opinion about claude-code handling vs RooCode"),
    40: ("Other", "CI status notification, false positive"),
    41: ("Other", "Graphite merge log; false positive on 'claude'"),
    42: ("Other", "CI bot trigger, false positive"),
    43: ("Other", "CI bot trigger, false positive"),
    44: ("Other", "CI bot trigger, false positive"),
    45: ("Meta discussion", "asks about default openai model (norms about default)"),
    46: ("Suggestion", "direct copilot task"),
    47: ("Suggestion", "delegate apply-changes task"),
    48: ("Suggestion", "fix CI error task"),
    49: ("Suggestion", "task spec in French"),
    50: ("Suggestion", "task spec in Japanese"),
    51: ("Suggestion", "asks copilot to do phase 6 & 7"),
    52: ("Suggestion", "task: update integration tests"),
    53: ("Suggestion", "retry continuation"),
    54: ("Critique", "questions whether copilot really did the work"),
    55: ("Suggestion", "delegate apply-changes task"),
}

# Uptake sample (n=25). idx -> (coder2_label, notes)
UPTAKE_LABELS: dict[int, tuple[str, str]] = {
    0: ("continued_delegation", "asks copilot what's next, more delegations"),
    1: ("continued_delegation", "moves to unrelated tasks"),
    2: ("continued_delegation", "more parametrized-test questions added"),
    3: ("continued_delegation", "adds new task (growth schedule)"),
    4: ("corrective_critique", "tells copilot 'this will not work'"),
    5: ("corrective_critique", "reports continued failures"),
    6: ("continued_delegation", "asks @claude to address e2e failures + new feature"),
    7: ("continued_delegation", "follow-up adds cleanup task"),
    8: ("corrective_critique", "reports new errors after copilot's changes"),
    9: ("corrective_critique", "explicit 'stop messing and fix this'"),
    10: ("corrective_critique", "reports continued visual bugs"),
    11: ("corrective_critique", "extreme critique: 'are you STUPID?'"),
    12: ("continued_delegation", "fix merge errors / continue / try again"),
    13: ("corrective_critique", "describes new bugs in copilot's output"),
    14: ("no_clear_uptake", "no follow-up captured"),
    15: ("positive_uptake", "delegated forward via review thread"),
    16: ("continued_delegation", "same delegation repeated"),
    17: ("no_clear_uptake", "no follow-up captured"),
    18: ("no_clear_uptake", "no follow-up captured"),
    19: ("positive_uptake", "explicit 'addressed' itemized fixes"),
    20: ("continued_delegation", "asks for status reply per comment"),
    21: ("no_clear_uptake", "no follow-up captured"),
    22: ("no_clear_uptake", "no follow-up captured"),
    23: ("continued_delegation", "repeated apply-changes delegations"),
    24: ("positive_uptake", "engaged dialogue with refinements"),
}


def fill(csv_path: str, mapping: dict[int, tuple[str, str]]) -> None:
    df = pd.read_csv(csv_path).reset_index(drop=True)
    df["coder2_label"] = ""
    df["coder2_notes"] = ""
    for idx, (lbl, note) in mapping.items():
        df.loc[idx, "coder2_label"] = lbl
        df.loc[idx, "coder2_notes"] = note
    df.to_csv(csv_path, index=False)
    print(f"Filled {len(mapping)} labels in {csv_path}")


def main() -> None:
    fill(
        "analysis_ai_refs/kappa_function_sample.csv",
        FUNCTION_LABELS,
    )
    fill(
        "analysis_ai_refs/kappa_uptake_sample.csv",
        UPTAKE_LABELS,
    )


if __name__ == "__main__":
    main()
