"""Threshold, age-standardization, cohort, feature and postprocessor randomness checks."""
import numpy as np
import pandas as pd
from .data import load_cohort,split,FEATURES
from .models import pipeline
from .measurement import observed_joint,eo
from .sensitivity import analysis_cohort
from .metrics import performance


def run_robustness(d,parts,pred,models,cfg,out):
    test=d.iloc[parts[2]].reset_index(drop=True);rows=[]
    def add(label,axis,decision,score,cohort=test):
        keep,groups=analysis_cohort(cohort,axis,cfg['sparse_min_class'])
        js=[observed_joint(cohort.two_year_recid.to_numpy()[keep & (cohort[axis]==g).to_numpy()],decision[keep & (cohort[axis]==g).to_numpy()]) for g in groups]
        rows.append(dict(check=label,axis=axis,n=int(keep.sum()),eo=eo(js),**performance(cohort.two_year_recid,score,decision)))
    for axis in ['race','sex','intersection']:
        for t in [.35,.5,.65]: add('LR threshold '+str(t),axis,(pred['LR']['score']>=t).astype(float),pred['LR']['score'])
        for seed in range(10): add('EO random seed '+str(seed),axis,pred[f'EO_{axis}_sample{seed}']['decision'],pred['EO_'+axis]['score'])
        # Direct standardization: same pooled age distribution within observed outcome class.
        keep,groups=analysis_cohort(test,axis,cfg['sparse_min_class'])
        for method in ['LR','RW_'+axis,'EO_'+axis]:
            standardized=[];supported=True
            for g in groups:
                group_rates=[]
                for y in [0,1]:
                    vals=[]
                    for age in sorted(test.age_band.unique()):
                        ref=keep & (test.two_year_recid==y).to_numpy()
                        weight=np.mean(test.loc[ref,'age_band']==age)
                        mask=ref & (test[axis]==g).to_numpy() & (test.age_band==age).to_numpy()
                        if not mask.any(): supported=False;break
                        vals.append(weight*pred[method]['decision'][mask].mean())
                    group_rates.append(sum(vals) if len(vals)==3 else np.nan)
                standardized.append(group_rates)
            gap=np.ptp(standardized,axis=0).max() if supported else np.nan
            rows.append(dict(check='age standardized '+method,axis=axis,n=int(keep.sum()),eo=gap,reason='ok' if supported else 'empty_age_outcome_cell'))
    noage=pipeline('LR',1,cfg['seed'],age=False).fit(d.iloc[parts[0]][FEATURES],d.iloc[parts[0]].two_year_recid)
    p=noage.predict_proba(test[FEATURES])[:,1]
    for axis in ['race','sex','intersection']: add('age feature removed',axis,(p>=.5).astype(float),p)
    # Cohort variation changes eligibility only among original test people, preserving the split.
    for window in [15,60]:
        cohort,_,_=load_cohort(window=window)
        if window==15:
            mask=test.person.isin(cohort.person).to_numpy();c=test.loc[mask].reset_index(drop=True)
        else:
            # Wider cohort is re-split and model trained afresh; test remains isolated.
            cparts=split(cohort,cfg['seed']);c=cohort.iloc[cparts[2]].reset_index(drop=True)
        if window==15: p=pred['LR']['score'][mask]
        else:
            model=pipeline('LR',1,cfg['seed']).fit(cohort.iloc[cparts[0]][FEATURES],cohort.iloc[cparts[0]].two_year_recid)
            p=model.predict_proba(c[FEATURES])[:,1]
        for axis in ['race','sex','intersection']: add('screening window '+str(window),axis,(p>=.5).astype(float),p,c)
    frame=pd.DataFrame(rows);frame.to_csv(out/'robustness.csv',index=False);return frame
