"""Check prior artifacts and all unedited v27 files without changing their evidence."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/intake-clarity-v27-20261024/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-intake-clarity-v27-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'270b2b263bd55b115d0bf18d0678447cd3f5175bf1441e812f646dbc784a5884'),(root.parent/'TrustLens-Pocket-iphone-test-v28.zip','5c0d499be57da06ec7e06f3891b5791d4e0211c16fbeac00aa66c24bdab60a82')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'tasks/todo.md', 'tests/source_controller.test.cjs', 'static/phone/index.html', 'static/quote-context.html', 'static/source-context.js', 'static/phone/share-demo.html', 'scripts/package.py', 'static/quote-context.css', 'tests/pocket_context_cache.test.cjs', 'static/phone/sw.js', 'README.md', 'tests/source_markup.test.cjs', 'tests/phone_companion.test.cjs', 'scripts/export_phone.py'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v27_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v27':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v27_entries':len(result['v27_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
