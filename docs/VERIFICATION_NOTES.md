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
