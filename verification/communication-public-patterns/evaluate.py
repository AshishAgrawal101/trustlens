"""Frozen adapted FTC scenarios; local execution only, no URL fetch or tuning."""
import hashlib
import json
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parents[2]
FOLDER=Path(__file__).parent
paths=['app/analyzers/text.py','app/analyzers/email.py','app/analyzers/url.py','app/guidance.py','app/models.py']
def pins():return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}
before=pins()
started=time.perf_counter()
from app.analyzers.text import analyze_text
from app.analyzers.email import analyze_email
from app.guidance import add_guidance
import_ms=(time.perf_counter()-started)*1000
contract=json.loads((FOLDER/'frozen-contract.json').read_text(encoding='utf-8'))
rows=[]
for case in contract['cases']:
    started=time.perf_counter()
    report=add_guidance(analyze_email('Subject: Review\n\n'+case['text']) if case['mode']=='email' else analyze_text(case['text'],case['mode']))
    elapsed=(time.perf_counter()-started)*1000
    warning=any(e.weight>0 for e in report.evidence)
    rows.append({'id':case['id'],'mode':case['mode'],'expected_warning':case['expected_warning'],'warning':warning,
                 'expectation_met':warning==case['expected_warning'],'risk_level':report.risk_level,
                 'risk_index':report.risk_index,'confidence':report.confidence,'summary':report.summary,
                 'evidence_ids':[e.id for e in report.evidence],
                 'actions':[a.model_dump() for a in report.actions],
                 'latency_ms':elapsed})
after=pins()
assert before==after,'Analyzer source changed during evaluation; discard this run.'
output={'contract_sha256':hashlib.sha256((FOLDER/'frozen-contract.json').read_bytes()).hexdigest(),
        'source_sha256':before,'source_unchanged_during_run':True,'import_ms':import_ms,
        'timing_scope':'One sequential in-process call per constructed case, including add_guidance, excluding module import; no HTTP/browser latency. Not a performance benchmark.',
        'median_ms':statistics.median(row['latency_ms'] for row in rows),'max_ms':max(row['latency_ms'] for row in rows),'rows':rows}
print(json.dumps(output,indent=2))
