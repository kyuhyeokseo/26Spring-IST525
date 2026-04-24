# Uptake x Merge: Temporal Hygiene Re-Analysis

The original 100-case test mixes invocations that occurred *before* and *after* the PR was merged. Post-merge invocations cannot have shaped merge outcome, so their inclusion inflates the apparent association. This document reports the original test and two stricter views.

## View 0 — Original (n=100)

- Full 4x2 chi-square: chi2=11.4586, df=3, perm p=0.0058
- Collapsed 2x2 (positive vs non-positive): chi2=9.1259, perm p=0.005

### Uptake by merge status, full 100

| group | n | continued_delegation | corrective_critique | no_clear_uptake | positive_uptake |
|---|---|---|---|---|---|
| False | 32 | 3 (9.38%) | 16 (50.0%) | 0 (0.0%) | 13 (40.62%) |
| True | 68 | 1 (1.47%) | 17 (25.0%) | 1 (1.47%) | 49 (72.06%) |

## View 1 — Drop merged cases whose first response post-dates the merge

- n=85: kept 53 merged + 32 non-merged. Dropped 15 merged cases whose first uptake response arrived only after the merge had occurred (uptake could not have shaped the merge decision in those cases).
- Full chi-square: chi2=6.3106, df=2, perm p=0.044
- 2x2 (positive vs non-positive): chi2=5.2421, perm p=0.023

### Uptake by merge status, pre-merge only

| group | n | continued_delegation | corrective_critique | positive_uptake |
|---|---|---|---|---|
| False | 32 | 3 (9.38%) | 16 (50.0%) | 13 (40.62%) |
| True | 53 | 1 (1.89%) | 17 (32.08%) | 35 (66.04%) |

- Pre-merge timing x uptake: chi2=4.9598, perm p=0.2841

### Uptake by timing phase, pre-merge only

| group | n | continued_delegation | corrective_critique | positive_uptake |
|---|---|---|---|---|
| early | 47 | 2 (4.26%) | 21 (44.68%) | 24 (51.06%) |
| late | 21 | 0 (0.0%) | 6 (28.57%) | 15 (71.43%) |
| middle | 17 | 2 (11.76%) | 6 (35.29%) | 9 (52.94%) |

## View 2 — Same as View 1, also drop merged cases with <1h invocation-to-merge gap

- n=79: kept 47 merged + 32 non-merged. Stricter check that uptake had room to operate before merge.
- Full chi-square: chi2=5.7553, perm p=0.0564
- 2x2: chi2=4.9512, perm p=0.041

### Uptake by merge status, pre-merge + early-response

| group | n | continued_delegation | corrective_critique | positive_uptake |
|---|---|---|---|---|
| False | 32 | 3 (9.38%) | 16 (50.0%) | 13 (40.62%) |
| True | 47 | 1 (2.13%) | 15 (31.91%) | 31 (65.96%) |

## Interpretation

Reporting the pre-merge subset removes the most obvious source of tautology: cases where the invocation happened after the PR had already been merged. If the association in View 1 weakens substantially relative to View 0, the original chi-square should be reported with that caveat.
View 2 is a stricter sensitivity check: it restricts further to invocations whose first human follow-up arrived within the early window. This is the closest available proxy for 'did the uptake occur in time to plausibly shape the PR outcome'.
