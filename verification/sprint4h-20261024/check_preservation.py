"""Preserve v21 and every prior review artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'verification/result-first-20261024/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
archive=root.parent/'TrustLens-professional-20261024-polish-v21-review.zip'
artifacts=[(Path(r['path']),r['sha256']) for r in old['artifacts']]+[(archive,'6bcb843e6f5bc71b5cbf26462c99b384c986ce99643a619dd9a66c5f8beb61b1')]
result={'artifacts':[{'path':str(p),'sha256':digest,'matches':sha(p)==digest} for p,digest in artifacts]}
result['original_source']=[{'path':r['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256']} for r in original['original_source_evidence']]
result['protected_files']=[dict(r,matches=sha(root/r['path'])==r['sha256']) for r in old['protected_files']]
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'tasks/todo.md', 'README.md', 'tests/frontend_professional.test.cjs', 'tests/mode_route.test.cjs', 'static/index.template.html', 'static/mode-route.js', 'app/analyzers/screenshot.py', 'static/app.js', 'app/analyzers/text.py', 'app/analyzers/qr.py', 'scripts/package.py', 'app/guidance.py', 'app/analyzers/email.py', 'tasks/plan.md'}
with zipfile.ZipFile(archive) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
result['v21_other_source']=[{'path':r['path'],'matches':sha(root/r['path'])==r['sha256']} for r in manifest['files'] if r['path'] not in allowed]
for name,rows in result.items():assert all(r['matches'] for r in rows),name
result['counts']={'previous_source_archives':sum('Pocket-iphone-test-' not in p.name for p,_ in artifacts),'phone_artifacts':sum('Pocket-iphone-test-' in p.name for p,_ in artifacts),'original_files':len(result['original_source']),'protected_unchanged_relative_v21':len(result['protected_files']),'historical_protected_unchanged':33,'historical_reviewed_resource_change':1,'other_v21_entries':len(result['v21_other_source'])}
result['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['counts']))
