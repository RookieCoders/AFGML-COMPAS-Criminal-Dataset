import numpy as np
import pandas as pd
import pytest
from compas_fairness.measurement import observed_joint,sweep,eo,invert
from compas_fairness.sensitivity import analysis_cohort
from compas_fairness.simulation import is_reversal

@pytest.mark.parametrize('y,d',[([[0],[1]],[0,1]),([0,1],[.5]),([0,1],[[0],[1]])])
def test_reject_broadcasted_decisions(y,d):
    with pytest.raises(ValueError):observed_joint(y,d)

@pytest.mark.parametrize('shape',[(1,1,2),(1,2,1),(2,2)])
def test_reject_broadcasted_scenarios(shape):
    with pytest.raises(ValueError):sweep(np.full((2,2,2,2),.25),np.zeros(shape))

def test_missing_outcome_not_eligible():
    d=pd.DataFrame({'race':['African-American']*40+['Caucasian']*40,'two_year_recid':[0]*80})
    mask,groups=analysis_cohort(d,'race');assert not mask.any() and not groups

def test_ties_are_not_simulation_reversals():
    assert not is_reversal(-1e-8,.2)
    assert not is_reversal(-.2,1e-8)
    assert is_reversal(-.2,.1)

def test_generic_linear_solve_matches_vectorized_random_cases():
    from scripts.verify_research import independent_inverse,independent_eo
    rng=np.random.default_rng(55)
    for _ in range(100):
        js=rng.dirichlet(np.ones(4),size=(2,3)).reshape(2,3,2,2)
        scenarios=rng.uniform(0,.45,size=(15,3,2))
        gaps,valid,_,_=sweep(js,scenarios)
        for i,s in enumerate(scenarios):
            try:expected=[independent_eo([independent_inverse(j,*e) for j,e in zip(m,s)]) for m in js]
            except ValueError:assert not valid[i];continue
            assert valid[i];np.testing.assert_allclose(gaps[i],expected,atol=1e-12)

def test_absent_bootstrap_group_records_all_scenarios(tmp_path,monkeypatch):
    from compas_fairness.uncertainty import run_bootstrap
    class Fixed:
        def integers(self,low,high,size):return np.tile([0,1],size//2)
    monkeypatch.setattr(np.random,'default_rng',lambda seed:Fixed())
    rows=[dict(race=r,sex=s,intersection=r+' / '+s,two_year_recid=y) for r in ['African-American','Caucasian'] for s in ['Female','Male'] for y in [0,1]]
    d=pd.DataFrame(rows);p=np.tile([.25,.75],4)
    names=['LR','GBT','BN','COMPAS']+[k+'_'+a for k in ['EO','RW'] for a in ['race','sex','intersection']]
    run_bootstrap(d,{n:{'score':p,'decision':p} for n in names},{'seed':0,'bootstrap':1,'sparse_min_class':1},tmp_path)
    result=pd.read_csv(tmp_path/'bootstrap.csv.gz')
    assert len(result)==54 and set(result.scenario)=={'observed','equal_05','contrast'}
    assert result.reason.eq('absent_group').all() and result.eo.isna().all()

def test_known_positive_population_reversal():
    rng=np.random.default_rng(88);params=np.array([[.2,0],[0,.2]])
    for _ in range(500):
        # Same latent prevalence across methods within each group; distinct decision mechanisms.
        latent=np.empty((2,2,2,2))
        for m in range(2):
            for g,pi in enumerate([.3,.6]):
                fpr,tpr=rng.uniform(.05,.95,2)
                latent[m,g]=[[(1-pi)*(1-fpr),pi*(1-tpr)],[(1-pi)*fpr,pi*tpr]]
        observed=np.array([[j@np.array([[1-a,b],[a,1-b]]).T for j,(a,b) in zip(m,params)] for m in latent])
        true=eo(latent[0])-eo(latent[1]);recorded=eo(observed[0])-eo(observed[1])
        if is_reversal(true,recorded):
            gaps,valid,_,_=sweep(observed,params[None]);assert valid[0]
            assert is_reversal(gaps[0,0]-gaps[0,1],recorded)
            np.testing.assert_allclose(gaps[0],[eo(m) for m in latent],atol=1e-12)
            break
    else:raise AssertionError('No positive control')

def test_robustness_uses_same_people_for_performance_and_eo():
    from compas_fairness.robustness import robustness_row
    d=pd.DataFrame({'race':['African-American']*2+['Caucasian']*2+['Other']*4,'two_year_recid':[0,1,0,1,0,1,0,1]})
    decision=np.array([0,1,0,1,1,0,1,0]);score=np.where(decision,.8,.2)
    row=robustness_row('test','race',decision,score,d,1)
    assert row['n']==4 and row['accuracy']==1 and row['eo']==0

def test_monte_carlo_intervals_handle_boundary_success_rates():
    from compas_fairness.monte_carlo import wilson
    from statsmodels.stats.proportion import proportion_confint
    for k in [0,100,200]:
        v=wilson(k,200);np.testing.assert_allclose([v['mc_low'],v['mc_high']],proportion_confint(k,200,method='wilson'),atol=1e-12)
    assert wilson(0,200)['mc_high']>0 and wilson(200,200)['mc_low']<1
