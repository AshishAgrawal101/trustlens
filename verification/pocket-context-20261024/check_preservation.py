"""Preserve v16, prior archives and both phone review artifacts."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/source-context-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-source-v16-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'b3ba0745eaf47b5df05c7a70e1e704da66349f074ffe13a04cae4aca45a4e97d'),(root.parent/'TrustLens-Pocket-iphone-test-v17.zip','b507755101ae54c23ec1571373d1e8dd761a6628c679d3389005a003238157c3')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'README.md','scripts/package.py','scripts/export_phone.py','tasks/plan.md','tasks/todo.md','app/analyzers/url.py','static/phone/guide.js','static/phone/index.html','static/phone/phone.css','static/phone/phone.js','static/phone/practice.js','static/phone/share-demo.html','static/phone/sw.js','tests/phone_companion.test.cjs','tests/pocket_practice.test.cjs','tests/test_phone_bundle.py','submission/DEMO.md','submission/DISCLOSURE.md'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v16_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':18,'phone_artifacts':2,'original_files':len(result['original_source']),'protected_unchanged_relative_v16':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v16_entries':len(result['v16_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
