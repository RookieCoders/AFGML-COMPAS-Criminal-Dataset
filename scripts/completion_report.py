"""Create completion tables/figures/report addendum from existing computed outputs."""
from pathlib import Path
import pandas as pd
from compas_fairness.report import plt,sns,md_table

out=Path('results/completion');fig=Path('figures/completion');fig.mkdir(exist_ok=True)
i=pd.read_csv(out/'intersection_summary.csv');s=pd.read_csv(out/'reversal_control_summary.csv')
plt.figure(figsize=(8,4));sns.barplot(data=i,x='comparator',y='reversal_fraction',hue='maximum');plt.ylabel('Reversed fraction of common feasible Sobol points');plt.xlabel('Comparator with LR');plt.tight_layout()
for ext in ['png','pdf','svg']:plt.savefig(fig/f'intersection_reversals.{ext}',dpi=300)
plt.close()
fig2,axes=plt.subplots(1,3,figsize=(13,4),sharey=True)
for ax,kind in zip(axes,['positive','negative','boundary']):
    for key,v in s[(s.kind==kind)&(s.method==0)].groupby(['strength','group_probability']):
        v=v.sort_values('n');ax.errorbar(v.n,v.detection_fraction,yerr=[(v.detection_fraction-v.detection_mc_low).clip(lower=0),(v.detection_mc_high-v.detection_fraction).clip(lower=0)],marker='o',label=f'noise={key[0]}, P(A=0)={key[1]}')
    ax.set_title('Sensitivity' if kind=='positive' else kind+' false reversals');ax.set_xlabel('Sample size');ax.set_ylim(0,1.05)
