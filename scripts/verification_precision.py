"""Summarize existing original and additional simulation rows, with Monte Carlo uncertainty."""
import json
from pathlib import Path
import pandas as pd
from compas_fairness.monte_carlo import wilson
from compas_fairness.report import plt,sns

rows=[]
for experiment,path in [('original','results/simulation.csv'),('validation','results/verification_simulation/simulation.csv')]:
    frame=pd.read_csv(path)
    for key,v in frame.groupby(['setting','n','method']):
        for metric,column in [('sensitivity_set_coverage','sensitivity_population_covered'),('sampling_ci_coverage','sampling_ci_covered'),('reversal_accuracy','reversal_detection_correct')]:
            values=v[column].dropna().astype(bool);n=len(values);k=int(values.sum())
            rows.append(dict(experiment=experiment,setting=key[0],n=key[1],method=key[2],metric=metric,repetitions=n,undefined=len(v)-n,successes=k,**wilson(k,n)))
p=pd.DataFrame(rows);p.to_csv('results/verification/monte_carlo_intervals.csv',index=False)
figdir=Path('figures/verification');figdir.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
for ax,metric in zip(axes,['sensitivity_set_coverage','sampling_ci_coverage']):
    for setting in ['equal','unequal','violation']:
        for method in [0,1]:
            v=p[(p.experiment=='validation')&(p.metric==metric)&(p.setting==setting)&(p.method==method)]
            x=v.n.to_numpy()+(method*150)
            ax.errorbar(x,v.fraction,yerr=[v.fraction-v.mc_low,v.mc_high-v.fraction],marker='o',linestyle='-' if method==0 else '--',label=f'{setting}, method {method}')
    ax.set_title(metric.replace('_',' '));ax.set_xlabel('Simulated sample size (method 1 offset by 150)');ax.set_ylim(0,1.05)
axes[0].set_ylabel('Coverage fraction and 95% Wilson Monte Carlo interval');axes[1].legend(fontsize=7)
fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(figdir/('simulation_coverage_mc.'+ext),dpi=300)
plt.close(fig)
print(p[(p.experiment=='validation')&(p.n==10000)&(p.metric=='sampling_ci_coverage')].to_string(index=False))
