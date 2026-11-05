"""Independently check every new intersection comparison and simulation summary."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.verify_research import independent_inverse,independent_eo
from compas_fairness.completion import control_population,cell_joints
from compas_fairness.monte_carlo import wilson

out=Path('results/completion');meta=json.loads((out/'manifest.json').read_text())
assert meta['source_sha256']==hashlib.sha256(Path('compas_fairness/completion.py').read_bytes()).hexdigest()
assert meta['predictions_sha256']==hashlib.sha256(Path('results/test_predictions.csv.gz').read_bytes()).hexdigest()
base=json.loads((out/'intersection_observed_joints.json').read_text());joints=np.array(base['joints']);summary=pd.read_csv(out/'intersection_summary.csv')
count=0
for r in summary.itertuples():
    params=pd.read_csv(out/f'intersection_{r.maximum}_parameters.csv.gz').to_numpy().reshape(-1,4,2)
    result=pd.read_csv(out/f'intersection_{r.maximum}_{r.comparator}.csv.gz');mi=base['methods'].index(r.comparator)
    assert len(result)==r.scenarios and result.feasible.sum()==r.feasible
    obs=independent_eo(joints[0])-independent_eo(joints[mi]);reversals=0
    for idx,s in enumerate(params):
        try:
            gaps=[independent_eo([independent_inverse(j,*e) for j,e in zip(m,s)]) for m in joints[[0,mi]]]
        except ValueError:
            assert not result.feasible.iloc[idx];continue
        assert result.feasible.iloc[idx]
        np.testing.assert_allclose(gaps,result.loc[idx,['eo_LR','eo_comparator']].to_numpy(dtype=float),atol=1e-12)
        diff=gaps[0]-gaps[1];rev=bool(diff*obs<0 and abs(diff)>1e-4 and abs(obs)>1e-4)
        assert rev==(result.ranking.iloc[idx]=='reversed');reversals+=rev
    assert reversals==r.reversals;count+=len(result)
frame=pd.read_csv(out/'reversal_control_replicates.csv.gz');s=pd.read_csv(out/'reversal_control_summary.csv')
assert len(frame)==12000 and frame.groupby(['kind','strength','group_probability','n','method']).rep.nunique().eq(200).all()
for r in s.itertuples():
    v=frame[(frame.kind==r.kind)&(frame.strength==r.strength)&(frame.group_probability==r.group_probability)&(frame.n==r.n)&(frame.method==r.method)]
    np.testing.assert_allclose([r.bias,r.rmse],[v.error.mean(),np.sqrt((v.error**2).mean())],atol=1e-12)
    for prefix,column in [('detection','detected_reversal'),('generating_metric_bound_coverage','known_scenario_in_bounds'),('sampling_coverage','ci_covered'),('generating_scenario_feasibility','feasible')]:
        expected=wilson(int(v[column].sum()),200)
        for key,value in expected.items():np.testing.assert_allclose(getattr(r,prefix+'_'+key),value,atol=1e-12)
# True population signs independently agree with the declared positive/stable/boundary labels.
for c in json.loads((out/'control_populations.json').read_text()):
    pop=control_population(np.array(c['base']),np.array(c['errors']),.5)
    latent=cell_joints(pop,True);observed=cell_joints(pop)
    l=independent_eo(latent[0])-independent_eo(latent[1]);r=independent_eo(observed[0])-independent_eo(observed[1])
    assert (l*r<0)==(c['kind']=='positive')
    if c['kind']=='boundary':assert abs(l)<1e-12 and abs(r)<1e-12
for stem in ['intersection_reversals','reversal_detection']:
    for ext in ['png','pdf','svg']:assert (Path('figures/completion')/(stem+'.'+ext)).stat().st_size>1000
validation={'status':'passed','independently_checked_intersection_comparisons':count,'independent_parameter_dimensions':8,'new_synthetic_datasets':6000,'repetitions_per_case':200,'summary_rows_checked':len(s),'figure_sets':2,'source_and_input_checksums':'passed'}
(out/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2))
