# When Noisy Outcomes Reverse Criminal-Justice Fairness Conclusions

Retrospective research audit. No recommendation for detention, sentencing, policing, or deployment. Hypothetical Y* is not recovered behavior or observed offenses.

## A. Empirically observed facts

The released data contain 7,214 rows; the notebook cohort contains 6,172 people. Repeated IDs: 0; repeated name/date-of-birth identities: 0. Notebook adjusted Black/white score coefficient 0.47721; reproduced 0.47720698 (odds ratio 1.6116). This reproduces notebook cell 21, not the different survival/truth-table cohort used elsewhere in the story. The notebook's 45% probability-ratio calculation is conditional on its reference profile; its coefficient implies an odds ratio of 1.61. Neither statistic is an EO disparity.

The full notebook cohort also yields the following independent released-score confusion audit at decile >=5 (Medium/High versus Low). It uses all eligible people rather than the prediction test subset. These are recorded-outcome rates, not recording-error parameters.

| group | n | tn | fp | fn | tp | fpr | tpr | fnr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| African-American | 3175 | 873.0000 | 641.0000 | 473.0000 | 1188.0000 | 0.4234 | 0.7152 | 0.2848 |
| Asian | 31 | 21.0000 | 2.0000 | 3.0000 | 5.0000 | 0.0870 | 0.6250 | 0.3750 |
| Caucasian | 2103 | 999.0000 | 282.0000 | 408.0000 | 414.0000 | 0.2201 | 0.5036 | 0.4964 |
| Hispanic | 509 | 258.0000 | 62.0000 | 110.0000 | 79.0000 | 0.1938 | 0.4180 | 0.5820 |
| Native American | 11 | 3.0000 | 3.0000 | 0.0000 | 5.0000 | 0.5000 | 1.0000 | 0.0000 |
| Other | 343 | 191.0000 | 28.0000 | 82.0000 | 42.0000 | 0.1279 | 0.3387 | 0.6613 |

The split is 3,703 train, 1,234 validation, 1,235 test people (60/20/20 rounded), stratified by sex/outcome. All models use the same split. LR and GBT hyperparameters and binary thresholds use validation only; BN bins are fixed and CPDs training-only. COMPAS is an independent decile audit, high risk at decile >=5; its probability calibration is fitted on validation only. Features are age, prior count, three juvenile history counts, and current charge degree. Race/sex are reserved for auditing and mitigation. No future outcome variables enter prediction.

| method | auroc | balanced_accuracy | accuracy | log_loss | brier |
| --- | --- | --- | --- | --- | --- |
| LR | 0.7187 | 0.6550 | 0.6567 | 0.6128 | 0.2120 |
| GBT | 0.7199 | 0.6676 | 0.6713 | 0.6106 | 0.2109 |
| BN | 0.7029 | 0.6506 | 0.6615 | 0.6340 | 0.2200 |
| COMPAS | 0.7223 | 0.6639 | 0.6664 | 0.6124 | 0.2116 |
| RW_race | 0.7178 | 0.6557 | 0.6575 | 0.6144 | 0.2129 |
| EO_race | 0.7187 | 0.6272 | 0.6278 | 0.6128 | 0.2120 |
| RW_sex | 0.7178 | 0.6566 | 0.6640 | 0.6129 | 0.2122 |
| EO_sex | 0.7187 | 0.6521 | 0.6532 | 0.6128 | 0.2120 |
| RW_intersection | 0.7167 | 0.6540 | 0.6623 | 0.6148 | 0.2131 |
| EO_intersection | 0.7187 | 0.6268 | 0.6275 | 0.6128 | 0.2120 |

Reweighing uses training observed A/Y cell frequencies. Unsupported empty training cells retain unit weights; Asian/Female and Native American/Female intersections are unsupported. EO optimizes validation observed equalized odds with Fairlearn; validation groups with fewer than five examples in either outcome retain original LR decisions. Supported groups are recorded in decision_rules.json. Primary EO metrics use expected randomized confusion cells; ten sampled seeds quantify additional decision variation. EO risk discrimination/calibration refer to the unchanged LR score, not the selection probability.

All released groups are reported in group_metrics.csv, including class counts, sparse flags, expected confusion cells, predictive metrics and calibration bins. Small groups are descriptive only. Primary sensitivity cohorts:

| axis | included_groups | included_n | excluded_n |
| --- | --- | --- | --- |
| race | African-American; Caucasian | 1087 | 148 |
| sex | Female; Male | 1235 | 0 |
| intersection | African-American / Female; African-American / Male; Caucasian / Female; Caucasian / Male | 1087 | 148 |

## B. Results conditional on hypothetical measurement assumptions

