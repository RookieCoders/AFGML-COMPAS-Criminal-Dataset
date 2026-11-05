"""Metrics on a common evaluation sample; zero denominators remain undefined."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,log_loss,brier_score_loss
from .measurement import observed_joint,eo,rates


def performance(y,score,decision):
    j=observed_joint(y,decision);fpr,tpr=rates(j)
    return dict(auroc=roc_auc_score(y,score) if len(np.unique(y))==2 else np.nan,
        balanced_accuracy=(tpr+1-fpr)/2,accuracy=j[0,0]+j[1,1],tpr=tpr,fpr=fpr,fnr=1-tpr,
        precision=j[1,1]/j[1].sum() if j[1].sum()>0 else np.nan,
        log_loss=log_loss(y,score,labels=[0,1]),brier=brier_score_loss(y,score))


def evaluate(d,predictions):
    y=d.two_year_recid.to_numpy();overall=[];groups=[];gaps=[];calibration=[]
    for name,p in predictions.items():
        overall.append(dict(method=name,**performance(y,p['score'],p['decision'])))
        for axis in ['race','sex','intersection']:
            js=[]
            for group,idx in d.groupby(axis).indices.items():
                yy=y[idx];ss=p['score'][idx];dd=p['decision'][idx];j=observed_joint(yy,dd);js.append(j)
                groups.append(dict(method=name,axis=axis,group=group,n=len(idx),n0=int((yy==0).sum()),n1=int((yy==1).sum()),sparse=min((yy==0).sum(),(yy==1).sum())<20,
                    tn=j[0,0]*len(idx),fp=j[1,0]*len(idx),fn=j[0,1]*len(idx),tp=j[1,1]*len(idx),**performance(yy,ss,dd)))
                for b in range(10):
                    mask=(ss>=b/10)&((ss<(b+1)/10) if b<9 else (ss<=1))
                    if mask.any(): calibration.append(dict(method=name,axis=axis,group=group,bin=b,n=int(mask.sum()),predicted=ss[mask].mean(),observed=yy[mask].mean()))
            valid_js=[j for j in js if np.isfinite(rates(j)).all()]
            gaps.append(dict(method=name,axis=axis,eo=eo(valid_js),valid_groups=len(valid_js),undefined_groups=len(js)-len(valid_js)))
    return pd.DataFrame(overall),pd.DataFrame(groups),pd.DataFrame(gaps),pd.DataFrame(calibration)
