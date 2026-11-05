"""Check retained fitted models and all test predictions without retraining."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,log_loss,brier_score_loss
from compas_fairness.data import load_cohort,split,FEATURES
from compas_fairness.models import DiscreteBN

d,parts,pred,models,selection=joblib.load('results/models.joblib')
fresh,_,_=load_cohort();assert fresh.person.equals(d.person)
assert all(np.array_equal(a,b) for a,b in zip(parts,split(fresh,2026)))
tr,va,te=parts;x=d.iloc[te][FEATURES];y=d.iloc[te].two_year_recid.to_numpy()
saved=pd.read_csv('results/test_predictions.csv.gz');assert saved.person.tolist()==d.iloc[te].person.tolist()
for name,entry in pred.items():
    np.testing.assert_allclose(saved[name+'__score'],entry['score'],atol=1e-12)
    np.testing.assert_allclose(saved[name+'__decision'],entry['decision'],atol=1e-12)
for name in ['LR','GBT','RW_race','RW_sex','RW_intersection']:
    np.testing.assert_allclose(models[name].predict_proba(x)[:,1],pred[name]['score'],atol=1e-12)
    scaler=models[name].named_steps['columntransformer'].named_transformers_['num'].named_steps['standardscaler']
    np.testing.assert_allclose(scaler.mean_,d.iloc[tr][FEATURES[:-1]].mean(),atol=1e-12)
for axis in ['race','sex','intersection']:
    support=json.loads(Path('results/decision_rules.json').read_text())['EO_'+axis]['supported_groups']
    mask=d.iloc[te][axis].isin(support).to_numpy()
    probabilities=models['EO_'+axis]._pmf_predict(x.loc[mask],sensitive_features=d.iloc[te][axis].to_numpy()[mask])[:,1]
    np.testing.assert_allclose(probabilities,pred['EO_'+axis]['decision'][mask],atol=1e-12)
    np.testing.assert_allclose(pred['EO_'+axis]['decision'][~mask],pred['LR']['decision'][~mask],atol=1e-12)
    np.testing.assert_allclose(pred['EO_'+axis]['score'],pred['LR']['score'],atol=1e-12)
bn=DiscreteBN().fit(d.iloc[tr],d.iloc[tr].two_year_recid)
model=bn.inference.model;columns=bn.transform(x);prior=model.get_cpds('Y').values
posterior=[]
for values in columns.itertuples(index=False,name=None):
    product=prior.copy()
    for c,value in zip(columns,values):product*=model.get_cpds(c).values[value,:]
    posterior.append(product[1]/product.sum())
np.testing.assert_allclose(posterior,pred['BN']['score'],atol=1e-12)
performance=pd.read_csv('results/predictive.csv').set_index('method')
for name,entry in pred.items():
    np.testing.assert_allclose(performance.loc[name,['auroc','log_loss','brier']].to_numpy(dtype=float),[roc_auc_score(y,entry['score']),log_loss(y,entry['score']),brier_score_loss(y,entry['score'])],atol=1e-12)
# Calibration bins: independently check saved means/counts against retained people.
cal=pd.read_csv('results/calibration.csv')
for r in cal.itertuples():
    score=saved[r.method+'__score'];mask=(saved[r.axis]==r.group)&(score>=r.bin/10)&((score<(r.bin+1)/10) if r.bin<9 else (score<=1))
    assert mask.sum()==r.n
    np.testing.assert_allclose([score[mask].mean(),saved.loc[mask,'outcome'].mean()],[r.predicted,r.observed],atol=1e-12)
Path('results/verification/pipeline_audit.json').write_text(json.dumps({'status':'passed','test_people':len(te),'all_saved_predictions':'checked against checkpoint','train_only_scaler_means':'checked','EO_expected_probabilities_and_fallbacks':'checked','BN_posteriors':'independent CPD product matches saved predictions','predictive_scores_and_calibration':'recomputed from saved people'},indent=2))
print('Pipeline audit passed')
