# Cohort reproduction report

Source notebook: ProPublica Compas Analysis.ipynb, cells 2–4, 8–13 and 21–23. Pinned commit and raw checksums are in data/raw/provenance.json.

| filter | n |
| --- | --- |
| released | 7214 |
| screening <= window | 6623 |
| screening >= -window | 6172 |
| valid recidivism flag | 6172 |
| not ordinary traffic | 6172 |
| valid score category | 6172 |
| person deduplication: first released ID | 6172 |

The expected 7,214 raw and 6,172 filtered rows are reproduced. Duplicate released IDs: 0; duplicate person keys among eligible records: 0. Person identity uses normalized first/last/DOB. Missing identities stop preprocessing; no person linkage based on outcomes is used. Original records are unchanged.

Notebook demographic counts are reproduced: African-American 3,175; Caucasian 2,103; Hispanic 509; Asian 31; Native American 11; Other 343. Female 1,175; Male 4,997. Split counts are 3,703/1,234/1,235; person manifests are retained. Missingness for every raw column, invalid general score counts, target class balance and feature missingness are in results/data_quality.json.

The adjusted logistic coefficient for African-American versus Caucasian membership in the notebook's high-score regression is 0.47720698, matching published .47721. No discrepancy beyond printed rounding was found. This regression conditions on recorded two-year recidivism to audit released score associations; it is not a predictive model and is not interpreted causally.

## Full-cohort released-score audit

Adverse decision is general COMPAS decile >=5 (Medium/High). Rates are conditional on recorded outcomes. The following audit uses all 6,172 eligible people; the learned-model comparisons use the held-out test people instead.

| axis | group | n | tn | fp | fn | tp | fpr | tpr | fnr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| race | African-American | 3175 | 873.0000 | 641.0000 | 473.0000 | 1188.0000 | 0.4234 | 0.7152 | 0.2848 |
| race | Asian | 31 | 21.0000 | 2.0000 | 3.0000 | 5.0000 | 0.0870 | 0.6250 | 0.3750 |
| race | Caucasian | 2103 | 999.0000 | 282.0000 | 408.0000 | 414.0000 | 0.2201 | 0.5036 | 0.4964 |
| race | Hispanic | 509 | 258.0000 | 62.0000 | 110.0000 | 79.0000 | 0.1938 | 0.4180 | 0.5820 |
| race | Native American | 11 | 3.0000 | 3.0000 | 0.0000 | 5.0000 | 0.5000 | 1.0000 | 0.0000 |
| race | Other | 343 | 191.0000 | 28.0000 | 82.0000 | 42.0000 | 0.1279 | 0.3387 | 0.6613 |

The story also reports error rates from a different survival-derived cohort using cox-parsed.csv and truth_tables.py. Those should not be equated with rates from this notebook cohort or the held-out test split. This project reproduces the requested notebook cohort and adjusted score-association audit, and reports its own confusion matrices explicitly. It does not claim to reproduce the separate survival analysis. Small groups and zero class denominators are flagged in the held-out group tables; they are not reliable comparative evidence.
