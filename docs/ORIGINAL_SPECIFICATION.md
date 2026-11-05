# CODEX MASTER PROMPT — COMPLETE COMPAS FAIRNESS RESEARCH IMPLEMENTATION

## ROLE

You are an expert machine-learning research engineer, Bayesian probabilistic modeler, fairness researcher, and Python developer.

Your task is to **implement, execute, validate, and document a complete reproducible research project** titled:

**When Noisy Outcomes Reverse Criminal-Justice Fairness Conclusions**

Do not stop after creating a project plan, writing pseudocode, or generating skeleton files. Implement the actual code, run experiments, debug failures, generate results, and produce the final research deliverables.

Work autonomously wherever possible. Make reasonable engineering decisions without repeatedly asking for confirmation. Ask questions only when a genuinely blocking ambiguity cannot be resolved from the specification or available sources.

The literature review and initial research specification have already been provided. Do not spend time writing a redundant literature review. However, verify source-specific methodological details needed for correct implementation.

## 1. RESEARCH OBJECTIVE

Investigate whether fairness improvements from observed-label post-processing remain stable when recorded recidivism is treated as a potentially noisy measurement of a hypothetical latent outcome.

Use ProPublica's released COMPAS two-year recidivism data.

Definitions:

- A: Recorded demographic group membership.
- X: Permissible pre-outcome covariates.
- Y_tilde: Observed recorded two-year recidivism.
- Y_star: Hypothetical latent outcome, used only for sensitivity modeling.
- D: Binary adverse high-risk classification, with D=1 representing high risk.

The project must determine whether two prediction or mitigation methods can exchange fairness rankings under explicitly specified group-dependent label-error assumptions.

Y_star is not identified from the dataset. Never describe it as recovered criminal behavior or actual offenses.

The project is strictly a retrospective audit, not a recommendation for detention, sentencing, policing, or deployment.

## 2. REQUIRED DATA

Primary source:

https://github.com/propublica/compas-analysis

Tasks:

1. Download the relevant released COMPAS two-year recidivism data.
2. Obtain and inspect the relevant ProPublica preprocessing and analysis notebooks.
3. Reproduce the documented cohort restrictions.
4. Record original and filtered sample sizes.
5. Examine missing values, invalid records, class balance, demographic distributions, and duplicate people.
6. Use person-level deduplication or grouped splitting as appropriate.
7. Prevent leakage between training, validation, and testing.
8. Exclude post-outcome and inappropriate future-information variables.
9. Maintain the released COMPAS score as an independent audit baseline rather than routinely including it as a predictive feature.
10. Reproduce a documented observed-label fairness audit and investigate any discrepancy.

Do not silently alter cohort restrictions to obtain preferred results.

Preserve raw data and maintain a reproducible preprocessing pipeline.

## 3. REQUIRED TECHNOLOGIES

Use Python 3.11 or later where compatible.

Preferred libraries:

- pandas
- NumPy
- SciPy
- scikit-learn
- Fairlearn
- pgmpy
- matplotlib
- seaborn
- pytest
- joblib

Optional:

- PyMC, only if necessary.
- tqdm for progress reporting.
- PyYAML for configurations.

Use existing reliable libraries rather than unnecessarily reimplementing established algorithms.

Create a clean, modular Python project with pinned dependencies, configuration files, reusable functions, logging, tests, and reproducible random seeds.

## 4. PREDICTIVE MODELS

Implement:

1. Logistic regression.
2. Gradient-boosted trees.
3. A Bayesian-network baseline that treats observed recidivism as error-free.
4. An independent audit of the released COMPAS risk score.

Use a person-disjoint train/validation/test split, initially targeting 60/20/20 where feasible.

Perform appropriate hyperparameter selection without using the final test set.

Calculate:

- AUROC.
- Balanced accuracy.
- Accuracy where useful.
- TPR.
- FPR.
- FNR.
- Precision.
- Log loss.
- Brier score.
- Calibration curves.
- Group-specific confusion matrices.

Document how continuous scores become binary adverse decisions.

## 5. FAIRNESS MITIGATION

Implement:

1. Unmitigated predictive baselines.
2. Reweighing based on observed labels.
3. Equalized-odds post-processing based on observed labels.

Use Fairlearn or a verified equivalent implementation.