The primary grid is alpha,beta=0:0.025:0.2 per group. It is exploratory, documented in docs/ASSUMPTIONS.md, not externally preregistered or empirically estimated. Historical pre-execution timing was not independently established. Race/sex use full four-dimensional grids; intersection uses two race-specific profiles shared across sexes. Each pair is evaluated on its common feasible set. Matrix inversion rejects invalid prevalence or joint cells; zero denominators are undefined. A valid inverse is compatible with the independence assumption, not evidence that it is true.

| axis | left | right | observed_difference | feasible | reversed | reversal_fraction | min_difference | max_difference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| race | LR | RW_race | 0.0000 | 6561 | 0 | 0.0000 | -0.0010 | 0.0031 |
| race | LR | EO_race | 0.2612 | 6561 | 0 | 0.0000 | 0.0638 | 0.3512 |
| race | LR | GBT | 0.0003 | 6561 | 5831 | 0.8887 | -0.0145 | 0.0115 |
| race | LR | BN | 0.0868 | 6561 | 0 | 0.0000 | 0.0825 | 0.0912 |
| race | LR | COMPAS | 0.0231 | 6561 | 657 | 0.1001 | -0.0966 | 0.0758 |
| sex | LR | RW_sex | -0.0004 | 6561 | 1379 | 0.2102 | -0.0041 | 0.0082 |
| sex | LR | EO_sex | 0.1449 | 6561 | 2068 | 0.3152 | -0.2627 | 0.2107 |
| sex | LR | GBT | 0.0247 | 6561 | 1774 | 0.2704 | -0.0754 | 0.0640 |
| sex | LR | BN | 0.0518 | 6561 | 192 | 0.0293 | -0.0678 | 0.0872 |
| sex | LR | COMPAS | 0.1045 | 6561 | 1525 | 0.2324 | -0.2188 | 0.1694 |
| intersection | LR | RW_intersection | 0.0411 | 6561 | 0 | 0.0000 | 0.0190 | 0.0411 |
| intersection | LR | EO_intersection | 0.3515 | 6561 | 0 | 0.0000 | 0.1506 | 0.4359 |
| intersection | LR | GBT | 0.0170 | 6561 | 405 | 0.0617 | -0.0210 | 0.0726 |
| intersection | LR | BN | 0.1865 | 6561 | 0 | 0.0000 | 0.1787 | 0.2224 |
| intersection | LR | COMPAS | 0.1079 | 6561 | 567 | 0.0864 | -0.0478 | 0.1854 |

The main mitigation comparison illustrates both stability and reversal: sex EO is lower than LR on observed labels, but its ranking reverses in 2,068/6,561 feasible primary scenarios (31.52%). Race EO has 0 primary reversals. Other pairs can start almost tied: the LR/GBT observed race EO difference is only about 0.00027, so its high reversal fraction should not be interpreted as a robust observed ranking.

Positive differences mean LR has larger disparity; negative differences mean its comparator has larger disparity. Zero-error scenarios reproduce the observed-label analysis exactly. Sensitivity extrema span assumptions, not sampling uncertainty. Equal-noise, narrower, broader and coarser analyses are in sensitivity_summary.csv. Reversal fractions count feasible grid scenarios and depend on the chosen grid; they are not probabilities.

A representative strict reversal is sex: LR versus EO_sex, with groups ['Female', 'Male'] and (alpha,beta) values [[0.175, 0.1], [0.15, 0.0]]. Observed EO values are [0.17399052904934065, 0.02911402100927546]; hypothetical EO values are [0.11612358176657592, 0.15374235787924317]. Inversion redistributes recorded decision/outcome cells differently across groups and methods. Different decision-stratum mixtures shift TPR and FPR enough to change the largest disparity. This mechanism is conditional on those error assumptions; all inferred cells for this example are in representative_scenarios.json.

### Synthetic validation

The generative population has known A,X,Y*,recorded Y,D; group prevalence and prediction quality differ. Exact population enumeration and inversion are independently unit-tested. The known-error scenario reconstructs population joint cells under class-conditional noise. Finite-sample results below compare recovered EO against exact latent population EO, not observed labels. Feasibility agreement compares candidate decisions with exact population compatibility.

