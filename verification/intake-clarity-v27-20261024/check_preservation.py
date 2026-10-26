"""Check prior artifacts and all unedited v26 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/claim-usability-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-context-polish-v26-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'515449ba37997ca65bf0d181d568eb588ba401be684d1675c9527bc3263e0a28'),(root.parent/'TrustLens-Pocket-iphone-test-v27.zip','dc8409e59ee4f8006b3ee8fd0edb64d56f96ce168c9804ac4a6486100876b091')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'app/analyzers/text.py','app/guidance.py','scripts/export_phone.py','scripts/package.py','static/claim-review.js','static/index.template.html','static/link-details.js','static/phone/index.html','static/phone/share-demo.html','static/phone/sw.js','static/styles.css','tests/link_details.test.cjs','tests/phone_companion.test.cjs','tests/pocket_context_cache.test.cjs','README.md','tasks/todo.md'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v26_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v26':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v26_entries':len(result['v26_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
