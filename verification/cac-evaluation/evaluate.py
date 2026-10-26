"""Preregistered local diagnostic only. Writes no app files and never visits supplied links."""
import hashlib
import html
import json
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parents[2]
FOLDER=Path(__file__).parent
SOURCES=['app/analyzers/text.py','app/analyzers/email.py','app/analyzers/url.py','app/guidance.py','app/models.py']

def source_pins():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}

def evaluate():
    contract_path=FOLDER/'frozen-contract.json'
    digest=hashlib.sha256(contract_path.read_bytes()).hexdigest()
    assert digest==(FOLDER/'frozen-contract.sha256').read_text().strip(),'Frozen expectations changed'
    contract=json.loads(contract_path.read_text())
    before=source_pins()
    from app.analyzers.text import analyze_text
    from app.analyzers.email import analyze_email
    from app.guidance import add_guidance
    def run():
        rows=[]
        for case in contract['cases']:
            t=time.perf_counter()
            report=add_guidance(analyze_email('Subject: Review\n\n'+case['text']) if case['mode']=='email' else analyze_text(case['text'],case['mode']))
            elapsed=(time.perf_counter()-t)*1000
            warning=any(e.weight>0 for e in report.evidence)
            titles={a.title for a in report.actions}
            observed=[key for key,title in contract['action_title_map'].items() if title in titles]
            expected=case['expected_specific_actions']
            missing=[theme for theme in expected if theme not in observed]
            usefulness=('not_requested' if not expected else 'all_desired_themes_present' if not missing else 'partial_specific_guidance' if len(missing)<len(expected) else 'generic_only' if 'Verify through a separate route' in titles else 'no_desired_guidance')
            rows.append({'id':case['id'],'group':case['group'],'mode':case['mode'],
             'expected_warning':case['expected_warning'],'warning':warning,
             'warning_alignment':None if case['expected_warning'] is None else warning==case['expected_warning'],
             'expected_specific_actions':expected,'present_action_themes':observed,'missing_action_themes':missing,
             'generic_verify_present':'Verify through a separate route' in titles,'action_usefulness_proxy':usefulness,
             'uncertainty_contract':{'null_risk_index':report.risk_index is None,'low_confidence':report.confidence=='low','no_model':report.model_ran is False,'rules_basis':report.decision_basis=='rules'},
             'risk_level':report.risk_level,'summary':report.summary,'evidence_ids':[e.id for e in report.evidence],
             'actions':[a.model_dump() for a in report.actions],'latency_ms':elapsed})
        return rows
    rows=run();repeated=run()
    project=lambda values:[{k:v for k,v in row.items() if k!='latency_ms'} for row in values]
    repeatable=project(rows)==project(repeated)
    assert before==source_pins(),'Source changed during execution; reject this run'
    output={'contract_sha256':digest,'source_sha256':before,'source_unchanged_during_run':True,'repeatability_identical_excluding_timing':repeatable,
            'median_ms':statistics.median(r['latency_ms'] for r in rows),'max_ms':max(r['latency_ms'] for r in rows),'rows':rows}
    return contract,output

def render(contract,output):
    esc=lambda value:html.escape(str(value),quote=True)
    rows=[]
    for case,result in zip(contract['cases'],output['rows']):
        expected='unresolved / unscored' if result['expected_warning'] is None else 'warning' if result['expected_warning'] else 'no concern'
        outcome='unresolved' if result['warning_alignment'] is None else 'aligned' if result['warning_alignment'] else 'miss' if result['expected_warning'] else 'extra concern'
        source=esc(contract['sources'][case['source_key']])
        actions=''.join('<li>'+esc(a['title'])+' — '+esc(a['detail'])+'</li>' for a in result['actions'])
        rows.append('<tr><td>'+esc(case['id'])+'<br>'+esc(case['mode'])+'</td><td>'+esc(case['group'])+'</td><td>'+esc(expected)+'<br><strong>'+esc(outcome)+'</strong><br>Observed warning: '+esc(result['warning'])+'</td><td>'+esc(result['action_usefulness_proxy'])+'<br>Missing: '+esc(', '.join(result['missing_action_themes']) or 'none')+'</td><td><details><summary>Wording, expectation and actions</summary><p>'+esc(case['text'])+'</p><p>'+esc(case['expectation_rationale'])+'</p><p>'+esc(result['summary'])+'</p><ul>'+actions+'</ul><p>Evidence: '+esc(', '.join(result['evidence_ids']))+'</p><p>Related guidance, not a label for this exact message: <a href="'+source+'" target="_blank" rel="noopener noreferrer">FTC reference</a></p></details></td></tr>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrustLens selected diagnostic</title><style>body{font:15px/1.5 system-ui;margin:24px;color:#18382f;background:#f5f6ee}main{max-width:1250px;margin:auto}table{border-collapse:collapse;width:100%;background:white}th,td{vertical-align:top;text-align:left;padding:12px;border:1px solid #ccd7ce;overflow-wrap:anywhere}th{background:#deeadb}summary{cursor:pointer;min-height:32px}code{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}th,td{padding:6px;font-size:12px}}</style><main><h1>Selected communication diagnostic — 36 authored cases</h1><p>Preregistered development material, not population accuracy, field validation or a user study. Ambiguous cases remain unscored. All misses and extra concerns are retained. Action-theme presence is a proxy, not proof of useful advice.</p><p>Contract SHA256: <code>'+esc(output['contract_sha256'])+'</code></p><table><thead><tr><th>Row / mode</th><th>Group</th><th>Warning expectation / result</th><th>Action coverage proxy</th><th>Inspect row</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></main></html>'

if __name__=='__main__':
    destination=FOLDER/'results.json'
    if destination.exists():raise SystemExit('Refusing to overwrite the original diagnostic results; use evaluate() for an in-memory repeat.')
    contract,output=evaluate()
    destination.write_text(json.dumps(output,indent=2)+'\n')
    (FOLDER/'results.html').write_text(render(contract,output))
    print(json.dumps({'rows':len(output['rows']),'repeatability':output['repeatability_identical_excluding_timing'],'median_ms':output['median_ms'],'max_ms':output['max_ms']}))
