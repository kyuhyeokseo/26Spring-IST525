# Invocation Uptake Sample Results Notes

This note summarizes the 29-case uptake coding sample for post-invocation interaction.

Source files:
- `analysis_ai_refs/invocation_uptake_coding_sample.csv`
- `analysis_ai_refs/invocation_uptake_coding_sample_labeled.csv`
- `analysis_ai_refs/invocation_uptake_summary.json`

## Headline Result

In the 29-case sample, the most common uptake pattern was `positive_uptake`.

- positive_uptake: 20 / 29 (68.97%)
- corrective_critique: 6 / 29 (20.69%)
- continued_delegation: 2 / 29 (6.90%)
- no_clear_uptake: 1 / 29 (3.45%)

Interpretation:
This suggests that direct AI invocation often leads to a response sequence that participants treat as usable or acceptable, but a substantial minority still shows corrective or supervisory behavior.

## By Merge Outcome

### Merged cases

- positive_uptake: 18
- corrective_critique: 1
- continued_delegation: 1
- no_clear_uptake: 0

Interpretation:
Merged cases are strongly associated with positive uptake in this sample.

### Non-merged cases

- positive_uptake: 2
- corrective_critique: 5
- continued_delegation: 1
- no_clear_uptake: 1

Interpretation:
Non-merged cases are much more likely to show corrective critique or unresolved delegation loops.

## By Timing

- early:
  - positive_uptake: 8
  - corrective_critique: 6
  - continued_delegation: 2
  - no_clear_uptake: 1

- middle:
  - positive_uptake: 4
  - no other labels in this sample

- late:
  - positive_uptake: 8
  - no other labels in this sample

Interpretation:
Early invocations show the most mixed outcomes. Later invocations in this sample are more consistently associated with positive uptake.

## By Role

- author:
  - positive_uptake: 1

- reviewer:
  - positive_uptake: 5
  - no_clear_uptake: 1

- other_commenter:
  - positive_uptake: 14
  - corrective_critique: 6
  - continued_delegation: 2

Interpretation:
Other commenters remain the most interactionally active role, and they are also where most critique appears. This fits the broader pattern that other commenters are central to invocation-driven coordination, but also to monitoring and correction.

## Analytical Takeaway

The uptake sample points toward `conditional trust` rather than blind acceptance.

Why:
- Positive uptake is the dominant pattern overall.
- But critique is concentrated in non-merged and especially early-phase cases.
- This suggests AI invocation is often accepted, but that acceptance is conditional and subject to supervision and revision.

## Writing-Friendly Summary

"A 29-case uptake coding sample suggests that direct AI invocation often leads to positive uptake, but not unconditional trust. While 69.0% of sampled cases were labeled as positive uptake, corrective critique remained substantial (20.7%) and was concentrated in non-merged cases. This pattern is consistent with conditional trust: AI is frequently treated as a usable collaborator, but its contributions remain subject to active monitoring and correction."