Fit mitigation methods using appropriate training/validation partitions.

Avoid test-set leakage.

For randomized equalized-odds post-processing, use reproducible random seeds and document whether reported metrics use sampled decisions or expected confusion rates.

Compare methods under the same evaluation cohort and fairness definitions.

Evaluate race and sex separately, then race-by-sex intersectional groups.

Report sparse cells explicitly.

## 6. FAIRNESS DEFINITIONS

Observed equalized odds:

For each group a, compute:

TPR_a = P(D=1 | Y_tilde=1, A=a)

FPR_a = P(D=1 | Y_tilde=0, A=a)

For two groups a and b:

DeltaEO(a,b) = max(
    abs(TPR_a - TPR_b),
    abs(FPR_a - FPR_b)
)

For multiple groups, use the maximum disparity across all valid group pairs.

Apply the same definition to scenario-dependent latent-outcome metrics.

Also report:

- Group-specific TPR and FPR.
- Intersectional disparities.
- Observed-label group calibration.
- Predictive-performance tradeoffs.

Do not confuse classifier error rates with outcome-recording error rates.

## 7. BAYESIAN MEASUREMENT MODEL

Implement a Bayesian measurement model connecting:

A, X, Y_star, Y_tilde, and D.

Draw the measurement DAG.

Explain which variables influence the hypothetical latent outcome and which influence the recording process.

Define group-specific outcome-label errors:

alpha_a = P(Y_tilde=1 | Y_star=0, A=a)

beta_a = P(Y_tilde=0 | Y_star=1, A=a)

The primary model assumes:

Y_tilde is conditionally independent of X and D given Y_star and A.

State and test the implications of this assumption.

Define the measurement matrix:

M_a = [
    [1-alpha_a, beta_a],
    [alpha_a, 1-beta_a]
]

Observed prevalence:

q_a = P(Y_tilde=1 | A=a)

Scenario-dependent latent prevalence:

pi_a = (q_a-alpha_a)/(1-alpha_a-beta_a)

Implement this relationship and its feasibility constraints.

Use variable elimination in a small discrete Bayesian network.

Cross-check variable-elimination outputs against direct enumeration.

Do not claim the latent outcome or measurement-error rates are identified from COMPAS.

## 8. FEASIBILITY CHECKER

This is a critical component.

For each demographic group and candidate measurement scenario:

1. Validate alpha and beta are legitimate probabilities.
2. For the primary informative-label model, require alpha+beta&lt;1.
3. Reject singular or numerically unstable measurement matrices.
4. Calculate implied latent prevalence.
5. Reject invalid latent prevalence.
6. Construct observed joint decision/outcome probability vectors.
7. Invert the measurement matrix to recover scenario-dependent latent joint probabilities.
8. Verify all recovered cells are nonnegative within a declared numerical tolerance.
9. Verify normalization and reconstruction accuracy.
10. Reject incompatible scenarios rather than clipping materially invalid probabilities.
11. Record why each scenario was rejected.
12. Verify feasibility for every method being compared.
13. Use a common feasible scenario set for pairwise comparisons.
14. Treat zero latent-class denominators as undefined metrics, not zero.

Write automated tests for valid, invalid, singular, and boundary cases.

## 9. SENSITIVITY ANALYSIS

Implement grid-based sensitivity analysis over group-specific alpha and beta.

Begin with a configurable exploratory grid:

alpha, beta in [0, 0.20], step 0.025.

This is an initial computational configuration, not a claim that these error rates are empirically plausible.

Document and justify the primary sensitivity region before inspecting final conclusions.

Support:

- Equal noise across groups.
- Unequal noise across groups.
- Narrower feasible regions.
- Broader feasible regions.
- Alternative grid resolutions.
- Race-specific scenarios.
- Sex-specific scenarios.
- Intersectional scenarios where statistically supportable.

Avoid uncontrolled combinatorial explosion for many groups. Use documented grid slices, coarse-to-fine strategies, or structured parameterizations when needed.

For each feasible scenario:

1. Calculate latent-label joint decision/outcome probabilities.
2. Calculate scenario-dependent TPR and FPR.
3. Calculate equalized-odds disparities.
4. Calculate fairness rankings for prespecified method pairs.
5. Determine whether the observed ranking remains stable, reverses, or becomes tied.
6. Store all metrics and feasibility diagnostics.

