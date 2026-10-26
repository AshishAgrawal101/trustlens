"""Run from project root; prints no private inputs and visits no links."""
import json
from pathlib import Path
from app.analyzers.text import analyze_text

folder = Path(__file__).parent
cases = json.loads((folder / 'frozen-cases.json').read_text())
rows = []
for case in cases:
    report = analyze_text(case['text'])
    rows.append({'id': case['id'], 'label': case['label'], 'expected_warning': case['expected_warning'],
                 'warning': any(e.weight > 0 for e in report.evidence),
                 'evidence_ids': [e.id for e in report.evidence], 'risk_level': report.risk_level,
                 'risk_index': report.risk_index, 'confidence': report.confidence})
print(json.dumps(rows, indent=2))
