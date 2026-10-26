import json
from pathlib import Path
from app.analyzers.text import request_evidence
folder=Path(__file__).parent
rows=[]
for case in json.loads((folder/'frozen-acceptance.json').read_text()):
 actual=sorted(e.id.removeprefix('request:') for e in request_evidence(case['text']) if e.weight>0)
 rows.append({'id':case['id'],'expected':sorted(case['expected_requests']),'actual':actual})
print(json.dumps(rows,indent=2))
