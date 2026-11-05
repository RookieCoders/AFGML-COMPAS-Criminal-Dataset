"""Paired person bootstrap conditional on fitted models; measurement assumptions held fixed."""
import logging
import numpy as np
import pandas as pd
from .sensitivity import analysis_cohort,joints_for
from .measurement import sweep,eo
from .metrics import performance


def run_bootstrap(d,pred,cfg,out):
    rng=np.random.default_rng(cfg['seed']+400);rows=[];predictive=[];group_rows=[]
    base_names=[n for n in pred if '_sample' not in n]
    for b in range(cfg['bootstrap']):
        idx=rng.integers(0,len(d),len(d));bd=d.iloc[idx].reset_index(drop=True)
        bp={n:{'decision':pred[n]['decision'][idx],'score':pred[n]['score'][idx]} for n in base_names}
        for name in base_names:
            perf=performance(bd.two_year_recid.to_numpy(),bp[name]['score'],bp[name]['decision'])
            predictive.extend(dict(replicate=b,method=name,metric=k,value=v) for k,v in perf.items())
        for axis in ['race','sex','intersection']:
            # Freeze eligible groups from original test set, never redefine them per replicate.
            keep,groups=analysis_cohort(d,axis,cfg['sparse_min_class'])
            mask=bd[axis].isin(groups).to_numpy(copy=True)
            if axis!='sex': mask &= bd.race.isin(['African-American','Caucasian']).to_numpy()
            names=['LR','RW_'+axis,'EO_'+axis,'GBT','BN','COMPAS']
            if any(not np.any(mask & (bd[axis]==g).to_numpy()) for g in groups):
                for name in names: rows.append(dict(replicate=b,axis=axis,method=name,scenario='observed',eo=np.nan,reason='absent_group',difference_from_LR=np.nan))
                continue
            j=joints_for(bd,bp,axis,names,mask,groups)
            # Fixed prespecified points, not selected based on test reversal maps.
            scenarios=[('observed',np.zeros((len(groups),2))),('equal_05',np.full((len(groups),2),.05)),
                       ('contrast',np.array([[.1,.05] if ('Caucasian' in g or g=='Male') else [.025,.1] for g in groups]))]
            for label,s in scenarios:
                gaps,valid,reason,grates=sweep(j,s[None])
                for m,name in enumerate(names):
                    for gidx,group in enumerate(groups):
                        group_rows.append(dict(replicate=b,axis=axis,method=name,scenario=label,group=group,reason=reason[0],
                            fpr=grates[0,m,gidx,0] if valid[0] else np.nan,tpr=grates[0,m,gidx,1] if valid[0] else np.nan))
                    rows.append(dict(replicate=b,axis=axis,method=name,scenario=label,eo=gaps[0,m],reason=reason[0],difference_from_LR=gaps[0,m]-gaps[0,0]))
        if (b+1)%200==0: logging.info('Bootstrap %d/%d',b+1,cfg['bootstrap'])
    group_frame=pd.DataFrame(group_rows)
    group_frame.to_csv(out/'group_bootstrap.csv.gz',index=False,compression='gzip')
    group_frame.melt(id_vars=['replicate','axis','method','scenario','group','reason'],value_vars=['fpr','tpr']).groupby(['axis','method','scenario','group','variable']).value.agg(low=lambda x:x.quantile(.025),high=lambda x:x.quantile(.975),valid='count').reset_index().to_csv(out/'group_bootstrap_intervals.csv',index=False)
    frame=pd.DataFrame(rows);frame.to_csv(out/'bootstrap.csv.gz',index=False,compression='gzip')
    summary=[]
    for keys,v in frame.groupby(['axis','method','scenario']):
        for metric in ['eo','difference_from_LR']:
            q=v[metric].dropna()
            summary.append(dict(axis=keys[0],method=keys[1],scenario=keys[2],metric=metric,valid=len(q),invalid=len(v)-len(q),
                low=q.quantile(.025),high=q.quantile(.975),bootstrap_mean=q.mean()))
    pd.DataFrame(summary).to_csv(out/'bootstrap_intervals.csv',index=False)
    predictive=pd.DataFrame(predictive);predictive.to_csv(out/'predictive_bootstrap.csv.gz',index=False,compression='gzip')
    predictive.groupby(['method','metric']).value.agg(low=lambda x:x.quantile(.025),high=lambda x:x.quantile(.975),valid='count').reset_index().to_csv(out/'predictive_intervals.csv',index=False)
    # Paired predictive differences use exactly the same resampled people.
    wide=predictive.pivot(index=['replicate','metric'],columns='method',values='value')
    (wide.subtract(wide['LR'],axis=0)).stack().rename('difference_from_LR').reset_index().groupby(['method','metric']).difference_from_LR.agg(low=lambda x:x.quantile(.025),high=lambda x:x.quantile(.975)).reset_index().to_csv(out/'predictive_difference_intervals.csv',index=False)
