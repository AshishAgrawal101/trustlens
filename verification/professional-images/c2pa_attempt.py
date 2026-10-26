"""Distinct C2PA-only diagnostic; exact production verifier, no visual imports."""
import attempt as boundary
from contextlib import ExitStack
import importlib.util
import io
import json
import msvcrt
import os
from pathlib import Path
import sys
import time

HERE=boundary.HERE
APP=boundary.APP
WORK=boundary.WORK
FOLDER=HERE/'c2pa-attempt'
PROTOCOL=HERE/'c2pa-protocol.json'
CREDS=WORK/'credentials-venv'
def pins():
    files=[APP/'app/analyzers/provenance.py',APP/'app/analyzers/content_credentials_worker.py',CREDS/'Scripts/python.exe',CREDS/'pyvenv.cfg',Path(__file__)]
    files+=list((APP/'app/trust').glob('*'))
    files += [p for p in (CREDS/'Lib/site-packages/c2pa').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return [{'path':str(p),'sha256':boundary.sha(p),'bytes':p.stat().st_size} for p in files]

def child():
    assert sys.stdin.readline().strip()=='CONTAINED'
    protocol=boundary.read(PROTOCOL)
    for pin in protocol['pins']: assert boundary.sha(pin['path'])==pin['sha256']
    sys.path.insert(0,str(CREDS/'Lib/site-packages'))
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='')
    def audit(event,args):
        if event.startswith('socket.') and event!='socket.gethostname' or event in ('subprocess.Popen','os.system','os.startfile','os.posix_spawn'):
            raise RuntimeError('External effects forbidden')
        if event=='open':
            path,mode,flags=args
            writing=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)
            if writing and (not isinstance(path,(str,bytes,os.PathLike)) or not Path(os.fsdecode(path)).resolve().is_relative_to(HERE)):
                raise RuntimeError('Write outside diagnostic')
    sys.addaudithook(audit)
    spec=importlib.util.spec_from_file_location('production_credentials',APP/'app/analyzers/content_credentials_worker.py')
    verifier=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    import c2pa
    memory=boundary.contain.usage(boundary.contain.K.GetCurrentProcess())
    if max(memory.values())+256*1024**2>=1280*1024**2: raise RuntimeError('C2PA import admission exceeded')
    results=[]
    for item in protocol['cohort']:
        boundary.guard.check()
        content=Path(item['absolute_image_path']).read_bytes()
        assert boundary.sha(item['absolute_image_path'])==item['original_bytes_sha256']
        mime='image/png' if content.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if content.startswith(b'\xff\xd8') else 'image/webp'
        began=time.monotonic()
        # Execute the production stdin/main transport and native verifier unchanged.
        old_stdin,old_stdout,old_argv=sys.stdin,sys.stdout,sys.argv
        output=io.StringIO()
        try:
            sys.stdin=io.TextIOWrapper(io.BytesIO(content))
            sys.stdout=output
            sys.argv=[str(APP/'app/analyzers/content_credentials_worker.py'),mime]
            verifier.main()
        finally:
            sys.stdin,sys.stdout,sys.argv=old_stdin,old_stdout,old_argv
        elapsed=time.monotonic()-began
        result=json.loads(output.getvalue())
        if elapsed>15: result={'status':'unavailable','detail':'Production 15 second transport timeout exceeded in diagnostic'}
        assert result['status'] in {'absent','external','verified','untrusted','invalid','unavailable'}
        results.append({'id':item['id'],'sha256':item['original_bytes_sha256'],'elapsed_seconds':elapsed,'result':result,'memory':boundary.contain.usage(boundary.contain.K.GetCurrentProcess())})
        boundary.save(FOLDER/'results.json',{'component':'native production C2PA worker main; in-process stdio transport under external supervisor, not read_credentials subprocess transport','results':results,'visual_model_ran':False,'image_origin_or_fraud_scores':None})
    assert 'torch' not in sys.modules
    return 0

def parent():
    assert not PROTOCOL.exists() and not FOLDER.exists(),'Single attempt only'
    protocol={'at_utc':time.time(),'root_authorization':'Distinct native C2PA-only check on SAME four hash-verified admitted development originals. Preserve STOPs/locks, 1.75 GiB inclusive/RAM guard, zero visual model/GPU/network/fitting/final data; unavailable on transport errors. Not a model retry.','cohort':boundary.protocol['cohort'],'pins':pins(),'entry':'production content_credentials_worker.main on bytes stdin; exact production verifier and trust snapshots; read_credentials subprocess wrapper not exercised','limits':{'seconds':60,'per_asset_production_transport_seconds':15,'inclusive_abort_bytes':1792*1024**2,'import_admission_with_reserve_bytes':1280*1024**2,'reserve_bytes':256*1024**2,'external_network':False,'gpu':False},'visual_results':None}
    boundary.save(PROTOCOL,protocol)
    boundary.guard.check()
    FOLDER.mkdir()
    with ExitStack() as stack:
        for item in boundary.receipt['locks']:
            stream=stack.enter_context(Path(item['path']).open('rb'))
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            stack.callback(lambda s=stream:(s.seek(0),msvcrt.locking(s.fileno(),msvcrt.LK_UNLCK,1)))
        for item in protocol['cohort']: assert boundary.sha(item['absolute_image_path'])==item['original_bytes_sha256']
        boundary.save(FOLDER/'prelaunch.json',{'protocol_sha256':boundary.sha(PROTOCOL),'all24locks':True,'four_original_hashes_verified':True,'STOP_sha256':boundary.sha(boundary.historical)})
        class Guard:
            def check(self):
                boundary.guard.check()
                if time.time()-boundary.start>=60: raise RuntimeError('C2PA 60 second timeout')
        return boundary.contain.supervise([sys._base_executable,'-S','-B',str(Path(__file__).resolve()),'--child'],FOLDER,Guard(),root_lock=False)

if __name__=='__main__': sys.exit(child() if '--child' in sys.argv else parent())
