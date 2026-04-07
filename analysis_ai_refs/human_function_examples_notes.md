# Human AI Mention Function Notes

This note summarizes example mentions and interpretation for the human-only AI function labeling results.

Source files:
- `analysis_ai_refs/llm_labeling_human_mentions.csv`
- `analysis_ai_refs/llm_labeling_human_mentions_labeled.csv`
- `analysis_ai_refs/llm_labeled_function_summary.json`

## Headline Result

Human-only AI mentions were dominated by `Suggestion` labels.

- Suggestion: 739 / 925 (79.89%)
- Critique: 85 / 925 (9.19%)
- Explanation: 53 / 925 (5.73%)
- Justification: 17 / 925 (1.84%)
- Meta discussion: 5 / 925 (0.54%)

An important qualitative point is that many `Suggestion` cases are not abstract recommendations like "maybe use AI," but direct invocations such as `@copilot` or `@claude`. In other words, participants are often not only talking about AI, but talking to AI.

## Role-Based Examples

### Author Suggestion

Examples:
- `strawgate/kb-yaml-to-lens#467`: "@claude can you address the pr feedback?"
- `BryceWayne/MemoryStore#12`: "@copilot what's up with the error. Fix it"
- `strawgate/kb-yaml-to-lens#467`: "@claude can you fix the merge conflicts for me?"

Interpretation:
Authors often invoked AI as an active collaborator to perform concrete follow-up work. These mentions look less like passive tool references and more like delegated task requests.

### Author Explanation

Examples:
- `JoA-MoS/garage#189`: "Generated with Claude Code"
- `JoA-MoS/garage#190`: "Generated with Claude Code"
- `567-labs/instructor#1976`: "added implementation for Claude models, but still needs further handling..."

Interpretation:
Author-side `Explanation` mentions often describe how AI or a particular model was used, or what part of the implementation was completed with AI-related tooling.

### Author Justification

Examples:
- `freenet/freenet-core#2520`: "Updated CI config ... Retrying CI. [AI-assisted - Claude]"
- `ardallie/plan-and-jam-with-claude-code#2`: "[x] Resolved - Added explicit ..."
- `ardallie/plan-and-jam-with-claude-code#2`: "[x] Resolved - Changed to conditional instruction ..."

Interpretation:
These mentions justify why a change was made, often framing the AI-assisted work as acceptable, resolved, or sufficient for the PR's needs.

### Reviewer Suggestion

Examples:
- `toddwseattle/toddwseattle-astro#5`: "Yes @copilot make consistent and correct"
- `GregorGullwi/FlashCpp#338`: "@copilot continue to look at the segfault"
- `machi0x/Memoiz#12`: "@copilot need Japanese string resource too"

Interpretation:
Reviewers do not only evaluate AI use. In many cases they actively mobilize AI during the review process, treating it as a tool or agent for ongoing revision.

### Reviewer Critique

Examples:
- `Entze/frost#37`: "@copilot This is unnecessary for this instructions file."
- `jchoi2x/hocuspocus#3`: "@copilot remove usage of globalThis. Nothing should be global"
- `mgradwohl/tasksmack#303`: "@copilot Looks like you forgot the clang-tidy and clang-format steps."

Interpretation:
Reviewer-side critique functions as quality control. The reviewer treats AI output as something that can be corrected, constrained, or disciplined within collaborative review norms.

### Other Commenter Suggestion

Examples:
- `aws-amplify-jp/aws-amplify-jp.github.io#73`: "@copilot package-lock.json のコンフリクト、解消して"
- `ranjitp16/ranjitp16.github.io#2`: "@copilot lets make the font a bit techie..."
- `Open-J-Proxy/ojp#196`: "@copilot did you push your latest commit?"

Interpretation:
Non-author, non-reviewer participants also invoke AI directly. This suggests AI is not only the author's private aid, but can become part of the shared collaborative interface in a PR thread.

### Other Commenter Critique

Examples:
- `PriorityLexusVB/AFTERMARKET-MENU#107`: "@copilot STILL FAILING CI BUILD AND TEST"
- `Open-J-Proxy/ojp#196`: "@copilot I see no commit, did you push your latest fixes?"
- `k0swe/arrl-co-yotc#58`: "@copilot Please fix the tests this time instead of reverting the production code changes."

Interpretation:
These critiques often sound like accountability talk. AI is addressed as if it were expected to respond, fix problems, and meet collaboration expectations.

## Analytical Takeaways

1. The dominant social function of human AI mention is `Suggestion`.
2. In this dataset, `Suggestion` frequently means direct agent invocation, not just abstract recommendation.
3. Authors are relatively more likely to use AI mentions for `Explanation` and `Justification`.
4. Reviewers and other commenters are relatively more likely to use AI mentions for `Suggestion` and `Critique`.
5. These patterns support the interpretation that AI is being treated not only as a referenced tool, but often as an interactive collaborative actor in PR discussion.

## Writing-Friendly Summary

A strong way to describe the result is:

"Most human AI mentions served a suggestive function, but many of these were direct invocations such as `@claude can you address the pr feedback?` or `@copilot what's up with the error. Fix it.` This indicates that participants were often not merely discussing AI, but addressing AI as an actionable collaborative agent. By contrast, author-side mentions more often explained or justified AI-assisted work, while reviewer and other-commenter mentions more often evaluated, redirected, or criticized AI-generated output."
