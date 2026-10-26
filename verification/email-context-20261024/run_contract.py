"""Replay only the frozen constructed contract through in-process ASGI; no socket/client source fetch."""
import asyncio,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import httpx
from app.main import app
ROOT=Path(__file__).parent
async def main():
    path=ROOT/'robustness-contract.json';raw=path.read_bytes();contract=json.loads(raw);rows=[]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://127.0.0.1') as client:
        for case in contract['cases']:
            assert len(case['raw'].encode())<=contract['max_case_bytes']
            for route in case['routes']:
                response=await client.post('/api/analyze/email',json={'raw_email':case['raw']}) if route=='paste' else await client.post('/api/analyze/email-file',files={'file':('constructed.eml',case['raw'].encode(),'message/rfc822')})
                try: data=response.json()
                except ValueError: data={'response_text':response.text}
                report=response.status_code==200;ids=[item.get('id') for item in data.get('evidence',[])] if report else []
                exposed=data.get('share_summary','') if report else response.text
                markers=[token for token in ['office@example.org','not-a-real-charset','unterminated','Constructed meeting','Constructed body.'] if token in case['raw']]
                leak=case['raw'] in exposed or any(token in exposed for token in markers)
                incomplete='email:incomplete' in ids
                rows.append({'case':case['id'],'route':route,'status':response.status_code,'risk':data.get('risk_level'),'evidence_ids':ids,'summary':data.get('summary'),'incomplete_expected':case['incomplete_expected_if_report'],'incomplete_observed':incomplete,'unhandled_500':response.status_code>=500,'error_or_export_echo':leak,'contract_gap':report and case['incomplete_expected_if_report'] and not incomplete,'response':data})
    result={'contract_sha256':hashlib.sha256(raw).hexdigest(),'utc':datetime.now(timezone.utc).isoformat(),'case_count':len(contract['cases']),'route_results':len(rows),'unhandled_500':sum(r['unhandled_500'] for r in rows),'echoes':sum(r['error_or_export_echo'] for r in rows),'contract_gaps':sum(r['contract_gap'] for r in rows),'results':rows}
    destination=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'results.json')
    with destination.open('x',encoding='utf-8') as output: output.write(json.dumps(result,indent=2,ensure_ascii=True))
    print(json.dumps({k:v for k,v in result.items() if k!='results'}))
    for row in rows:
        if row['contract_gap'] or row['unhandled_500'] or row['error_or_export_echo']: print(row['case'],row['route'],row['status'],row['risk'],row['evidence_ids'])
asyncio.run(main())
