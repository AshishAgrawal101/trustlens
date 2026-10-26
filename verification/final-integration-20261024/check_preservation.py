"""Check prior artifacts and all unedited v32 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/endorsement-entry-v32-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-endorsement-context-v32-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'5813be2d4a6f838d216a0773b59a256fdb615e3c605c288e33e9e3d1a5854624'),(root.parent/'TrustLens-Pocket-iphone-test-v33.zip','e12a7d4318341ec9df675945e5b3f079404d0d586cc19fa877cb5a81f662bed9')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'scripts/export_phone.py', 'static/phone/sw.js', 'tests/pocket_context_cache.test.cjs', 'tests/phone_companion.test.cjs', 'static/phone/index.html', 'static/quote-context.html', 'static/source-context.js', 'scripts/package.py', 'README.md', 'tasks/todo.md', 'static/phone/share-demo.html'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v32_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v32':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v32_entries':len(result['v32_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
