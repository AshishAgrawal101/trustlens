"""Check prior artifacts and all unedited v28 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/passage-paging-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-passage-navigation-v28-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'64c887f5f3a7a97dd7fb19c63937dab97c19226a2c765f5fb12e394cab909254'),(root.parent/'TrustLens-Pocket-iphone-test-v29.zip','4f500b4d0c73da452b1a45f9607b57fe5be7fa3791cbb2a8425bec672cded303')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'static/numbers-context.js', 'static/phone/index.html', 'static/quote-context.js', 'app/analyzers/text.py', 'tests/pocket_context_cache.test.cjs', 'static/phone/sw.js', 'static/media-context.js', 'scripts/package.py', 'README.md', 'tasks/todo.md', 'static/phone/share-demo.html', 'scripts/export_phone.py', 'static/numbers-context.css', 'static/numbers-context.html', 'tests/phone_companion.test.cjs'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v28_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v28':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v28_entries':len(result['v28_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
