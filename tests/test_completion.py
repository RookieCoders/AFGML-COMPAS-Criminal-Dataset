import numpy as np
import pandas as pd
import pytest
from compas_fairness.completion import independent_design,choose_control,control_population,cell_joints
from compas_fairness.measurement import eo,sweep


def test_independent_intersection_parameters_and_overrides():
    groups=['BlackFemale','BlackMale','WhiteFemale','WhiteMale'];s=independent_design(groups,6,.2,7)
    assert s.shape==(65,4,2) and not s[0].any()
    assert np.all(s>=0) and np.all(s<=.2)
    assert len(np.unique(s[1:].reshape(64,8),axis=1))>1
    assert not np.array_equal(s[:,0],s[:,1])
    overridden=independent_design(groups,6,.2,7,{'BlackFemale':[.1,.05]})
    np.testing.assert_allclose(overridden[:,0],np.tile([.1,.05],(65,1)))
    with pytest.raises(ValueError):independent_design(groups,6,.2,7,{'unknown':[0,0]})

@pytest.mark.parametrize('kind,strength',[('positive',.5),('positive',1),('negative',.5),('negative',1),('boundary',0)])
def test_selected_population_ground_truth_and_exact_recovery(kind,strength):
    base,errors=choose_control(kind,strength);population=control_population(base,errors,.2)
    observed=cell_joints(population);latent=cell_joints(population,True)
    r=eo(observed[0])-eo(observed[1]);truth=eo(latent[0])-eo(latent[1])
    assert ((r*truth<0)==(kind=='positive'))
    if kind=='boundary':assert abs(r)<1e-12 and abs(truth)<1e-12
    gaps,valid,_,_=sweep(observed,errors[None]);assert valid[0]
    np.testing.assert_allclose(gaps[0],[eo(m) for m in latent],atol=1e-12)


def test_person_bootstrap_on_cell_counts_equals_expanded_people():
    # A categorical bootstrap is the count representation of sampling the same people for both methods.
    counts=np.zeros(64,dtype=int);counts[[0,7,32,63]]=[3,2,4,1]
    expanded=np.repeat(np.arange(64),counts)
    sample=np.random.default_rng(99).choice(expanded,len(expanded))
    recovered_counts=np.bincount(sample,minlength=64)
    from compas_fairness.completion import CELLS
    from compas_fairness.measurement import observed_joint
    j=cell_joints(recovered_counts)
    for m in [0,1]:
        for g in [0,1]:
            people=CELLS[sample];p=people[people[:,0]==g]
            np.testing.assert_allclose(j[m,g],observed_joint(p[:,3],p[:,4+m]),atol=1e-12)


def test_cache_invalidates_on_changed_input_and_checkpoint(tmp_path):
    from compas_fairness.provenance import write_model_metadata,validate_model_metadata
    checkpoint=tmp_path/'model';checkpoint.write_bytes(b'example')
    d=pd.DataFrame({'x':[1,2]});parts=[np.array([0]),np.array([1])]
    write_model_metadata(checkpoint,d,parts);validate_model_metadata(checkpoint,d,parts)
    with pytest.raises(ValueError):validate_model_metadata(checkpoint,d.assign(x=[1,3]),parts)
    checkpoint.write_bytes(b'modified')
    with pytest.raises(ValueError):validate_model_metadata(checkpoint,d,parts)
