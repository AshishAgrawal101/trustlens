"""Check prior artifacts and all unedited v31 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/next-scope-v31-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-focused-practice-v31-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'653c9cb44e0dc9946a4bac5384b64c1d0f7b96743fd3aef753d0dd306497f591'),(root.parent/'TrustLens-Pocket-iphone-test-v32.zip','d120772437a3d47aa98546a71dc4a012f3c0a50652574a1ffb4b36947e683431')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'scripts/package.py', 'README.md', 'static/phone/share-demo.html', 'tasks/todo.md', 'static/claim-review.js', 'submission/CAC-2026.md', 'static/phone/index.html', 'static/claim-review.html', 'scripts/export_phone.py', 'static/phone/context.html', 'submission/CAC-DEMO-3MIN.md', 'static/phone/sw.js', 'app/analyzers/text.py', 'tests/phone_context_markup.test.cjs', 'submission/DEMO.md', 'tests/phone_companion.test.cjs', 'app/pocket_workspaces.py', 'tests/test_desktop_context_guide.py', 'tests/pocket_context_cache.test.cjs'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v31_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v31':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v31_entries':len(result['v31_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
