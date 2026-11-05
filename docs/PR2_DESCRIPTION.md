# Complete and verify all remaining COMPAS Problem 7 analyses

Complete the remaining computational requirements on top of the verified corrections, preserving the original exploratory outputs and merged PR #1 history.

- Add independently configurable recording errors for four race-by-sex groups, with two reproducible 8D Sobol designs, pairwise feasibility and 163,850 comparisons.
- Add 6,000 positive, negative and zero-noise boundary simulation datasets across sample size, imbalance and error strength. Report detection sensitivity, false reversals, recovery, generating-scenario compatibility, two coverage measures and Monte Carlo intervals.
- Preserve the exact original specification and provide clause-by-clause traceability. The supplied text requires a documented observed-label audit, not a separate Cox analysis. Historical original preregistration timing remains unverifiable; new analyses have a prospectively committed protocol.
- Add cache integrity/input guards and append-only CLI execution provenance. Update the existing final report, figures, assumptions, status and requirements matrix.

Validation: 40 tests pass; independent linear solves verify all 163,850 added intersection comparisons; all 60 simulation summaries verified from replicate rows; original and completion artifact validation pass; cached-model CLI smoke reproduces every saved prediction without retraining. Original models and production bootstrap were not rerun.

Limits: finite scenario coverage and simulation precision; measurement errors and hypothetical latent outcomes are not identified; no deployment recommendation. The original pre-analysis timing cannot be repaired retroactively and is not marked PASS.
