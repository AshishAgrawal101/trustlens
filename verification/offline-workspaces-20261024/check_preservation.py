"""Preserve v17 and every prior review artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/pocket-context-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-pocket-v17-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'1669aa08f4506301298ec9e3fed6ce18b416c18e1b1a9a8460c0e27e62b3040c'),(root.parent/'TrustLens-Pocket-iphone-test-v18.zip','e1e137b6de1e952aadd9a03cec697e522f78942a966fe159be18b0e25bf64656')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'static/phone/sw.js', 'tests/phone_companion.test.cjs', 'tests/test_phone_offline_manifest.py', 'tests/phone_context_markup.test.cjs', 'tasks/plan.md', 'static/phone/index.html', 'verification/offline-workspaces-20261024/spec.md', 'tasks/todo.md', 'static/phone/share-demo.html', 'scripts/export_phone.py', 'static/phone/context.html', 'tests/pocket_context_cache.test.cjs', 'app/main.py', 'submission/DEMO.md', 'scripts/package.py', 'README.md', 'tests/test_phone_bundle.py', 'submission/DISCLOSURE.md'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v17_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v17':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v17_entries':len(result['v17_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
