"""Preserve v14 with explicit quality changes and one reviewed resource-only exception."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
old=json.loads((root/'verification/quote-context/preservation-final.json').read_text())
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
artifacts=[(Path(row['path']),row['sha256']) for row in old['artifacts']]+[(root.parent/'TrustLens-professional-20261023-quotes-v14-review.zip','93da147d2e8409dac5ad6692e15dbd5a9992e2064fb7da37a16aed33c79530f5')]
results={'artifacts':[{'path':str(p),'sha256':s,'matches':sha(p)==s} for p,s in artifacts]}
results['original_source']=[{'path':row['path'],'matches':sha(root.parent/'neighborhood_hacks_20261021'/row['path'])==row['expected_sha256']} for row in original['original_source_evidence']]
results['protected_files']=[]
for row in old['protected_files']:
    expected=row['sha256'];record={'path':row['path'],'sha256':expected}
    if row['path']=='app/analyzers/image.py':
        assert expected=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
        record.update(baseline_sha256=expected,sha256='19ba25ed5e3b1ba331c90b9d4f2ef776336bc8da4810115998ce0bc0c6a8fe1f',reviewed_exception='Explicit pixel closing only; pinned source fixture and complete AST reversal/report equivalence checked by tests/test_image_lifecycle.py.')
    record['matches']=sha(root/row['path'])==record['sha256'];results['protected_files'].append(record)
assert sha(root/'tests/fixtures/frozen_v14_image.py.txt')=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
allowed={'README.md','frontend.py','scripts/package.py','tasks/plan.md','tasks/todo.md','app/analyzers/image.py','app/analyzers/qr.py','app/analyzers/screenshot.py','app/analyzers/text.py','static/app.js','static/index.template.html','static/tools.css','static/tools.html','tests/frontend_state.test.cjs','tests/tools_markup.test.cjs','tests/test_launcher.py'}
with zipfile.ZipFile(artifacts[-1][0]) as archive:manifest=json.loads(archive.read('SOURCE_MANIFEST.json'))
results['v14_other_source']=[{'path':row['path'],'matches':sha(root/row['path'])==row['sha256']} for row in manifest['files'] if row['path'] not in allowed]
for group,rows in results.items():assert all(row['matches'] for row in rows),group
results['counts']={'previous_source_archives':16,'phone_artifact':1,'original_files':len(results['original_source']),'protected_unchanged':33,'protected_reviewed_resource_change':1,'other_v14_entries':len(results['v14_other_source'])}
results['intentional_existing_file_changes']=sorted(allowed)
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results['counts']))
