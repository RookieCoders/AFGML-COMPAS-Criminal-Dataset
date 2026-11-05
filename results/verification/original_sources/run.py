"""Configuration-driven, checkpointed experiment CLI."""
import argparse
import hashlib
import json
import logging
from pathlib import Path
import platform
import joblib
import pandas as pd
from .data import load_cohort,split,reproduce_audit
from .models import fit_models
from .metrics import evaluate
from .measurement import validate_variable_elimination,observed_joint,rates
from .sensitivity import run_sensitivity
from .simulation import run_simulation
from .uncertainty import run_bootstrap
from .robustness import run_robustness


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',default='configs/full.json')
    parser.add_argument('--stages',default='audit,models,sensitivity,simulation,bootstrap,robustness,report')
    parser.add_argument('--reuse-models',action='store_true')
    args=parser.parse_args();cfg=json.loads(Path(args.config).read_text())
    out=Path('results');out.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(out/'run.log')])
    stages=args.stages.split(',');d,flow,info=load_cohort();parts=split(d,cfg['seed'])
    if 'audit' in stages:
        flow.to_csv(out/'cohort_flow.csv',index=False);(out/'data_quality.json').write_text(json.dumps(info,indent=2))
        coef,audit=reproduce_audit(d);coef.to_csv(out/'audit_regression.csv');(out/'audit_reproduction.json').write_text(json.dumps(audit,indent=2))
        ve=validate_variable_elimination();(out/'variable_elimination.json').write_text(json.dumps(ve,indent=2))
        full_audit=[]
        for axis in ['race','sex','intersection']:
            for group,g in d.groupby(axis):
                j=observed_joint(g.two_year_recid,(g.decile_score>=5).astype(float))
                fpr,tpr=rates(j)
                full_audit.append(dict(axis=axis,group=group,n=len(g),tn=j[0,0]*len(g),fp=j[1,0]*len(g),fn=j[0,1]*len(g),tp=j[1,1]*len(g),fpr=fpr,tpr=tpr,fnr=1-tpr))
        pd.DataFrame(full_audit).to_csv(out/'compas_cohort_audit.csv',index=False)
        for axis in ['race','sex','intersection']:
            d.groupby([axis,'two_year_recid']).size().rename('n').reset_index().to_csv(out/f'cohort_{axis}.csv',index=False)
        manifest={'python':platform.python_version(),'config':cfg,'sha256_raw':hashlib.sha256(Path('data/raw/compas-scores-two-years.csv').read_bytes()).hexdigest(),
                  'assumptions_sha256':hashlib.sha256(Path('docs/ASSUMPTIONS.md').read_bytes()).hexdigest()}
        (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
    needs_models=any(s in stages for s in ['models','sensitivity','bootstrap','robustness'])
    if needs_models:
        if args.reuse_models and (out/'models.joblib').exists():
            cached_d,cached_parts,pred,models,selection=joblib.load(out/'models.joblib')
            if not d.person.equals(cached_d.person) or any((a!=b).any() for a,b in zip(parts,cached_parts)):
                raise ValueError('cached_model_split_mismatch')
        else:
            pred,models,selection=fit_models(d,parts,cfg['seed']);joblib.dump((d,parts,pred,models,selection),out/'models.joblib')
        selection.to_csv(out/'model_selection.csv',index=False)
        test=d.iloc[parts[2]].reset_index(drop=True)
        tables=evaluate(test,pred)
        for name,tab in zip(['predictive','group_metrics','observed_fairness','calibration'],tables):tab.to_csv(out/f'{name}.csv',index=False)
        decisions=pd.DataFrame({'person':test.person,'outcome':test.two_year_recid,'race':test.race,'sex':test.sex,'intersection':test.intersection,'age_band':test.age_band})
        for name,p in pred.items(): decisions[name+'__score']=p['score'];decisions[name+'__decision']=p['decision']
        decisions.to_csv(out/'test_predictions.csv.gz',index=False,compression='gzip')
        pd.DataFrame([{'person':d.iloc[idx].person,'partition':name} for name,ii in zip(['train','validation','test'],parts) for idx in ii]).to_csv(out/'partitions.csv',index=False)
        (out/'decision_rules.json').write_text(json.dumps({name:{k:v for k,v in p.items() if k not in ['score','decision']} for name,p in pred.items()},indent=2))
    if 'sensitivity' in stages: run_sensitivity(test,pred,cfg,out)
    if 'simulation' in stages: run_simulation(cfg,out)
    if 'bootstrap' in stages: run_bootstrap(test,pred,cfg,out)
    if 'robustness' in stages: run_robustness(d,parts,pred,models,cfg,out)
    if 'report' in stages:
        from .report import create_report
        create_report(out,Path('figures'))
    source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('compas_fairness').glob('*.py'))}
    (out/'source_hashes.json').write_text(json.dumps(source_hashes,indent=2))
    logging.info('Requested stages completed: %s',args.stages)

if __name__=='__main__':main()
