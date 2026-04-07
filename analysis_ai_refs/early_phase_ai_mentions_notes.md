# Early-Phase AI Mention Notes

This note summarizes what kinds of human AI mentions cluster in the early phase of PR discussion.

Source files:
- `analysis_ai_refs/llm_labeling_human_mentions.csv`
- `analysis_ai_refs/llm_labeling_human_mentions_labeled.csv`

## Headline Pattern

More than half of human AI mentions occurred in the early phase.

- Total human mentions: 925
- Early-phase mentions: 472
- Early-phase share: 51.0%

Within the early phase, the dominant function was `Suggestion`.

- Suggestion: 382 / 472 (80.93%)
- Critique: 45 / 472 (9.53%)
- Explanation: 29 / 472 (6.14%)
- Justification: 7 / 472 (1.48%)
- Meta discussion: 2 / 472 (0.42%)

## Structural Pattern

### By role

- other_commenter: 269
- reviewer: 162
- author: 41

Interpretation:
Early AI mentions are not primarily author-only behavior. They are more often produced by other participants in the PR thread.

### By location

- issue_comment: 420
- review_comment: 41
- review: 11

Interpretation:
Early AI mentions happen overwhelmingly in general discussion rather than formal review artifacts.

## What Is Concentrated Early?

The early phase is mostly filled with:

1. Direct AI invocation
2. Task delegation
3. Requests to fix merge conflicts, tests, or type errors
4. Step-by-step implementation instructions
5. Early correction when AI-assisted work failed

This means early-phase AI mention is less about retrospective explanation and more about launching or steering work.

## Example Mentions

### Early Suggestion by Author

Examples:
- `strawgate/kb-yaml-to-lens#467`: "@claude can you fix the merge conflicts for me?"
- `strawgate/kb-yaml-to-lens#484`: "@claude this is failing type checking, can you get this ready to merge?"
- `strawgate/kb-yaml-to-lens#474`: "@claude lets make the assignments an \"Advanced Topic\""

Interpretation:
Authors often use early AI mention to assign concrete repair or revision tasks.

### Early Suggestion by Reviewer

Examples:
- `impakt73/ai-rust-hw-dev#40`: "@copilot try again please"
- `mgradwohl/tasksmack#303`: "@copilot Great keep going"
- `pradeepmouli/x-to-zod#36`: "@copilot See above"

Interpretation:
Reviewers also mobilize AI early, using it as an active participant in the revision process.

### Early Suggestion by Other Commenter

Examples:
- `Open-J-Proxy/ojp#196`: "@copilot implement phase 1"
- `Open-J-Proxy/ojp#196`: "@copilot implement phase 2"
- `Open-J-Proxy/ojp#196`: "@copilot implement phase 5"
- `Jayc82/Orion#1`: "@copilot Let's do issue #3"

Interpretation:
Other commenters frequently use early AI mention to sequence work into phases and delegate implementation steps.

### Early Explanation

Examples:
- `influxdata/docs-v2#6622`: "## Code review Found 1 issue ..."
- `frankbria/narrative-modeling-app#131`: "## Update: Package Lock and Workflow Files Added ..."

Interpretation:
Early `Explanation` mentions often summarize AI- or tool-related changes already made, but they are far less common than direct suggestions.

### Early Critique by Other Commenter

Examples:
- `Open-J-Proxy/ojp#196`: "@copilot I see no commit, did you push your latest fixes?"
- `NREL/HPC#827`: "@copilot The pull request was not made, something went wrong"
- `Stage4000/420th#1`: "@copilot that didn't quite fix it, the tooltips are still clipping ..."

Interpretation:
When critique appears early, it usually reacts to failed execution, missing commits, or incomplete fixes.

### Early Critique by Reviewer

Examples:
- `pradeepmouli/homebridge-rabbitair#10`: "@copilot you were on the wrong branch - i've just fixed it"
- `jchoi2x/hocuspocus#3`: "@copilot remove usage of globalThis. Nothing should be global"
- `dbosk/ladok3#122`: "@copilot this will not work ..."

Interpretation:
Reviewer critique in the early phase focuses on correcting AI-generated code or redirecting it toward project norms.

## Analytical Takeaway

Early-phase AI mention is best understood as coordination-through-invocation.

Participants are often not merely mentioning AI as a topic. They are invoking AI to begin work, structure tasks, request revisions, and correct failed outputs. This makes the early phase especially important for interpreting AI not just as a tool reference, but as part of the collaborative workflow itself.

## Writing-Friendly Summary

"More than half of human AI mentions occurred in the early phase of PR discussion, and over 80% of these early mentions were labeled as Suggestion. Qualitatively, these early mentions were often direct invocations such as `@claude can you fix the merge conflicts for me?` or `@copilot implement phase 1`, indicating that early-stage AI mention primarily functioned as a mechanism for initiating, delegating, and coordinating concrete work."
