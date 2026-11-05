"""Generate figures and an evidence-based audit report from completed result tables."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'compas-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'compas-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx


def md_table(d):
    d=d.copy()
    for c in d:
        if pd.api.types.is_float_dtype(d[c]):d[c]=d[c].map(lambda x:f'{x:.4f}')
    return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in d.itertuples(index=False,name=None))


def create_report(out,figdir):
    figdir.mkdir(exist_ok=True);sns.set_theme(style='whitegrid',context='paper',font_scale=1.1)
    captions=[]
    manifest=json.loads((out/'run_manifest.json').read_text())
    cfg=manifest['config']
    sim_reps=pd.read_csv(out/'simulation.csv').rep.nunique()
    bootstrap_reps=pd.read_csv(out/'bootstrap_intervals.csv').eval('valid + invalid').max()
    def save(name,caption):
        plt.tight_layout()
        for ext in ['png','pdf','svg']:plt.savefig(figdir/f'{name}.{ext}',dpi=300,bbox_inches='tight')
        plt.close();captions.append(f'## {name}\n\n{caption}\n')
    plt.figure(figsize=(7,4));graph=nx.DiGraph([('A','X'),('A','Y*'),('X','Y*'),('A','D'),('X','D'),('A','Recorded Y'),('Y*','Recorded Y')])
    positions={'A':(0,1),'X':(1,1),'Y*':(2,1),'D':(1,0),'Recorded Y':(3,0)}
    nx.draw_networkx(graph,pos=positions,node_size=2500,node_color='#d5e9f5',arrowsize=20,font_size=10)
    plt.axis('off');save('01_measurement_dag','Illustrative generative DAG. A and pre-outcome X influence hypothetical Y* and decisions D. The recording process depends on A,Y* only. Statistical assumptions, not causal identification.')
    flow=pd.read_csv(out/'cohort_flow.csv');plt.figure(figsize=(7,7));ax=plt.gca();ax.axis('off')
    for i,r in enumerate(flow.itertuples()):
        y=.94-i*.14
        ax.text(.5,y,f'{r.filter}\nN = {r.n:,}',ha='center',va='center',transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=.5',fc='#d5e9f5',ec='#2878a0'))
        if i<len(flow)-1:ax.annotate('',xy=(.5,y-.10),xytext=(.5,y-.04),xycoords='axes fraction',arrowprops=dict(arrowstyle='->'))
    save('02_cohort_flow','Sequential notebook restrictions; counts are remaining rows. Raw and analytic IDs and person identities are unique.')
    distribution=pd.read_csv(out/'cohort_race.csv');plt.figure(figsize=(8,4));sns.barplot(data=distribution,x='race',y='n',hue='two_year_recid');plt.xticks(rotation=25,ha='right');plt.ylabel('People');save('03_group_outcomes','Recorded two-year recidivism by released race category in the full analytic cohort; no latent outcome is observed.')
    fairness=pd.read_csv(out/'observed_fairness.csv');predictive=pd.read_csv(out/'predictive.csv');base=['LR','GBT','BN','COMPAS','RW_race','EO_race','RW_sex','EO_sex','RW_intersection','EO_intersection']
    primary_summary=pd.read_csv(out/'sensitivity_summary.csv').query('region == "primary"')
    plotted=[]
    for axis,rows in primary_summary.groupby('axis'):
        plotted.append({'method':'LR','axis':axis,'eo':rows.iloc[0].observed_left})
        for r in rows.itertuples():plotted.append({'method':r.right.split('_')[0],'axis':axis,'eo':r.observed_right})
    plt.figure(figsize=(9,4));sns.barplot(data=pd.DataFrame(plotted),x='method',y='eo',hue='axis');plt.xticks(rotation=35,ha='right');plt.ylabel('Observed EO disparity');save('04_observed_fairness','Observed EO=max pairwise TPR or FPR gap on each primary sensitivity cohort (race Black/white; sex; supported Black/white intersections). RW/EO indicate the mitigation fitted for the plotted axis. All released-group descriptive metrics, including sparse groups, are saved separately.')
    plt.figure(figsize=(8,4));p=predictive[predictive.method.isin(base)];plt.scatter(p.auroc,p.balanced_accuracy)
    for r in p.itertuples():plt.annotate(r.method,(r.auroc,r.balanced_accuracy),fontsize=7,xytext=(3,3),textcoords='offset points')
    plt.xlabel('Risk-score AUROC');plt.ylabel('Decision balanced accuracy');save('05_predictive_tradeoffs','Held-out discrimination of underlying risk scores and balanced accuracy of adverse decisions. EO integrates randomization; it retains LR risk scores.')
    cal=pd.read_csv(out/'calibration.csv');plt.figure(figsize=(6,5));sel=cal[(cal.method=='LR')&(cal.axis=='race')&cal.group.isin(['African-American','Caucasian'])]
    for g,v in sel.groupby('group'):plt.plot(v.predicted,v.observed,'o-',label=g)
    plt.plot([0,1],[0,1],'k--');plt.xlabel('Mean LR predicted recorded-outcome probability');plt.ylabel('Observed recorded-outcome frequency');plt.legend();save('06_calibration','Ten fixed probability bins; points require at least one person. These are observed-label calibration curves, not latent calibration. All method/group bins and sizes are in calibration.csv.')
    summary=pd.read_csv(out/'sensitivity_summary.csv');primary=summary[(summary.region=='primary')&(summary.left=='LR')&(summary.right=='EO_sex')&(summary.axis=='sex')].iloc[0]
    grid=pd.read_csv(out/'sensitivity'/primary.file)
    alphas=[c for c in grid if c.startswith('alpha:')];betas=[c for c in grid if c.startswith('beta:')]
    # Slice beta=.10 for both groups; retain both alpha dimensions.
    sliced=grid[np.isclose(grid[betas[0]],.1)&np.isclose(grid[betas[1]],.1)].copy()
    for number,name,col,title in [('07','feasibility','feasible','Common feasibility'),('08','sensitivity','difference','EO(LR) minus EO(EO sex)'),('09','ranking_reversal','ranking','Fairness ranking')]:
        view=sliced.copy()
        if col=='ranking':view[col]=view[col].map({'infeasible':-1,'stable':0,'tie':1,'reversed':2,'observed_tie_broken':3})
        plt.figure(figsize=(7,5))
        opts={'cmap':'coolwarm','cbar_kws':{'label':title}}
        if col=='ranking':
            from matplotlib.colors import ListedColormap
            opts={'cmap':ListedColormap(['#999999','#2878a0','#f1cc55','#c04a44','#82589f']),
                'vmin':-1.5,'vmax':3.5,'cbar_kws':{'label':title,'ticks':[-1,0,1,2,3]}}
        elif col=='feasible':opts={'cmap':'Greens','vmin':0,'vmax':1,'cbar_kws':{'label':title,'ticks':[0,1]}}
        ax=sns.heatmap(view.pivot(index=alphas[0],columns=alphas[1],values=col).astype(float),**opts)
        if col=='ranking':ax.collections[0].colorbar.set_ticklabels(['Infeasible','Stable','Tie','Reversed','Observed tie broken'])
        if col=='feasible':ax.collections[0].colorbar.set_ticklabels(['Infeasible','Feasible'])
        plt.xlabel('alpha ('+alphas[1].split(':')[1]+')');plt.ylabel('alpha ('+alphas[0].split(':')[1]+')')
        plt.title('Sex slice: both beta = .10');save(number+'_'+name,f'{title}. Female/male alpha vary; both beta fixed to .10. Ranking codes: infeasible -1, stable 0, tie 1, reversed 2. White cells in EO-difference map are infeasible. This is a slice of the primary four-dimensional grid.')
    ranges=summary[summary.region=='primary'];plt.figure(figsize=(8,5))
    labels=[]
    for k,r in enumerate(ranges.itertuples()):
        plt.plot([r.min_difference,r.max_difference],[k,k],lw=2);plt.scatter([r.observed_difference],[k],s=12,color='black');labels.append(f'{r.axis}: {r.left} - {r.right}')
    plt.axvline(0,color='gray',ls='--');plt.yticks(range(len(labels)),labels,fontsize=7);plt.xlabel('EO-gap difference over common feasible scenarios');save('10_eo_ranges','Sensitivity ranges (lines) and observed-label point differences (dots). Crossing zero permits a ranking change; these are not confidence intervals.')
    sim=pd.read_csv(out/'simulation_summary.csv');plt.figure(figsize=(8,4));sns.lineplot(data=sim,x='n',y='rmse',hue='setting',style='method',markers=True);plt.ylabel('RMSE of EO recovery against exact population');save('11_simulation_recovery',f'{sim_reps} independent datasets per sample size/setting. Both methods shown; recording violations depend on X while retaining the same group-marginal alpha/beta. RMSE includes sampling variability and assumption bias.')
    plt.figure(figsize=(9,4));ss=sim.melt(id_vars=['setting','n','method'],value_vars=['sensitivity_coverage','sampling_coverage'],var_name='coverage_type',value_name='coverage');sns.lineplot(data=ss,x='n',y='coverage',hue='setting',style='coverage_type',markers=True,errorbar=None);plt.ylim(0,1.05);plt.ylabel('Empirical coverage fraction');save('12_simulation_coverage','Sensitivity-set coverage of exact population EO and percentile sampling-interval coverage are distinct. Lines average the two synthetic methods; complete per-method values and Monte Carlo counts are saved. Sampling intervals use 100 bootstrap replicates, not the 1,000 used for COMPAS.')
    plt.figure(figsize=(8,4));ab=summary[(summary.axis=='race')&(summary.right=='EO_race')&summary.region.isin(['primary','equal_noise','narrow'])];plt.bar(ab.region,ab.reversal_fraction);plt.ylabel('Fraction of common feasible scenarios reversed');save('13_ablations','Equal-noise and narrower grids compared with the primary group-dependent grid for LR versus race EO. Identity measurement and fixed points are separately reported; fractions are grid summaries, not probabilities.')
    robustness=pd.read_csv(out/'robustness.csv');plt.figure(figsize=(10,5));rv=robustness[(robustness.axis=='race')&(~robustness.check.str.startswith('EO random'))];plt.barh(rv['check'],rv.eo);plt.xlabel('Observed race EO disparity');save('14_robustness','Threshold, age and screening-window robustness. Age-standardized comparisons use common within-outcome age weights and require nonempty cells. Wider-cohort models are re-trained with isolated splits; narrower-cohort evaluation subsets original test people.')
    (figdir/'CAPTIONS.md').write_text('# Figure captions\n\n'+'\n'.join(captions))
    audit=json.loads((out/'audit_reproduction.json').read_text());quality=json.loads((out/'data_quality.json').read_text());manifest=json.loads((out/'run_manifest.json').read_text())
    boot=pd.read_csv(out/'bootstrap_intervals.csv');cohorts=json.loads((out/'sensitivity_cohorts.json').read_text());ex=json.loads((out/'representative_scenarios.json').read_text())
    report='# When Noisy Outcomes Reverse Criminal-Justice Fairness Conclusions\n\n'
    report+='Retrospective research audit. No recommendation for detention, sentencing, policing, or deployment. Hypothetical Y* is not recovered behavior or observed offenses.\n\n'
    report+='## A. Empirically observed facts\n\n'
    report+=f"The released data contain {quality['raw_n']:,} rows; the notebook cohort contains {quality['filtered_n']:,} people. Repeated IDs: {quality['duplicate_ids']}; repeated name/date-of-birth identities: {quality['duplicate_people']}. Notebook adjusted Black/white score coefficient {audit['notebook_black_coefficient']:.5f}; reproduced {audit['reproduced_black_coefficient']:.8f} (odds ratio {audit['odds_ratio']:.4f}). This reproduces notebook cell 21, not the different survival/truth-table cohort used elsewhere in the story. The notebook's 45% probability-ratio calculation is conditional on its reference profile; its coefficient implies an odds ratio of 1.61. Neither statistic is an EO disparity.\n\n"
    cohort_audit=pd.read_csv(out/'compas_cohort_audit.csv')
    report+='The full notebook cohort also yields the following independent released-score confusion audit at decile >=5 (Medium/High versus Low). It uses all eligible people rather than the prediction test subset. These are recorded-outcome rates, not recording-error parameters.\n\n'
    report+=md_table(cohort_audit[cohort_audit.axis=='race'][['group','n','tn','fp','fn','tp','fpr','tpr','fnr']])+'\n\n'
    report+='The split is 3,703 train, 1,234 validation, 1,235 test people (60/20/20 rounded), stratified by sex/outcome. All models use the same split. LR and GBT hyperparameters and binary thresholds use validation only; BN bins are fixed and CPDs training-only. COMPAS is an independent decile audit, high risk at decile >=5; its probability calibration is fitted on validation only. Features are age, prior count, three juvenile history counts, and current charge degree. Race/sex are reserved for auditing and mitigation. No future outcome variables enter prediction.\n\n'
    report+=md_table(p[['method','auroc','balanced_accuracy','accuracy','log_loss','brier']])+'\n\n'
    report+='Reweighing uses training observed A/Y cell frequencies. Unsupported empty training cells retain unit weights; Asian/Female and Native American/Female intersections are unsupported. EO optimizes validation observed equalized odds with Fairlearn; validation groups with fewer than five examples in either outcome retain original LR decisions. Supported groups are recorded in decision_rules.json. Primary EO metrics use expected randomized confusion cells; ten sampled seeds quantify additional decision variation. EO risk discrimination/calibration refer to the unchanged LR score, not the selection probability.\n\n'
    report+='All released groups are reported in group_metrics.csv, including class counts, sparse flags, expected confusion cells, predictive metrics and calibration bins. Small groups are descriptive only. Primary sensitivity cohorts:\n\n'
    report+=md_table(pd.DataFrame(cohorts).assign(included_groups=lambda x:x.included_groups.map('; '.join)))+'\n\n'
    report+='## B. Results conditional on hypothetical measurement assumptions\n\n'
    report+=f"The primary grid is alpha,beta=0:{cfg['grid_step']}:{cfg['grid_max']} per group. It is exploratory, documented in docs/ASSUMPTIONS.md, not externally preregistered or empirically estimated. Historical pre-execution timing was not independently established. Race/sex use full four-dimensional grids; intersection uses two race-specific profiles shared across sexes. Each pair is evaluated on its common feasible set. Matrix inversion rejects invalid prevalence or joint cells; zero denominators are undefined. A valid inverse is compatible with the independence assumption, not evidence that it is true.\n\n"
    table=ranges[['axis','left','right','observed_difference','feasible','reversed','reversal_fraction','min_difference','max_difference']]
    report+=md_table(table)+'\n\n'
    sex_main=ranges[(ranges.axis=='sex')&(ranges.right=='EO_sex')].iloc[0]
    race_main=ranges[(ranges.axis=='race')&(ranges.right=='EO_race')].iloc[0]
    report+=f"The main mitigation comparison illustrates both stability and reversal: sex EO is lower than LR on observed labels, but its ranking reverses in {int(sex_main.reversed):,}/{int(sex_main.feasible):,} feasible primary scenarios ({100*sex_main.reversal_fraction:.2f}%). Race EO has {int(race_main.reversed)} primary reversals. Other pairs can start almost tied: the LR/GBT observed race EO difference is only about 0.00027, so its high reversal fraction should not be interpreted as a robust observed ranking.\n\n"
    report+='Positive differences mean LR has larger disparity; negative differences mean its comparator has larger disparity. Zero-error scenarios reproduce the observed-label analysis exactly. Sensitivity extrema span assumptions, not sampling uncertainty. Equal-noise, narrower, broader and coarser analyses are in sensitivity_summary.csv. Reversal fractions count feasible grid scenarios and depend on the chosen grid; they are not probabilities.\n\n'
    reversed_examples=[e for e in ex if e['ranking']=='reversed']
    if reversed_examples:
        e=next((v for v in reversed_examples if v['axis']=='sex' and v['right']=='EO_sex'),reversed_examples[0])
        report+=f"A representative strict reversal is {e['axis']}: {e['left']} versus {e['right']}, with groups {e['groups']} and (alpha,beta) values {e['parameters']}. Observed EO values are {e['observed_eo']}; hypothetical EO values are {e['eo']}. Inversion redistributes recorded decision/outcome cells differently across groups and methods. Different decision-stratum mixtures shift TPR and FPR enough to change the largest disparity. This mechanism is conditional on those error assumptions; all inferred cells for this example are in representative_scenarios.json.\n\n"
    else:report+='No strict reversal was found in the primary common feasible grids; no reversal mechanism is asserted.\n\n'
    report+='### Synthetic validation\n\nThe generative population has known A,X,Y*,recorded Y,D; group prevalence and prediction quality differ. Exact population enumeration and inversion are independently unit-tested. The known-error scenario reconstructs population joint cells under class-conditional noise. Finite-sample results below compare recovered EO against exact latent population EO, not observed labels. Feasibility agreement compares candidate decisions with exact population compatibility.\n\n'
    report+=md_table(sim)+'\n\n'
    report+=f'{sim_reps} repetitions give limited Monte Carlo precision (worst-case standard error {(.25/sim_reps)**.5:.3f} for a coverage fraction). Coverage under X-dependent errors is a stress test, not a guarantee. Invalid true-scenario replicates remain recorded. Sensitivity coverage is not a confidence-interval coverage statement; sampling intervals condition on fixed generating error rates.\n\n'
    report+=f'### Sampling uncertainty\n\n{bootstrap_reps:,} paired person bootstrap replicates resample identical people for every method; fitted models and splits are fixed. Fixed measurement points were specified before the sweep. Percentile intervals below are exploratory and conditional on feasibility. Invalid/undefined replicates are counted, never converted to zero. Intervals do not include training, measurement-rate or model-selection uncertainty.\n\n'
    report+=md_table(boot[(boot.axis=='race')&boot.method.isin(['LR','EO_race'])][['method','scenario','metric','valid','invalid','low','high']])+'\n\n'
    sex_ci=boot[(boot.axis=='sex')&(boot.method=='EO_sex')&(boot.scenario=='observed')&(boot.metric=='difference_from_LR')].iloc[0]
    report+=f"For the central sex comparison, the 95% paired observed EO(EO policy)-EO(LR) interval is [{sex_ci.low:.4f}, {sex_ci.high:.4f}]. It includes zero; the observed test-sample advantage does not establish a population fairness ranking. Conditional ranking reversals are sensitivity findings and should be interpreted with this sampling uncertainty.\n\n"
    report+='Predictive intervals and paired predictive differences are in predictive_intervals.csv and predictive_difference_intervals.csv. Conditional EO and paired fairness intervals for all axes are in bootstrap_intervals.csv. No sensitivity range is labeled a confidence interval.\n\n'
    report+='### Ablations and robustness\n\nIdentity measurement is the observed-label ablation. Equal-noise constraints reduce the scenario set; fixed-point versus range comparisons are available in bootstrap_intervals.csv and sensitivity_summary.csv. These isolate measurement assumptions rather than refitting predictions.\n\n'
    report+=md_table(summary[(summary.axis=='race')&(summary.right=='EO_race')][['region','feasible','reversed','reversal_fraction','min_difference','max_difference']])+'\n\n'
    report+=md_table(robustness[robustness.axis=='race'][['check','eo']])+'\n\n'
    report+='Thresholds alter the decision itself; age standardization alters composition; removal of age alters the fitted predictor; cohort windows change eligibility. These are distinct perturbations. Race, sex and intersection analyses and ten postprocessing seeds were executed, with results saved for each. Nonempty age/outcome cells are required for standardization; undefined checks are explicit. Wider-window comparisons involve a different isolated split, so are not paired estimates on the original people.\n\n'
    report+='## C. Claims not established by these data\n\nThe data do not identify Y*, alpha, beta, actual offense incidence, causal discrimination, or deployment utility. Conditional independence of recording and decisions cannot be verified from recorded outcomes alone. Scenario compatibility is necessary, not sufficient, for substantive plausibility. Error grids carry no empirical prior. Minority and intersectional estimates can be unstable; restricting sensitivity contrasts leaves other racial groups outside those conclusions. Missing features use training-only imputation; unmeasured errors remain possible. Person linkage by released names/date of birth cannot guarantee absence of identity errors. Fairness rankings depend on cohort, thresholds, metric, sampling variation and measurement assumptions; exploratory reversals do not establish real-world injustice or identify the superior method.\n\n'
    report+='## Reproduction and artifacts\n\nSee README.md for exact commands. Source files, raw data, pinned requirements, tests, configs, checkpoints, all machine-readable experiment tables and 14 figures in PNG/PDF/SVG are retained. Current run configuration and raw/assumption hashes are in results/run_manifest.json. Figures and the report are generated only from completed result files. The original run did not publish or push; a later Git delivery is documented in docs/GIT_DELIVERY.md.\n'
    notes=Path('docs/VERIFICATION_NOTES.md')
    if notes.exists():report+='\n'+notes.read_text()
    Path('docs/FINAL_REPORT.md').write_text(report)
