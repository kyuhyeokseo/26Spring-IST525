# Agent-Commanding vs Discursive Reference

This split partitions human-authored AI mentions by whether the body contains an @-mention of an AI bot account (`agent_commanding`) or only references AI in prose (`discursive`). The original headline finding of `Talking-to-AI` 99% is re-evaluated against this split to test whether it reflects discursive participation of AI or workflow-level bot orchestration.

## All human-authored AI mentions (n=925)

- Total: 925
- Agent-commanding: 819 (88.54%)
- Discursive: 106 (11.46%)

### agent_commanding (n=819)

Function (LLM primary label):
- Suggestion: 89.87% (736)
- Critique: 8.91% (73)
- Justification: 0.61% (5)
- Meta discussion: 0.24% (2)
- Explanation: 0.24% (2)
- Other: 0.12% (1)

Speaker role:
- other_commenter: 58.73% (481)
- reviewer: 34.55% (283)
- author: 6.72% (55)

Timing phase:
- early: 51.89% (425)
- late: 27.84% (228)
- middle: 20.27% (166)

Location:
- issue_comment: 89.99% (737)
- review_comment: 8.18% (67)
- review: 1.83% (15)

### discursive (n=106)

Function (LLM primary label):
- Explanation: 48.11% (51)
- Other: 22.64% (24)
- Justification: 11.32% (12)
- Critique: 11.32% (12)
- Meta discussion: 2.83% (3)
- Suggestion: 2.83% (3)
- Explaination: 0.94% (1)

Speaker role:
- other_commenter: 49.06% (52)
- author: 43.4% (46)
- reviewer: 7.55% (8)

Timing phase:
- late: 48.11% (51)
- early: 44.34% (47)
- middle: 7.55% (8)

Location:
- issue_comment: 86.79% (92)
- review_comment: 9.43% (10)
- review: 3.77% (4)

## Suggestion subset (n=739)

- Total: 739
- Agent-commanding: 736 (99.59%)
- Discursive: 3 (0.41%)

### agent_commanding (n=736)

Suggestion subtype:
- Suggestion-Invocation: 84.92% (625)
- Suggestion-TaskDelegation: 9.38% (69)
- Suggestion-StepInstruction: 4.76% (35)
- Suggestion-Recommendation: 0.95% (7)

Addressing mode:
- Talking-to-AI: 99.18% (730)
- Talking-about-AI: 0.68% (5)
- Mixed: 0.14% (1)

Speaker role:
- other_commenter: 56.93% (419)
- reviewer: 36.55% (269)
- author: 6.52% (48)

Timing phase:
- early: 51.63% (380)
- late: 27.31% (201)
- middle: 21.06% (155)

Location:
- issue_comment: 89.95% (662)
- review_comment: 8.15% (60)
- review: 1.9% (14)

### discursive (n=3)

Suggestion subtype:
- Suggestion-Invocation: 66.67% (2)
- Suggestion-TaskDelegation: 33.33% (1)

Addressing mode:
- Talking-to-AI: 66.67% (2)
- Talking-about-AI: 33.33% (1)

Speaker role:
- author: 33.33% (1)
- reviewer: 33.33% (1)
- other_commenter: 33.33% (1)

Timing phase:
- early: 66.67% (2)
- late: 33.33% (1)

Location:
- issue_comment: 66.67% (2)
- review: 33.33% (1)

## Interpretation hooks

- Across all 925 human-authored AI mentions, 88.54% are agent-commanding (@-mention an AI bot account) and only 11.46% are purely discursive references.
- Within the Suggestion subset (n=739), the agent-commanding share climbs to 99.59%, with only 3 purely discursive cases.
- The original 99% `Talking-to-AI` finding therefore reflects, almost entirely, workflow-level orchestration of AI bot agents (primarily Copilot) via @-mention, rather than discursive participation of AI in the open prose of code review.
- The discursive subset is small but qualitatively distinct: it captures the cases where developers reference AI tools in prose (e.g., `I asked ChatGPT...`, `Copilot suggested earlier`). It is this subset that maps onto the existing CHI/CSCW literature on AI-as-referenced-tool, while the agent-commanding subset maps onto the emerging governance question of bot-mediated workflow.
