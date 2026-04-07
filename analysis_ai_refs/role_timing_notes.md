# Role x Timing Notes

This note summarizes how human AI mentions vary by speaker role and timing phase.

Source files:
- `analysis_ai_refs/llm_labeling_human_mentions.csv`
- `analysis_ai_refs/llm_labeling_human_mentions_labeled.csv`

## Overall Counts

Role x timing counts:

- author: early 41, middle 17, late 43
- reviewer: early 162, middle 73, late 56
- other_commenter: early 269, middle 84, late 180

## Within-Role Percentages

These percentages answer: "Given a role, when do they tend to mention AI?"

- author:
  - early: 40.59%
  - middle: 16.83%
  - late: 42.57%
- reviewer:
  - early: 55.67%
  - middle: 25.09%
  - late: 19.24%
- other_commenter:
  - early: 50.47%
  - middle: 15.76%
  - late: 33.77%

Interpretation:
- Reviewers are clearly early-heavy.
- Other commenters are also early-heavy, though less extremely than reviewers.
- Authors are split between early and late, with very little middle-phase activity.

This means AI mention behaves differently by role:
- reviewers often engage early to direct or shape work,
- other commenters also push early coordination,
- authors return later to explain or close out work.

## Within-Timing Percentages

These percentages answer: "Given a timing phase, who is doing the talking?"

- early:
  - author: 8.69%
  - reviewer: 34.32%
  - other_commenter: 56.99%
- middle:
  - author: 9.77%
  - reviewer: 41.95%
  - other_commenter: 48.28%
- late:
  - author: 15.41%
  - reviewer: 20.07%
  - other_commenter: 64.52%

Interpretation:
- Early mentions are dominated by other commenters and reviewers.
- Authors are a small share of early-stage AI mention.
- By the late phase, authors become more visible, though other commenters still dominate overall.

## Functional Differences Inside Role x Timing

### Authors

Late author mentions lean more toward `Explanation` and `Justification` than early reviewer or early other-commenter mentions.

Examples:
- `ardallie/plan-and-jam-with-claude-code#2`: "[x] Resolved - Added note documenting ..."
- `JoA-MoS/garage#189`: "Generated with Claude Code"
- `freenet/freenet-core#2520`: "Updated CI config ... [AI-assisted - Claude]"

Interpretation:
Authors often come back later to explain what was done, document AI assistance, or justify why a change should now be acceptable.

### Reviewers

Reviewer mentions are overwhelmingly `Suggestion` in every phase, especially early.

Examples:
- `pradeepmouli/x-to-zod#36`: "@copilot Continue with phase 7"
- `mgradwohl/tasksmack#303`: "@copilot let's do the next steps"
- `dotnet/runtime#122791`: "@copilot Delete extra blank lines"

Interpretation:
Reviewers frequently treat AI as an active reviser during review, not just an object of evaluation.

### Other Commenters

Other commenters are strongly early-stage and also heavily `Suggestion`-oriented.

Examples:
- `Jayc82/Orion#1`: "@copilot What's our next steps"
- `Jayc82/Orion#1`: "@copilot What else needs done?"
- `daisytuner/sdfglib#423`: "@copilot Debug the test failures"

Interpretation:
Other commenters often use AI mention to push work forward, assign next steps, or request debugging.

## Analytical Takeaways

1. Role and timing are clearly linked.
2. Reviewer AI mention is especially early-stage.
3. Author AI mention is split between early tasking and late explanation/justification.
4. Other commenters dominate early AI mention and appear central to coordination-through-invocation.

## Writing-Friendly Summary

"Role and timing interacted in systematic ways. Reviewer AI mentions were especially early-stage, with 55.7% of reviewer mentions appearing in the early phase. Other commenters were also early-heavy (50.5%), while author mentions were split between early (40.6%) and late (42.6%) phases. Qualitatively, reviewer and other-commenter early mentions were often directive invocations such as `@copilot Continue with phase 7`, whereas late author mentions more often explained or justified completed AI-assisted changes."
