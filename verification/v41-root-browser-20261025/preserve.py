"""Read-only v41 preservation; no packaging or app mutation."""
import hashlib,json,zipfile
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
prior=json.loads((root/'verification/v40-root-browser-20261025/preservation.json').read_text());artifacts=[dict(path=r['path'],sha256=r['sha256']) for r in prior['artifacts']]
source=root.parent/'TrustLens-professional-20261025-email-coverage-v40-review.zip';phone=root.parent/'TrustLens-Pocket-iphone-test-v40.zip';phone_sha='048eb7ddc9068e9d05fc4073d011a45d86f241f37266654c2bde2d105735444a'
artifacts.extend([{'path':str(source),'sha256':'295c25bf6801f3428d144355d3bbe35514b72966d92443a6a759247ea1cfcef4'},{'path':str(phone),'sha256':phone_sha}]);assert len(artifacts)==62
for r in artifacts:r['matches']=sha(r['path'])==r['sha256'];assert r['matches'],r['path']
original=json.loads((root/'verification/model-next-integration/preservation-final.json').read_text())['original_source_evidence']
for r in original:assert sha(root.parent/'neighborhood_hacks_20261021'/r['path'])==r['expected_sha256'],r['path']
protected=json.loads((root/'verification/final-integration-20261024/preservation-final.json').read_text())['protected_files']
for r in protected:assert sha(root/r['path'])==r['sha256'],r['path']
image_sha='19ba25ed5e3b1ba331c90b9d4f2ef776336bc8da4810115998ce0bc0c6a8fe1f';assert sha(root/'app/analyzers/image.py')==image_sha
allowed={'README.md','app/analyzers/qr.py','static/app.js','static/index.template.html','tasks/todo.md','scripts/package.py'}
with zipfile.ZipFile(source) as z:rows=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
assert len(rows)==1471;changed=[r['path'] for r in rows if sha(root/r['path'])!=r['sha256']];assert set(changed)<=allowed,sorted(set(changed)-allowed)
from app.pocket_workspaces import render_pocket_workspace
from scripts.export_phone import README
phone_rows=[]
with zipfile.ZipFile(phone) as z:
 for r in json.loads(z.read('PHONE_TEST_MANIFEST.json'))['files']:
  name=r['path'];assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256']
  if name.startswith('phone/workspace/'):
   current=render_pocket_workspace(Path(name).stem).encode()
  elif name=='README-IPHONE-TEST.md':current=README.encode()
  else:current=(root/('static/'+name if name.startswith('phone/') else name)).read_bytes()
  match=hashlib.sha256(current).hexdigest()==r['sha256'];assert match,name;phone_rows.append({'path':name,'matches':match})
record={'previous_artifacts':62,'original_files':len(original),'protected_files_unchanged_relative_v33':len(protected),'historical_protected_accounting':{'unchanged':33,'reviewed_resource_cleanup':1},'image_entire_sha256':image_sha,'v40_manifest_entries':len(rows),'unchanged_entries':len(rows)-len(changed),'intentional_existing_changes':sorted(changed),'permitted_existing_changes':sorted(allowed),'ongoing_documentation_exclusions':['README.md','tasks/todo.md','scripts/package.py'],'artifacts':artifacts,'unchanged_phone_v40':{'sha256':phone_sha,'manifest_source_entries':len(phone_rows),'all_source_and_archive_entries_match':True,'entries':phone_rows},'scope':'New helper/tests/evidence outside prior manifest; no source packaging performed.'}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ('artifacts','unchanged_phone_v40')},indent=2));print('Phone40 current source and archive entries:',len(phone_rows))
