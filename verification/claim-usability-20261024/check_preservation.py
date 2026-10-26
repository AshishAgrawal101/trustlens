"""Preserve v25 and every prior review artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/ads-context-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-ads-context-v25-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'1d35c4fdf27741d52b26bf9daf9b32e17f4e56e12abf06dd7026c48a7d1a9123'),(root.parent/'TrustLens-Pocket-iphone-test-v26.zip','a7ed149a79685ae343edc8df3c9ac682e4840153caf7fbae4e41e7248b7a19d6')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'static/claim-review.js', 'scripts/export_phone.py', 'static/numbers-context.html', 'tasks/todo.md', 'static/phone/index.html', 'static/phone/share-demo.html', 'static/phone/sw.js', 'tests/pocket_context_cache.test.cjs', 'scripts/package.py', 'app/analyzers/text.py', 'static/claim-review.html', 'README.md', 'static/numbers-context.js', 'static/claim-review.css', 'tests/phone_companion.test.cjs'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v25_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v25':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v25_entries':len(result['v25_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
