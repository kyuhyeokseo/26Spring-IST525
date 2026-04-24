# Normative Challenges to AI Use in PR Discussions

This pass searches the AI-reference comment and review corpus for utterances that *regulate* AI use as a practice rather than merely respond to a single AI output. The goal is to surface community norm formation around AI participation: bans, attribution demands, trust markers, low-effort attributions, and verification requirements.

## Total hits: 108
- Distinct PRs with hits: 50
- Hits authored by bot accounts: 87
- Hits authored by humans: 21

## Hits by pattern

- `policy_or_guideline`: 33
- `ai_disclosure_required`: 24
- `verify_before_merge`: 19
- `vibe_coding`: 10
- `human_review_framing`: 10
- `explicit_ban`: 9
- `low_effort`: 2
- `ai_inverse_human`: 1

## Examples per pattern (human-authored only)

### `ai_disclosure_required` (3 shown)

- **fritz-net/AoE2-Civbuilder#189** by `Copilot` (comment, 2025-12-28T19:15:26Z) matched `label contrast with darker color (#333)


> @copilot`
  >  > - minimal version does not use attack,... icons; also text like "Or enter custom ID:" is still there  > - the text for switching between condenst version has bad contrast  > - range and attack speed or re...  Fixed all compact mode issues (f546c64): - Added icons to all stat l
- **thedotmack/claude-mem#509** by `james5294` (comment, 2025-12-31T22:42:38Z) matched `label is a limitation in Claude Code's hooks API, not a bug in claude`
  > Closing this PR after discussion with the maintainer.  The current behavior (exit code 3 + stderr) is **intentional** - it's a workaround to display messages to users without adding them to Claude's context. This is a valuable feature for showing localhost UI links, update notice
- **rjmurillo/ai-agents#715** by `rjmurillo` (comment, 2025-12-31T21:06:05Z) matched `label](https://github.com/rjmurillo/ai`
  > <!-- TRIAGE-REQUIRED --> ## Review Triage Required  > [!NOTE] > **Priority: NORMAL** - Human approval required before bot responds  ### Review Summary  | Source | Reviews | Comments | |--------|---------|----------| | **Human** | 0 | 0 | | Bot | 1 | 3 |    ### Next Steps  1. Revi

### `verify_before_merge` (5 shown)

- **arcade-cabinet/protocol-silent-night#70** by `jbdevprimary` (comment, 2025-12-31T19:41:05Z) matched `verify
```bash
pnpm typecheck
```

---
<sub>🤖 Generated`
  > ## 🔧 CI Fix Suggestion  **Branch:** sentinel-seeded-random-security-12463160577482274073  ### 1. Root cause The TypeScript build failed because `src/__tests__/unit/SeededRandom.test.ts` contains an unused `@ts-expect-error` directive and a declared but unused variable `_rng`.  ##
- **arcade-cabinet/protocol-silent-night#70** by `jbdevprimary` (comment, 2026-01-02T14:53:19Z) matched `verify
```bash
pnpm typecheck
```

---
<sub>🤖 Generated`
  > ## 🔧 CI Fix Suggestion  **Branch:** sentinel-seeded-random-security-12463160577482274073  ### Root cause The type check failed due to two issues: incorrect mocking of a Zustand store in test files (type incompatibility between `UseBoundStore` and Jest's `Mock` type) and a missing
- **arcade-cabinet/protocol-silent-night#69** by `jbdevprimary` (comment, 2026-01-01T21:11:09Z) matched `Verify AI`
  > ## 🤖 AI Code Review  ### Summary of Changes - Migrated from Node.js to Python runtime for all GitHub Actions - Replaced `agentic-control` npm package with `vendor-connectors` Python package - Added support for Cursor AI agent as an alternative to Google Jules - Simplified CI reso
- **arcade-cabinet/protocol-silent-night#69** by `jbdevprimary` (comment, 2026-01-03T18:14:47Z) matched `verify AI`
  > ## 🤖 AI Code Review  ## Summary of Changes - Migrated from Node.js to Python for all agentic actions - Replaced direct API calls with `vendor-connectors` CLI tool - Added support for Cursor AI agent alongside Google Jules - Simplified CI resolution workflow to fetch failure logs 
- **fzymgc-house/router-hosts#195** by `seanb4t` (comment, 2025-12-31T22:00:31Z) matched `re-review.

