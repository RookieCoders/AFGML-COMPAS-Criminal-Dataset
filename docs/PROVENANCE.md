# Dataset and source provenance

Source: https://github.com/propublica/compas-analysis
Pinned source commit: bafff5da3f2e45eca6c2d5055faad269defd135a
Data: compas-scores-two-years.csv (7,214 released records, 53 columns).
Methodology source inspected: Compas Analysis.ipynb, cells 2–4, 8–13, 19–23. Its R cohort code and printed outputs are preserved locally in data/raw. truth_tables.py is preserved to document that the story's survival-derived truth-table cohort is a distinct analysis. We reproduce the notebook's score-association regression and demographics, not silently substitute this cohort for the story's survival truth table. No R execution is required for the equivalent statsmodels GLM reproduction.

The cohort excludes screening/arrest offsets outside [-30,30], is_recid=-1, charge degree O, and score_text=N/A. Missing filter fields fail the relevant restriction. pandas is configured to preserve literal N/A so the notebook restriction is explicit. Raw source is unchanged, verified by SHA256 in provenance.json. The released binary two_year_recid outcome is retained; we do not rebuild time at risk, undo the source's follow-up decisions, or claim a new censoring adjustment. Those upstream design choices limit the interpretation of recorded outcomes.

Identifiers, names, DOB, screening timestamps, jail dates, recidivism flags/counts and case details are not predictive features. Released ID is unique, and (first,last,dob) is checked for duplicate identities; duplicates would retain the smallest released ID. A SHA256 identity is used for splitting/output manifests; it is a linkage device, not anonymization. The public source contains identifying records; generated output avoids adding raw names. Age is derived from the release, not recomputed against the current date. Current/prior-history features may reflect historical enforcement practices and are not intrinsically fair or causally permissible merely because they predate follow-up.

Probability calibration of released COMPAS deciles is trained only on the validation split. The released score itself stays out of predictive feature matrices. No claim is made that deciles are probabilities.

Original ProPublica data/methodology attribution is retained. This project asserts no new license over the upstream public records.
