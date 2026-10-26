"""Read-only v39 preservation against immutable v37; writes only this receipt."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
old=json.loads((root/'verification/v37-root-browser-20261025/preservation.json').read_text())
artifacts=[dict(path=r['path'],sha256=r['sha256']) for r in old['artifacts']]
artifacts += [dict(path=str(root.parent/name),sha256=sha) for name,sha in [
 ('TrustLens-professional-20261025-connected-workflows-v37-review.zip','15059fa3389980e695f0851823c4db5e1357ee009c27ded9771c9047cde843e3'),
 ('TrustLens-Pocket-iphone-test-v37.zip','b45940325d515170f20ddd0b8af5bdc15aceefd75ca2501b1bf3f96d03d1a3ea'),
 ('TrustLens-Pocket-iphone-test-v38.zip','1cd3cafafc721278ccfac051c360aea062f9b82e2313e0616beacceea4dec0ff')]]
assert len(artifacts)==58
for r in artifacts:r['matches']=digest(r['path'])==r['sha256'];assert r['matches'],r['path']
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())['original_source_evidence']
for r in original:assert digest(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256'],r['path']
protected=json.loads((root/'verification/final-integration-20261024/preservation-final.json').read_text())['protected_files']
for r in protected:assert digest(root/r['path'])==r['sha256'],r['path']
allowed={'scripts/export_phone.py','static/claim-review.html','static/claim-review.js','static/phone/index.html','static/phone/share-demo.html','static/phone/sw.js','tests/claim_example_route.test.cjs','tests/claim_sources_disclosure.test.cjs','tests/phone_companion.test.cjs','tests/pocket_context_cache.test.cjs','README.md','tasks/todo.md','scripts/package.py'}
with zipfile.ZipFile(artifacts[-3]['path']) as z:manifest=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
changed=[r['path'] for r in manifest if digest(root/r['path'])!=r['sha256']]
assert set(changed)<=allowed,sorted(set(changed)-allowed)
phone=root.parent/'TrustLens-Pocket-iphone-test-v39.zip';phone_sha='9339040772bd8f246b1208eba73b4f59101602069d17cbd6a64c64d164e2cd31';assert digest(phone)==phone_sha
record={'previous_artifacts':58,'original_files':len(original),'protected_files_unchanged_relative_v33':len(protected),'historical_protected_accounting':{'unchanged':33,'reviewed_resource_cleanup':1},'v37_manifest_entries':len(manifest),'unchanged_entries':len(manifest)-len(changed),'intentional_existing_changes':sorted(changed),'permitted_existing_changes':sorted(allowed),'ongoing_documentation_exclusions':['README.md','tasks/todo.md','scripts/package.py'],'artifacts':artifacts,'current_phone':{'path':str(phone),'sha256':phone_sha,'matches':True},'scope':'Current phone separate from58 previous; source v39 not packaged by this audit.'}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record,indent=2))
print(json.dumps({k:v for k,v in record.items() if k!='artifacts'},indent=2))
