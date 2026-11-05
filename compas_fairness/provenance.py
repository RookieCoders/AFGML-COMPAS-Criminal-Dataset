"""Content-addressed model-cache guards and append-only stage records."""
import hashlib,json
from pathlib import Path
import pandas as pd


def file_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model_key(data,parts):
    """Include all source input values, split ordering, model/data code and exact dependency lock."""
    content={'data':hashlib.sha256(pd.util.hash_pandas_object(data,index=True).values.tobytes()).hexdigest(),
        'parts':[p.tolist() for p in parts],
        'code':{name:file_hash(Path(__file__).with_name(name)) for name in ['models.py','data.py']},
        'dependencies':file_hash('requirements.txt')}
    return hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()


def write_model_metadata(checkpoint,data,parts):
    Path(str(checkpoint)+'.json').write_text(json.dumps({'input_key':model_key(data,parts),'checkpoint_sha256':file_hash(checkpoint)},indent=2))


def validate_model_metadata(checkpoint,data,parts):
    metadata=Path(str(checkpoint)+'.json')
    if not metadata.exists():raise ValueError('unverified_model_cache: refit or verify/register the legacy checkpoint')
    value=json.loads(metadata.read_text())
    if value['input_key']!=model_key(data,parts) or value['checkpoint_sha256']!=file_hash(checkpoint):
        raise ValueError('stale_or_modified_model_cache: refit before reuse')
