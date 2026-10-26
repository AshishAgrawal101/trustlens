"""Single bounded native plumbing attempt; no retry or accuracy estimate."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import types
from contextlib import ExitStack

HERE=Path(__file__).resolve().parent
APP=HERE.parents[1]
WORK=Path('C:/Users/round/Documents/Codex/2026-10-05/con/work')
OLD=APP.parent/'neighborhood_hacks_20261021/artifacts/sprint48/image-comparison/v2'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,value,check=lambda:None):
    check()
    assert Path(p).resolve().is_relative_to(HERE)
    Path(p).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

# Reuse the existing Windows supervisor unchanged; route its receipts to this run.
core=types.ModuleType('core')
core.HERE=HERE
core.save=save
sys.modules['core']=core
spec=importlib.util.spec_from_file_location('contain',OLD/'contain.py')
contain=importlib.util.module_from_spec(spec)
spec.loader.exec_module(contain)
contain.bind()
MIB=1024**2
protocol=read(HERE/'protocol.json')
receipt=read(HERE/'audit-receipt.json')
historical=WORK/'training-v2-20261011/STOP'
start=time.time()
class Guard:
    def check(self):
        assert sha(HERE/'protocol.json')=='9bc51f2adcfe7adc17e4c6b556d7f5d3d8c83b3b73d9414863980b663e87d277'
        assert sha(historical)=='c19c82e1d90a42542c305e1cc984e7ce16151e0e0925f1f65f4d1d822b212ada'
        for lock in receipt['locks']:
            p=Path(lock['path']).parent/'STOP'
            if p!=historical and p.exists(): raise RuntimeError('STOP '+str(p))
        for p in [WORK/'STOP',Path('D:/TrustLensData/STOP'),APP/'artifacts/sprint48/STOP',OLD.parents[1]/'STOP',OLD.parent/'STOP',OLD/'STOP',HERE/'STOP']:
            if p.exists(): raise RuntimeError('STOP '+str(p))
        if time.time()-start>=600: raise RuntimeError('600 second timeout')
        status=type('Mem',(contain.C.Structure,),{'_fields_':[('length',contain.W.DWORD),('load',contain.W.DWORD)]+[(n,contain.C.c_ulonglong) for n in ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]})()
        status.length=contain.C.sizeof(status)
        contain.ok(contain.K.GlobalMemoryStatusEx(contain.C.byref(status)))
        if status.available//2<2048*MIB: raise RuntimeError('2 GiB reservation exceeds half available RAM')
        if sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())>10000000: raise RuntimeError('Output bound')
guard=Guard()
def memory(admission=False):
    guard.check()
    value=contain.usage(contain.K.GetCurrentProcess())
    save(HERE/'attempt/worker-memory.json',{'phase':'import_admission' if admission else 'runtime','memory':value,'reserve':256*MIB})
    if max(value.values())+256*MIB >= (1280 if admission else 1792)*MIB:
        raise RuntimeError('Native import admission exceeded' if admission else 'Native runtime memory exceeded')

def child():
    assert sys.stdin.readline().strip()=='CONTAINED'
    sys.path.extend([str(WORK/'gpu-venv/Lib/site-packages'),str(WORK/'venv/Lib/site-packages'),str(APP)])
    os.environ.update(TRUSTLENS_DEVICE='cpu',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='')
    for k,v in read(APP/'local-runtime.json').items(): os.environ[k]=v
    def audit(event,args):
        if event.startswith('socket.') and event!='socket.gethostname' or event in ('subprocess.Popen','os.system','os.startfile','os.posix_spawn'):
            raise RuntimeError('External effects forbidden')
        if event=='open':
            path,mode,flags=args
            writing=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)
            if writing and (not isinstance(path,(str,bytes,os.PathLike)) or not Path(os.fsdecode(path)).resolve().is_relative_to(HERE)):
                raise RuntimeError('Write outside diagnostic forbidden')
    sys.addaudithook(audit)
    import torch
    memory(True)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    from app.analyzers.image import decode_image
    from ai_detector.image_ensemble import ImageEnsemble
    from ai_detector.decision_policy import is_inconclusive
    memory(True)
    runtime=ImageEnsemble(APP,os.environ['TRUSTLENS_CLIP_CACHE'],'cpu')
    memory()
    assert str(next(runtime.encoder.parameters()).device)=='cpu' and str(next(runtime.community.parameters()).device)=='cpu'
    import io
    results=[]
    for item in protocol['cohort']:
        guard.check()
        content=Path(item['absolute_image_path']).read_bytes()
        assert hashlib.sha256(content).hexdigest()==item['original_bytes_sha256']
        original=decode_image(content)
        transformed=io.BytesIO()
        original.save(transformed,format='JPEG',quality=60)
        for view,data in [('original',content),('jpeg60',transformed.getvalue())]:
            memory()
            began=time.monotonic()
            scores=runtime.score_details(decode_image(data))
            results.append({'id':item['id'],'view':view,'input_sha256':hashlib.sha256(data).hexdigest(),'scores':scores,'inconclusive':is_inconclusive(scores),'elapsed_seconds':time.monotonic()-began,'memory':contain.usage(contain.K.GetCurrentProcess())})
            save(HERE/'attempt/native-results.json',{'purpose':'integration plumbing only; labels contextual; no aggregate accuracy','results':results},guard.check)
    return 0

def parent():
    guard.check()
    folder=HERE/'attempt'
    assert not folder.exists(),'No retries'
    folder.mkdir()
    import msvcrt
    with ExitStack() as stack:
        for item in receipt['locks']:
            stream=stack.enter_context(Path(item['path']).open('rb'))
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            stack.callback(lambda s=stream: (s.seek(0),msvcrt.locking(s.fileno(),msvcrt.LK_UNLCK,1)))
        for pin in protocol['source_pins']: assert sha(pin['path'])==pin['sha256']
        verified=[]
        for item in protocol['cohort']:
            assert item['partition']=='validation' and item['official_split']=='train' and item['dataset_license']
            assert sha(item['absolute_image_path'])==item['original_bytes_sha256']
            verified.append({'id':item['id'],'sha256':item['original_bytes_sha256'],'verified':True})
        save(folder/'prelaunch.json',{'verified_assets':verified,'locks_acquired':24,'STOP_preserved':sha(historical),'attempt_script_sha256':sha(__file__),'supervisor_sha256':sha(OLD/'contain.py')})
        executable=Path(sys._base_executable)
        return contain.supervise([str(executable),'-S','-B',str(Path(__file__).resolve()),'--child'],folder,guard,worker_cap=1408*MIB,parent_cap=192*MIB,soft=1792*MIB,root_lock=False,declared_ceiling=2048*MIB)

if __name__=='__main__': sys.exit(child() if '--child' in sys.argv else parent())
