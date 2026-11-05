"""Prespecified pair comparisons on common feasible scenarios."""
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from .measurement import observed_joint,eo,scenarios,sweep,invert,rates


def analysis_cohort(d,axis,min_class=20):
    # Race sensitivity is the prespecified Black/white contrast; observed audit retains all races.
    keep=np.ones(len(d),dtype=bool) if axis=='sex' else d.race.isin(['African-American','Caucasian']).to_numpy(copy=True)
    counts=pd.crosstab(d.loc[keep,axis],d.loc[keep,'two_year_recid'])
    valid=counts.index[counts.min(axis=1)>=min_class].tolist()
    keep &= d[axis].isin(valid).to_numpy()
    return keep,sorted(valid)


def joints_for(d,pred,axis,names,keep,groups):
    return np.array([[observed_joint(d.two_year_recid.to_numpy()[keep & (d[axis]==g).to_numpy()],p['decision'][keep & (d[axis]==g).to_numpy()])
                      for g in groups] for p in [pred[n] for n in names]])


def run_sensitivity(d,pred,cfg,out):
    directory=out/'sensitivity';directory.mkdir(exist_ok=True)
    summaries=[];examples=[];excluded=[]
    regions=[('primary',cfg['grid_max'],cfg['grid_step'],False),('equal_noise',.2,.025,True),
             ('narrow',.1,.025,False),('broad',.3,.05,False),('coarse',.2,.05,False)]
    for axis in ['race','sex','intersection']:
        keep,groups=analysis_cohort(d,axis,cfg['sparse_min_class'])
        excluded.append({'axis':axis,'included_groups':groups,'included_n':int(keep.sum()),'excluded_n':int((~keep).sum())})
        pairs=[('LR','RW_'+axis),('LR','EO_'+axis),('LR','GBT'),('LR','BN'),('LR','COMPAS')]
        for region,mx,step,equal in regions:
            s=scenarios(groups,mx,step,equal)
            for left,right in pairs:
                j=joints_for(d,pred,axis,[left,right],keep,groups)
                gap,valid,reason,rr=sweep(j,s)
                obs=np.array([eo(v) for v in j]);r0=obs[0]-obs[1];diff=gap[:,0]-gap[:,1];tol=cfg['tie_tolerance']
                classification=np.full(len(s),'infeasible',dtype=object)
                classification[valid]='stable'
                classification[valid & (abs(diff)<=tol)]='tie'
                classification[valid & (diff*r0 < 0) & (abs(diff)>tol) & (abs(r0)>tol)]='reversed'
                if abs(r0)<=tol: classification[valid & (abs(diff)>tol)]='observed_tie_broken'
                tab=pd.DataFrame({'scenario':np.arange(len(s)),'feasible':valid,'reason':reason,'eo_left':gap[:,0],'eo_right':gap[:,1],
                    'difference':diff,'ranking':classification})
                for k,g in enumerate(groups):
                    tab[f'alpha:{g}']=s[:,k,0];tab[f'beta:{g}']=s[:,k,1]
                    for mi,name in enumerate(['left','right']):
                        tab[f'fpr_{name}:{g}']=rr[:,mi,k,0];tab[f'tpr_{name}:{g}']=rr[:,mi,k,1]
                        q=j[mi,k,:,1].sum()
                        tab[f'prevalence_{name}:{g}']=(q-s[:,k,0])/(1-s[:,k].sum(axis=1))
                filename=f'{axis}__{region}__{left}__{right}.csv.gz'
                tab.to_csv(directory/filename,index=False,compression='gzip')
                summaries.append(dict(axis=axis,region=region,left=left,right=right,n=int(keep.sum()),groups=';'.join(groups),
                    scenarios=len(s),feasible=int(valid.sum()),reversed=int((classification=='reversed').sum()),ties=int((classification=='tie').sum()),
                    reversal_fraction=float(np.mean(classification[valid]=='reversed')) if valid.any() else np.nan,
                    observed_left=obs[0],observed_right=obs[1],observed_difference=r0,
                    min_left=float(gap[valid,0].min()) if valid.any() else np.nan,max_left=float(gap[valid,0].max()) if valid.any() else np.nan,
                    min_right=float(gap[valid,1].min()) if valid.any() else np.nan,max_right=float(gap[valid,1].max()) if valid.any() else np.nan,
                    min_difference=float(diff[valid].min()) if valid.any() else np.nan,max_difference=float(diff[valid].max()) if valid.any() else np.nan,file=filename))
                if region=='primary':
                    for label in ['stable','reversed','tie']:
                        ids=np.flatnonzero(classification==label)
                        if len(ids):
                            i=ids[len(ids)//2]
                            examples.append(dict(axis=axis,left=left,right=right,ranking=label,scenario=int(i),parameters=s[i].tolist(),groups=groups,
                                eo=gap[i].tolist(),observed_eo=obs.tolist(),latent_joints=[[invert(j[mi,k],*s[i,k]).tolist() for k in range(len(groups))] for mi in range(2)]))
        logging.info('Sensitivity complete for %s',axis)
    pd.DataFrame(summaries).to_csv(out/'sensitivity_summary.csv',index=False)
    (out/'representative_scenarios.json').write_text(json.dumps(examples,indent=2))
    (out/'sensitivity_cohorts.json').write_text(json.dumps(excluded,indent=2))
    return pd.DataFrame(summaries)
