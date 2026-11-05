import numpy as np
from compas_fairness.data import load_cohort,split,reproduce_audit,FEATURES


def test_source_reproduction():
    d,flow,info=load_cohort()
    assert info['raw_n']==7214 and len(d)==6172
    assert reproduce_audit(d)[1]['reproduced_n']==6172
    assert info['duplicate_people']==0
    assert not {'two_year_recid','is_recid','decile_score','score_text','race','sex'} & set(FEATURES)


def test_split_identity_disjoint():
    d,_,_=load_cohort();parts=split(d,2026)
    assert sum(map(len,parts))==len(d)
    for a,b in [(0,1),(0,2),(1,2)]: assert not set(d.iloc[parts[a]].person)&set(d.iloc[parts[b]].person)
    assert all(np.array_equal(a,b) for a,b in zip(parts,split(d,2026)))
