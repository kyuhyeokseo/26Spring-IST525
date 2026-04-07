# Suggestion Refinement Notes

This note summarizes the second-pass refinement of human `Suggestion` mentions.

Source files:
- `analysis_ai_refs/suggestion_refinement_human_mentions.csv`
- `analysis_ai_refs/suggestion_refinement_human_mentions_labeled.csv`
- `analysis_ai_refs/suggestion_refinement_summary.json`

## Headline Result

The original `Suggestion` category was not merely large. It was overwhelmingly dominated by direct invocation.

- Total refined suggestion mentions: 739
- Suggestion-Invocation: 627 (84.84%)
- Suggestion-TaskDelegation: 70 (9.47%)
- Suggestion-StepInstruction: 35 (4.74%)
- Suggestion-Recommendation: 7 (0.95%)

This means the dominant form of `Suggestion` was not abstract recommendation, but direct calling or prompting of AI agents.

## Talking About AI vs Talking To AI

The results are even more striking on the addressing dimension.

- Talking-to-AI: 732 (99.05%)
- Talking-about-AI: 6 (0.81%)
- Mixed: 1 (0.14%)

This strongly supports the claim that these PR comments are usually not just references to AI. They are interactions with AI.

## By Role

### Subtype by role

- author:
  - Invocation: 39
  - TaskDelegation: 7
  - StepInstruction: 2
  - Recommendation: 1

- reviewer:
  - Invocation: 242
  - TaskDelegation: 18
  - StepInstruction: 10
  - Recommendation: 0

- other_commenter:
  - Invocation: 346
  - TaskDelegation: 45
  - StepInstruction: 23
  - Recommendation: 6

Interpretation:
- All three roles are dominated by `Invocation`.
- Other commenters contribute the largest number of delegated and stepwise instructions.
- Reviewers also invoke AI heavily, which is notable because this means reviewers are often directing AI rather than merely evaluating AI-generated work.

### Addressing mode by role

- author: 49 / 49 are `Talking-to-AI`
- reviewer: 270 / 270 are `Talking-to-AI`
- other_commenter: 413 / 420 are `Talking-to-AI`, 6 `Talking-about-AI`, 1 `Mixed`

Interpretation:
The talking-to-AI pattern is not confined to authors. It appears across roles.

## By Timing

### Suggestion subtype by timing

- early:
  - Invocation: 322
  - TaskDelegation: 38
  - StepInstruction: 18
  - Recommendation: 4

- middle:
  - Invocation: 131
  - TaskDelegation: 16
  - StepInstruction: 6
  - Recommendation: 2

- late:
  - Invocation: 174
  - TaskDelegation: 16
  - StepInstruction: 11
  - Recommendation: 1

Interpretation:
Direct invocation is dominant across all phases, especially early. This supports the idea that PR discussion often begins by actively calling AI into the workflow.

### Addressing mode by timing

- early: 380 `Talking-to-AI`, 2 `Talking-about-AI`
- middle: 153 `Talking-to-AI`, 2 `Talking-about-AI`
- late: 199 `Talking-to-AI`, 2 `Talking-about-AI`, 1 `Mixed`

Interpretation:
The interactional pattern remains stable across the PR lifecycle.

## By Location

### Suggestion subtype by location

- issue_comment:
  - Invocation: 556
  - TaskDelegation: 66
  - StepInstruction: 35
  - Recommendation: 7

- review_comment:
  - Invocation: 56
  - TaskDelegation: 4

- review:
  - Invocation: 15

Interpretation:
The interactional use of AI is centered in general PR discussion, not formal review artifacts.

## Analytical Takeaway

The refined results support a much stronger claim than the original first-pass labeling:

1. The dominant function of AI mention is not generic suggestion, but direct invocation.
2. The dominant interactional mode is not talking about AI, but talking to AI.
3. This pattern holds across role, timing, and location.

## Writing-Friendly Summary

"A second-pass refinement of the `Suggestion` category showed that it was overwhelmingly composed of direct invocation rather than abstract recommendation. Of 739 suggestion mentions, 84.8% were labeled `Suggestion-Invocation`, while only 0.95% were labeled `Suggestion-Recommendation`. Even more strikingly, 99.1% of these suggestion mentions were classified as `Talking-to-AI` rather than `Talking-about-AI`. This indicates that AI in PR discussion was typically not merely referenced as a tool, but directly addressed as an interactive collaborator."
