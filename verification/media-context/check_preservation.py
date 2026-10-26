"""Check v11 preservation with explicit media integration edits."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[2]
old=json.loads((root/'verification/evidence-roles/preservation-final.json').read_text())
model_baseline=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
artifacts=[(Path(row['path']),row['sha256']) for row in old['artifacts']]
artifacts.append((root.parent/'TrustLens-professional-20261023-evidence-v11-review.zip','bbbed87964b1390bec3ed83cb3fb5cde99f589097049bc6b26bc4fa5c77f0133'))
results={'artifacts':[{'path':str(path),'sha256':expected,'matches':sha(path)==expected} for path,expected in artifacts]}
results['original_source']=[{'path':row['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/row['path'])==row['expected_sha256']} for row in model_baseline['original_source_evidence']]
results['protected_files']=[{'path':row['path'],'sha256':row['sha256'],'matches':sha(root/row['path'])==row['sha256']} for row in old['protected_files']]
with zipfile.ZipFile(root.parent/'TrustLens-professional-20261023-evidence-v11-review.zip') as archive:
    manifest=json.loads(archive.read('SOURCE_MANIFEST.json'))
allowed={'app/intake.py','app/upload_limits.py','tests/test_upload_limits.py','static/index.template.html','README.md','tasks/todo.md','scripts/package.py'}
results['v11_other_source']=[{'path':row['path'],'matches':sha(root/row['path'])==row['sha256']} for row in manifest['files'] if row['path'] not in allowed]
for group,rows in results.items():assert all(row['matches'] for row in rows),group
results['counts']={'previous_source_archives':13,'phone_artifact':1,'original_files':len(results['original_source']),'protected_files':len(results['protected_files']),'other_v11_entries':len(results['v11_other_source'])}
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results['counts']))
