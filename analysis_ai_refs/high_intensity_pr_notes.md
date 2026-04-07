# High-Intensity PR Notes

This note summarizes representative PRs with 11+ AI-reference comments, focusing on why discussion becomes long and why merge outcomes may be weaker or slower in high-intensity cases.

Source files:
- `data_ai_refs/pull_requests.csv`
- `data_ai_refs/comments.csv`

## Important Caveat

High-intensity PRs are not all the same.

Some are inflated by bot repetition or automated review loops, while others reflect genuine human-in-the-loop AI coordination. That distinction matters when interpreting why comment counts grow and merge rates drop.

## Literal Top Outlier Cases

### `rcy1314/weather-action#308`


- AI-reference comments: 880
- Total comments: 881
- Merged: False
- Bot-heavy pattern: 880 comments from `cr-gpt[bot]`

Interpretation:
This is effectively a bot-loop outlier rather than a rich human collaboration case. It should not be treated as representative of discussion depth.

### `AndyMik90/Auto-Claude#417`

- AI-reference comments: 108
- Total comments: 186
- Merged: False
- Bot-heavy pattern: 183 bot comments, mostly `coderabbitai[bot]`

Interpretation:
Again, this is largely automated review inflation rather than sustained human debate.

## Representative Human-in-the-Loop High-Intensity Cases

These are better close-reading examples because they contain substantial human participation.

### `arcade-cabinet/protocol-silent-night#69`

- AI-reference comments: 162
- Total comments: 697
- Human comments: 544
- Bot comments: 153
- Merged: False

Observed pattern:
- repeated CI failure diagnosis
- repeated AI review summaries
- multiple rounds of fix / test / re-review
- human and bot messages interleave in a repair loop

Representative examples:
- human summary of CI root cause and fix
- AI/bot reposting structured review analysis
- repeated review cycles tied to E2E failures

Interpretation:
This looks like long-running repair work around failing tests and accessibility issues. Discussion length is driven by repeated diagnosis and verification, not just by one-time AI mention.

### `arcade-cabinet/protocol-silent-night#70`

- AI-reference comments: 145
- Total comments: 447
- Human comments: 308
- Bot comments: 139
- Merged: False

Observed pattern:
- security/entropy change triggers many rounds of testing
- repeated "root cause" and "fix applied" messages
- AI review and CI remediation keep looping

Interpretation:
This is another iterative debug-and-verify PR. High AI intensity here seems tied to instability, repeated validation, and multiple fix attempts.

### `Open-J-Proxy/ojp#196`

- AI-reference comments: 131
- Total comments: 131
- Human comments: 66
- Bot comments: 65
- Merged: False

Observed pattern:
- user repeatedly instructs Copilot step-by-step
- "use this doc as a guide"
- "implement the tests"
- "create an implementation plan in phases"
- "implement phase 1"
- "implement phase 2"

Interpretation:
This PR is less about code review and more about phased AI-driven project management inside the PR thread. Discussion is long because the PR becomes a command-and-response workspace.

### `Stage4000/420th#1`

- AI-reference comments: 79
- Total comments: 79
- Human comments: 39
- Bot comments: 40
- Merged: True
- Time to merge: 193.04 hours

Observed pattern:
- user keeps extending feature scope
- asks for new features, UX refinements, DB simplification, role logic, dashboard changes
- repeated incremental change requests to Copilot

Representative examples:
- requests for role aliases and automatic role linking
- dark-mode-only request
- dashboard cleanup and schema simplification request

Interpretation:
This is a scope-expansion case. The PR stays active because the user continues adding requirements. High AI intensity here is linked to feature accretion rather than pure bug fixing.

### `mgradwohl/tasksmack#303`

- AI-reference comments: 67
- Total comments: 106
- Human comments: 38
- Bot comments: 68
- Merged: True
- Time to merge: 24.66 hours

Observed pattern:
- explicit phase-based workflow
- AI instructed to monitor CI and move to next phase
- code review comments folded into later phases
- iterative development across multiple implementation phases

Representative examples:
- "monitor CI workflows and iterate on fixes until they pass"
- "Let's address all of those in Phase 2"
- "Start on phase 2 work"

Interpretation:
This is a highly structured human-AI coordination case. The PR discussion becomes a lightweight orchestration layer for staged implementation.

## Cross-Case Pattern

Across representative high-intensity cases, at least three mechanisms recur:

1. Debug-and-verify loops
   - repeated CI failures
   - repeated diagnosis and fix attempts
   - repeated AI review outputs

2. Phase-based delegation
   - participants assign work step-by-step
   - AI is instructed to continue through explicit phases

3. Scope expansion
   - new requirements are added during the PR
   - the PR becomes a running backlog rather than a narrowly scoped patch

## Why Might Merge Rate Fall in 11+ Mention PRs?

The statistical result showed that 11+ mention PRs had:
- lower merge rate
- longer time to merge
- much higher comment counts

These close readings suggest several reasons:

- some PRs are structurally unstable because they involve repeated failure and rework
- some PRs accumulate requirements instead of converging
- some high counts are partly inflated by bot review loops
- some PRs use the thread as an AI coordination workspace, which lengthens discussion before closure

## Writing-Friendly Summary

"Close reading of high-intensity AI PRs suggests that long discussion is not produced by a single mechanism. Some outliers are inflated by repeated bot comments, but representative human-in-the-loop cases show three recurring dynamics: iterative debug-and-verify loops, phase-based delegation to AI agents, and scope expansion during implementation. These dynamics help explain why PRs with 11+ AI mentions tend to accumulate more comments and may merge less often or more slowly."