---
🤖 Co-Authored-By: Claude`
  > ## 🤖 Review Comments Processed  I've addressed the following feedback:  ### Required Changes (1 addressed) - ✅ Updated `cog.toml` comment to reference release-please instead of release-plz - 2f53eec  ### Optional Suggestions (skipped per standard practice) - ⏭️ workflow_dispatch 

### `vibe_coding` (8 shown)

- **algesten/str0m#810** by `algesten` (comment, 2026-01-01T09:26:41Z) matched `vibe code`
  > @xnorpx exciting stuff!    I think the SPED part is something I'd prefer to hand roll (as opposed to vibe code), since it is important to maintain a clear idea of separation-of-concerns throughout the code base at the same time as you're mashing the layers together.    It might r
- **algesten/str0m#810** by `xnorpx` (comment, 2026-01-01T12:59:16Z) matched `vibe code`
  > > @xnorpx exciting stuff!  >   > I think the SPED part is something I'd prefer to hand roll (as opposed to vibe code), since it is important to maintain a clear idea of separation-of-concerns throughout the code base at the same time as you're mashing the layers together.  >   > 
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T20:55:48Z) matched `vibe coding`
  > - `Hive Mind runs in full autonomous mode.` With no permission limitations, sudo access to virtual machine, that means AI can have as much creative freedom as real programmer.  - `Runs on dedicated VMs` or locally in isolated docker container, means any unintended damage (which c
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T20:55:48Z) matched `vibe coding`
  > - `Hive Mind runs in full autonomous mode.` With no permission limitations, sudo access to virtual machine, that means AI can have as much creative freedom as real programmer.  - `Runs on dedicated VMs` or locally in isolated docker container, means any unintended damage (which c
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T20:55:48Z) matched `vibe coding`
  > - `Hive Mind runs in full autonomous mode.` With no permission limitations, sudo access to virtual machine, that means AI can have as much creative freedom as real programmer.  - `Runs on dedicated VMs` or locally in isolated docker container, means any unintended damage (which c
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T20:55:48Z) matched `vibe coding`
  > - `Hive Mind runs in full autonomous mode.` With no permission limitations, sudo access to virtual machine, that means AI can have as much creative freedom as real programmer.  - `Runs on dedicated VMs` or locally in isolated docker container, means any unintended damage (which c
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T21:05:07Z) matched `vibe coding`
  > ## 🤖 Solution Draft Log This log file contains the complete execution trace of the AI solution draft process.  ### Changes Made  Based on the feedback in the PR comments, I've made the following updates:  1. **Created `docs/COMPARISON.md`** - A comprehensive comparison document t
- **link-assistant/hive-mind#1050** by `konard` (comment, 2025-12-31T23:11:28Z) matched `Vibe Coding`
  > - `Good for defined problems`, our agent also has high level of creativity if requirements are not defined, I think it is indistinguishable from most (average) programmers. But of course the more detailed the problem definition the better the result. By I think it is the same wit

### `explicit_ban` (3 shown)

- **arcade-cabinet/protocol-silent-night#69** by `jbdevprimary` (comment, 2026-01-02T14:02:34Z) matched `No AI`
  > ## 🤖 AI Code Review  ### Summary of Changes The diff refactors GitHub Actions from Node.js to Python, replacing custom npm-based tooling with a unified `vendor-connectors` CLI. It removes agent instruction files and metaprompts, simplifying the AI curation workflow to use control
- **arcade-cabinet/protocol-silent-night#69** by `jbdevprimary` (comment, 2026-01-04T00:38:48Z) matched `No AI`
  > ## 🤖 AI Code Review  ## Summary Migrates from Node.js to Python runtime, replaces direct API calls with vendor-connectors CLI, and adds Cursor AI support alongside Jules. Removes agent instruction files and simplifies AI curator workflow.  ## Issues Found  🔴 **Critical**:  - No a
- **DamienLove/pulselink#311** by `DamienLove` (comment, 2025-12-31T22:59:30Z) matched `No CLAUDE`
  > @jules.google.com  🔴 Critical Issues  1. Missing Foreground Service Type Declaration (Android 14+ Compatibility)  Severity: HIGH    The CrashDetectionService uses accelerometer data for crash detection, which may require location permissions when deployed as a foreground service 

## Interpretation hooks

- The patterns matched here capture *first-order* normative talk: explicit bans, attribution demands, trust markers, low-effort attributions, and verification requirements. These are the kinds of utterances that signal a community is actively negotiating how AI fits into its work, rather than treating AI use as an individual decision.
- For CSCW framing, the relevant question is not the absolute count of hits but whether the hits cluster: a single repository rolling out an `attribute AI use` rule is qualitatively more important than the same number of hits scattered across 50 repositories. Look at the per-PR and per-repo distribution.
- For the writeup, even 5-10 well-chosen examples of these utterances would substantially enrich the descriptive section: they show what the data looks like beyond the invocation/uptake frame.
