"""Check v10 preservation while allowing the six intentional workspace/handoff edits."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[2]
old=json.loads((root/'verification/scope-expansion/preservation-final.json').read_text())
model_baseline=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
artifacts=[(Path(row['path']),row['sha256']) for row in old['artifacts']]
artifacts.append((root.parent/'TrustLens-professional-20261023-context-v10-review.zip','acfe23d42014b5d85917de7c575c716686bb47c908e8732942ae57999abfc57e'))
results={'artifacts':[{'path':str(path),'sha256':expected,'matches':sha(path)==expected} for path,expected in artifacts]}
results['original_source']=[{'path':row['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/row['path'])==row['expected_sha256']} for row in model_baseline['original_source_evidence']]
results['protected_files']=[{'path':row['path'],'sha256':row['sha256'],'matches':sha(root/row['path'])==row['sha256']} for row in old['protected_relative_to_v9']]
with zipfile.ZipFile(root.parent/'TrustLens-professional-20261023-context-v10-review.zip') as archive:
    manifest=json.loads(archive.read('SOURCE_MANIFEST.json'))
allowed={'static/claim-review.js','static/claim-review.html','static/claim-review.css','README.md','tasks/todo.md','scripts/package.py'}
results['v10_other_source']=[{'path':row['path'],'matches':sha(root/row['path'])==row['sha256']} for row in manifest['files'] if row['path'] not in allowed]
for group,rows in results.items():assert all(row['matches'] for row in rows),group
results['counts']={'previous_source_archives':12,'phone_artifact':1,'original_files':len(results['original_source']),'protected_files':len(results['protected_files']),'other_v10_entries':len(results['v10_other_source'])}
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results['counts']))
