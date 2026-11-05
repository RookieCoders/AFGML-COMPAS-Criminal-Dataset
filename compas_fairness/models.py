"""Training-only preprocessing, validation selection, observed-label mitigation."""
from itertools import product
import logging
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,balanced_accuracy_score
from fairlearn.postprocessing import ThresholdOptimizer
from .data import FEATURES


def pipeline(kind,parameter,seed,age=True):
    num=[x for x in FEATURES if x!='c_charge_degree' and (age or x!='age')]
    pre=ColumnTransformer([('num',make_pipeline(SimpleImputer(strategy='median'),StandardScaler()),num),
        ('cat',make_pipeline(SimpleImputer(strategy='most_frequent'),OneHotEncoder(handle_unknown='ignore',sparse_output=False)),['c_charge_degree'])])
    est=LogisticRegression(C=parameter,max_iter=2000,random_state=seed) if kind=='LR' else HistGradientBoostingClassifier(max_leaf_nodes=parameter,max_iter=100,l2_regularization=2,random_state=seed)
    return make_pipeline(pre,est)


class DiscreteBN:
    """Laplace-smoothed naive Bayes network Y -> discretized pre-outcome covariates.

    Fixed bins specified before fitting, CPDs fitted on train only; posterior via pgmpy VE.
    """
    def transform(self,x):
        return pd.DataFrame({'age_bin':np.digitize(x.age,[25,45]),
            'prior_bin':np.digitize(x.priors_count,[1,3,6]),
            'juvenile':((x.juv_fel_count+x.juv_misd_count+x.juv_other_count)>0).astype(int),
            'charge':(x.c_charge_degree=='F').astype(int)},index=x.index)
    def fit(self,x,y):
        from pgmpy.models import DiscreteBayesianNetwork
        from pgmpy.factors.discrete import TabularCPD
        from pgmpy.inference import VariableElimination
        t=self.transform(x); y=np.asarray(y)
        bn=DiscreteBayesianNetwork([('Y',c) for c in t])
        counts=np.bincount(y,minlength=2)+1
        cpds=[TabularCPD('Y',2,(counts/counts.sum())[:,None])]
        for c,k in zip(t,[3,4,2,2]):
            v=np.array([np.bincount(t.loc[y==z,c],minlength=k)+1 for z in [0,1]]).T
            v=v/v.sum(axis=0)
            cpds.append(TabularCPD(c,k,v,evidence=['Y'],evidence_card=[2]))
        bn.add_cpds(*cpds);assert bn.check_model()
        self.inference=VariableElimination(bn);self.cache={}; return self
    def predict_proba(self,x):
        t=self.transform(x); ps=[]
        for row in t.itertuples(index=False,name=None):
            if row not in self.cache:
                self.cache[row]=self.inference.query(['Y'],evidence=dict(zip(t.columns,row)),show_progress=False).values[1]
            ps.append(self.cache[row])
        return np.column_stack([1-np.array(ps),ps])


def fit_models(d,parts,seed):
    tr,va,te=parts; x=d[FEATURES];y=d.two_year_recid
    predictions={};models={};selection=[]
    for kind,params in [('LR',[.01,.1,1,10]),('GBT',[7,15,31])]:
        best=None
        for p in params:
            m=pipeline(kind,p,seed).fit(x.iloc[tr],y.iloc[tr])
            s=roc_auc_score(y.iloc[va],m.predict_proba(x.iloc[va])[:,1])
            selection.append({'model':kind,'parameter':p,'validation_auroc':s})
            if best is None or s>best[0]: best=(s,m)
        m=best[1];pv=m.predict_proba(x.iloc[va])[:,1];pt=m.predict_proba(x.iloc[te])[:,1]
        thresholds=np.arange(.2,.801,.025)
        threshold=max(thresholds,key=lambda t:balanced_accuracy_score(y.iloc[va],pv>=t))
        predictions[kind]={'score':pt,'decision':(pt>=threshold).astype(float),'threshold':float(threshold)}
        models[kind]=m
    bn=DiscreteBN().fit(x.iloc[tr],y.iloc[tr]);p=bn.predict_proba(x.iloc[te])[:,1]
    predictions['BN']={'score':p,'decision':(p>=.5).astype(float),'threshold':.5}
    # Deciles are ordinal, not calibrated probabilities. Calibrate probability mapping on validation only.
    decile=d.decile_score.to_numpy()
    cal=LogisticRegression(C=1e3).fit(decile[va,None],y.iloc[va])
    predictions['COMPAS']={'score':cal.predict_proba(decile[te,None])[:,1],
                          'decision':(decile[te]>=5).astype(float),'threshold':5}
    for axis in ['race','sex','intersection']:
        a=d[axis].to_numpy();w=np.ones(len(tr));yt=y.iloc[tr].to_numpy();at=a[tr]
        for group,z in product(np.unique(at),[0,1]):
            mask=(at==group)&(yt==z)
            if any(np.sum((at==group)&(yt==zz))==0 for zz in [0,1]):
                logging.warning('Reweighing unsupported group %s %s: retaining unit weights',axis,group)
                continue
            w[mask]=np.mean(at==group)*np.mean(yt==z)/np.mean(mask)
        rw=pipeline('LR',models['LR'].named_steps['logisticregression'].C,seed).fit(x.iloc[tr],yt,logisticregression__sample_weight=w)
        pv=rw.predict_proba(x.iloc[va])[:,1];pt=rw.predict_proba(x.iloc[te])[:,1]
        threshold=max(np.arange(.2,.801,.025),key=lambda t:balanced_accuracy_score(y.iloc[va],pv>=t))
        predictions['RW_'+axis]={'score':pt,'decision':(pt>=threshold).astype(float),'threshold':float(threshold)}
        eo=ThresholdOptimizer(estimator=models['LR'],constraints='equalized_odds',objective='balanced_accuracy_score',prefit=True,predict_method='predict_proba',grid_size=1000)
        counts=pd.crosstab(a[va],y.iloc[va].to_numpy())
        supported=counts.index[(counts.min(axis=1)>=5)].to_numpy()
        eligible=np.isin(a[va],supported)
        logging.info('EO %s supported validation groups: %s; others retain LR decisions',axis,list(supported))
        eo.fit(x.iloc[va].loc[eligible],y.iloc[va].loc[eligible],sensitive_features=a[va][eligible])
        # Fairlearn public predict samples decisions. PMF is used for exact expected confusion rates.
        eligible_test=np.isin(a[te],supported)
        pt=predictions['LR']['decision'].copy()
        pt[eligible_test]=eo._pmf_predict(x.iloc[te].loc[eligible_test],sensitive_features=a[te][eligible_test])[:,1]
        predictions['EO_'+axis]={'score':predictions['LR']['score'],'decision':pt,'threshold':'expected randomized selection', 'supported_groups':supported.tolist()}
        for rseed in range(10):
            sample=predictions['LR']['decision'].copy()
            sample[eligible_test]=eo.predict(x.iloc[te].loc[eligible_test],sensitive_features=a[te][eligible_test],random_state=seed+rseed)
            predictions[f'EO_{axis}_sample{rseed}']={'score':predictions['LR']['score'],'decision':sample,'threshold':'sampled'}
        models['RW_'+axis]=rw;models['EO_'+axis]=eo
    logging.info('Fitted models using %d train, %d validation, %d test people',len(tr),len(va),len(te))
    return predictions,models,pd.DataFrame(selection)
