"""Reproduce the notebook cohort; preserve raw records and person-disjoint partitions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.formula.api as smf
import statsmodels.api as sm

FEATURES=['age','priors_count','juv_fel_count','juv_misd_count','juv_other_count','c_charge_degree']


def load_cohort(root=Path('.'), window=30):
    raw=pd.read_csv(root/'data/raw/compas-scores-two-years.csv',keep_default_na=False,na_values=[''])
    d=raw.copy(); flow=[{'filter':'released','n':len(d)}]
    conditions=[('screening <= window',lambda x: x.days_b_screening_arrest<=window),
                ('screening >= -window',lambda x:x.days_b_screening_arrest>=-window),
                ('valid recidivism flag',lambda x:x.is_recid!=-1),
                ('not ordinary traffic',lambda x:x.c_charge_degree!='O'),
                ('valid score category',lambda x:x.score_text.notna() & (x.score_text!='N/A'))]
    for name,mask in conditions:
        d=d.loc[mask(d)].copy();flow.append({'filter':name,'n':len(d)})
    # Released IDs are unique, but stable identity also guards duplicate people across IDs.
    keys=d[['first','last','dob']].fillna('').astype(str).agg('|'.join,axis=1)
    if (d[['first','last','dob']].isna().any(axis=1)).any():
        raise ValueError('missing_person_identity')
    d['person']=keys.map(lambda s:hashlib.sha256(s.lower().encode()).hexdigest())
    duplicates=int(d.person.duplicated().sum())
    d=d.sort_values('id').drop_duplicates('person').copy()
    flow.append({'filter':'person deduplication: first released ID','n':len(d)})
    d['intersection']=d.race+' / '+d.sex
    d['age_band']=pd.cut(d.age,[0,25,45,200],right=False,labels=['under25','25to44','45plus']).astype(str)
    if not d.two_year_recid.isin([0,1]).all(): raise ValueError('invalid_target')
    info={'raw_n':len(raw),'filtered_n':len(d),'duplicate_people':duplicates,
          'duplicate_ids':int(raw.id.duplicated().sum()),'missing_raw':raw.isna().sum().to_dict(),
          'invalid_scores':int((~raw.decile_score.between(1,10)).sum()),
          'outcome_counts':d.two_year_recid.value_counts().to_dict(),
          'missing_features':d[FEATURES].isna().sum().to_dict()}
    return d.reset_index(drop=True),pd.DataFrame(flow),info


def split(d,seed):
    strata=d.race+'|'+d.sex+'|'+d.two_year_recid.astype(str)
    # Sparse racial groups cannot support 3-way joint stratification; use outcome/sex.
    strata=d.sex+'|'+d.two_year_recid.astype(str)
    train,other=train_test_split(np.arange(len(d)),test_size=.4,stratify=strata,random_state=seed)
    val,test=train_test_split(other,test_size=.5,stratify=strata.iloc[other],random_state=seed+1)
    assert not (set(d.iloc[train].person)&set(d.iloc[test].person))
    assert not (set(d.iloc[train].person)&set(d.iloc[val].person))
    assert not (set(d.iloc[val].person)&set(d.iloc[test].person))
    return train,val,test


def reproduce_audit(d):
    """Exactly reproduce notebook cell 21, including outcome adjustment only for this audit."""
    x=d.copy();x['high']=(x.score_text!='Low').astype(int)
    formula='high ~ C(sex, Treatment("Male")) + C(age_cat, Treatment("25 - 45")) + C(race, Treatment("Caucasian")) + priors_count + C(c_charge_degree, Treatment("F")) + two_year_recid'
    fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit()
    out=pd.DataFrame({'coefficient':fit.params,'se':fit.bse,'p':fit.pvalues})
    term=[t for t in fit.params.index if 'African-American' in t][0]
    assert len(d)==6172, 'Source cohort differs: investigate rather than alter filters'
    assert abs(fit.params[term]-.47721)<1e-5
    return out,{'notebook_black_coefficient':.47721,'reproduced_black_coefficient':float(fit.params[term]),
                'notebook_n':6172,'reproduced_n':len(d),'odds_ratio':float(np.exp(fit.params[term]))}
