import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).parent
if len(sys.argv)>1:
    from app.analyzers.email import analyze_email_bytes
    case=next(c for c in json.loads((ROOT/'contract.json').read_text())['cases']if c['id']==sys.argv[1]);raw=(ROOT/case['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==case['sha256'];start=time.perf_counter();report=analyze_email_bytes(raw);print(json.dumps({'id':case['id'],'method':'perf_counter only; no tracing/profiling','analysis_wall_seconds':time.perf_counter()-start,'status':'report'}));sys.exit()
rows=[]
for id in ['email-parts-1000','email-parts-6000']:
    try:
        child=subprocess.run([sys.executable,str(Path(__file__).resolve()),id],capture_output=True,text=True,timeout=10);row=json.loads(child.stdout)if child.returncode==0 else{'id':id,'status':'child_error'}
    except subprocess.TimeoutExpired:row={'id':id,'status':'timeout','limit_seconds':10}
    rows.append(row);print(json.dumps(row),flush=True)
with(ROOT/'baseline-results.json').open('x',encoding='utf-8')as output:json.dump({'same_frozen_workloads':True,'results':rows},output,indent=2)
