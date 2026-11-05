# Project status for independent audit

This archive packages existing research outputs. No experiments were rerun for packaging. It records the final retained state, not an external preregistration or independent replication.

## Implemented components

- Immutable-source data fetch/checksum verification, notebook cohort filtering, data-quality summaries, identity checks and person-disjoint partitions.
- Training-only preprocessing; validation selection for logistic regression and histogram gradient-boosted trees; discretized, Laplace-smoothed Bayesian-network baseline using pgmpy variable elimination; independent released COMPAS score audit.
- Separate observed-label reweighing and Fairlearn equalized-odds policies for race, sex and intersections, with explicit unsupported-group fallbacks.
- Predictive metrics, group confusion matrices, calibration bins, observed EO gaps, decision thresholds, expected randomized decisions and ten sampled policy seeds.
- Group-specific measurement matrices, prevalence inversion, joint-cell inversion, informative-label constraints, numerical feasibility/reconstruction checks and explicit undefined metrics.
- A small generative measurement Bayesian network with independent direct-enumeration validation.
- Vectorized common-feasibility sensitivity comparisons, ranking/tie classification, per-scenario diagnostics and representative recovered hypothetical joint cells.
- Synthetic known-population simulation, exact enumeration, class-conditional and covariate-dependent recording, recovery/bias/RMSE, feasibility agreement, reversal detection and distinct sensitivity/CI coverage measures.
- Paired person-level bootstrap for predictive, fairness and group rates, fixed-scenario gaps and paired method differences.
- Ablations, robustness, 14 figure sets, configuration-driven CLI, tests, artifact validation and final reporting.

## Experiments actually executed

1. Notebook cohort and score-association regression reproduction; full-cohort released-score confusion audit.
2. Common held-out predictive and mitigation comparison. Training: 3,703; validation: 1,234; testing: 1,235 people.
3. Primary measurement grid alpha,beta in {0,.025,...,.20}; equal-noise grid; narrower [0,.1], broader [0,.3], and coarse .05 grids. Race, sex and supported intersections; LR compared with reweighed LR, EO LR, GBT, BN and COMPAS. 75 saved tables containing 154,395 scenario comparisons (not all distinct scenarios).
4. 270 synthetic datasets: 30 repetitions x sample sizes 1,000/5,000/10,000 x equal/unequal/covariate-dependent recording settings. Two methods per dataset. 100 sampling-bootstrap replicates per synthetic dataset.
5. Stable, tied and reversed rankings and representative inverse joint cells.
6. 1,000 paired test-person bootstrap replicates with fixed fitted models and prespecified identity, equal-.05 and contrast measurement points.
7. Identity-measurement, equal-noise, point-versus-range ablations; alternative regions/resolutions; age standardization; removal of age; screening windows 15/60 days; decision thresholds .35/.5/.65; race/sex/intersection analyses; ten sampled EO seeds; covariate-dependent error violations.
8. Isolated end-to-end smoke run in /tmp/compas-smoke-fs2apur1 with configs/smoke.json. Its outputs are separate from the full outputs packaged here.

Execution evidence is results/run.log, results/run_manifest.json, stage-specific tables, results/tests.xml and results/artifact_validation.json. The log is a retained application log, not a complete shell transcript; early failed development invocations were not all captured in it.

## Exact commands used

Working directory for production stages: /workspace/AFGML_COMPAS_Criminal_Dataset. Interpreter: /workspace/compas-venv/bin/python (Python 3.12.14). Commands below were executed during development/validation; some stages were repeated after fixes. Their listing does not imply that every intermediate attempt succeeded.

```bash
# Initial source and dependency setup:
git clone --depth 1 https://github.com/propublica/compas-analysis.git /workspace/compas-source
python -m venv /workspace/compas-venv
/workspace/compas-venv/bin/pip install numpy pandas scipy scikit-learn fairlearn pgmpy matplotlib seaborn pytest joblib pyyaml nbformat
/workspace/compas-venv/bin/pip freeze > requirements.txt

# From the project directory, production stages and repeated validation:
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages audit,models,sensitivity --reuse-models
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages simulation
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages models,sensitivity,bootstrap,robustness
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages bootstrap,robustness --reuse-models
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages simulation,bootstrap,robustness,report --reuse-models
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages models,report --reuse-models
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages audit,sensitivity,report --reuse-models
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages report
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --stages audit,report
/workspace/compas-venv/bin/python scripts/fetch_data.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m pytest -q --junitxml=results/tests.xml
/workspace/compas-venv/bin/python scripts/check_results.py

# Smoke invocation, working directory /tmp/compas-smoke-fs2apur1:
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /workspace/compas-venv/bin/python -m compas_fairness.run --config configs/smoke.json
```

