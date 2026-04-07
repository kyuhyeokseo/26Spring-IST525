# LLM Labeling Prompt (bot)

Task:
Classify the social function of an AI-reference mention in a GitHub PR discussion.
Focus on bot-like or tool-generated collaboration language.

Available labels:
- Justification: Uses AI mention to defend, justify, or legitimize a code/design choice.
- Explanation: Uses AI mention to disclose provenance, explain where content came from, or document process.
- Suggestion: Recommends using an AI tool or directly asks an AI tool/agent to do something.
- Critique: Challenges the quality, correctness, or appropriateness of AI-generated output.
- Meta discussion: Talks about policy, norms, trust, or philosophy of AI use.
- Other: AI mention is present but the main function does not fit the labels above.

Instructions:
- Choose exactly one `primary_label`.
- Optionally choose one `secondary_label` if a second function is clearly present.
- Return `contains_multiple_functions=true` only when two functions are meaningfully present.
- Base the label on the function of the mention in context, not just the keyword itself.
- If uncertain, prefer `Other` over overclaiming.

Return JSON only with this shape:
{"mention_uid":"...", "primary_label":"...", "secondary_label":"...", "confidence":"high", "contains_multiple_functions":"false", "rationale":"..."}