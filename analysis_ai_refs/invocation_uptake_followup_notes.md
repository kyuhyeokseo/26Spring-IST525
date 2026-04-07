# Invocation Uptake Follow-Up Notes

This note adds three pieces on top of the 100-case stratified uptake sample:

1. percentage-based summaries
2. representative example cases
3. simple association tests using permutation-based chi-square

Source files:
- `analysis_ai_refs/invocation_uptake_stratified_100.csv`
- `analysis_ai_refs/invocation_uptake_stratified_100_labeled.csv`
- `analysis_ai_refs/invocation_uptake_summary.json`

## 1. Percentage-Based Summary

## Overall uptake distribution

- positive_uptake: 62.0%
- corrective_critique: 33.0%
- continued_delegation: 4.0%
- no_clear_uptake: 1.0%

Interpretation:
The dominant pattern is positive uptake, but critique remains substantial. This supports a `conditional trust` interpretation rather than either blind acceptance or purely symbolic invocation.

## Uptake by timing

### Early

- positive_uptake: 52.0%
- corrective_critique: 42.0%
- continued_delegation: 4.0%
- no_clear_uptake: 2.0%

### Middle

- positive_uptake: 63.64%
- corrective_critique: 27.27%
- continued_delegation: 9.09%

### Late

- positive_uptake: 78.57%
- corrective_critique: 21.43%

Interpretation:
Early invocations are the most mixed and supervisory. Late invocations are much more likely to be associated with positive uptake.

## Uptake by role

### Author

- positive_uptake: 81.82%
- corrective_critique: 18.18%

### Reviewer

- positive_uptake: 59.46%
- corrective_critique: 32.43%
- continued_delegation: 5.41%
- no_clear_uptake: 2.70%

### Other commenter

- positive_uptake: 59.62%
- corrective_critique: 36.54%
- continued_delegation: 3.85%

Interpretation:
Author invocations are more likely to end in positive uptake, while reviewer and other-commenter invocations are more mixed and more supervisory.

## Uptake by merge status

### Non-merged

- positive_uptake: 40.62%
- corrective_critique: 50.0%
- continued_delegation: 9.38%

### Merged

- positive_uptake: 72.06%
- corrective_critique: 25.0%
- continued_delegation: 1.47%
- no_clear_uptake: 1.47%

Interpretation:
This is one of the clearest descriptive patterns in the sample. Merged cases are much more likely to show positive uptake, while non-merged cases are more likely to show corrective critique.

## 2. Representative Example Cases

## Immediate positive uptake

Example:
- `heyns1000/omnigrid#31`
- Invocation: a long `@copilot` status/update prompt integrating cross-PR ecosystem context
- Follow-up: another immediate `@copilot` continuation, followed by `@copilot continue`
- Outcome: merged within 2.874 hours

Interpretation:
This is a case where invocation is not ignored. It quickly enters an active workflow that moves toward completion.

Another concise example:
- `Hexagon/hemulator#214`
- Invocation: `@copilot check format clippy and lint`
- Follow-up: `@copilot check format and clippy`
- Outcome: merged

Interpretation:
The interaction remains tightly task-oriented and converges.

## Critique followed by eventual merge

Example:
- `FreeForCharity/FFC-EX-PAGboosters.org#28`
- Invocation: `@copilot Fix and understand why you are not properly reading comments...`
- Follow-up:
  - asks whether Copilot can correctly read a code snippet
  - explicitly explains what Copilot misunderstood
- Outcome: merged after 7.178 hours

Interpretation:
This is a strong `conditional trust` case. The AI is not simply accepted; it is corrected and then still incorporated into a merged workflow.

Another example:
- `Xenthio/UITest#30`
- Invocation: `@copilot Please fix the build errors`
- Follow-up reports the issue is still not fixed
- Outcome: merged after 0.955 hours

Interpretation:
Critique and correction do not necessarily prevent resolution. They can be part of the path to it.

## Early-phase supervisory invocation

Example:
- `jchoi2x/hocuspocus#3`
- Invocation: `@copilot add cursorrules for testing conventions...`
- Follow-up:
  - `This needs to go away...`
  - `dont put crypto on globalThis...`
- Outcome: not merged

Interpretation:
This is a clear case of active supervision and norm enforcement. AI is being directed, but also constrained and corrected.

Another example:
- `ollieb89/jules_api_ui#74`
- Invocation: `@copilot apply changes based on the comments in this thread`
- Follow-up:
  - `fix these merge errors`
  - `continue`
- Outcome: not merged

Interpretation:
The interaction keeps delegating work forward, but does not clearly converge.

## 3. Simple Statistical Tests

Because the sample is modest and the environment did not include SciPy, a permutation-based chi-square test was used as a lightweight association check.

## Timing × uptake category

- Observed chi-square: 8.1836
- df: 6
- permutation p-value: 0.2108

Interpretation:
The descriptive timing pattern is interesting, especially the stronger critique share in early cases, but in this 100-case sample the timing × uptake association is not strong enough to treat as statistically compelling.

## Merge status × uptake category

- Observed chi-square: 11.4586
- df: 3
- permutation p-value: 0.0070

Interpretation:
This is the strongest quantitative result from the uptake sample. Merge status is meaningfully associated with uptake pattern: merged cases are much more likely to show positive uptake, while non-merged cases are much more likely to show corrective critique.

## Analytical Takeaway

These follow-up analyses strengthen the argument in three ways:

1. Invocation is often followed by uptake rather than stopping at mention.
2. That uptake is not uniformly trusting; critique remains substantial.
3. The strongest and most robust distinction is between merged and non-merged cases, which is highly consistent with a `conditional trust` interpretation.

## Writing-Friendly Summary

"In a 100-case stratified uptake sample, direct AI invocation most often led to positive uptake (62%), but corrective critique remained substantial (33%). Timing differences were descriptively suggestive but not statistically strong in this sample. By contrast, merge status showed a clearer association with uptake pattern: non-merged cases were more critique-heavy (50.0% corrective critique), whereas merged cases were substantially more likely to show positive uptake (72.1%). These results suggest that AI invocation is often taken up in practice, but typically under conditions of active supervision rather than unconditional trust."
