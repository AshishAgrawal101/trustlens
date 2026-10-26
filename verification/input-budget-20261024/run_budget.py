"""Isolated sequential replay of the frozen local CPU contract."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).parent
if len(sys.argv)>1 and sys.argv[1]=='--child':
    import tracemalloc
    from app.analyzers.email import analyze_email_bytes
    from app.analyzers.text import analyze_text
    contract=json.loads((ROOT/'contract.json').read_text());case=next(c for c in contract['cases'] if c['id']==sys.argv[2]);raw=(ROOT/case['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==case['sha256']
    tracemalloc.start();start=time.perf_counter()
    try:
        report=analyze_email_bytes(raw) if case['kind']=='email' else analyze_text(raw.decode())
        outcome={'status':'report','risk':report.risk_level,'evidence_count':len(report.evidence),'incomplete':any(e.id=='email:incomplete' for e in report.evidence)}
    except Exception as exc: outcome={'status':'exception','exception_type':type(exc).__name__}
    elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();print(json.dumps({'id':case['id'],'analysis_wall_seconds':elapsed,'traced_peak_bytes':peak,**outcome}));sys.exit()
contract_path=ROOT/'contract.json';contract_raw=contract_path.read_bytes();contract=json.loads(contract_raw);rows=[]
for case in contract['cases']:
    start=time.perf_counter()
    try:
        child=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',case['id']],capture_output=True,text=True,timeout=contract['timeout_seconds_per_case'])
        row=json.loads(child.stdout) if child.returncode==0 else {'id':case['id'],'status':'child_error','returncode':child.returncode,'error_type':'nonzero child exit'}
    except subprocess.TimeoutExpired: row={'id':case['id'],'status':'timeout','limit_seconds':contract['timeout_seconds_per_case']}
    row['process_wall_seconds']=time.perf_counter()-start;rows.append(row);print(json.dumps(row),flush=True)
result={'contract_sha256':hashlib.sha256(contract_raw).hexdigest(),'python':sys.version,'platform':sys.platform,'results':rows};destination=ROOT/'results.json'
with destination.open('x',encoding='utf-8')as output:json.dump(result,output,indent=2)
