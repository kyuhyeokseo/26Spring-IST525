# Author Accountability Modes: Coded Distribution

Second-pass coding of the 46 author-authored discursive AI mentions. Codebook: `author_accountability_codebook.md`. Labels assigned by close reading of each body against the 6-category scheme; a 15-case stratified subsample is reserved for inter-coder reliability in `author_accountability_phase_b_template.csv`.

## Distribution (n=46)

- `provenance_only`: 16 (34.78%)
- `process_documentation`: 9 (19.57%)
- `defensive_justification`: 1 (2.17%)
- `credit_partition`: 0 (0.0%)
- `fault_to_ai`: 1 (2.17%)
- `other`: 19 (41.3%)

## Distribution excluding `other` (n=27 genuine AI-accountability cases)

- `provenance_only`: 16 (59.26%)
- `process_documentation`: 9 (33.33%)
- `defensive_justification`: 1 (3.7%)
- `credit_partition`: 0 (0.0%)
- `fault_to_ai`: 1 (3.7%)

## Representative quotes by category

### `provenance_only` examples

- **AWeber-Imbi/imbi-api#148** (`gmr`)
  > 🤖 *This comment was posted by Claude on behalf of @gmr*  ## PR Monitor Summary - Monitoring iteration #1 of 10  ### CI/CD Status ✅ All checks passing: - OSSAR-Scan: success - test (3.12, 3.13, 3.14): all success - CodeRabbit: success  ### Code Review Feedback Addressed  #### ✅ Docstring References (Already Fixed in 6aeb818) The incorrect references to `aj.errors.DatabaseError` were already correct
- **AWeber-Imbi/imbi-api#148** (`gmr`)
  > 🤖 *This comment was posted by Claude on behalf of @gmr*  ## PR Monitor Update - Monitoring iteration #2 of 10  ### CI/CD Status Update ✅ **All CI checks passing after latest commit (7c952ea):** - OSSAR-Scan: success - test (3.12): success ✅ - test (3.13): success ✅ - test (3.14): success ✅ - bandit: success - binskim: success - eslint: success  ### Review Status ✅ All review threads resolved ✅ No 
- **AndyMik90/Auto-Claude#417** (`sumca1`)
  > לא זה נוצר על ידי copilot אבל רק עבור יהודים

### `process_documentation` examples

- **Scetrov/evefrontier-rs#51** (`Scetrov`)
  > ## Review Comments Addressed  All 5 Copilot review comments have been addressed in commit e913659:  ### 1. Spec Documentation (spec.md) ✅ **Addressed**: Updated feature spec to document fuel color styling (orange for hop cost, magenta for remaining) and padding fixes as core feature requirements (FR-3, FR-4) and acceptance criteria.  ### 2. Dead Code in output.rs (calculate_route_fuel) ✅ **Address
- **ardallie/plan-and-jam-with-claude-code#2** (`ardallie`)
  > ## Review response  All review comments have been addressed.  ---  ### Medium severity  **[x] Missing subagent type specification** (.claude/commands/plan-create.md:13) - **Modified:** `.claude/commands/plan-create.md` - **Change:** Added explicit `subagent_type: "plan-create"` parameter to the Task tool invocation instruction  **[x] Redundant issue fetch in plan-validate** (.claude/commands/plan-
- **frankbria/narrative-modeling-app#131** (`frankbria`)
  > ## Update: Package Lock and Workflow Files  Added commit `6ff59be` with the following changes:  ### Package Management - **Updated `package-lock.json`** after running `npm install`   - Ensures dependency versions are locked for the new `@types/jest` package   - Resolves any transitive dependency updates  ### Workflow Files (.claude-flow/) Added 38 workflow orchestration files: - Agent specificatio

### `defensive_justification` examples

- **joshsmithxrm/ppds-tools#10** (`joshsmithxrm`)
  > ## Addressing Review Feedback  Thanks for the thorough reviews! I've addressed the feedback in commit 1e23be9:  ### Fixed Issues  1. **README path mismatch** (Gemini) ✅    - Added explicit `-OutputPath "./registrations.json"` to make the example clearer  2. **CHANGELOG version terminology** (Gemini) ✅      - Changed "v2.x Pattern" → "v1.2.x Pattern" for consistency with version 1.2.0  3. **Redunda

### `fault_to_ai` examples

- **jkoelker/oneiro#62** (`jkoelker`)
  > @dobbyphus review this again, also check out the resolved comments from copilot to see if they were really resolved. ignore the one it said about AGENTS.md

## Interpretation

Of the 46 author-authored discursive AI mentions, 19 (41.3%) were `other` — primarily false positives where an AI keyword appears in a filename, product description, or repo name without doing accountability work. Restricting to the 27 genuine AI-accountability cases:

- `provenance_only` dominates at 59.26% — authors overwhelmingly use bare disclosure markers ('🤖 Generated with Claude Code', '[AI-assisted - Claude]', 'Co-Authored-By: Claude') with no accompanying defense or partition.
- `process_documentation` is the second most common mode (33.33%) — authors describe how they processed AI-generated review feedback or AI-assisted tooling, typically as structured 'addressed' lists.
- `defensive_justification` (3.7%) and `fault_to_ai` (3.7%) are rare. `credit_partition` does not appear at all in this sample.

This is a stronger and more conservative finding than the initial 'author attribution regime' hypothesis. Authors are *not* performing elaborate accountability theater. They are doing **minimal, routinized disclosure** — a provenance tag at the end of a comment, or a 'here is how I processed AI review' checklist. Credit partition and fault attribution to AI, which would require more agonistic framing, are essentially absent. This aligns with the Tier-3 finding that explicit normative challenge is rare: AI participation is being absorbed through lightweight, template-like conventions rather than contested in prose.

For the paper, this supports the revised framing: the discursive subset is the layer where AI is made visible, but the mode of visibility is **disclosure-and-proceed**, not active accountability negotiation. Two results sections follow naturally from this: a quantitative distribution, and a short qualitative note on the near-absence of credit partition and defensive argumentation (which is itself a CSCW finding about how OSS communities handle AI).