Define:

R(s) = DeltaEO_method1(s) - DeltaEO_method2(s)

A strict reversal occurs when R(s) has the opposite sign from the observed-label ranking, outside a prespecified numerical tie tolerance.

Calculate:

- Minimum scenario-dependent EO gap.
- Maximum scenario-dependent EO gap.
- Difference in EO gaps between methods.
- Number of feasible scenarios.
- Number of reversed scenarios.
- Fraction of feasible grid scenarios with reversals.
- Stable-ranking regions.
- Reversal regions.
- Tie regions.

The reversal fraction is a grid sensitivity summary, not a probability unless a defensible probability distribution over scenarios is specified.

Generate sensitivity maps and feasibility maps.

Identify and explain representative reversal mechanisms.

Do not fabricate reversals if none are observed.

## 10. SYNTHETIC VALIDATION

Simulation is mandatory.

Construct a synthetic data-generating process with known:

- Group membership A.
- Covariates X.
- Latent outcome Y_star.
- Observed outcome Y_tilde.
- Decisions D.
- Group-specific label-error rates.

Generate both equal-noise and unequal-noise scenarios.

Include controlled group differences in prevalence and prediction performance.

Run the sensitivity procedure using only the simulated observed labels.

Compare its results against known generating latent outcomes.

Measure:

- Recovery error.
- Bias.
- RMSE.
- Reversal-detection accuracy.
- Feasibility-checker accuracy.
- Coverage of reported sensitivity bounds.
- Coverage of sampling-confidence procedures where applicable.

Initially use multiple sample sizes, such as 1,000, 5,000, and 10,000, and a configurable number of simulation repetitions.

Test violations of class-conditional noise by making recording errors depend on covariates within demographic groups.

Measure how assumption violations affect recovery and coverage.

Distinguish population sensitivity-set coverage from sampling-confidence-interval coverage.

The known generating parameter scenario should reconstruct the generating latent metrics up to sampling variability when the model assumptions hold.

## 11. MAIN EXPERIMENTS

Execute all mandatory experiments:

Experiment 1:
Reproduce a documented COMPAS observed-label audit.

Experiment 2:
Compare unmitigated and mitigated models against observed recorded recidivism.

Experiment 3:
Sweep the preregistered feasible group-dependent outcome-error region.

Experiment 4:
Use synthetic simulation to validate recovery and coverage.

Experiment 5:
Identify stable and reversed method rankings and explain representative mechanisms.

Save machine-readable results for every experiment.

## 12. REQUIRED ABLATIONS

Run:

1. Equal label noise across groups.
2. No measurement layer, using observed outcomes directly.
3. Point-estimate analysis versus sensitivity ranges.

Explain how each ablation changes conclusions.

## 13. ROBUSTNESS TESTS

Run:

1. Alternative feasible noise regions.
2. Alternative grid resolutions.
3. Age adjustment.
4. Reasonable cohort-filter variations.
5. Alternative decision thresholds.
6. Race-only analysis.
7. Sex-only analysis.
8. Intersectional analysis.
9. Randomized post-processing sensitivity.
10. Violations of class-conditional noise in simulation.

Where a test is impossible or statistically unreliable, document the reason rather than inventing results.

## 14. STATISTICAL VALIDATION

Implement paired person-level bootstrapping.

All methods must use the same resampled people within each bootstrap replicate.

Use an initially configurable target of 1,000 bootstrap replicates.

Calculate uncertainty intervals for:

- Observed predictive metrics.
- Observed fairness metrics.
- Scenario-dependent fairness metrics at selected fixed feasible scenarios.
- Paired differences between methods.

Handle infeasible bootstrap replicates and undefined denominators explicitly.

Report sampling uncertainty separately from uncertainty about measurement assumptions.

Do not label a sensitivity range as a confidence interval.

## 15. REQUIRED FIGURES

Generate publication-quality figures, including:

1. Measurement DAG.
2. Cohort-filtering flow diagram.
3. Group outcome distributions.
4. Observed-label fairness comparison.
5. Predictive-performance comparison.
6. Calibration curves.
7. Feasibility maps.
8. Sensitivity heatmaps.
9. Ranking-reversal maps.
10. Scenario-dependent EO-gap ranges.
11. Simulation recovery-error plots.
12. Simulation coverage plots.
13. Ablation comparison plots.
14. Robustness comparison plots.

