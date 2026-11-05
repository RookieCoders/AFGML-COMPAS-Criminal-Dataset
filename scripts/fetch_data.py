"""Download immutable upstream files with normal TLS and verify recorded checksums."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import quote

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'data/raw/provenance.json').read_text())
for name,expected in manifest['sha256'].items():
    path=root/'data/raw'/name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected:
        print('Verified',name);continue
    url=f"https://raw.githubusercontent.com/propublica/compas-analysis/{manifest['commit']}/{quote(name)}"
    with urlopen(url,timeout=60) as response: content=response.read()
    if hashlib.sha256(content).hexdigest()!=expected:raise ValueError('Checksum mismatch: '+name)
    if path.exists():raise FileExistsError('Refusing to overwrite changed raw file: '+str(path))
    path.write_bytes(content);print('Downloaded and verified',name)