The source was copied from the pinned upstream clone into data/raw. Provenance and exact source checksums are in data/raw/provenance.json. requirements.txt captures the installed dependency versions, rather than versions selected before installation. For independent reproduction, follow README.md and install those pinned versions. The single default command below is a reproduction command, not a claim that the original full experiment ran as one invocation:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m compas_fairness.run
python -m pytest -q
python scripts/check_results.py
```

## Tests, failures and corrections

Final retained JUnit result: 19 tests passed, 0 failures, 0 errors, 0 skipped. One pgmpy upstream deprecation warning was reported. Tests cover cohort/regression reproduction, identity-disjoint splits, measurement inversion and boundary/invalid cases, common feasibility, VE/enumeration agreement, exact synthetic population recovery, marginal-preserving violations, paired bootstrap identity and grid boundaries.

Artifact validation passed: 75 sensitivity tables, 154,395 comparisons, 270 synthetic datasets, 1,000 bootstrap replicates, 1,235 test people, 14 PNG/PDF/SVG figure sets and source hashes. Existing figures/report were generated from results. No expensive computations were repeated for this archive.

Earlier development attempts failed on degenerate Fairlearn validation labels in sparse groups, empty training reweighing cells and read-only pandas/NumPy boolean arrays. Corrections explicitly restrict supported EO fitting groups and retain baseline decisions elsewhere, use unit reweighing weights for unsupported groups, and copy mutable masks. A decision-selection probability was initially used as an EO risk score; final outputs retain LR risk probabilities for score metrics and separate expected policy decisions. Initial plotting cache/font warnings were resolved or benign; non-scalable emoji fonts were not required. Final retained results supersede intermediate outputs. Early complete traceback/console records are not included where no log was retained.

## Data and cohort

Source: ProPublica compas-analysis, commit bafff5da3f2e45eca6c2d5055faad269defd135a. Raw release: 7,214 rows, 53 parsed columns. The CSV repeats decile_score and priors_count headers; pandas disambiguates duplicates. Raw data are retained unchanged.

Sequential filtering: 7,214 released; 6,623 after screening offset <=30; 6,172 after offset >=-30; no additional removals by is_recid!=-1, charge degree!=O, score category valid, or person deduplication. Eligible duplicate IDs/person keys: zero. Full cohort race counts: African-American 3,175; Caucasian 2,103; Hispanic 509; Asian 31; Native American 11; Other 343. Female 1,175; Male 4,997. Class balance, missingness, sensitivity-cohort sizes, class counts and sparse flags are in the saved tables/JSON.

## Key numerical findings

- Notebook adjusted African-American/Caucasian high-score coefficient reproduced as 0.4772069788 versus published 0.47721; odds ratio 1.611567. This score-association audit is distinct from EO error disparities and from the story's survival-derived truth table.
- Held-out AUROC: LR 0.718697; GBT 0.719872; BN 0.702859; independently calibrated COMPAS baseline 0.722344. Balanced accuracy: LR 0.654977; GBT 0.667583; BN 0.650612; COMPAS 0.663879.
- Sex EO disparity: observed LR 0.1739905 versus EO policy 0.0291140. Strict ranking reversals occur in 2,068/6,561 feasible primary scenarios (31.5196%). Race LR-versus-EO has zero primary reversals. Fractions summarize a chosen grid, not probabilities.
- Example sex scenario: (alpha,beta) Female=(.175,.1), Male=(.15,0). Hypothetical EO changes to LR 0.1161236 versus EO policy 0.1537424; all inverse cells are feasible.
- The paired observed sex EO(policy)-EO(LR) 95% interval is [-0.2284, 0.0051], including zero. The observed test-sample advantage does not establish a population ranking.
- At N=10,000 under unequal class-conditional noise, synthetic EO recovery RMSE is 0.013723 and 0.012847 for the two methods. Under marginal-preserving covariate-dependent violations, method-0 bias is -0.022543, RMSE 0.026335, sampling-CI coverage 20/30 (66.67%). Sensitivity coverage is a separate measure. Complete metrics are in simulation_summary.csv.

## Incomplete work and scope limits

The implemented configured research workflow executed and has retained outputs; this is not a claim that every possible interpretation of the original specification was exhaustively studied. The separate ProPublica survival/Cox truth-table analysis was not reproduced: the notebook cohort and adjusted score audit were reproduced instead. Intersectional sensitivity uses race-specific noise profiles shared across sexes, not a full eight-dimensional error grid. Sparse groups cannot support reliable fitted mitigation/estimation; fallbacks and exclusions are explicit. The assumption register was specified during implementation before sensitivity execution, not externally preregistered. There is no external replication, deployment validation, causal identification or independent review. The exact locked environment was tested on Python 3.12/Linux, not every Python >=3.11 platform. No Git commit or GitHub push was completed.

## Methodological limitations

Hypothetical Ystar, recording errors and actual offense incidence are not identified from COMPAS. Feasibility is necessary compatibility, not proof of class-conditional independence or empirical plausibility. Historical covariates can encode enforcement/recording biases. Source follow-up/censoring decisions are inherited, not rebuilt. Name/DOB linkage cannot rule out all identity errors. Small groups and intersections have unstable estimates; primary race contrasts cover Black/white groups only. EO uses expected randomized decisions; sampled decisions vary. COMPAS decile probability calibration uses validation data and is separate from its released binary score audit. Bootstrap is conditional on fixed fitted models, thresholds and fixed error points; it omits training/model-selection and error-assumption uncertainty. Percentile intervals and multiple comparisons are exploratory and unadjusted. Thirty simulation repetitions give substantial Monte Carlo uncertainty. Sensitivity bounds are not confidence intervals and reversal fractions are not posterior probabilities; near-tied observed rankings are especially fragile. This is retrospective research, not a recommendation for detention, sentencing, policing or deployment.

## Archive contents and exclusions

Includes source, all tests/configurations/documentation, reports, public raw dataset and upstream analysis notebook, provenance/checksums, all substantive experiment tables (including compressed replicate/scenario outputs), figures, retained execution log/JUnit evidence, pinned requirements and safe environment metadata. Raw source includes public identifying records; it is not anonymized or secret credential material.

Excludes virtual environments, caches, bytecode, Git internals, credential/configuration secrets and the regenerable 4.4-MB results/models.joblib checkpoint. The checkpoint is not needed to inspect predictions/results; rerun model fitting before using --reuse-models in a fresh extraction. The archive does not contain /workspace/compas-venv. No environment variable values or credential files were inspected or exported. Archive integrity is recorded in ARCHIVE_MANIFEST.json, and an external SHA256 sidecar covers the ZIP.
