import json,hashlib
from pathlib import Path
from app.analyzers.email import analyze_email,analyze_email_bytes,VisibleText
from app.analyzers.text import analyze_text
folder=Path(__file__).parent
cases=json.loads((folder/'frozen-cases.json').read_text())['cases']
rows=[]
for c in cases:
 r=analyze_email(c['raw']);b=analyze_email_bytes(c['raw'].encode())
 row={'id':c['id'],'weighted_ids':[e.id for e in r.evidence if e.weight>0],'incomplete':any(e.id=='email:incomplete' for e in r.evidence),'risk_level':r.risk_level,'summary':r.summary,'byte_intake_same_findings':[e.id for e in b.evidence]==[e.id for e in r.evidence]}
 if 'expected' in c:row['expected']=c['expected']
 if 'expected_incomplete' in c:row['expected_incomplete']=c['expected_incomplete']
 if c['raw'].startswith('Content-Type: text/html'):
  p=VisibleText();p.feed(c['raw'].split('\n\n',1)[1]);p.close();row['reconstructed']=''.join(p.parts);row['plain_visible_weighted']=[e.id for e in analyze_text(c['visible']).evidence if e.weight>0]
 rows.append(row)
print(json.dumps({'source_sha256':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['app/analyzers/email.py','app/analyzers/text.py']},'rows':rows},indent=2))
