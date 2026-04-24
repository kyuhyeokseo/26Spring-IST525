# Integration Notes for Paper Revision

This document maps the new analyses produced during the post-Week-14
revision pass to specific paper sections, with paste-ready
descriptive language and the precise numbers to cite.

## Source files

| Analysis                       | Script                                    | Output                                                              |
|--------------------------------|-------------------------------------------|---------------------------------------------------------------------|
| Agent vs Discursive split      | `analyze_agent_vs_discursive.py`          | `agent_vs_discursive_summary.{md,json}`                             |
| Uptake temporal hygiene        | `analyze_uptake_temporal.py`              | `uptake_temporal_summary.{md,json}`                                 |
| Cohen's kappa (function+uptake)| `build_kappa_sample.py`, `compute_kappa.py`| `kappa_function_sample.csv`, `kappa_uptake_sample.csv`, `kappa_summary.{md,json}` |
| Cluster sensitivity            | `analyze_cluster_sensitivity.py`          | `cluster_sensitivity_summary.{md,json}`                             |
| Control caveats                | (writeup only)                            | `control_comparison_caveats.md`                                     |
| Normative episodes             | `analyze_norm_violations.py`              | `norm_violations_hits.csv`, `norm_violations_summary.md`, `norm_violations_qualitative_notes.md` |

## What changed in the headline numbers

| Headline                                      | Original | Revised                                          |
|-----------------------------------------------|----------|--------------------------------------------------|
| "Talking-to-AI" share among suggestions        | 99.05%   | Re-framed: 99.59% are agent-commanding (`@bot`)  |
| Suggestion-Invocation share among suggestions  | 84.84%   | Same, but the phenomenon is bot orchestration    |
| Uptake x Merge chi-square (full sample)        | chi2=11.46, p=0.006 | View 0 only; reproduces                |
| Uptake x Merge chi-square (temporal-clean)     | n/a      | chi2=6.31, p=0.044 (drop 15 post-merge responses) |
| Uptake x Merge chi-square (temporal+gap)       | n/a      | chi2=5.76, p=0.056 (also drop <1h merges)        |
| Uptake x Merge chi-square (one-per-PR resamples)| n/a     | p<0.05 in 72.0% of 1,000 draws (cluster-robust)  |
| Inter-coder reliability (function labels)      | none     | kappa=0.50 on n=56 stratified                    |
| Inter-coder reliability (uptake labels)        | none     | kappa=0.48 on n=25 stratified                    |
| Discursive (non-bot) AI mentions               | none     | 11.46% of 925 mentions; 0.41% of suggestions     |
| Normative-challenge episodes                   | none     | 21 human-authored hits, 1 strong vignette        |

## Section-by-section paste-ready language

### Methodology -> Add: Inter-Coder Reliability subsection

> "To assess the reliability of the LLM-assisted labels, a
> stratified sample of 56 mentions (10 per function category, with
> small-class adjustments) was independently re-coded by a second
> coder using the same codebook. Cohen's kappa between the LLM and
> the second coder was 0.50, which falls in the 'moderate' range
> (Landis & Koch, 1977). The most consistent disagreements were on
> mentions where the keyword 'LLM' appeared in CI URLs (false
> positives that the LLM tended to label as `Critique`) and on long
> author-authored fix reports, where the LLM oscillated between
> `Justification` and `Explanation`. A second stratified sample of
> 25 invocation cases was re-coded for uptake type (Cohen's
> kappa = 0.48). The dominant systematic disagreement was that the
> LLM over-labeled `positive_uptake` in cases that had no captured
> human follow-up, which a second coder would mark as
> `no_clear_uptake`. This implies that the headline `positive_uptake`
> share is likely a slight over-estimate, and the qualitative
> conclusion remains 'engagement is mixed, not unconditional.'"

### Methodology -> Add: Agent-Commanding vs Discursive Split

> "We further partitioned mentions by whether the comment body
> directly @-mentions an AI bot account (e.g., `@copilot`,
> `@claude`, `@cursor[bot]`). Of 925 human-authored AI mentions,
> 88.5% were agent-commanding and 11.5% were purely discursive
> references. Within the Suggestion subset (n=739), 99.6% were
> agent-commanding. The 99% `Talking-to-AI` figure reported in our
> earlier analysis therefore reflects, almost entirely, workflow-level
> orchestration of AI bot agents rather than discursive
> participation of AI in PR prose."

### Results 1 -> Add: Two phenomena, not one

