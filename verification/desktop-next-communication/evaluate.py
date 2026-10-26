import json,hashlib
from pathlib import Path
from app.analyzers.text import request_evidence
folder=Path(__file__).parent
cases=json.loads((folder/'frozen-cases.json').read_text())['cases']
rows=[]
for c in cases:
 actual=sorted(e.id for e in request_evidence(c['text']) if e.weight>0)
 rows.append({'id':c['id'],'expected':c['expected_requests'],'actual':actual})
print(json.dumps({'source_sha256':hashlib.sha256(Path('app/analyzers/text.py').read_bytes()).hexdigest(),'rows':rows},indent=2))
