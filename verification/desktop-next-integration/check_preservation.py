"""Recheck previous immutable receipts; no model or source mutation."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
baseline = json.loads((root / 'verification/desktop-next-intake/preservation.json').read_text())
results = {}
for group, base, expected in (
    ('archive_evidence', None, 'expected_sha256'),
    ('original_source_evidence', root.parent / 'neighborhood_hacks_20261021', 'expected_sha256'),
    ('protected_evidence', root, 'expected_v7_sha256'),
):
    rows = []
    for item in baseline[group]:
        path = Path(item['path']) if base is None else base / item['path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({'path': item['path'], 'expected_sha256': item[expected], 'actual_sha256': actual, 'matches': actual == item[expected]})
    assert all(row['matches'] for row in rows), group
    results[group] = rows
results['counts'] = {group: len(rows) for group, rows in results.items()}
destination = Path(__file__).with_name('preservation-final.json')
destination.write_text(json.dumps(results, indent=2))
print(json.dumps(results['counts']))
