"""Independent numerical audit using generic linear solves, saved people and decisions.

No production inversion, sweep, EO or cohort helper is used in reversal verification.
"""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd


def independent_inverse(j,alpha,beta):
    if not (np.isfinite([alpha,beta]).all() and 0<=alpha<=1 and 0<=beta<=1 and 1-alpha-beta>1e-8):
        raise ValueError('matrix')
    matrix=np.array([[1-alpha,beta],[alpha,1-beta]])
    recovered=np.linalg.solve(matrix,np.asarray(j).T).T
    if recovered.min() < -1e-10 or abs(recovered.sum()-1)>1e-10:raise ValueError('joint')
    np.testing.assert_allclose(recovered@matrix.T,j,atol=1e-10,rtol=0)
    if np.any(recovered.sum(axis=0)<=1e-10):raise ValueError('undefined')
    return recovered


def independent_eo(joints):
    r=np.array([j[1]/j.sum(axis=0) for j in joints])
    return max(max(r[:,0])-min(r[:,0]),max(r[:,1])-min(r[:,1]))


def joint(y,d):
    n=len(y)
    return np.array([[sum((1-d)[y==0]),sum((1-d)[y==1])],[sum(d[y==0]),sum(d[y==1])]])/n


def run():
    out=Path('results/verification');out.mkdir(exist_ok=True)
    p=pd.read_csv('results/test_predictions.csv.gz');summ=pd.read_csv('results/sensitivity_summary.csv')
    evidence=[];representative=[]
    for axis in ['sex','race']:
        names=['LR','EO_'+axis]
        mask=np.ones(len(p),dtype=bool) if axis=='sex' else p.race.isin(['African-American','Caucasian']).to_numpy()
        groups=sorted(p.loc[mask,axis].unique())
        js=np.array([[joint(p.loc[mask & (p[axis]==g),'outcome'].to_numpy(),p.loc[mask & (p[axis]==g),name+'__decision'].to_numpy()) for g in groups] for name in names])
        observed=np.array([independent_eo(j) for j in js]);observed_difference=observed[0]-observed[1]
        saved=pd.read_csv('results/sensitivity/'+axis+'__primary__LR__EO_'+axis+'.csv.gz')
        results=[];feasible=0;reversed_count=0
        # Independently generate all 9^4 combinations, not the saved grid rows.
        for i,values in enumerate(itertools.product([k/40 for k in range(9)],repeat=4)):
            parameters=np.array(values).reshape(2,2)
            try:
                latent=np.array([[independent_inverse(j,*s) for j,s in zip(m,parameters)] for m in js])
                gaps=np.array([independent_eo(m) for m in latent]);feasible+=1
            except ValueError:
                assert not saved.feasible.iloc[i];continue
            delta=gaps[0]-gaps[1]
            rev=bool(delta*observed_difference<0 and abs(delta)>1e-4 and abs(observed_difference)>1e-4)
            reversed_count+=rev
            np.testing.assert_allclose(gaps,saved.loc[i,['eo_left','eo_right']].to_numpy(dtype=float),atol=1e-12)
            assert rev==(saved.ranking.iloc[i]=='reversed')
            if axis=='sex' and np.allclose(parameters,[[.175,.1],[.15,0]]):
                for mi,name in enumerate(names):
                    for gidx,g in enumerate(groups):
                        z=latent[mi,gidx];mat=np.array([[1-parameters[gidx,0],parameters[gidx,1]],[parameters[gidx,0],1-parameters[gidx,1]]])
                        representative.append(dict(method=name,group=g,observed_joint=js[mi,gidx].tolist(),latent_joint=z.tolist(),reconstructed=(z@mat.T).tolist(),fpr=float(z[1,0]/z[:,0].sum()),tpr=float(z[1,1]/z[:,1].sum()),eo=float(gaps[mi])))
        evidence.append(dict(axis=axis,observed_eo=observed.tolist(),feasible=feasible,reversed=reversed_count,fraction=reversed_count/feasible))
    # Independent resampling audit of original saved bootstrap, all 1,000 replicates.
    boot=pd.read_csv('results/bootstrap.csv.gz');rng=np.random.default_rng(2026+400);max_error=0.
    for b in range(1000):
        idx=rng.integers(0,len(p),len(p));sample=p.iloc[idx]
        for axis in ['sex','race','intersection']:
            eligible=p if axis=='sex' else p[p.race.isin(['African-American','Caucasian'])]
            counts=pd.crosstab(eligible[axis],eligible.outcome).reindex(columns=[0,1],fill_value=0)
            groups=sorted(counts.index[counts.min(axis=1)>=20])
            bp=sample[sample[axis].isin(groups)]
            names=['LR','RW_'+axis,'EO_'+axis,'GBT','BN','COMPAS']
            js=np.array([[joint(bp.loc[bp[axis]==g,'outcome'].to_numpy(),bp.loc[bp[axis]==g,name+'__decision'].to_numpy()) for g in groups] for name in names])
            scenarios={'observed':np.zeros((len(groups),2)),'equal_05':np.full((len(groups),2),.05),
                'contrast':np.array([[.1,.05] if ('Caucasian' in g or g=='Male') else [.025,.1] for g in groups])}
            for label,errors in scenarios.items():
                try:gaps=np.array([independent_eo([independent_inverse(j,*s) for j,s in zip(m,errors)]) for m in js])
                except ValueError:
                    assert boot[(boot.replicate==b)&(boot.axis==axis)&(boot.scenario==label)].eo.isna().all();continue
                v=boot[(boot.replicate==b)&(boot.axis==axis)&(boot.scenario==label)].set_index('method').loc[names]
                max_error=max(max_error,float(np.max(abs(gaps-v.eo.to_numpy()))))
                np.testing.assert_allclose(gaps,v.eo,atol=1e-12)
                np.testing.assert_allclose(gaps-gaps[0],v.difference_from_LR,atol=1e-12)
    intervals=pd.read_csv('results/bootstrap_intervals.csv')
    for row in intervals.itertuples():
        v=boot[(boot.axis==row.axis)&(boot.method==row.method)&(boot.scenario==row.scenario)][row.metric]
        np.testing.assert_allclose([row.low,row.high],v.quantile([.025,.975]),atol=1e-12)
    # Original synthetic aggregate statistics from retained replicate outcomes.
    sim=pd.read_csv('results/simulation.csv');ss=pd.read_csv('results/simulation_summary.csv')
    for r in ss.itertuples():
        v=sim[(sim.setting==r.setting)&(sim.n==r.n)&(sim.method==r.method)]
        np.testing.assert_allclose([r.bias,r.rmse,r.sampling_coverage,r.sensitivity_coverage],[v.error.mean(),np.sqrt((v.error**2).mean()),v.sampling_ci_covered.mean(),v.sensitivity_population_covered.mean()],atol=1e-12)
    output={'reversals':evidence,'representative_sex_scenario':representative,'bootstrap_replicates_independently_checked':1000,'bootstrap_max_absolute_error':max_error,'bootstrap_intervals':'all quantiles verified','original_simulation_summaries':'verified from replicate rows'}
    (out/'independent_numerical_audit.json').write_text(json.dumps(output,indent=2));print(json.dumps(evidence,indent=2))

if __name__=='__main__':run()
