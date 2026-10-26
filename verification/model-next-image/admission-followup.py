"""Stream existing model bytes for identity only; never deserialize or extract."""
import hashlib
import json
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORK=Path('C:/Users/round/Documents/Codex/2026-10-05/con/work')
BASE=WORK/'b-free'
def digest(p,md5=False):
    before=p.stat(); sha=hashlib.sha256(); legacy=hashlib.md5() if md5 else None
    start=time.perf_counter()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):
            sha.update(block)
            if legacy: legacy.update(block)
    after=p.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    return {'path':str(p),'bytes':after.st_size,'sha256':sha.hexdigest(),'md5':legacy.hexdigest() if legacy else None,'seconds':time.perf_counter()-start,'unchanged_during_read':True}
z=BASE/'BFREE_dino2reg4.zip'
archive=digest(z,True)
with zipfile.ZipFile(z) as f:
    entries=[{'name':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size,'crc32':format(x.CRC,'08x')} for x in f.infolist()]
checkpoint=digest(BASE/'weights/BFREE_dino2reg4/model_epoch_best.pth')
metadata=[BASE/p for p in ('README.md','main_bfree.py','main_bfree_single.py','networks_init.py','normalization.py','wrapper5crops.py','requirements.txt')]
metadata += [WORK/p for p in ('external-cf-bfree.json','check_bfree.py','verify_bfree_adapter.py') if (WORK/p).is_file()]
result={'at_utc':datetime.now(timezone.utc).isoformat(),'stream_buffer_bytes':1048576,'archive':archive,'published_zip_md5':'f3f53fa647848b16cf81c913f148a198','published_md5_matches':archive['md5']=='f3f53fa647848b16cf81c913f148a198','checkpoint':checkpoint,'matches_historical_sprint48_checkpoint_sha256':checkpoint['sha256']=='5948ca78f4d94e820c250d24cdf155035b4a85960443800bfe6bb7f06bffe947','zip_central_directory':entries,'zip_license_entries':[x for x in entries if 'license' in x['name'].lower() or 'copying' in x['name'].lower()],'local_code_pins':[digest(p) for p in metadata],'local_git_metadata_present':(BASE/'.git').exists(),'official_license_url':'https://github.com/grip-unina/B-Free/blob/main/LICENSE.txt','official_license_verified_via_web':'2026-10-23; informational/nonprofit only; preserve original notices; credit original authors for public results; no other use authorized; warranty disclaimer','model_deserialized':False,'zip_extracted':False,'image_payloads_read':False,'inference':False,'resource_repolled':False}
out=HERE/'admission-followup.json'; assert not out.exists()
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':archive,'checkpoint':checkpoint,'md5_match':result['published_md5_matches'],'license_entries':result['zip_license_entries'],'entries':len(entries),'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
