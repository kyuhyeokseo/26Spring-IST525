# Control Comparison: Caveats and Recommended Framing

This note documents why the AI-reference vs control PR comparison
(comparison_ai_vs_control.json) cannot support causal claims, and
provides language to use in the writeup instead.

## What the comparison currently shows

| Metric                         | AI-reference (n=418) | Control (n=376) |
|--------------------------------|----------------------|-----------------|
| Merged rate                    | 77.51%               | 50.27%          |
| Median total comments / PR     | 5.0                  | 2.0             |
| Median time to merge (hours)   | 0.395                | 0.002           |
| Mean comments / PR             | 17.38                | 13.38           |

The headline gap (77.51% vs 50.27% merge rate) is the kind of number
that invites readers to assume "AI invocation makes PRs more likely to
merge." That inference is not supported by the design.

## Confounds that block a causal reading

1. **Bot-driven selection.** The AI-reference set captures PRs in
   which an AI bot account (most often `@copilot`) was invoked.
   Repositories that adopt Copilot agent workflows tend to produce
   small, automated PRs that are designed to merge. The Agent vs
   Discursive split (`agent_vs_discursive_summary.md`) shows that
   88.5% of human AI mentions and 99.6% of suggestion mentions are
   `@`-mentions of AI bot accounts, not discursive references. The
   merge-rate gap therefore reflects, in large part, the merge
   behavior of repositories that have institutionalized bot use, not
   a property of "discussions where AI is mentioned" in a general
   sense.

2. **PR-size and author asymmetry.** The control set was drawn from
   the same repositories but filtered to PRs without AI keywords. No
   matching was performed on PR size (lines added/deleted, files
   changed), PR author identity (human author vs bot account), or
   review intensity. The lower control merge rate is partly driven
   by long-tail PRs that ship slowly without bot involvement.

3. **Comment-volume confound.** The AI-reference set has higher
   median comment counts (5.0 vs 2.0). The reference pattern
   analysis already showed `r = 0.857` between AI mentions and total
   comments. PRs with more total comments are themselves selected for
   activity, which correlates with the kinds of PRs that get merged.

4. **Temporal/repo concentration.** A few high-throughput
   bot-orchestrated repositories likely contribute a disproportionate
   share of the AI-reference set. The cluster sensitivity analysis
   on the uptake sample already shows clustering matters; the same
   concern applies at the PR-level comparison.

## Recommended framing in the writeup

Replace any wording that implies AI invocation produces merging.
Suggested replacements:

- Instead of: "AI-reference PRs were 27 percentage points more
  likely to be merged."
- Use: "AI-reference PRs in this dataset show a substantially
  higher merge rate than the control set (77.51% vs 50.27%). This
  comparison is descriptive only and cannot be interpreted causally:
  the AI-reference set is dominated by bot-orchestrated workflows
  whose PRs are systematically smaller and more automation-friendly
  than the control."

- Add as an explicit limitation: "We do not perform PR-size or
  author-type matching, so the AI-reference vs control comparison
  cannot be read as the effect of AI invocation on PR success."

## Optional follow-up cuts (if time permits)

These would substantively strengthen the comparison:

1. **Author-type stratification.** Re-compute merge rates after
   removing PRs whose author is a bot account or auto-PR machinery.
   This removes the most obvious source of merge-rate inflation.

2. **PR-size matched comparison.** For each AI-reference PR, find a
   control PR within the same repository and within +/-50% of the
   line count, and compare merge rates within that matched subset.

3. **Repo fixed-effect comparison.** Restrict to repositories that
   appear in both sets and compare AI-reference vs control merge
   rates within each repository, then aggregate.

4. **Agent-only vs discursive-only split of the AI-reference set.**
   Re-run the merge comparison separately for PRs whose AI mentions
   are agent-commanding vs purely discursive (using the new
   invocation_class column). If the merge gap is concentrated in
   the agent-commanding subset, that confirms bot orchestration is
   doing the work in the headline number.

## What is still defensible from the comparison

The comparison can still be reported as descriptive context for the
sample. The sentence "in our sample, AI-reference PRs cluster around
shorter time to merge and higher comment counts" is fine as a
description of the dataset. What is not defensible is "AI invocation
predicts merge."
