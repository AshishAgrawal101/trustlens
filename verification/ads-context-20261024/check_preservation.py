"""Preserve v24 and every prior review artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/event-context-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-event-context-v24-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'705f72ec240b83907c665d28715867a5f9f8aaf81470300247b52da51620af8a'),(root.parent/'TrustLens-Pocket-iphone-test-v25.zip','c270625ae74a05cfebeddc9c3453db904ab69f5d06f8c3a4f14a1bbeb3c3112f')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'app/pocket_workspaces.py', 'tests/learning_practice.test.cjs', 'README.md', 'static/phone/share-demo.html', 'static/phone/context.html', 'tests/pocket_context_practice.test.cjs', 'app/analyzers/email.py', 'static/tools.html', 'tests/tools_markup.test.cjs', 'scripts/export_phone.py', 'tasks/todo.md', 'static/phone/sw.js', 'static/media-context.js', 'static/phone/practice.js', 'static/index.template.html', 'tests/test_phone_offline_manifest.py', 'tests/pocket_context_cache.test.cjs', 'tests/phone_companion.test.cjs', 'static/learning-practice.js', 'app/main.py', 'tests/phone_context_markup.test.cjs', 'static/phone/index.html', 'scripts/package.py', 'tests/pocket_practice.test.cjs'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v24_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v24':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v24_entries':len(result['v24_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