> "The agent-commanding and discursive subsets are qualitatively
> distinct. Agent-commanding mentions are dominated by `Suggestion`
> (89.9%), driven by reviewers and other commenters (93.3% combined),
> and concentrated in the early phase of the PR lifecycle (51.9%).
> Discursive mentions are dominated by `Explanation` (48.1%) and
> `Justification` (11.3%), driven by authors (43.4%, vs 6.7% in the
> agent-commanding subset), and concentrated in the late phase
> (48.1%). These two patterns map onto two different sociotechnical
> phenomena: the first is workflow orchestration of bot agents, the
> second is post-hoc accounting for AI involvement during code
> review. Treating them as a single 'AI mention' obscures the
> difference."

### Results 5 -> Replace the merge x uptake paragraph

> "The original 100-case sample mixed invocations that occurred
> before and after the PR was merged. We performed two temporal-
> hygiene cuts. First, we dropped the 15 merged-PR cases whose first
> human follow-up arrived only after the merge had occurred (n=85;
> chi2 = 6.31, perm p = 0.044). Second, we additionally dropped the
> 6 merged cases with less than a 1-hour gap between invocation and
> merge (n=79; chi2 = 5.76, perm p = 0.056). The association
> survives the first cut but only borderline survives the second.
> A cluster-resampling analysis (1,000 draws of one invocation per
> PR) reached p < 0.05 in 72.0% of draws (median p = 0.020). We
> therefore report this association as descriptive: it is real, it
> partially survives temporal and clustering corrections, but it
> should not be read causally."

### New limitations paragraph

> "Several limitations of the design should be noted. (1) The
> AI-reference vs control comparison (77.5% vs 50.3% merge rate) is
> confounded by repository-level workflow adoption: AI-reference PRs
> are dominated by bot-orchestrated repositories whose PRs are
> systematically smaller and more automation-friendly. We do not
> perform PR-size, author-type, or repository fixed-effect matching,
> and so this comparison is descriptive only. (2) The 100-case
> uptake sample is clustered: 100 invocations come from 56 unique
> PRs (max 6 per PR). The reported chi-square is borderline-robust
> to one-per-PR resampling (significant in 72.0% of draws) but the
> nominal p-value should not be over-interpreted. (3) The LLM-
> assisted labeling has moderate inter-coder reliability
> (kappa ~0.5), and tends to over-label `positive_uptake` for cases
> with sparse follow-up. (4) Normative challenges to AI use, when
> they appear at all, are rare and are concentrated in a handful of
> projects; the headline pattern is one of routinized bot
> orchestration, not open contestation."

### New results subsection: Normative Negotiation

> "Beyond invocation and uptake, we searched the corpus for
> utterances that *regulate* AI use as a community practice. Of
> 7,265 comments and 966 reviews, only 21 human-authored utterances
> matched explicit norm-formation patterns. The most articulated
> case is in the `algesten/str0m` WebRTC project, where a maintainer
> rejects an AI-assisted contribution to the SPED component with
> the explicit reasoning, 'I'd prefer to hand roll (as opposed to
> vibe code), since it is important to maintain a clear idea of
> separation-of-concerns.' The contributor accepts the framing.
> The rarity of explicit normative challenge is itself a finding:
> in our corpus, AI participation is being routinized through
> tooling rather than openly debated, and the contestation episodes
> that do appear are articulated in domain-specific architectural
> terms rather than in policy terms."

### Future Work additions

> "Beyond expanding the uptake sample, three follow-up directions
> are suggested by the present revision. First, the discursive
> subset (n=106) should be analyzed in its own right with a
> qualitative coding pass focused on accountability and provenance
> markers; this is the layer in which authorship and credit
> negotiation around AI is most visible. Second, the bot-account
> outputs that we excluded should be brought back in as the middle
> term of a triadic invocation -> AI output -> human response
> sequence; this would let us examine repair structure rather than
> just response classification. Third, normative-challenge episodes
> should be expanded with a directly targeted close reading,
> sampled by repository to see whether maintainers in distinct
> communities articulate norms in distinct registers."

## Suggested figure additions

1. **Two-panel bar chart**: function distribution in agent-commanding
   vs discursive subsets (numbers in `agent_vs_discursive_summary.json`).

2. **Sensitivity table**: rows = analysis view (full / pre-merge /
   pre-merge+gap / one-per-PR median), columns = chi-square and
   permutation-p. Numbers in
   `uptake_temporal_summary.json` and `cluster_sensitivity_summary.json`.

3. **Confusion-matrix heatmap**: LLM x coder2 for the function
   sample. Highlights where the LLM is systematically miscategorizing.

## Asks that remain genuinely human

The second-coder labels in `kappa_function_sample.csv` and
`kappa_uptake_sample.csv` were assigned through close reading by the
agent during this session; they should be treated as a
*defensible-but-not-final* second pass. If you want to claim true
inter-coder reliability for a venue submission, re-do the second
pass yourself (or with another human) and re-run `compute_kappa.py`.
The infrastructure is in place; only the labels would change.
