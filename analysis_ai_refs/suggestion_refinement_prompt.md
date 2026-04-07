# Suggestion Refinement Prompt

Task:
You are doing a second-pass refinement for GitHub PR mentions that were already labeled as Suggestion.
Refine each mention along two dimensions:
1. suggestion_subtype
2. addressing_mode

Suggestion subtype labels:
- Suggestion-Invocation: directly invokes an AI agent/tool with an address like @copilot, @claude, or a short imperative call.
- Suggestion-Recommendation: recommends using AI, or suggests AI as an option, without directly tasking it.
- Suggestion-TaskDelegation: assigns a concrete piece of work to AI, often larger than a single edit, such as fixing tests, implementing a feature, or addressing PR feedback.
- Suggestion-StepInstruction: directs AI through phased or sequential steps, e.g. implement phase 1, continue to next step, do X then Y.

Addressing mode labels:
- Talking-to-AI: the text is addressed to the AI system/agent as an interaction partner.
- Talking-about-AI: the text discusses AI or AI usage without addressing it directly.
- Mixed: both are meaningfully present.

Notes:
- A mention can be both Invocation and TaskDelegation in spirit, but choose the single best suggestion_subtype.
- If the utterance is directly addressed to AI, prefer Talking-to-AI.
- Very short agent calls like '@copilot' or '@claude review' are usually Suggestion-Invocation and Talking-to-AI.
- If the mention says content was generated with AI, that is usually Talking-about-AI rather than Talking-to-AI.

Return JSON only with this shape:
{"mention_uid":"...", "suggestion_subtype":"...", "addressing_mode":"...", "confidence":"high", "rationale":"..."}