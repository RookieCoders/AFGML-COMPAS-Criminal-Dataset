import numpy as np
import pytest
from compas_fairness.measurement import invert,observed_joint,eo,sweep,scenarios,validate_variable_elimination


def test_known_forward_inverse():
    latent=np.array([[.4,.1],[.2,.3]])
    for alpha,beta in [(.1,.2),(0,0),(0,.2),(.2,0)]:
        mat=np.array([[1-alpha,beta],[alpha,1-beta]])
        np.testing.assert_allclose(invert(latent@mat.T,alpha,beta),latent,atol=1e-12)


@pytest.mark.parametrize('a,b',[(-.1,0),(.1,1.1),(.5,.5),(.6,.5),(np.nan,.1),(.5,.499999999)])
def test_invalid_parameters(a,b):
    with pytest.raises(ValueError): invert(np.full((2,2),.25),a,b)


def test_invalid_prevalence_and_joint():
    with pytest.raises(ValueError,match='prevalence'): invert(np.array([[.95,.01],[.03,.01]]),.1,.1)
    with pytest.raises(ValueError,match='negative_latent_joint'): invert(np.array([[.49,.01],[.01,.49]]),.1,.1)
    with pytest.raises(ValueError,match='observed_joint'): invert(np.ones((2,2)),0,0)


def test_boundary_undefined():
    j=np.array([[1.,0],[0,0]])
    np.testing.assert_allclose(invert(j,0,0),j)
    assert np.isnan(eo([j,j]))
    assert not sweep(np.array([[j,j]]),np.zeros((1,2,2)))[1][0]


def test_vectorized_agrees_with_scalar_and_common_feasibility():
    j=np.array([[[[.4,.1],[.2,.3]],[[.3,.2],[.2,.3]]],
                [[[.45,.05],[.05,.45]],[[.3,.2],[.2,.3]]]])
    s=scenarios(['a','b'],.2,.1)
    gaps,valid,reason,_=sweep(j,s)
    for i,param in enumerate(s):
        try: scalar=[eo([invert(g,*e) for g,e in zip(m,param)]) for m in j]
        except ValueError:
            assert not valid[i];continue
        assert valid[i];np.testing.assert_allclose(gaps[i],scalar)
    assert (~valid).any()


def test_variable_elimination():
    assert validate_variable_elimination()['max_error']<1e-12


def test_decision_probabilities():
    np.testing.assert_allclose(observed_joint([0,1],[.2,.7]),[[.4,.15],[.1,.35]])


def test_population_recovery():
    from compas_fairness.simulation import population
    errors=np.array([[.05,.15],[.15,.05]])
    latent,obs=population(errors)
    for m in range(2):
        for g in range(2): np.testing.assert_allclose(invert(obs[m,g],*errors[g]),latent[m,g],atol=1e-12)
    # Within-outcome decision association with recording errors appears under violations.
    _,broken=population(errors,True)
    assert np.max(abs(invert(broken[0,0],*errors[0])-latent[0,0]))>.005


def test_grid_never_exceeds_declared_region():
    grid=scenarios(['a','b'],.2,.075)
    assert grid.max() <= .2
    with pytest.raises(ValueError,match='invalid_grid_bounds'):scenarios(['a','b'],.2,0)