| setting | n | method | bias | rmse | known_feasible | sensitivity_coverage | sampling_coverage | reversal_accuracy | feasibility_agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| equal | 1000 | 0 | 0.0142 | 0.0436 | 1.0000 | 0.9667 | 0.9000 | 0.9333 | 1.0000 |
| equal | 1000 | 1 | 0.0303 | 0.0458 | 1.0000 | 0.9333 | 0.9333 | 0.9333 | 1.0000 |
| equal | 5000 | 0 | 0.0067 | 0.0208 | 1.0000 | 1.0000 | 0.9333 | 1.0000 | 1.0000 |
| equal | 5000 | 1 | -0.0007 | 0.0181 | 1.0000 | 1.0000 | 0.9667 | 1.0000 | 1.0000 |
| equal | 10000 | 0 | 0.0038 | 0.0129 | 1.0000 | 1.0000 | 0.9333 | 1.0000 | 1.0000 |
| equal | 10000 | 1 | 0.0015 | 0.0126 | 1.0000 | 1.0000 | 0.9667 | 1.0000 | 1.0000 |
| unequal | 1000 | 0 | 0.0213 | 0.0475 | 1.0000 | 0.9667 | 0.9333 | 0.9667 | 0.9267 |
| unequal | 1000 | 1 | 0.0213 | 0.0343 | 1.0000 | 0.9667 | 0.9667 | 0.9667 | 0.9267 |
| unequal | 5000 | 0 | 0.0035 | 0.0148 | 1.0000 | 1.0000 | 0.9667 | 1.0000 | 0.9733 |
| unequal | 5000 | 1 | 0.0075 | 0.0237 | 1.0000 | 1.0000 | 0.9000 | 1.0000 | 0.9733 |
| unequal | 10000 | 0 | -0.0018 | 0.0137 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9933 |
| unequal | 10000 | 1 | 0.0017 | 0.0128 | 1.0000 | 1.0000 | 0.9667 | 1.0000 | 0.9933 |
| violation | 1000 | 0 | -0.0076 | 0.0431 | 1.0000 | 1.0000 | 0.9333 | 1.0000 | 0.9067 |
| violation | 1000 | 1 | 0.0208 | 0.0400 | 1.0000 | 1.0000 | 0.9333 | 1.0000 | 0.9067 |
| violation | 5000 | 0 | -0.0188 | 0.0267 | 1.0000 | 1.0000 | 0.8000 | 1.0000 | 0.9933 |
| violation | 5000 | 1 | -0.0088 | 0.0176 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9933 |
| violation | 10000 | 0 | -0.0225 | 0.0263 | 1.0000 | 1.0000 | 0.6667 | 1.0000 | 0.9800 |
| violation | 10000 | 1 | -0.0123 | 0.0172 | 1.0000 | 1.0000 | 0.9667 | 1.0000 | 0.9800 |

30 repetitions give limited Monte Carlo precision (worst-case standard error 0.091 for a coverage fraction). Coverage under X-dependent errors is a stress test, not a guarantee. Invalid true-scenario replicates remain recorded. Sensitivity coverage is not a confidence-interval coverage statement; sampling intervals condition on fixed generating error rates.

### Sampling uncertainty

1,000 paired person bootstrap replicates resample identical people for every method; fitted models and splits are fixed. Fixed measurement points were specified before the sweep. Percentile intervals below are exploratory and conditional on feasibility. Invalid/undefined replicates are counted, never converted to zero. Intervals do not include training, measurement-rate or model-selection uncertainty.

| method | scenario | metric | valid | invalid | low | high |
| --- | --- | --- | --- | --- | --- | --- |
| EO_race | contrast | eo | 1000 | 0 | 0.0268 | 0.1482 |
| EO_race | contrast | difference_from_LR | 1000 | 0 | -0.3216 | -0.0530 |
| EO_race | equal_05 | eo | 1000 | 0 | 0.0118 | 0.1237 |
| EO_race | equal_05 | difference_from_LR | 1000 | 0 | -0.3528 | -0.1180 |
| EO_race | observed | eo | 1000 | 0 | 0.0114 | 0.1153 |
| EO_race | observed | difference_from_LR | 1000 | 0 | -0.3491 | -0.1333 |
| LR | contrast | eo | 1000 | 0 | 0.1806 | 0.3788 |
| LR | contrast | difference_from_LR | 1000 | 0 | 0.0000 | 0.0000 |
| LR | equal_05 | eo | 1000 | 0 | 0.2172 | 0.4032 |
| LR | equal_05 | difference_from_LR | 1000 | 0 | 0.0000 | 0.0000 |
| LR | observed | eo | 1000 | 0 | 0.2216 | 0.3950 |
| LR | observed | difference_from_LR | 1000 | 0 | 0.0000 | 0.0000 |

For the central sex comparison, the 95% paired observed EO(EO policy)-EO(LR) interval is [-0.2284, 0.0051]. It includes zero; the observed test-sample advantage does not establish a population fairness ranking. Conditional ranking reversals are sensitivity findings and should be interpreted with this sampling uncertainty.

Predictive intervals and paired predictive differences are in predictive_intervals.csv and predictive_difference_intervals.csv. Conditional EO and paired fairness intervals for all axes are in bootstrap_intervals.csv. No sensitivity range is labeled a confidence interval.

