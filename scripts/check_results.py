"""Audit generated artifacts for internal consistency; fail on stale or incorrect outputs."""
import json
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

out=Path('results');cfg=json.loads((out/'run_manifest.json').read_text())['config']
summary=pd.read_csv(out/'sensitivity_summary.csv');count=0
for row in summary.itertuples():
    t=pd.read_csv(out/'sensitivity'/row.file)
    assert len(t)==row.scenarios and t.feasible.sum()==row.feasible
    assert (t.ranking=='reversed').sum()==row.reversed
    assert t.feasible.iloc[0]
    np.testing.assert_allclose(t.loc[0,['eo_left','eo_right']].to_numpy(dtype=float),[row.observed_left,row.observed_right],atol=1e-10)
    rev=t[t.ranking=='reversed']
    assert (rev.difference*row.observed_difference<0).all()
    assert (rev.difference.abs()>cfg['tie_tolerance']).all()
    rates=t.loc[t.feasible,[c for c in t if c.startswith(('fpr_','tpr_'))]].to_numpy()
    assert np.isfinite(rates).all() and rates.min()>=-1e-10 and rates.max()<=1+1e-10
    count+=len(t)
pred=pd.read_csv(out/'test_predictions.csv.gz');parts=pd.read_csv(out/'partitions.csv')
assert len(pred)==parts.partition.eq('test').sum() and pred.person.is_unique
assert parts.person.is_unique and set(pred.person)==set(parts.loc[parts.partition=='test','person'])
bs=pd.read_csv(out/'bootstrap_intervals.csv')
assert (bs.valid+bs.invalid).eq(cfg['bootstrap']).all()
sim=pd.read_csv(out/'simulation.csv')
assert len(sim)==3*len(cfg['sample_sizes'])*cfg['simulation_reps']*2
assert sim.groupby(['setting','n','method']).rep.nunique().eq(cfg['simulation_reps']).all()
assert len(list(Path('figures').glob('*.png')))==14
assert len(list(Path('figures').glob('*.pdf')))==14
assert len(list(Path('figures').glob('*.svg')))==14
assert (out/'run_manifest.json').exists() and Path('docs/FINAL_REPORT.md').stat().st_size>1000
hashes=json.loads((out/'source_hashes.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
result={'status':'passed','sensitivity_tables':len(summary),'scenario_comparisons':count,'synthetic_datasets':len(sim)//2,
        'bootstrap_replicates':cfg['bootstrap'],'test_people':len(pred),'figure_sets':14,'source_hashes':'verified'}
(out/'artifact_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
