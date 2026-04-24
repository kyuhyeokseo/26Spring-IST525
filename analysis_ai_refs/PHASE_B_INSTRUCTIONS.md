# Phase B — 14-Case Spot Check Instructions

You are the second coder. Your job is to independently assign an
accountability label to 14 author-authored discursive AI mentions,
using the codebook in `author_accountability_codebook.md`. After you
finish, we compute Cohen's kappa between your labels and the primary
LLM-assisted labels.

Estimated time: 60-90 minutes.

## Setup

Open the file:
```
analysis_ai_refs/author_accountability_phase_b_template.csv
```

Each row has:
- `mention_body` — the full comment text to code
- `accountability_label` — the primary coder's label (the one you are
  validating)
- `accountability_rationale` — one-line rationale from the primary coder
- `coder2_label` — empty; you fill this
- `coder2_notes` — empty; optional

## Procedure

For each row:
1. Read `mention_body` **without** looking at `accountability_label`
   first. Block that column mentally.
2. Apply the codebook (`author_accountability_codebook.md`). Pick
   exactly one of: `provenance_only`, `defensive_justification`,
   `credit_partition`, `fault_to_ai`, `process_documentation`, `other`.
3. Fill `coder2_label` with your pick.
4. *Only then* compare to `accountability_label`. If you disagree,
   leave your label as-is. Optionally note the reason in `coder2_notes`.
5. Move to the next row.

Do not edit `accountability_label` or `accountability_rationale` — those
are the primary coder's labels, frozen for the reliability check.

## Decision heuristics (quick reference)

- **provenance_only**: the mention is a bare disclosure tag
  (`🤖 Generated with Claude Code`, `[AI-assisted - Claude]`,
  `Co-Authored-By: Claude`) without defense, partition, or procedural
  detail.

- **process_documentation**: the mention describes *how* the author
  processed AI-produced work (itemized fix lists, structured "addressed"
  responses, descriptions of AI-tooling workflow files). The focus is
  procedural.

- **defensive_justification**: the author acknowledges AI use AND frames
  their own verification/review/retention of responsibility, OR defends
  a specific decision against AI reviewer critique ("intentionally not
  changed").

- **credit_partition**: the author neutrally splits "this part came from
  AI / this part is mine." No defense, just allocation.

- **fault_to_ai**: the author attributes a bug, missing case, or
  incorrect suggestion to AI ("Copilot got this wrong", "ignore what
  Copilot said about X").

- **other**: AI keyword appears but no accountability work. Common
  subcases: AI is the *product* being built (the repo implements AI
  support); AI keyword is in a filename or URL only; the body is mostly
  quoted AI review text.

## Run the kappa calculation

After you have filled at least 10 rows:
```
source .venv/bin/activate
python compute_author_accountability_kappa.py
```

Outputs:
- `analysis_ai_refs/author_accountability_kappa.md`
- `analysis_ai_refs/author_accountability_kappa.json`

## What to report in the paper

One sentence, paste-ready:
> "A stratified 14-case subsample of the author-accountability coding
> was independently relabeled by the first author; Cohen's kappa
> between the primary LLM-assisted labels and the second coder was
> X.XX (raw agreement Y.YY), indicating Z agreement under Landis & Koch
> (1977)."

If kappa comes back low (<0.40), the codebook may need a revision pass;
see the confusion matrix in `author_accountability_kappa.md` to
identify which categories are being systematically confused.
