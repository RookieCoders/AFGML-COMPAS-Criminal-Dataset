"""Known-population validation, including covariate-dependent recording violations."""
from itertools import product
import logging
import numpy as np
import pandas as pd
from .measurement import observed_joint,eo,sweep,scenarios

PX=np.array([.35,.6])
PY=np.array([[.15,.65],[.3,.8]])
EX0=PX*(1-PY[:,1])/(1-((1-PX)*PY[:,0]+PX*PY[:,1]))
EX1=PX*PY[:,1]/((1-PX)*PY[:,0]+PX*PY[:,1])
PD=np.array([[[.1,.8],[.15,.8]],[[.2,.7],[.2,.65]]])  # method,group,x


def population(errors,violate=False):
    latent=np.zeros((2,2,2,2));observed=latent.copy()
    for m,a,x,z,d,t in product(range(2),repeat=6):
        p=(PX[a] if x else 1-PX[a])*(PY[a,x] if z else 1-PY[a,x])*(PD[m,a,x] if d else 1-PD[m,a,x])
        alpha,beta=errors[a]
        # Center within A,Ystar: marginal group alpha/beta remain exactly unchanged.
        if violate: alpha=alpha*(1+1.4*(x-EX0[a]));beta=beta*(1-1.4*(x-EX1[a]))
        pt=(1-beta if z else alpha)
        observed[m,a,d,t]+=p*(pt if t else 1-pt)
        if t==0: latent[m,a,d,z]+=p
    return latent,observed


def generate(n,errors,rng,violate=False):
    a=rng.integers(0,2,n);x=(rng.random(n)<PX[a]).astype(int)
    z=(rng.random(n)<PY[a,x]).astype(int)
    e=errors[a].copy()
    if violate: e[:,0]*=1+1.4*(x-EX0[a]);e[:,1]*=1-1.4*(x-EX1[a])
    t=(rng.random(n)<np.where(z==1,1-e[:,1],e[:,0])).astype(int)
    decisions=np.array([(rng.random(n)<PD[m,a,x]).astype(int) for m in range(2)])
    return a,x,z,t,decisions


def sample_joints(a,y,decisions,indices=None):
    if indices is not None: a,y,decisions=a[indices],y[indices],decisions[:,indices]
    return np.array([[observed_joint(y[a==g],dd[a==g]) for g in [0,1]] for dd in decisions])


def run_simulation(cfg,out):
    directory=out/'simulation';directory.mkdir(exist_ok=True)
    rows=[]; config_path=directory/'config.json'
    signature={k:cfg[k] for k in ['seed','sample_sizes','simulation_reps']}
    signature['source_sha256']=__import__('hashlib').sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest()
    signature['bootstrap_reps']=cfg.get('simulation_bootstrap',100)
    signature['tie_tolerance']=cfg.get('tie_tolerance',1e-4)
    signature['measurement_sha256']=__import__('hashlib').sha256(__import__('pathlib').Path(__file__).with_name('measurement.py').read_bytes()).hexdigest()
    reuse=config_path.exists() and __import__('json').loads(config_path.read_text())==signature
    candidates=scenarios(['g0','g1'],.2,.05)
    for setting,errors,violate in [('equal',np.array([[.1,.1],[.1,.1]]),False),
        ('unequal',np.array([[.05,.15],[.15,.05]]),False),('violation',np.array([[.05,.15],[.15,.05]]),True)]:
        pop_lat,pop_obs=population(errors,violate);truth=np.array([eo(j) for j in pop_lat]);obs_truth=np.array([eo(j) for j in pop_obs])
        _,pop_valid,_,_=sweep(pop_obs,candidates)
        true_reversal=is_reversal(truth[0]-truth[1],obs_truth[0]-obs_truth[1],signature['tie_tolerance'])
        for n in cfg['sample_sizes']:
            path=directory/f'{setting}_{n}.csv'
            if reuse and path.exists():
                previous=pd.read_csv(path)
                if len(previous)==2*cfg['simulation_reps']:
                    rows.extend(previous.to_dict('records'));continue
            for rep in range(cfg['simulation_reps']):
                rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],n,rep,{'equal':0,'unequal':1,'violation':2}[setting]]))
                a,x,z,t,dd=generate(n,errors,rng,violate)
                j=sample_joints(a,t,dd);recovered,valid,reason,_=sweep(j,errors[None])
                bounds,feas,_,_=sweep(j,candidates)
                observed=np.array([eo(q) for q in j]);empirical=np.array([eo(q) for q in sample_joints(a,z,dd)])
                boots=[]
                for b in range(signature['bootstrap_reps']):
                    idx=rng.integers(0,n,n);bj=sample_joints(a,t,dd,idx)
                    bg,bv,_,_=sweep(bj,errors[None])
                    if bv[0]: boots.append(bg[0])
                ci=np.quantile(boots,[.025,.975],axis=0) if len(boots)>10 else np.full((2,2),np.nan)
                reversal=is_reversal(recovered[0,0]-recovered[0,1],observed[0]-observed[1],signature['tie_tolerance']) if valid[0] else None
                for m in range(2):
                    lo=bounds[feas,m].min() if feas.any() else np.nan;hi=bounds[feas,m].max() if feas.any() else np.nan
                    rows.append(dict(setting=setting,n=n,rep=rep,method=m,population_latent_eo=truth[m],empirical_latent_eo=empirical[m],
                        recovered_eo=recovered[0,m],error=recovered[0,m]-truth[m],known_scenario_feasible=bool(valid[0]),reason=reason[0],
                        sensitivity_low=lo,sensitivity_high=hi,sensitivity_population_covered=bool(lo<=truth[m]<=hi),
                        sampling_ci_low=ci[0,m],sampling_ci_high=ci[1,m],sampling_ci_covered=bool(ci[0,m]<=truth[m]<=ci[1,m]),bootstrap_valid=len(boots),
                        true_reversal=true_reversal,detected_reversal=reversal,reversal_detection_correct=(reversal==true_reversal) if valid[0] else np.nan,
                        feasibility_tp=int((feas & pop_valid).sum()),feasibility_tn=int((~feas & ~pop_valid).sum()),feasibility_fp=int((feas & ~pop_valid).sum()),feasibility_fn=int((~feas & pop_valid).sum()),feasibility_population_agreement=float(np.mean(feas==pop_valid))))
            pd.DataFrame([r for r in rows if r['setting']==setting and r['n']==n]).to_csv(path,index=False)
            logging.info('Simulation %s n=%d repetitions=%d complete',setting,n,cfg['simulation_reps'])
    frame=pd.DataFrame(rows);frame.to_csv(out/'simulation.csv',index=False)
    summary=frame.groupby(['setting','n','method']).agg(bias=('error','mean'),rmse=('error',lambda v:np.sqrt(np.mean(v*v))),
        known_feasible=('known_scenario_feasible','mean'),sensitivity_coverage=('sensitivity_population_covered','mean'),
        sampling_coverage=('sampling_ci_covered','mean'),reversal_accuracy=('reversal_detection_correct','mean'),
        feasibility_agreement=('feasibility_population_agreement','mean')).reset_index()
    summary.to_csv(out/'simulation_summary.csv',index=False)
    config_path.write_text(__import__('json').dumps(signature,indent=2))
    return summary


def is_reversal(latent_difference,observed_difference,tolerance=1e-4):
    """Strict reversal excludes either observed or scenario ties, as in COMPAS sweeps."""
    return bool(latent_difference*observed_difference<0 and abs(latent_difference)>tolerance and abs(observed_difference)>tolerance)
