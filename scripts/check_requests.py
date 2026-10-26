"""Constructed regression cases, not an independent estimate of scam accuracy."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.analyzers.text import request_evidence

def evaluate():
    cases = json.loads((ROOT/'tests/fixtures/request_cases.json').read_text())
    rows = []
    for case in cases:
        got = sorted(e.id.removeprefix('request:') for e in request_evidence(case['text']))
        rows.append({**case, 'actual': got, 'passed': got == sorted(case['keys'])})
    return {'scope': '32 developer-constructed English rule cases; not a held-out accuracy benchmark',
            'passed': sum(r['passed'] for r in rows), 'total': len(rows), 'cases': rows}

if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2))
