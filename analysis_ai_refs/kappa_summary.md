# Inter-Coder Reliability (Cohen's kappa)

Stratified samples were drawn from each labeled dataset. The second coder independently re-read each mention or invocation body and assigned a label using the same codebook used for LLM labeling. Cohen's kappa was then computed between the LLM labels and the second coder.

## Function labels (n=56 stratified, ~10 per class)

- n compared: 56
- Raw agreement: 0.5893
- Expected agreement: 0.1712
- Cohen's kappa: **0.5044**

Confusion matrix (rows = LLM, columns = coder2):

| llm \ coder2 | Critique | Explanation | Justification | Meta discussion | Other | Suggestion |
|---|---|---|---|---|---|---|
| Critique | 5 | 0 | 0 | 0 | 3 | 2 |
| Explanation | 0 | 8 | 0 | 1 | 2 | 0 |
| Justification | 0 | 3 | 3 | 0 | 2 | 2 |
| Meta discussion | 0 | 0 | 0 | 3 | 0 | 2 |
| Other | 0 | 1 | 0 | 3 | 5 | 1 |
| Suggestion | 1 | 0 | 0 | 0 | 0 | 9 |

- LLM label counts: {'Critique': 10, 'Explanation': 11, 'Justification': 10, 'Meta discussion': 5, 'Other': 10, 'Suggestion': 10}
- Coder2 label counts: {'Critique': 6, 'Other': 12, 'Suggestion': 16, 'Meta discussion': 7, 'Explanation': 12, 'Justification': 3}

## Uptake labels (n=25 stratified, all classes)

- n compared: 25
- Raw agreement: 0.6
- Expected agreement: 0.232
- Cohen's kappa: **0.4792**

Confusion matrix (rows = LLM, columns = coder2):

| llm \ coder2 | continued_delegation | corrective_critique | no_clear_uptake | positive_uptake |
|---|---|---|---|---|
| continued_delegation | 4 | 0 | 0 | 0 |
| corrective_critique | 3 | 7 | 0 | 0 |
| no_clear_uptake | 0 | 0 | 1 | 0 |
| positive_uptake | 3 | 0 | 4 | 3 |

- LLM label counts: {'continued_delegation': 4, 'corrective_critique': 10, 'no_clear_uptake': 1, 'positive_uptake': 10}
- Coder2 label counts: {'continued_delegation': 10, 'corrective_critique': 7, 'no_clear_uptake': 5, 'positive_uptake': 3}

## Interpretation

Landis & Koch (1977) benchmark: <0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial, >0.80 almost perfect. Kappa values around or below 0.40 should be reported as a limitation, and the codebook should be tightened in future passes. The most informative output here is the confusion matrix: it shows which categories the LLM and the second coder are systematically confusing.
