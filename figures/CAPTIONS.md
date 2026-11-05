# Figure captions

## 01_measurement_dag

Illustrative generative DAG. A and pre-outcome X influence hypothetical Y* and decisions D. The recording process depends on A,Y* only. Statistical assumptions, not causal identification.

## 02_cohort_flow

Sequential notebook restrictions; counts are remaining rows. Raw and analytic IDs and person identities are unique.

## 03_group_outcomes

Recorded two-year recidivism by released race category in the full analytic cohort; no latent outcome is observed.

## 04_observed_fairness

Observed EO=max pairwise TPR or FPR gap on each primary sensitivity cohort (race Black/white; sex; supported Black/white intersections). RW/EO indicate the mitigation fitted for the plotted axis. All released-group descriptive metrics, including sparse groups, are saved separately.

## 05_predictive_tradeoffs

Held-out discrimination of underlying risk scores and balanced accuracy of adverse decisions. EO integrates randomization; it retains LR risk scores.

## 06_calibration

Ten fixed probability bins; points require at least one person. These are observed-label calibration curves, not latent calibration. All method/group bins and sizes are in calibration.csv.

## 07_feasibility

Common feasibility. Female/male alpha vary; both beta fixed to .10. Ranking codes: infeasible -1, stable 0, tie 1, reversed 2. White cells in EO-difference map are infeasible. This is a slice of the primary four-dimensional grid.

## 08_sensitivity

EO(LR) minus EO(EO sex). Female/male alpha vary; both beta fixed to .10. Ranking codes: infeasible -1, stable 0, tie 1, reversed 2. White cells in EO-difference map are infeasible. This is a slice of the primary four-dimensional grid.

## 09_ranking_reversal

Fairness ranking. Female/male alpha vary; both beta fixed to .10. Ranking codes: infeasible -1, stable 0, tie 1, reversed 2. White cells in EO-difference map are infeasible. This is a slice of the primary four-dimensional grid.

## 10_eo_ranges

Sensitivity ranges (lines) and observed-label point differences (dots). Crossing zero permits a ranking change; these are not confidence intervals.

## 11_simulation_recovery

30 independent datasets per sample size/setting. Both methods shown; recording violations depend on X while retaining the same group-marginal alpha/beta. RMSE includes sampling variability and assumption bias.

## 12_simulation_coverage

Sensitivity-set coverage of exact population EO and percentile sampling-interval coverage are distinct. Lines average the two synthetic methods; complete per-method values and Monte Carlo counts are saved. Sampling intervals use 100 bootstrap replicates, not the 1,000 used for COMPAS.

## 13_ablations

Equal-noise and narrower grids compared with the primary group-dependent grid for LR versus race EO. Identity measurement and fixed points are separately reported; fractions are grid summaries, not probabilities.

## 14_robustness

Threshold, age and screening-window robustness. Age-standardized comparisons use common within-outcome age weights and require nonempty cells. Wider-cohort models are re-trained with isolated splits; narrower-cohort evaluation subsets original test people.
