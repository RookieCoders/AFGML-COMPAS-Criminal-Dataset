"""Independent intersection errors and finite-sample reversal controls.

All analyses use retained predictions or synthetic population cells; no original models are retrained.
"""
from itertools import product
from pathlib import Path
import hashlib,json,logging
import numpy as np
import pandas as pd
from scipy.stats import qmc
from .measurement import observed_joint,sweep,eo
from .monte_carlo import wilson


def independent_design(groups,power,maximum,seed,overrides=None):
    """Space-filling 2G dimensional Sobol design plus identity; each group's two rates vary."""
    samples=qmc.Sobol(2*len(groups),scramble=True,seed=seed).random_base2(power).reshape(-1,len(groups),2)*maximum
    samples=np.concatenate([np.zeros((1,len(groups),2)),samples])
    for group,values in (overrides or {}).items():
        if group not in groups or len(values)!=2 or not np.isfinite(values).all() or min(values)<0 or max(values)>1:raise ValueError('invalid_group_override')
        samples[:,groups.index(group)]=values
    return samples


def intersection(cfg,out):
    p=pd.read_csv('results/test_predictions.csv.gz');p=p[p.race.isin(['African-American','Caucasian'])]
    counts=pd.crosstab(p.intersection,p.outcome).reindex(columns=[0,1],fill_value=0)
    groups=sorted(counts.index[counts.min(axis=1)>=20]);assert len(groups)==4
    names=['LR','RW_intersection','EO_intersection','GBT','BN','COMPAS']
    joints=np.array([[observed_joint(p.loc[p.intersection==g,'outcome'],p.loc[p.intersection==g,n+'__decision']) for g in groups] for n in names])
    summary=[]
    for maximum in cfg['intersection_maxima']:
        s=independent_design(groups,cfg['sobol_power'],maximum,cfg['seed'])
        label=f'intersection_{maximum}'
        params=pd.DataFrame(s.reshape(len(s),-1),columns=[f'{g}:{parameter}' for g in groups for parameter in ['alpha','beta']]);params.to_csv(out/(label+'_parameters.csv.gz'),index=False)
        for i in range(1,len(names)):
            gaps,valid,reason,r=sweep(joints[[0,i]],s);observed=eo(joints[0])-eo(joints[i]);difference=gaps[:,0]-gaps[:,1]
            reversed_mask=valid & (difference*observed<0)&(abs(difference)>cfg['tie_tolerance'])&(abs(observed)>cfg['tie_tolerance'])
            rank=np.where(~valid,'infeasible',np.where(abs(difference)<=cfg['tie_tolerance'],'tie',np.where(reversed_mask,'reversed','stable')))
            if abs(observed)<=cfg['tie_tolerance']:rank[valid & (abs(difference)>cfg['tie_tolerance'])]='observed_tie_broken'
            tab=pd.DataFrame({'scenario':np.arange(len(s)),'feasible':valid,'reason':reason,'eo_LR':gaps[:,0],'eo_comparator':gaps[:,1],'difference':difference,'ranking':rank})
            for m,method in enumerate(['LR',names[i]]):
                for gidx,g in enumerate(groups):
                    tab[f'{method}:{g}:fpr']=r[:,m,gidx,0];tab[f'{method}:{g}:tpr']=r[:,m,gidx,1]
            tab.to_csv(out/(label+'_'+names[i]+'.csv.gz'),index=False)
            summary.append(dict(maximum=maximum,comparator=names[i],groups=';'.join(groups),n=len(p),scenarios=len(s),feasible=int(valid.sum()),reversals=int(reversed_mask.sum()),reversal_fraction=float(reversed_mask[valid].mean()),ties=int(np.sum(rank=='tie')),min_difference=float(np.nanmin(difference)),max_difference=float(np.nanmax(difference))))
    pd.DataFrame(summary).to_csv(out/'intersection_summary.csv',index=False)
    (out/'intersection_observed_joints.json').write_text(json.dumps({'groups':groups,'methods':names,'joints':joints.tolist()},indent=2))


# Category ordering: A,X,Ystar,Ytilde,D0,D1. Counts retain every variable.
CELLS=np.array(list(product(range(2),repeat=6)))

def control_population(base,errors,group_probability):
    a,x,z,t,d0,d1=CELLS.T
    prob_a=np.where(a==0,group_probability,1-group_probability)
    pi=np.array([.3,.6])[a]+.08*(2*x-1)
    pd0=base[0,a,z]+.05*(2*x-1);pd1=base[1,a,z]+.05*(2*x-1)
    pt=np.where(z==1,1-errors[a,1],errors[a,0])
    probabilities=prob_a*.5*np.where(z,pi,1-pi)*np.where(t,pt,1-pt)*np.where(d0,pd0,1-pd0)*np.where(d1,pd1,1-pd1)
    assert np.isclose(probabilities.sum(),1) and probabilities.min()>=0
    return probabilities


def cell_joints(counts,latent=False):
    """Accept counts shape (...,64); normalize within A. Also used for vectorized paired bootstrap."""
    counts=np.asarray(counts);result=np.empty(counts.shape[:-1]+(2,2,2,2))
    ycolumn=2 if latent else 3
    for m,g,d,y in product(range(2),repeat=4):
        mask=(CELLS[:,0]==g)&(CELLS[:,4+m]==d)&(CELLS[:,ycolumn]==y)
        denom=counts[...,CELLS[:,0]==g].sum(axis=-1)
        result[...,m,g,d,y]=np.divide(counts[...,mask].sum(axis=-1),denom,out=np.full_like(denom,np.nan,dtype=float),where=denom>0)
    return result


