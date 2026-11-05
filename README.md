# When Noisy Outcomes Reverse Criminal-Justice Fairness Conclusions

Reproducible retrospective COMPAS fairness audit. Hypothetical latent outcomes and recording errors are **not identified** by these data. This research is not a recommendation for criminal-justice deployment.

## Run

Python 3.12 was used; Python >=3.11 is intended, but the exact lock is validated on 3.12/Linux. From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/fetch_data.py       # checksum-verified pinned source; raw files also included
python -m pytest -q
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m compas_fairness.run
python scripts/check_results.py
```

In the prepared workspace the installed interpreter is `/workspace/compas-venv/bin/python`. No services, secrets, GPU or external database are required. Each task is already isolated; use the existing checkout and do not create a worktree unless requested. No environment configuration was changed or published by this research task.

The default command runs all five experiments, ablations, robustness, 1,000 paired bootstrap replicates, 270 synthetic datasets (30 repetitions × 3 sample sizes × 3 recording settings), and creates the report/figures. CPU threads are limited to avoid oversubscription. All random seeds and primary grid settings are in configs/full.json. Sensitivity tables are vectorized. Model selection never uses the test set.

For a quick executable pipeline check, use `--config configs/smoke.json`; outputs replace the current result tables, so run smoke checks in a temporary copy or regenerate the full results afterwards. Full results in this checkout used full.json.

## Resume / selected stages

```bash
python -m compas_fairness.run --stages audit,models
python -m compas_fairness.run --stages sensitivity --reuse-models
python -m compas_fairness.run --stages simulation
python -m compas_fairness.run --stages bootstrap,robustness --reuse-models
python -m compas_fairness.run --stages report
```

Each completed stage is retained. Synthetic simulation checkpoints per setting/sample-size can be reused if their run configuration matches. Model checkpoints are version-specific trusted local joblib files; never load untrusted pickle/joblib data. `--reuse-models` checks the cohort/split. Changing model code/dependencies requires retraining without this flag. No code changes or lock updates are needed to rerun. Fetching data requires the configured HTTPS proxy and TLS verification; offline computation works from retained raw files.

## Deliverables

- [Final audit report](docs/FINAL_REPORT.md): empirical facts, conditional results, and unidentifiable claims.
- [Assumption register](docs/ASSUMPTIONS.md): grids, estimands, pair comparisons, feasibility, uncertainty, sparse-group handling.
- [Provenance](docs/PROVENANCE.md), [data dictionary](docs/DATA_DICTIONARY.csv), data/raw/provenance.json: source commit, checksums and roles.
- compas_fairness/: cohort, models, metrics, measurement BN/inversion, vectorized sensitivity, simulation, paired uncertainty, robustness, reporting.
- results/predictive.csv, group_metrics.csv, observed_fairness.csv, calibration.csv: observed results and expected randomized confusion cells.
- results/sensitivity_summary.csv and sensitivity/*.csv.gz: every scenario's parameters, feasibility reason, group rates, latent prevalence, gaps and ranking. Pairwise common feasible sets; no invalid-cell clipping.
- results/representative_scenarios.json: representative valid inversions including recovered hypothetical joint cells.
- results/simulation.csv, simulation_summary.csv: known-population recovery, bias/RMSE, reversal detection, feasibility agreement and two different coverage measures.
- results/bootstrap*.csv*, predictive*intervals.csv: paired sampling uncertainty, conditional on fixed fitted models and fixed measurement scenarios.
- results/robustness.csv: thresholds, cohort windows, age, randomized-seed variation; narrower/broader/resolution/axis checks are in sensitivity_summary.csv.
- figures/: 14 PNG, PDF and SVG figures, with [captions](figures/CAPTIONS.md).
- tests/: independent mathematical checks, source reproduction, leakage/split guards and executable smoke validation.

Expected selection probabilities define EO policy decisions. Underlying LR outcome probabilities remain the score for calibration/log loss and AUROC; decision randomness is not mislabeled predictive risk. Reweighing and EO fit separate race, sex and intersection mitigations. Sparse validation groups retain baseline decisions and are explicitly recorded. Main sensitivity compares Black/white race groups, sex groups and supported Black/white intersections on a common cohort per comparison. The intersection grid shares race-specific errors across sexes, not an exhaustive eight-dimensional grid.

Sensitivity bounds are **not confidence intervals**. Reversal fractions are **not probabilities**. Bootstrap intervals condition on the fixed model fits; they omit training and measurement-assumption uncertainty. See the report for finite Monte Carlo precision and assumption-violation results.

Validation evidence: `results/tests.xml` records the automated tests; `results/artifact_validation.json` checks all 75 sensitivity tables, exact zero-error reconstruction, ranking signs, person partitions, repetition counts, figures and current source hashes. The original notebook cohort and score-association audit also have a separate [cohort report](docs/COHORT_REPORT.md).

Final verification: see [requirements matrix](docs/REQUIREMENTS_MATRIX.md), the final verification section of [the same audit report](docs/FINAL_REPORT.md), and results/verification/. The additional 200-repetition simulation has its own configuration and results/verification_simulation/ outputs; it does not replace the original exploratory outputs.
