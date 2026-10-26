"""Run the frozen constructed diagnostic once; preserve outputs, never tune rules."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.analyzers.text import analyze_text
from app.guidance import add_guidance

contract = Path(__file__).with_name('continuation-contract.json')
output = contract.with_name('continuation-results.json')
assert not output.exists(), 'Preserve the first diagnostic result'
cases = json.loads(contract.read_text(encoding='utf-8'))['cases']
assert len(cases) == 10 and len({c['id'] for c in cases}) == 10
rows = []
tracemalloc.start()
for case in cases:
    started = time.perf_counter()
    report = add_guidance(analyze_text(case['text']))
    elapsed = time.perf_counter() - started
    requests = {e.id.removeprefix('request:') for e in report.evidence
                if e.id.startswith('request:') and e.weight > 0}
    rows.append({'id': case['id'], 'seconds': elapsed,
                 'false_warning': case['negative'] and any(e.weight > 0 for e in report.evidence),
                 'missing': sorted(set(case['required']) - requests),
                 'action_present': case['action'] in [a.title for a in report.actions],
                 'report': report.model_dump(mode='json')})
_, peak = tracemalloc.get_traced_memory()
output.write_text(json.dumps({'contract_sha256': hashlib.sha256(contract.read_bytes()).hexdigest(),
    'cases': rows, 'negative_cases': sum(c['negative'] for c in cases),
    'false_warnings': sum(r['false_warning'] for r in rows),
    'missed_request_cases': sum(bool(r['missing']) for r in rows),
    'required_action_present': sum(r['action_present'] for r in rows),
    'unresolved_risk_labels': sum(r['report']['risk_level'] == 'unknown' for r in rows),
    'median_seconds': statistics.median(r['seconds'] for r in rows),
    'max_seconds': max(r['seconds'] for r in rows),
    'peak_traced_python_bytes_after_imports': peak,
    'population_accuracy': False}, indent=2), encoding='utf-8')
print(output)
