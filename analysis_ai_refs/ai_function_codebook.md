# AI Function Coding Codebook

Primary labels:
- Justification
- Explanation
- Suggestion
- Critique
- Meta discussion
- Other

Definitions:
- Justification: Uses AI mention to defend, justify, or legitimize a code or design choice.
- Explanation: Uses AI mention to disclose provenance, explain where content came from, or document process.
- Suggestion: Recommends using an AI tool or addresses an AI agent with a task/request.
- Critique: Challenges the quality, correctness, or appropriateness of AI-generated output.
- Meta discussion: Talks about policy, norms, trust, or philosophy of AI use in the team/project.
- Other: AI mention is present but does not clearly fit the above labels.

Recommended coding rules:
- Code the function of the mention in context, not just the keyword itself.
- If multiple functions appear, put the dominant one in `manual_function_label` and the second in `manual_secondary_label`.
- Use `manual_notes` for ambiguity, sarcasm, or cases where bot-generated content complicates interpretation.