def choose_control(kind,strength):
    errors=np.array([[.2,0],[0,.2]])*strength
    rng=np.random.default_rng(410)
    if kind=='boundary':
        base=np.array([[[.2,.7],[.3,.8]]]*2);return base,np.zeros((2,2))
    for _ in range(100000):
        base=rng.uniform(.1,.9,(2,2,2));pop=control_population(base,errors,.5)
        truth=np.array([eo(j) for j in cell_joints(pop,True)]);obs=np.array([eo(j) for j in cell_joints(pop)])
        d=truth[0]-truth[1];r=obs[0]-obs[1]
        if abs(d)>=.025 and abs(r)>=.01 and ((d*r<0)==(kind=='positive')):return base,errors
    raise RuntimeError('No prespecified control found')


def simulate_controls(cfg,out):
    rows=[];controls=[]
    cases=[(k,s) for k in ['positive','negative'] for s in cfg['noise_strengths']]+[('boundary',cfg['boundary_noise_strength'])]
    for case_id,(kind,strength) in enumerate(cases):
        base,errors=choose_control(kind,strength);controls.append({'kind':kind,'strength':strength,'base':base.tolist(),'errors':errors.tolist()})
        for probability,n in product(cfg['group_probabilities'],cfg['sample_sizes']):
            pop=control_population(base,errors,probability);true_joints=cell_joints(pop,True);truth=np.array([eo(j) for j in true_joints]);obs=np.array([eo(j) for j in cell_joints(pop)])
            for rep in range(cfg['simulation_reps']):
                rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],case_id,int(probability*1000),n,rep]))
                counts=rng.multinomial(n,pop);j=cell_joints(counts)
                recovered,valid,reason,_=sweep(j,errors[None]);observed=np.array([eo(g) for g in j]);delta=recovered[0,0]-recovered[0,1]
                detected=bool(valid[0] and delta*(observed[0]-observed[1])<0 and abs(delta)>cfg['tie_tolerance'] and abs(observed[0]-observed[1])>cfg['tie_tolerance'])
                # Exact multinomial person bootstrap of categorical records, paired for both methods.
                boots=rng.multinomial(n,counts/n,size=200);bj=cell_joints(boots)
                # sweep vectorizes scenarios, so invert each bootstrap analytically (same group errors).
                a,b=errors.T;det=1-a-b
                z0=((1-b[None,None,:,None])*bj[...,0]-b[None,None,:,None]*bj[...,1])/det[None,None,:,None]
                z1=((1-a[None,None,:,None])*bj[...,1]-a[None,None,:,None]*bj[...,0])/det[None,None,:,None]
                z=np.stack([z0,z1],axis=-1);denom=z.sum(axis=3)
                rr=np.divide(z[:,:,:,1,:],denom,out=np.full_like(denom,np.nan),where=denom>1e-10)
                good=(z>=-1e-10).all(axis=(1,2,3,4)) & np.isfinite(rr).all(axis=(1,2,3))
                bg=np.ptp(rr,axis=2).max(axis=2);ci=np.quantile(bg[good],[.025,.975],axis=0) if good.sum()>10 else np.full((2,2),np.nan)
                # Independent 8? Here two-group full coarse 4D sensitivity bounds, include generating point.
                noise=np.array(list(product([0,.1,.2],repeat=4))).reshape(-1,2,2);noise=np.concatenate([noise,errors[None]])
                gaps,feasible,_,_=sweep(j,noise)
                for m in range(2):
                    lo=np.nanmin(gaps[:,m]);hi=np.nanmax(gaps[:,m])
                    rows.append(dict(kind=kind,strength=strength,group_probability=probability,n=n,rep=rep,method=m,true_reversal=kind=='positive',detected_reversal=detected,feasible=bool(valid[0]),reason=reason[0],true_eo=truth[m],recovered_eo=recovered[0,m],error=recovered[0,m]-truth[m],known_scenario_in_bounds=bool(lo<=truth[m]<=hi),ci_covered=bool(ci[0,m]<=truth[m]<=ci[1,m]),bootstrap_valid=int(good.sum())))
            logging.info('Reversal controls %s strength=%s p=%s n=%s complete',kind,strength,probability,n)
    frame=pd.DataFrame(rows);frame.to_csv(out/'reversal_control_replicates.csv.gz',index=False)
    (out/'control_populations.json').write_text(json.dumps(controls,indent=2))
    summary=[]
    for key,v in frame.groupby(['kind','strength','group_probability','n','method']):
        row=dict(zip(['kind','strength','group_probability','n','method'],key));row.update(bias=v.error.mean(),rmse=np.sqrt((v.error**2).mean()),infeasible=int((~v.feasible).sum()))
        for metric,column in [('detection','detected_reversal'),('generating_metric_bound_coverage','known_scenario_in_bounds'),('sampling_coverage','ci_covered'),('generating_scenario_feasibility','feasible')]:
            row.update({metric+'_'+k:value for k,value in wilson(int(v[column].sum()),len(v)).items()})
        row['interpretation']='sensitivity' if key[0]=='positive' else 'false_reversal_frequency'
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'reversal_control_summary.csv',index=False)


def main():
    logging.basicConfig(level=logging.INFO,handlers=[logging.StreamHandler(),logging.FileHandler('results/completion/run.log')])
    cfg=json.loads(Path('configs/completion.json').read_text());out=Path('results/completion')
    intersection(cfg,out);simulate_controls(cfg,out)
    (out/'manifest.json').write_text(json.dumps({'config':cfg,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'predictions_sha256':hashlib.sha256(Path('results/test_predictions.csv.gz').read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
