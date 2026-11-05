import numpy as np
import pandas as pd
from compas_fairness.uncertainty import run_bootstrap
from compas_fairness.measurement import sweep,invert


def test_paired_bootstrap_identical_methods(tmp_path):
    rows=[]
    for race in ['African-American','Caucasian']:
        for sex in ['Female','Male']:
            for y in [0,1]:
                rows.extend([dict(race=race,sex=sex,intersection=race+' / '+sex,two_year_recid=y)]*30)
    d=pd.DataFrame(rows);n=len(d);prob=np.tile([.25,.75],n//2)
    names=['LR','GBT','BN','COMPAS']+[k+'_'+a for k in ['EO','RW'] for a in ['race','sex','intersection']]
    pred={name:{'score':prob,'decision':prob} for name in names}
    run_bootstrap(d,pred,{'seed':2,'bootstrap':5,'sparse_min_class':20},tmp_path)
    intervals=pd.read_csv(tmp_path/'bootstrap_intervals.csv')
    dif=intervals[intervals.metric=='difference_from_LR']
    np.testing.assert_allclose(dif[['low','high']].to_numpy(),0)
    assert intervals.valid.eq(5).all()
    assert len(pd.read_csv(tmp_path/'group_bootstrap_intervals.csv'))>0


def test_invalid_observed_vector_input():
    import pytest
    with pytest.raises(ValueError,match='invalid_observed_joints'):
        sweep(np.full((2,2,2,2),.5),np.zeros((1,2,2)))


def test_violation_retains_marginal_error_rates():
    from compas_fairness.simulation import population
    errors=np.array([[.05,.15],[.15,.05]])
    latent,observed=population(errors,True)
    for g in range(2):
        pi=latent[0,g,:,1].sum();q=observed[0,g,:,1].sum()
        assert np.isclose(q,errors[g,0]*(1-pi)+(1-errors[g,1])*pi)
    assert np.max(abs(invert(observed[0,0],*errors[0])-latent[0,0]))>.005
