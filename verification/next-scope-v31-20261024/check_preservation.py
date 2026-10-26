"""Check prior artifacts and all unedited v30 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/shared-context-integration-v30-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-shared-context-v30-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'1beb896d5ed31666dcbdd3b81f2eeefba838056602b7d5aff2cbf6296b761235'),(root.parent/'TrustLens-Pocket-iphone-test-v31.zip','7ce559ff33db4ff761da9e7672d188f0820756fefd6c8352a8f1763d73b1d209')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'static/index.template.html', 'tasks/todo.md', 'README.md', 'static/learning-practice.js', 'tests/phone_companion.test.cjs', 'static/phone/index.html', 'static/phone/practice.js', 'static/phone/share-demo.html', 'scripts/package.py', 'tests/learning_practice.test.cjs', 'tests/pocket_context_cache.test.cjs', 'tests/pocket_context_practice.test.cjs', 'static/phone/sw.js', 'tests/pocket_practice.test.cjs', 'scripts/export_phone.py'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v30_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v30':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v30_entries':len(result['v30_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
