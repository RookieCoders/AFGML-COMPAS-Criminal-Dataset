# Git delivery

The research branch preserves the upstream initial commit and README (docs/UPSTREAM_README.md). PROJECT_STATUS.md describes the earlier archive snapshot; its statement that no commit/push was completed refers to that snapshot.

For Git delivery, the public raw CSV, local model checkpoint, ZIP archives, caches, environments, credentials and archive-specific manifest are excluded. All substantive scenario/replicate result tables, predictions, figures, reports, provenance and execution evidence are retained. Fetch the checksum-verified public CSV with `python scripts/fetch_data.py` before running data-dependent checks. Refit models before requesting `--reuse-models` in a fresh clone. Existing local raw data and the downloadable ZIP remain untouched.

No research experiments were rerun for this Git delivery. Source and generated outputs retain their existing bytes. Upstream notebook and generated SVG whitespace is retained as produced.
