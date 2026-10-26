"""Preserve v18 and every intermediate phone artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/offline-workspaces-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-offline-v18-final-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'e1eaeca9805c2004cf70d99151b9e6a91263e302c4f5111c4db3c20e25b1b0f0'),(root.parent/'TrustLens-professional-20261024-offline-v18-review.zip','c40d96a916d6a55fd146eb250b6a7baef30ce121e536dacfde7fcd51f409562b'),(root.parent/'TrustLens-Pocket-iphone-test-v19.zip','0104930915857aac9853b7838cc3f07980086dedbbb47ea2ef1d5f96a8040bcd'),(root.parent/'TrustLens-Pocket-iphone-test-v20.zip','84221cc6d9c825130cc6b91ba5da0a394f90a955fadcb92732698fe6f41fc8e2'),(root.parent/'TrustLens-Pocket-iphone-test-v21.zip','e78d0451cb151468f2e6f04a4905786d557c6ea2899d9ffac4e0a76fc0c10e0d')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'static/numbers-context.html', 'tests/pocket_context_cache.test.cjs', 'static/phone/share-demo.html', 'static/phone/index.html', 'scripts/package.py', 'scripts/export_phone.py', 'static/phone/sw.js', 'static/claim-review.html', 'tasks/plan.md', 'static/quote-context.js', 'tests/claim_controller.test.cjs', 'tests/claim_roles_markup.test.cjs', 'static/claim-review.js', 'static/numbers-context.js', 'static/quote-context.html', 'tasks/todo.md', 'tests/frontend_state.test.cjs', 'tests/quote_controller.test.cjs', 'tests/numbers_controller.test.cjs', 'tests/phone_companion.test.cjs', 'README.md'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v18_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v18':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v18_entries':len(result['v18_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
