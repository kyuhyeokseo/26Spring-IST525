# Invocation Uptake Notes

This note summarizes the first-pass aftermath analysis for human `Suggestion-Invocation` mentions.

Source files:
- `analysis_ai_refs/invocation_aftermath_dataset.csv`
- `analysis_ai_refs/invocation_aftermath_summary.json`
- `analysis_ai_refs/invocation_uptake_coding_sample.csv`

## Headline Result

The data suggest that AI invocation is usually followed by additional interaction, not left as a dead-end command.

- Total human invocation mentions: 627
- Has a subsequent human comment: 81.98%
- Has a subsequent bot comment: 97.45%
- Overall merged rate of invocation-bearing PR events: 70.33%

Interpretation:
These invocation events are usually embedded in active interaction sequences. They are not typically isolated symbolic gestures.

## Latency After Invocation

- Median time to next any comment: 0.057 hours
- Median time to next bot comment: 0.062 hours
- Median time to next human comment: 0.291 hours

Interpretation:
The thread usually reacts quickly after invocation. Bot responses are slightly faster than human ones, as expected, but human follow-up also tends to happen on the scale of minutes rather than days.

## Pre-Merge Invocation

Some invocations happen after the PR was effectively already resolved, so the key subset is invocation-before-merge.

- Invocation before merge: 438 / 627 (69.86%)
- Median time to merge after invocation, valid pre-merge cases only: 7.392 hours
- Mean time to merge after invocation, valid pre-merge cases only: 45.824 hours

Interpretation:
Many invocations happen before closure, and the typical pre-merge invocation is followed by resolution within hours rather than weeks, although there is a long tail.

## By Role

### Invocation counts by role

- other_commenter: 346
- reviewer: 242
- author: 39

### Aftermath by role

- author:
  - next human rate: 64.1%
  - merged rate: 87.2%
  - median next human latency: 1.157 hours
  - median time to merge after invocation: 2.524 hours

- reviewer:
  - next human rate: 85.5%
  - merged rate: 82.2%
  - median next human latency: 0.291 hours
  - median time to merge after invocation: 8.696 hours

- other_commenter:
  - next human rate: 81.5%
  - merged rate: 60.1%
  - median next human latency: 0.271 hours
  - median time to merge after invocation: 5.143 hours

Interpretation:
- Reviewer and other-commenter invocations are much more conversationally active.
- Author invocations are fewer, somewhat slower to receive a human response, but more often associated with merged cases.
- Other-commenter invocations seem especially interaction-heavy but less merge-convergent.

## By Timing

### Invocation counts by timing

- early: 322
- middle: 131
- late: 174

### Aftermath by timing

- early:
  - next human rate: 93.2%
  - merged rate: 68.0%
  - median next human latency: 0.334 hours
  - median time to merge after invocation: 31.775 hours

- middle:
  - next human rate: 83.2%
  - merged rate: 71.0%
  - median next human latency: 0.229 hours
  - median time to merge after invocation: 2.451 hours

- late:
  - next human rate: 60.3%
  - merged rate: 74.1%
  - median next human latency: 0.307 hours
  - median time to merge after invocation: 0.875 hours

Interpretation:
- Early invocations are the most interaction-heavy.
- Late invocations are less likely to receive more human discussion, but when they happen before merge they tend to be close to closure.
- This fits a plausible sequence model: early invocations open work; late invocations often happen near resolution.

## What This Supports

These numbers do not yet prove uptake on their own, but they do support a strong intermediate claim:

1. Invocation is usually followed by additional interaction.
2. Invocation is often embedded in active conversational sequences rather than isolated mentions.
3. Timing matters: early invocation tends to open longer interaction loops, while late invocation sits closer to closure.

## What Still Needs Human Coding

The next step is to code the *type* of uptake in the next 1-3 human utterances.

Recommended uptake labels:
- positive uptake
- corrective critique
- continued delegation
- no clear uptake

This is why `invocation_uptake_coding_sample.csv` was created.

## Writing-Friendly Summary

"A first-pass aftermath analysis suggests that direct AI invocation is typically followed by further interaction rather than ending as a symbolic command. Across 627 human invocation mentions, 82.0% were followed by at least one subsequent human utterance, and 69.9% occurred before the PR was merged. Among valid pre-merge cases, the median time from invocation to merge was 7.4 hours. These results suggest that AI invocation often enters an active interaction sequence, although further close reading is needed to distinguish positive uptake from corrective or supervisory response."
