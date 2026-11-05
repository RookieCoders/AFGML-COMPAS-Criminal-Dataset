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