Use accurate labels, units, captions, and reproducible plotting scripts.

## 16. REQUIRED OUTPUTS

Produce:

- Complete working Python source code.
- Dependency file.
- README with setup and execution commands.
- Dataset provenance documentation.
- Data dictionary.
- Cohort reproduction report.
- Baseline predictive results.
- Fairness mitigation results.
- Measurement-assumption register.
- Measurement DAG.
- Bayesian-network implementation.
- Feasibility checker.
- Sensitivity engine.
- Synthetic simulation framework.
- Statistical validation outputs.
- Ablation and robustness results.
- All required figures.
- Machine-readable experiment tables.
- Final research audit report.
- Automated tests.

The final report must clearly separate:

A. Empirically observed facts.

B. Results conditional on hypothetical measurement assumptions.

C. Claims that cannot be established from the available data.

## 17. IMPLEMENTATION QUALITY

Follow these requirements:

- Modular and readable Python code.
- Type hints where useful.
- Docstrings for important functions.
- Configuration-driven experiments.
- Reproducible seeds.
- Deterministic behavior where possible.
- Clear logging.
- Progress indicators for long experiments.
- Automated tests.
- No hardcoded fabricated results.
- No unnecessary external dependencies.
- No silent exception suppression.
- No silent clipping of invalid probabilities.
- No train/test leakage.
- No replacement of failed experiments with invented outputs.

Optimize expensive sensitivity sweeps using vectorized NumPy operations and caching where appropriate.

Do not sacrifice mathematical correctness for speed.

## 18. EXECUTION STRATEGY

Work in the following order:

Stage 1: Set up the repository and reproduce the COMPAS observed-label audit.

Stage 2: Implement predictive baselines and fairness mitigation.

Stage 3: Implement and independently test the measurement model and feasibility checker.

Stage 4: Implement synthetic validation and verify recovery at known generating parameters.

Stage 5: Implement and execute the main sensitivity analysis.

Stage 6: Execute ablations, robustness tests, and statistical validation.

Stage 7: Generate figures, tables, documentation, and the final report.

At each stage:

1. Write the required code.
2. Run it.
3. Inspect actual outputs.
4. Debug errors.
5. Run relevant tests.
6. Save results.
7. Continue to the next stage.

Do not stop after planning a stage.

## 19. RESOURCE AND TIME EFFICIENCY

Use the available computational resources efficiently.

First run small smoke tests to verify the entire pipeline.

Then run full experiments.

Use configurable experiment sizes so expensive simulations can be resumed or rerun.

Avoid unnecessary repeated model training when the same fitted predictions can be reused.

Checkpoint intermediate outputs.

If computation is interrupted, preserve completed results and provide exact commands to resume.

If time or resources are insufficient, prioritize a correct end-to-end implementation over cosmetic enhancements.

Do not claim an experiment was executed unless it actually ran.

## 20. COMPLETION CRITERIA

The project is complete only when:

1. The documented observed-label COMPAS audit is reproduced or discrepancies are explained.
2. Predictive and fairness baselines are implemented and evaluated.
3. The measurement model is mathematically validated.
4. The feasibility checker passes automated tests.
5. Synthetic experiments validate the sensitivity procedure.
6. The main feasible sensitivity analysis has been executed.
7. Ranking stability or reversals have been measured.
8. Ablation and robustness experiments have been executed.
9. Statistical uncertainty has been evaluated.
10. All figures and tables are generated from actual results.
11. The final audit report is written.
12. The entire project can be reproduced from documented commands.

At the end, provide:

- A concise summary of completed work.
- The actual experimental findings.
- The location of all deliverables.
- Commands to reproduce the experiments.
- Test results.
- Any remaining limitations or incomplete tasks.

## FINAL INSTRUCTION

**Begin implementing the project immediately.**

Do not respond with another research proposal or lengthy explanation of what you intend to do.

Inspect the workspace, establish the environment, obtain the data, and start writing and executing code.

Continue through the stages autonomously, validating results as you proceed.

Never invent findings, claim unexecuted experiments are complete, or misrepresent hypothetical latent outcomes as observed criminal behavior.