### Ablations and robustness

Identity measurement is the observed-label ablation. Equal-noise constraints reduce the scenario set; fixed-point versus range comparisons are available in bootstrap_intervals.csv and sensitivity_summary.csv. These isolate measurement assumptions rather than refitting predictions.

| region | feasible | reversed | reversal_fraction | min_difference | max_difference |
| --- | --- | --- | --- | --- | --- |
| primary | 6561 | 0 | 0.0000 | 0.0638 | 0.3512 |
| equal_noise | 81 | 0 | 0.0000 | 0.2171 | 0.2643 |
| narrow | 625 | 0 | 0.0000 | 0.1923 | 0.3190 |
| broad | 2401 | 439 | 0.1828 | -0.3586 | 0.3899 |
| coarse | 625 | 0 | 0.0000 | 0.0638 | 0.3495 |

| check | eo |
| --- | --- |
| LR threshold 0.35 | 0.1973 |
| LR threshold 0.5 | 0.2509 |
| LR threshold 0.65 | 0.1783 |
| EO random seed 0 | 0.0530 |
| EO random seed 1 | 0.0752 |
| EO random seed 2 | 0.0419 |
| EO random seed 3 | 0.0681 |
| EO random seed 4 | 0.0469 |
| EO random seed 5 | 0.0641 |
| EO random seed 6 | 0.0406 |
| EO random seed 7 | 0.0271 |
| EO random seed 8 | 0.0711 |
| EO random seed 9 | 0.0274 |
| age standardized LR | 0.2529 |
| age standardized RW_race | 0.2529 |
| age standardized EO_race | 0.1270 |
| age feature removed | 0.2254 |
| screening window 15 | 0.2691 |
| screening window 60 | 0.2914 |

Thresholds alter the decision itself; age standardization alters composition; removal of age alters the fitted predictor; cohort windows change eligibility. These are distinct perturbations. Race, sex and intersection analyses and ten postprocessing seeds were executed, with results saved for each. Nonempty age/outcome cells are required for standardization; undefined checks are explicit. Wider-window comparisons involve a different isolated split, so are not paired estimates on the original people.

## C. Claims not established by these data

The data do not identify Y*, alpha, beta, actual offense incidence, causal discrimination, or deployment utility. Conditional independence of recording and decisions cannot be verified from recorded outcomes alone. Scenario compatibility is necessary, not sufficient, for substantive plausibility. Error grids carry no empirical prior. Minority and intersectional estimates can be unstable; restricting sensitivity contrasts leaves other racial groups outside those conclusions. Missing features use training-only imputation; unmeasured errors remain possible. Person linkage by released names/date of birth cannot guarantee absence of identity errors. Fairness rankings depend on cohort, thresholds, metric, sampling variation and measurement assumptions; exploratory reversals do not establish real-world injustice or identify the superior method.

## Reproduction and artifacts

See README.md for exact commands. Source files, raw data, pinned requirements, tests, configs, checkpoints, all machine-readable experiment tables and 14 figures in PNG/PDF/SVG are retained. Current run configuration and raw/assumption hashes are in results/run_manifest.json. Figures and the report are generated only from completed result files. The original run did not publish or push; a later Git delivery is documented in docs/GIT_DELIVERY.md.

## Final verification and conclusion (additional computational audit)

This section records verification of the existing research, not a second research study or an external preregistration. The checkpoint is commit `1be36dfdd9172be20a5e78ba73f93abeaceba62e`; corrections are on `compas-fairness-verification`. [Requirements matrix](REQUIREMENTS_MATRIX.md) gives PASS/PARTIAL/NOT VERIFIABLE assessments with evidence. Core configured Problem 7 analyses are supported; full unqualified compliance is not claimed.

### Objective and mathematical verification

The objective remains whether observed-label fairness improvements are stable under explicitly hypothetical, group-dependent recording errors. The matrix is M=[[1-alpha,beta],[alpha,1-beta]] with columns latent and rows recorded. For each group and each decision row j, z=solve(M,j), pi=(q-alpha)/(1-alpha-beta). Validity requires probabilities in [0,1], determinant>1e-8, normalized nonnegative joint cells within 1e-10, exact forward reconstruction and nonzero class denominators. D=1 is an adverse classification. No latent behavior is recovered or identified.

