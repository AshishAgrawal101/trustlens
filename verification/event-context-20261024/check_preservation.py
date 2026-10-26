"""Preserve v23 and every prior review artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/reported-percentages-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-percentages-v23-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'8203aa16c2572f2fb3fdeac2a3c1f1b33b88300809f5e54c1bddda0c2960c97e'),(root.parent/'TrustLens-Pocket-iphone-test-v24.zip','4699b60e7cbdd92845ee55f41c7130cc99b376f880d5fe1bbebaca1a852825be')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'app/analyzers/email.py', 'static/claim-review.html', 'app/analyzers/url.py', 'static/tools.html', 'static/app.js', 'README.md', 'static/phone/share-demo.html', 'scripts/package.py', 'tasks/todo.md', 'tests/pocket_context_cache.test.cjs', 'static/claim-review.js', 'tests/phone_companion.test.cjs', 'static/phone/sw.js', 'scripts/export_phone.py', 'static/phone/index.html'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v23_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v23':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v23_entries':len(result['v23_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
