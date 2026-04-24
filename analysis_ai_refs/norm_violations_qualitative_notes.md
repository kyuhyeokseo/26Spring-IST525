# Normative Episodes Around AI Use: Qualitative Notes

This note distills the human-authored hits from
`norm_violations_hits.csv` into the small set of episodes that are
substantively interesting for CSCW framing. The grep pass returned
108 hits across 8 patterns, but 87 of those were bot-generated text
(e.g., `🤖 AI Code Review` headers) and most of the remaining 21 were
either policy/tooling self-description or false positives.

The cases below are the ones in which a human is *actively
negotiating* whether or how AI may participate in the work.

## Episode 1: explicit rejection of AI for architectural reasons
**`algesten/str0m#810`** — a contributor proposes adding an SPED
component. The maintainer (`algesten`) replies:

> "I think the SPED part is something I'd prefer to hand roll (as
> opposed to vibe code), since it is important to maintain a clear
> idea of separation-of-concerns throughout the code base at the same
> time as you're mashing the layers together."

The contributor (`xnorpx`) acknowledges and re-aligns. This is a
clean CSCW vignette: a maintainer enforces a craft norm by name
("hand roll, not vibe code") and tied to a substantive
architectural rationale. The norm is articulated *during the PR
exchange*, not in policy documentation.

This is exactly the kind of in-thread negotiation that the
quantitative invocation/uptake frame cannot see, because it never
contains an `@copilot` mention.

## Episode 2: defending AI autonomy as a product/process choice
**`link-assistant/hive-mind#1050`** — the author (`konard`) argues
extensively in PR comments that their `Hive Mind` system gives AI
"as much creative freedom as a real programmer," running with sudo
access in dedicated VMs. Multiple comments compare the AI's
creativity to "average programmers" and frame `vibe coding websites`
as a category. Here the author is *resisting* the implicit norm
that AI should be tightly bounded; they make the case for fewer
constraints.

This is the inverse polarity of Episode 1: instead of a norm being
enforced, a participant is trying to shift the norm.

## Episode 3: explicit "No AI" headers in PR review templates
**`arcade-cabinet/protocol-silent-night#69`** — the same human
account posts multiple `## 🤖 AI Code Review` reports that
themselves embed disclosure conventions. Here the norm has been
*templatized*: the human authoring the comment has built a workflow
in which AI involvement is announced up front, and concerns are
flagged in a fixed structure. This is norm reproduction via tooling,
not norm contestation.

## Pattern-level quantitative summary

The full grep hit profile (108 hits over 50 PRs, 45 repos, 21 of
which were human-authored):

| Pattern                   | Total | Notable case                          |
|---------------------------|-------|---------------------------------------|
| `policy_or_guideline`     | 33    | mostly bot-generated CLAUDE.md text   |
| `ai_disclosure_required`  | 24    | mostly tooling/config strings         |
| `verify_before_merge`     | 19    | mostly auto-generated check lists     |
| `vibe_coding`             | 10    | str0m#810 + hive-mind#1050 discussions|
| `human_review_framing`    | 10    | mostly bot review templates           |
| `explicit_ban`            | 9     | arcade-cabinet template + a false hit |
| `low_effort` / `ai_inverse_human` | 3 | single-line snippets             |

The headline observation from this sweep: at the corpus-level
(n=7,265 comments + 966 reviews), explicit human-authored normative
challenges to AI use are **rare**. The dominant mode of "talking
about AI" in this dataset is workflow orchestration (`@copilot ...`)
and process documentation (`🤖 Co-Authored-By`). Active norm
contestation is a minority phenomenon, but when it appears it is
substantive and articulated in domain-specific terms (e.g., "hand
roll for separation of concerns").

## Why this matters for the writeup

1. The discursive subset (n=106 in the agent_vs_discursive split)
   is the layer in which CSCW-relevant norm formation is visible.
   Even small, this subset is qualitatively distinct from the
   bot-orchestration subset.

2. The rarity of explicit norm contestation is itself a finding.
   It supports framing the current OSS environment as one in which
   AI participation is being **routinized through tooling** rather
   than openly debated. Episode 1 is the exception that proves the
   rule.

3. For the paper, two or three vignettes (Episode 1 is the
   strongest) can be lifted directly into a results subsection on
   "Normative Negotiation" without any further coding. They will
   anchor the otherwise quantitative narrative.
