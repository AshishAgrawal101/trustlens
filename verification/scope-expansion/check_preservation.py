"""Preserve previous models, reports, releases and original source during scope expansion."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[2]
old=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
results={}
artifacts=[(Path(row['path']),row['expected_sha256']) for row in old['archive_evidence']]
artifacts += [(Path(row['path']),row['sha256']) for row in old['additional_artifacts']]
artifacts.append((root.parent/'TrustLens-professional-20261023-crosschecks-v9-review.zip','a115e2ce57a578eb13eab61f90a4cefaeb74f7997e07f247e549a368a789207a'))
results['artifacts']=[{'path':str(path),'sha256':expected,'matches':sha(path)==expected} for path,expected in artifacts]
results['original_source']=[{'path':row['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/row['path'])==row['expected_sha256']} for row in old['original_source_evidence']]
results['protected_relative_to_v9']=[{'path':row['path'],'sha256':row['actual_sha256'],'matches':sha(root/row['path'])==row['actual_sha256']} for row in old['protected_evidence']]
with zipfile.ZipFile(root.parent/'TrustLens-professional-20261023-crosschecks-v9-review.zip') as archive:
    manifest=json.loads(archive.read('SOURCE_MANIFEST.json'))
allowed={'static/index.template.html','README.md','tasks/todo.md','scripts/package.py'}
results['v9_source_preservation']=[{'path':row['path'],'matches':sha(root/row['path'])==row['sha256']} for row in manifest['files'] if row['path'] not in allowed]
for group,rows in results.items():assert all(row['matches'] for row in rows),group
results['counts']={'previous_source_archives':11,'phone_artifact':1,'original_files':len(results['original_source']),'protected_v9_files':len(results['protected_relative_to_v9']),'other_v9_source_entries':len(results['v9_source_preservation'])}
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results['counts']))
