"""Read-only v40 baseline preservation; rerunnable after authorized documentation edits."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
prior=json.loads((root/'verification/v39-root-browser-20261025/preservation.json').read_text())
artifacts=[dict(path=r['path'],sha256=r['sha256']) for r in prior['artifacts']]
source=root.parent/'TrustLens-professional-20261025-source-repair-v39-review.zip'
artifacts.extend([{'path':str(source),'sha256':'f4bba3350acd60a1d19c39a0f5d45136135c1b163ef93aff99f97902e565231e'},{'path':str(root.parent/'TrustLens-Pocket-iphone-test-v39.zip'),'sha256':'9339040772bd8f246b1208eba73b4f59101602069d17cbd6a64c64d164e2cd31'}])
assert len(artifacts)==60
for r in artifacts:r['matches']=sha(r['path'])==r['sha256'];assert r['matches'],r['path']
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())['original_source_evidence']
for r in original:assert sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256'],r['path']
protected=json.loads((root/'verification/final-integration-20261024/preservation-final.json').read_text())['protected_files']
for r in protected:assert sha(root/r['path'])==r['sha256'],r['path']
allowed={'app/analyzers/email.py','app/guidance.py','static/source-context.js','static/phone/index.html','static/phone/share-demo.html','static/phone/sw.js','scripts/export_phone.py','scripts/package.py','tests/phone_companion.test.cjs','tests/pocket_context_cache.test.cjs','README.md','tasks/todo.md'}
with zipfile.ZipFile(source) as z:rows=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
assert len(rows)==1420
changed=[r['path'] for r in rows if sha(root/r['path'])!=r['sha256']];assert set(changed)<=allowed,sorted(set(changed)-allowed)
phone=root.parent/'TrustLens-Pocket-iphone-test-v40.zip';phone_sha='048eb7ddc9068e9d05fc4073d011a45d86f241f37266654c2bde2d105735444a';assert sha(phone)==phone_sha
record={'previous_artifacts':60,'original_files':len(original),'protected_files_unchanged_relative_v33':len(protected),'historical_protected_accounting':{'unchanged':33,'reviewed_resource_cleanup':1},'v39_manifest_entries':len(rows),'unchanged_entries':len(rows)-len(changed),'intentional_existing_changes':sorted(changed),'permitted_existing_changes':sorted(allowed),'ongoing_documentation_exclusions':['README.md','tasks/todo.md','scripts/package.py'],'artifacts':artifacts,'current_phone':{'path':str(phone),'sha256':phone_sha,'matches':True},'scope':'Current phone separate from60 prior artifacts; source v40 packaging not performed here.'}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k!='artifacts'},indent=2))
