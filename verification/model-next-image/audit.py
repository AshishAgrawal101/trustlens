"""Metadata/resource audit only: no model imports or image payload reads."""
import ctypes
import hashlib
import json
import msvcrt
import subprocess
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
APP = HERE.parents[1]
WORK = Path('C:/Users/round/Documents/Codex/2026-10-05/con/work')
DATA = Path('D:/TrustLensData')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p): return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
dirs = [Path(p) for p in read(WORK/'training-v2-photo-adaptation-20261018/protocol.json')['lock_directories']]
locks = []
for d in dirs:
    for name in ('runner.lock','gpu.lock'):
        p = d/name
        row = {'path':str(p),'exists':p.is_file(),'acquired':False}
        if p.is_file():
            before = pin(p)
            try:
                with p.open('rb') as f:
                    msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
                    msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
                row['acquired'] = True
            except OSError as e: row['error'] = str(e)
            row.update(before)
            row['unchanged'] = pin(p) == before
        locks.append(row)
stops = [WORK/'STOP', DATA/'STOP', APP.parent/'neighborhood_hacks_20261021/artifacts/sprint48/STOP', APP.parent/'neighborhood_hacks_20261021/artifacts/sprint48/image-comparison/STOP', APP.parent/'neighborhood_hacks_20261021/artifacts/sprint48/image-comparison/v2/STOP', APP/'STOP'] + [d/'STOP' for d in dirs]
class Memory(ctypes.Structure):
    _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong)] + [(n,ctypes.c_ulonglong) for n in ('total','available','total_page','available_page','total_virtual','available_virtual','extended')]
m = Memory(); m.length = ctypes.sizeof(m)
assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
files = [APP/'models/image_pipeline.json', APP/'local-runtime.json', APP/'ai_detector/bfree.py', WORK/'b-free/README.md', WORK/'b-free/weights/BFREE_dino2reg4/config.yaml', WORK/'detector-source-research-20261010/shortlist.json', DATA/'pe_test_decision_models.json', DATA/'test_allocations.json', WORK/'openfake-round3-20261007/test_decision_models.json', WORK/'training-v2-ten-hour-20261012/test_decision_models.json', WORK/'training-v2-generalization-20261013/data/admitted.json', DATA/'pinned_README.md']
for d in ('training-v2-local-detail-20261017','training-v2-robust-local-20261018','training-v2-photo-adaptation-20261018','training-v2-photo-complement-20261018'):
    files.append(WORK/d/'REPORT.md')
receipt = {'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'metadata only; no model loading, unpickling, image payloads, final/Arena/user examples, training or GPU jobs','pins':[pin(p) for p in files], 'locks':locks,'lock_scope':'momentary nonblocking probes, released; not a launch reservation','stop_checks':[{'path':str(p),'exists':p.is_file(),**(pin(p) if p.is_file() else {})} for p in stops], 'ram':{'available_bytes':m.available,'total_bytes':m.total,'existing_2GiB_reservation_below_half_available_now':2147483648 <= m.available/2,'import_admission_bytes':1342177280,'inclusive_abort_bytes':1879048192,'launch_admitted':False},'gpu_snapshot':subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,timeout=10).stdout.strip(),'bfree_checkpoint_metadata':{'path':str(WORK/'b-free/weights/BFREE_dino2reg4/model_epoch_best.pth'),'bytes':(WORK/'b-free/weights/BFREE_dino2reg4/model_epoch_best.pth').stat().st_size,'weight_hash_verified':False,'required_LICENSE_txt_present':(WORK/'b-free/LICENSE.txt').exists()},'candidate_eligible':None,'scores':None}
out = HERE/'receipt.json'
assert not out.exists()
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':pin(out),'locks_acquired':sum(x['acquired'] for x in locks),'ram':receipt['ram'],'stops':[x for x in receipt['stop_checks'] if x['exists']],'gpu':receipt['gpu_snapshot']},indent=2))
