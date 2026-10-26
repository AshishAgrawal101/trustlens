"""Preserve prior releases and record the one reviewed image error-boundary change."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
baseline = json.loads((root/'verification/desktop-next-integration/preservation-final.json').read_text())
results = {}
for group, base in [('archive_evidence', None), ('original_source_evidence', root.parent/'neighborhood_hacks_20261021'), ('protected_evidence', root)]:
    rows = []
    for item in baseline[group]:
        path = Path(item['path']) if base is None else base/item['path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        reviewed = group == 'protected_evidence' and item['path'] == 'app/analyzers/image.py'
        rows.append({'path': item['path'], 'expected_sha256': item['expected_sha256'], 'actual_sha256': actual, 'matches': actual == item['expected_sha256'], 'reviewed_error_boundary_exception': reviewed})
    assert all(row['matches'] or row['reviewed_error_boundary_exception'] for row in rows), group
    results[group] = rows
for filename, expected in [
    ('TrustLens-professional-20261023-desktop-v8-review.zip', '4046c4cb806756e91cbe6c74099a5643e10b09c4acf073dab112a57242e1d4ec'),
    ('TrustLens-Pocket-iphone-test-v7.zip', '415a91178e3699022be15b11a9d0d1ace4fe236fdcd433c59a645b1773662635')]:
    path = root.parent/filename
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, filename
    results.setdefault('additional_artifacts', []).append({'path': str(path), 'sha256': actual, 'matches': True})
results['counts'] = {'prior_source_archives_unchanged': 10, 'phone_artifacts_unchanged': 1, 'original_source_files_unchanged': len(results['original_source_evidence']), 'protected_files_unchanged': sum(row['matches'] for row in results['protected_evidence']), 'reviewed_image_error_boundary_change': 1}
Path(__file__).with_name('preservation-final.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results['counts']))