An independent implementation uses generic linear-system solves and explicit group maxima, not production inversion/sweep functions. It regenerated all 6,561 primary scenarios for each of the two headline comparisons from saved people/decisions. Sex LR/EO reversals remain **2,068/6,561 (31.5196%)**; race reversals remain **0/6,561**. Every feasible EO value matched to 1e-12. Randomized scalar/vectorized comparisons and a true-reversal population positive control pass. Representative Female (.175,.10), Male (.15,0) has latent EO LR=.11612358 versus EO=.15374236, reversing observed .17399053 versus .02911402. All four joint arrays, forward reconstructions and group TPR/FPR values are in `results/verification/independent_numerical_audit.json`.

All 1,000 paired bootstrap resamples were independently regenerated from saved people, using shared indices for each method. All six methods on all three axes and three fixed scenarios matched; every stored fairness interval quantile was recomputed. The observed sex EO-policy-minus-LR interval [-.2284,.0051] still includes zero. Point-estimate reversals are therefore sensitivity findings, not statistically established population ranking changes. Pipeline verification also checked saved predictions, train-only scaler means, EO probabilities/fallbacks, calibration bins, predictive-score metrics, and BN posteriors against independent products of fitted CPDs.

### Confirmed corrections and their impact

1. Recording decisions and scenarios could silently broadcast mismatched array shapes. Strict shape checks now reject them; current valid inputs and all original primary results are unchanged.
2. Group eligibility could accept a single observed class when crosstab omitted the other column. Columns are now explicitly [0,1]; the original cohort has both, so saved eligibility is unchanged.
3. A bootstrap replicate losing an eligible group recorded only the observed scenario. It now records undefined metrics and reasons for every fixed scenario/group. A forced-absence test covers this path. None of the original replicates lost a required group; no full bootstrap rerun was necessary.
4. Robustness predictive metrics used the full sample while EO/N used a subset. Predictive metrics now use exactly the EO cohort. This small stage was rerun; prior `robustness.csv` is retained in `results/verification/original_robustness.csv`. EO values and the robustness figure are unchanged.
5. Synthetic reversal detection lacked the main analysis tie tolerance. It now excludes near ties at 1e-4. Expanding the previous arithmetic seed formula beyond 30 repetitions could reuse streams across sample sizes; additional validation uses SeedSequence(seed,N,rep,setting). Signature checks now include measurement code, bootstrap size and tolerance, and the completed signature is written only after success. Original 270 datasets remain intact.
6. Simulation reporting lacked binomial Monte Carlo intervals. Original and additional validation now have per-setting/method Wilson intervals, counts and SEs. The report generator includes this verification section rather than dropping the corrections on regeneration.

### Additional synthetic validation and precision

`docs/VERIFICATION_PROTOCOL.json` was timestamped before the additional simulation. It is a post-exploratory computational protocol, not external preregistration or confirmatory COMPAS inference. New seed 7102026, 200 repetitions at each N=1,000/5,000/10,000 for equal, unequal and marginal-preserving X-dependent errors gives **1,800 additional datasets**. Each uses 200 paired sampling-bootstrap replicates. Maximum binomial MC SE is .0354 versus .0913 for the original 30-replicate study. Both finite repetition count and finite bootstrap size remain limitations.

At N=10,000 sampling-CI coverage is .970/.970 for equal noise and .945/.940 for unequal noise. Under covariate-dependent violations it is .735/.945; method 0's .735 estimate has a 95% Wilson MC interval [.6698,.7913]. These intervals quantify Monte Carlo error of the estimated coverage, not uncertainty intervals for COMPAS EO. Sensitivity-set coverage is reported separately and is not a confidence-interval claim. Bias/RMSE, exact-population feasibility agreement and reversal accuracy are separately retained. Main synthetic DGPs provide limited positive population-reversal cases; an exact positive-control test demonstrates a reversal but is not a comprehensive finite-sample true-positive study. Overall accuracy should not be advertised as universal reversal-detection sensitivity.

Original figures 11/12 and their report table still describe the original 270 datasets. The additional coverage plot with MC intervals is `figures/verification/simulation_coverage_mc.{png,pdf,svg}`. Complete added tables are under `results/verification_simulation/`; original versus added MC intervals are in `results/verification/monte_carlo_intervals.csv`. Rows are method-specific because the two methods share each dataset; they are not treated as twice as many independent repetitions.

### Scope, ethics and remaining requirements

The intersectional grid shares race-specific errors across sexes. A fully independent grid would contain 9^8=43,046,721 scenarios before methods/outputs; the implemented structured 6,561-scenario slice does not cover every intersection-specific recording process. Sparse groups, the separate story survival/Cox truth table, and external preregistration remain limited or unverified as detailed in the requirements matrix. Notebook cohort/audit reproduction is verified, not relabeled as the distinct survival audit. The historical register is treated as exploratory; its original timing is not independently established by this verification. Stage caching/provenance is not a full workflow engine, and original console history is incomplete.