axes[0].set_ylabel('Fraction and 95% Wilson Monte Carlo interval');axes[1].legend(fontsize=6);fig2.tight_layout()
for ext in ['png','pdf','svg']:fig2.savefig(fig/f'reversal_detection.{ext}',dpi=300)
plt.close(fig2)
text='''## Completion of outstanding achievable requirements

This section supersedes the earlier verification's remaining-work assessment without erasing its historical findings. The original available specification is preserved verbatim in `docs/ORIGINAL_SPECIFICATION.md`; there is no separate external Problem 7 rubric available. The original text asks for a documented observed-label audit (§2.10, §11 experiment 1, §20.1), not a mandatory Cox model. The reproduced notebook cohort and score-association audit satisfy that task. A separate survival model is an optional extension, not an unexecuted mandatory analysis. No event times or censoring values were fabricated.

### Independent intersectional recording parameters

`completion.independent_design` varies all eight alpha/beta coordinates for the four supported Black/white-by-sex groups, using scrambled Sobol points (seed 8172026). Each group's two rates can also be explicitly overridden through the function's `overrides` mapping; tests exercise that capability. The Sobol design has 16,384 points plus the identity, in each of [0,.2]^8 and [0,.3]^8. This reproducible space-filling design replaces exhaustive 9^8 enumeration, as permitted by original §9. It is not an empirical prior, an exhaustive grid, or a guarantee that narrow reversal pockets have been discovered. Each comparison checks all groups and both methods, rejects incompatible cells, and reports undefined metrics explicitly. The original restricted-slice outputs remain separate.

'''
text+=md_table(i[['maximum','comparator','scenarios','feasible','reversals','reversal_fraction','min_difference','max_difference']])+'\n\n'
text+='''Both methods use the same 1,087 supported test people. LR versus intersectional EO reverses in 508/13,287 feasible points of the broader design (3.8233%) and in zero points of the narrower design. These fractions summarize the sampling design, not population probabilities. All parameters, pairwise feasibility reasons, group rates, gaps, ties and classifications are retained in `results/completion/intersection_*.csv.gz`, with observed joint arrays in `intersection_observed_joints.json`. Latent joints are exactly reproducible by solving each stored group's measurement matrix against those observed joints.

### Finite-sample positive, negative and boundary controls

New simulations comprise 6,000 datasets: 200 repetitions for each of five population/noise cases, two group proportions (.5 and .2), and N=1,000/5,000/10,000. The positive and stable populations were selected by the prespecified deterministic population-only search (not from COMPAS outcomes); all parameters are saved in `control_populations.json`. Covariate X, hypothetical Ystar, recorded labels and two decisions are all represented in the generative cells. Positive cases use two error strengths (.5 and 1 times fixed group error profiles), negative cases are stable population rankings, and the zero-noise boundary has identical population decision mechanisms and a tied ranking. Classification uses the same 1e-4 tolerance. All methods share each simulated dataset.

Simulation counts are multinomial representations of individual categorical records. A paired multinomial person bootstrap is distributionally identical to resampling those same records; a regression test cross-checks expanded individuals against the cell representation. Each dataset uses 200 bootstrap replicates. Feasibility is common across both methods. Infeasible recovery is recorded and counts as a detection failure, rather than being silently dropped from sensitivity denominators. Wilson intervals quantify Monte Carlo uncertainty across independent datasets, not uncertainty about COMPAS measurement assumptions. Generating-scenario feasibility, generating-metric sensitivity-bound coverage, sampling-CI coverage, bias and RMSE are distinct saved outcomes. The known error point is included explicitly in the sensitivity evaluation; its feasibility rate does not establish the plausibility of any error assumption.

'''
compact=s[s.method==0][['kind','strength','group_probability','n','detection_fraction','detection_mc_low','detection_mc_high','bias','rmse']]
text+=md_table(compact)+'\n\n'
text+='''At N=10,000 positive-case sensitivity spans 50.5–94.5% across settings; negative-case false-reversal frequency spans 0–6%; zero-noise boundary false reversals are 0/200 in every configuration. These limitations are results of the validation, not reasons to alter the populations until they pass. Full per-method recovery and coverage tables are in `reversal_control_summary.csv`, with all replicate rows in `reversal_control_replicates.csv.gz`.

### Protocol timing and irreducible limitations

`docs/COMPLETION_PROTOCOL.json` was dated and committed (`d85de2b`) before the new experiments, with fixed seeds, designs, control-selection rules and precision targets. This is a prospective computational protocol for the added analyses, not externally registered human-subject research or retroactive preregistration of the original results. The original §11 experiment 3 calls its region “preregistered,” while §9 calls for exploratory configuration. Historical pre-analysis timing for the original exploratory register cannot now be independently established or repaired retroactively. That requirement remains NOT VERIFIABLE; it is never marked PASS. The new independent intersection design and positive controls are post-original-result validation, not new evidence of actual offenses or identified label errors.

The remaining scientific limits are identification, sparse groups, finite scenario coverage, finite simulation/CI precision, fixed-trained-model sampling uncertainty, and absent external replication. These are explicitly disclosed; no uniquely fair deployable method is established. Every achievable mandatory computation in the available specification and current completion request has now been implemented, executed and tested, subject to the matrix's historical NOT VERIFIABLE item. This assessment does not invent an unavailable external rubric.

### Reproduction and deliverables

Run `python -m compas_fairness.completion`, then `python -m scripts.completion_report`, `python -m pytest`, and `python scripts/check_results.py` from the project directory with the pinned environment. These commands rerun only the added analyses, not original model training. Full original reproduction remains documented in README. Content-addressed model cache checks now include input values, ordered splits, model/data code and dependency pins, and reject modified checkpoints. Append-only stage history captures the exact CLI arguments, config and code fingerprints for new CLI executions. Historical missing shell transcripts remain unavailable, not backfilled as invented logs.

Figures: `figures/completion/intersection_reversals.*` shows the two independent-parameter designs; `reversal_detection.*` shows method-pair detection sensitivity and false-reversal frequency with Monte Carlo intervals. The latter uses method 0 rows only because detection is a pair-level statistic repeated on both method rows; it does not double the simulation sample count.
'''
Path('docs/COMPLETION_NOTES.md').write_text(text)
# Replace only the addendum when updating, preserving the existing audit report.
p=Path('docs/FINAL_REPORT.md');original=p.read_text().split('## Completion of outstanding achievable requirements')[0];p.write_text(original+'\n'+text)
