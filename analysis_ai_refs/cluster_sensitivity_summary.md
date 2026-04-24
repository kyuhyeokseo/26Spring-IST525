# Cluster Sensitivity for Uptake x Merge Chi-Square

The 100-case stratified uptake sample contains 56 unique PRs across 51 repositories. Up to 6 invocations come from the same PR (mean 1.786). The original chi-square assumes independent observations, which is violated by within-PR clustering. This script repeats the test 1,000 times, each time sampling one invocation per PR, and reports the resulting distribution.

## Per-iteration distributions

- Full 4x2 chi-square: {'mean': 9.2741, 'median': 9.012, 'p05': 4.3675, 'p95': 15.4359, 'min': 1.8713, 'max': 20.3897}
- Collapsed 2x2 chi-square: {'mean': 6.8272, 'median': 6.3348, 'p05': 2.729, 'p95': 11.7098, 'min': 0.9825, 'max': 16.8}
- Full p (perm): {'mean': 0.0528, 'median': 0.022, 'p05': 0.002, 'p95': 0.2036, 'min': 0.002, 'max': 0.5449}
- Collapsed 2x2 p (perm): {'mean': 0.0485, 'median': 0.02, 'p05': 0.002, 'p95': 0.1776, 'min': 0.002, 'max': 0.5309}

## Significance rates across draws

- Full table p < 0.05 in 71.8% of draws
- Collapsed 2x2 p < 0.05 in 72.0% of draws

## Interpretation

The association partially survives within-PR clustering. About half of the one-per-PR resamples still reach p < 0.05, so the original chi-square should be reported alongside this sensitivity check, not as the sole evidence.