The conclusion is conditional: observed-label fairness rankings can reverse within compatible hypothetical measurement scenarios, and the recording-independence assumption matters for recovery and interval coverage. Neither compatibility nor simulation establishes true error rates, actual offenses, causal discrimination, a uniquely fair method or safe deployment. This remains a retrospective research audit, not a criminal-justice recommendation.

### Exact verification commands

Run from the project directory with `/workspace/compas-venv/bin/python` (or a recreated pinned environment):

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python scripts/verify_research.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m scripts.verify_pipeline
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m scripts.run_verification_simulation
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m scripts.verification_precision
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m pytest -q --junitxml=results/verification/tests.xml
/workspace/compas-venv/bin/python scripts/check_results.py
```

The added simulation initially executed as a Python invocation of `run_simulation` with `configs/verification_simulation.json` and output `results/verification_simulation`, logged in `results/verification/simulation.log`; the provided wrapper reproduces that invocation. Cached-model pipeline verification requires the trusted local checkpoint; it was deliberately excluded from Git delivery. Scalar reversal/bootstrap verification uses committed prediction tables alone. Original production-source snapshots and corrected-source fingerprints are retained separately so current source is not falsely labeled as the source that originally generated every table.

### Final verification outcome

The final complete test suite passed **32 tests**, with zero failures/errors/skips and one upstream pgmpy deprecation warning (`results/verification/tests.xml`). Artifact validation passed. All 14 original PNG figures regenerated byte-for-byte from the retained tables (`results/verification/figure_reproduction.json`); no original figure was replaced. Extended simulation source/config fingerprints and the original raw-data checksum were checked. The artifact checker permits a 1e-12 endpoint tolerance for floating-point Wilson bounds; this changes no numerical result. No COMPAS model training, primary sensitivity experiment or production bootstrap was rerun. Only the small corrected robustness stage, additional separately configured simulation, deterministic numerical audits, tests and report/figure validation ran.

## Completion of outstanding achievable requirements

This section supersedes the earlier verification's remaining-work assessment without erasing its historical findings. The original available specification is preserved verbatim in `docs/ORIGINAL_SPECIFICATION.md`; there is no separate external Problem 7 rubric available. The original text asks for a documented observed-label audit (§2.10, §11 experiment 1, §20.1), not a mandatory Cox model. The reproduced notebook cohort and score-association audit satisfy that task. A separate survival model is an optional extension, not an unexecuted mandatory analysis. No event times or censoring values were fabricated.

### Independent intersectional recording parameters

`completion.independent_design` varies all eight alpha/beta coordinates for the four supported Black/white-by-sex groups, using scrambled Sobol points (seed 8172026). Each group's two rates can also be explicitly overridden through the function's `overrides` mapping; tests exercise that capability. The Sobol design has 16,384 points plus the identity, in each of [0,.2]^8 and [0,.3]^8. This reproducible space-filling design replaces exhaustive 9^8 enumeration, as permitted by original §9. It is not an empirical prior, an exhaustive grid, or a guarantee that narrow reversal pockets have been discovered. Each comparison checks all groups and both methods, rejects incompatible cells, and reports undefined metrics explicitly. The original restricted-slice outputs remain separate.

| maximum | comparator | scenarios | feasible | reversals | reversal_fraction | min_difference | max_difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2000 | RW_intersection | 16385 | 16385 | 0 | 0.0000 | 0.0193 | 0.0498 |
| 0.2000 | EO_intersection | 16385 | 16385 | 0 | 0.0000 | 0.1638 | 0.4481 |
| 0.2000 | GBT | 16385 | 16385 | 1910 | 0.1166 | -0.0684 | 0.0723 |
| 0.2000 | BN | 16385 | 16385 | 0 | 0.0000 | 0.1473 | 0.2476 |
| 0.2000 | COMPAS | 16385 | 16385 | 2469 | 0.1507 | -0.0950 | 0.1930 |
| 0.3000 | RW_intersection | 16385 | 13698 | 1321 | 0.0964 | -0.0454 | 0.0981 |
| 0.3000 | EO_intersection | 16385 | 13287 | 508 | 0.0382 | -0.2159 | 0.5057 |
| 0.3000 | GBT | 16385 | 12851 | 3358 | 0.2613 | -0.1433 | 0.1541 |
| 0.3000 | BN | 16385 | 13146 | 432 | 0.0329 | -0.2194 | 0.3311 |
| 0.3000 | COMPAS | 16385 | 10711 | 1630 | 0.1522 | -0.2067 | 0.2712 |

Both methods use the same 1,087 supported test people. LR versus intersectional EO reverses in 508/13,287 feasible points of the broader design (3.8233%) and in zero points of the narrower design. These fractions summarize the sampling design, not population probabilities. All parameters, pairwise feasibility reasons, group rates, gaps, ties and classifications are retained in `results/completion/intersection_*.csv.gz`, with observed joint arrays in `intersection_observed_joints.json`. Latent joints are exactly reproducible by solving each stored group's measurement matrix against those observed joints.

### Finite-sample positive, negative and boundary controls

New simulations comprise 6,000 datasets: 200 repetitions for each of five population/noise cases, two group proportions (.5 and .2), and N=1,000/5,000/10,000. The positive and stable populations were selected by the prespecified deterministic population-only search (not from COMPAS outcomes); all parameters are saved in `control_populations.json`. Covariate X, hypothetical Ystar, recorded labels and two decisions are all represented in the generative cells. Positive cases use two error strengths (.5 and 1 times fixed group error profiles), negative cases are stable population rankings, and the zero-noise boundary has identical population decision mechanisms and a tied ranking. Classification uses the same 1e-4 tolerance. All methods share each simulated dataset.

Simulation counts are multinomial representations of individual categorical records. A paired multinomial person bootstrap is distributionally identical to resampling those same records; a regression test cross-checks expanded individuals against the cell representation. Each dataset uses 200 bootstrap replicates. Feasibility is common across both methods. Infeasible recovery is recorded and counts as a detection failure, rather than being silently dropped from sensitivity denominators. Wilson intervals quantify Monte Carlo uncertainty across independent datasets, not uncertainty about COMPAS measurement assumptions. Generating-scenario feasibility, generating-metric sensitivity-bound coverage, sampling-CI coverage, bias and RMSE are distinct saved outcomes. The known error point is included explicitly in the sensitivity evaluation; its feasibility rate does not establish the plausibility of any error assumption.

| kind | strength | group_probability | n | detection_fraction | detection_mc_low | detection_mc_high | bias | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| boundary | 0.0000 | 0.2000 | 1000 | 0.0000 | 0.0000 | 0.0188 | 0.0280 | 0.0525 |
| boundary | 0.0000 | 0.2000 | 5000 | 0.0000 | 0.0000 | 0.0188 | 0.0105 | 0.0207 |
| boundary | 0.0000 | 0.2000 | 10000 | 0.0000 | 0.0000 | 0.0188 | 0.0058 | 0.0152 |
| boundary | 0.0000 | 0.5000 | 1000 | 0.0000 | 0.0000 | 0.0188 | 0.0207 | 0.0398 |
| boundary | 0.0000 | 0.5000 | 5000 | 0.0000 | 0.0000 | 0.0188 | 0.0109 | 0.0184 |
| boundary | 0.0000 | 0.5000 | 10000 | 0.0000 | 0.0000 | 0.0188 | 0.0062 | 0.0128 |
| negative | 0.5000 | 0.2000 | 1000 | 0.2750 | 0.2178 | 0.3407 | -0.0035 | 0.0505 |
| negative | 0.5000 | 0.2000 | 5000 | 0.1700 | 0.1243 | 0.2282 | -0.0002 | 0.0226 |
| negative | 0.5000 | 0.2000 | 10000 | 0.0400 | 0.0204 | 0.0769 | 0.0022 | 0.0145 |
| negative | 0.5000 | 0.5000 | 1000 | 0.2100 | 0.1593 | 0.2716 | 0.0055 | 0.0433 |
| negative | 0.5000 | 0.5000 | 5000 | 0.1350 | 0.0945 | 0.1893 | 0.0010 | 0.0198 |
| negative | 0.5000 | 0.5000 | 10000 | 0.0600 | 0.0347 | 0.1019 | 0.0007 | 0.0134 |
| negative | 1.0000 | 0.2000 | 1000 | 0.0250 | 0.0107 | 0.0572 | -0.0030 | 0.0472 |
| negative | 1.0000 | 0.2000 | 5000 | 0.0000 | 0.0000 | 0.0188 | -0.0010 | 0.0204 |
| negative | 1.0000 | 0.2000 | 10000 | 0.0000 | 0.0000 | 0.0188 | -0.0000 | 0.0150 |
| negative | 1.0000 | 0.5000 | 1000 | 0.0000 | 0.0000 | 0.0188 | 0.0016 | 0.0437 |
| negative | 1.0000 | 0.5000 | 5000 | 0.0000 | 0.0000 | 0.0188 | -0.0005 | 0.0195 |
| negative | 1.0000 | 0.5000 | 10000 | 0.0000 | 0.0000 | 0.0188 | 0.0013 | 0.0138 |
| positive | 0.5000 | 0.2000 | 1000 | 0.1400 | 0.0987 | 0.1949 | -0.0130 | 0.0782 |
| positive | 0.5000 | 0.2000 | 5000 | 0.3300 | 0.2686 | 0.3978 | -0.0014 | 0.0342 |
| positive | 0.5000 | 0.2000 | 10000 | 0.5050 | 0.4363 | 0.5735 | -0.0004 | 0.0245 |
| positive | 0.5000 | 0.5000 | 1000 | 0.2650 | 0.2087 | 0.3302 | -0.0010 | 0.0472 |
| positive | 0.5000 | 0.5000 | 5000 | 0.5700 | 0.5007 | 0.6367 | 0.0044 | 0.0227 |
| positive | 0.5000 | 0.5000 | 10000 | 0.6800 | 0.6125 | 0.7407 | 0.0003 | 0.0164 |
| positive | 1.0000 | 0.2000 | 1000 | 0.4950 | 0.4265 | 0.5637 | -0.0027 | 0.0553 |
| positive | 1.0000 | 0.2000 | 5000 | 0.7050 | 0.6384 | 0.7639 | 0.0022 | 0.0213 |
| positive | 1.0000 | 0.2000 | 10000 | 0.8700 | 0.8163 | 0.9097 | 0.0014 | 0.0160 |
| positive | 1.0000 | 0.5000 | 1000 | 0.6600 | 0.5919 | 0.7221 | -0.0017 | 0.0490 |
| positive | 1.0000 | 0.5000 | 5000 | 0.7850 | 0.7230 | 0.8363 | 0.0027 | 0.0236 |
| positive | 1.0000 | 0.5000 | 10000 | 0.9450 | 0.9042 | 0.9690 | -0.0000 | 0.0150 |

At N=10,000 positive-case sensitivity spans 50.5–94.5% across settings; negative-case false-reversal frequency spans 0–6%; zero-noise boundary false reversals are 0/200 in every configuration. These limitations are results of the validation, not reasons to alter the populations until they pass. Full per-method recovery and coverage tables are in `reversal_control_summary.csv`, with all replicate rows in `reversal_control_replicates.csv.gz`.

### Protocol timing and irreducible limitations

`docs/COMPLETION_PROTOCOL.json` was dated and committed (`d85de2b`) before the new experiments, with fixed seeds, designs, control-selection rules and precision targets. This is a prospective computational protocol for the added analyses, not externally registered human-subject research or retroactive preregistration of the original results. The original §11 experiment 3 calls its region “preregistered,” while §9 calls for exploratory configuration. Historical pre-analysis timing for the original exploratory register cannot now be independently established or repaired retroactively. That requirement remains NOT VERIFIABLE; it is never marked PASS. The new independent intersection design and positive controls are post-original-result validation, not new evidence of actual offenses or identified label errors.

The remaining scientific limits are identification, sparse groups, finite scenario coverage, finite simulation/CI precision, fixed-trained-model sampling uncertainty, and absent external replication. These are explicitly disclosed; no uniquely fair deployable method is established. Every achievable mandatory computation in the available specification and current completion request has now been implemented, executed and tested, subject to the matrix's historical NOT VERIFIABLE item. This assessment does not invent an unavailable external rubric.

### Reproduction and deliverables

Run `python -m compas_fairness.completion`, then `python -m scripts.completion_report`, `python -m pytest`, and `python scripts/check_results.py` from the project directory with the pinned environment. These commands rerun only the added analyses, not original model training. Full original reproduction remains documented in README. Content-addressed model cache checks now include input values, ordered splits, model/data code and dependency pins, and reject modified checkpoints. Append-only stage history captures the exact CLI arguments, config and code fingerprints for new CLI executions. Historical missing shell transcripts remain unavailable, not backfilled as invented logs.

Figures: `figures/completion/intersection_reversals.*` shows the two independent-parameter designs; `reversal_detection.*` shows method-pair detection sensitivity and false-reversal frequency with Monte Carlo intervals. The latter uses method 0 rows only because detection is a pair-level statistic repeated on both method rows; it does not double the simulation sample count.

### Completion validation outcome

The full suite passed **40 tests**, with zero failures/errors/skips and one upstream pgmpy deprecation warning (`results/completion/tests.xml`). An independent scalar solve checked all **163,850** added intersection comparisons and their ranking flags; all 60 simulation-summary rows matched their retained replicate rows and Wilson intervals (`results/completion/validation.json`). Original and new artifact validation passed. A temporary-copy CLI smoke check reused the content-verified cache without training and reproduced every saved prediction while leaving production outputs untouched (`results/completion/cache_smoke.json`). Original 14 scientific figures remain unchanged; two completion figure sets were added. The branch was reconciled with the merged PR #1 through a regular merge of origin/main, preserving both histories.
