"""Bounded repeats of two existing frozen inputs, without tracemalloc; no new workload."""
import cProfile,hashlib,json,pstats,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).parent
if len(sys.argv)>1:
    from app.analyzers.email import analyze_email_bytes
    case=next(c for c in json.loads((ROOT/'contract.json').read_text())['cases'] if c['id']==sys.argv[1]);raw=(ROOT/case['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==case['sha256']
    profile=cProfile.Profile();start=time.perf_counter();profile.enable();report=analyze_email_bytes(raw);profile.disable();elapsed=time.perf_counter()-start
    stats=pstats.Stats(profile).stats;top=sorted(stats.items(),key=lambda item:item[1][2],reverse=True)[:12]
    print(json.dumps({'id':case['id'],'method':'cProfile enabled, tracemalloc disabled','analysis_wall_seconds':elapsed,'status':'report','incomplete':any(e.id=='email:incomplete' for e in report.evidence),'focused_functions':[{'function':Path(key[0]).name+':'+str(key[1])+':'+key[2],'calls':value[1],'own_seconds':value[2],'cumulative_seconds':value[3]}for key,value in stats.items()if key[2]in{'body_parts','analyze_message','analyze_email_bytes','analyze_text','request_evidence','unscanned_parts_count','link_label_evidence','parsebytes'}or(Path(key[0]).name=='feedparser.py'and key[2]in{'feed','close','_parsegen'})], 'top_own_time':[{'function':Path(key[0]).name+':'+str(key[1])+':'+key[2],'calls':value[1],'own_seconds':value[2],'cumulative_seconds':value[3]} for key,value in top]}));sys.exit()
rows=[]
for id in ['email-parts-1000','email-parts-6000']:
    start=time.perf_counter()
    try:
        child=subprocess.run([sys.executable,str(Path(__file__).resolve()),id],capture_output=True,text=True,timeout=10);row=json.loads(child.stdout) if child.returncode==0 else {'id':id,'status':'child_error'}
    except subprocess.TimeoutExpired:row={'id':id,'status':'timeout','limit_seconds':10}
    row['process_wall_seconds']=time.perf_counter()-start;rows.append(row);print(json.dumps(row),flush=True)
with(ROOT/'profile-focus-results.json').open('x',encoding='utf-8')as output:json.dump({'same_frozen_workloads':True,'results':rows},output,indent=2)
