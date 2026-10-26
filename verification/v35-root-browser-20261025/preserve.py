"""Read-only baseline comparison; write a separate v35 preservation record."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((root / 'verification/final-integration-20261024/preservation-final.json').read_text())
artifacts = json.loads((root / 'verification/v34-root-browser-20261025/preservation.json').read_text())['artifacts'] + [{
    'path': str(root.parent / 'TrustLens-professional-20261025-email-media-v34-review.zip'),
    'sha256': '6e2b14ae16b0c43fdcdc03e0f0af0b51fab70b79ca9cd2215d427b070f8752e3',
}]
for row in artifacts:
    assert digest(Path(row['path'])) == row['sha256'], row['path']
original = json.loads((root / 'verification/model-next-integration/preservation-final.json').read_text())
for row in original['original_source_evidence']:
    assert digest(root.parent / 'neighborhood_hacks_20261021' / row['path']) == row['expected_sha256'], row['path']
for row in prior['protected_files']:
    assert digest(root / row['path']) == row['sha256'], row['path']
allowed = {'tests/phone_companion.test.cjs', 'app/analyzers/media_context.py', 'README.md', 'scripts/package.py', 'static/numbers-context.html', 'tests/reported_percentages_markup.test.cjs', 'static/numbers-context.js', 'static/phone/sw.js', 'app/intake.py', 'tests/pocket_context_cache.test.cjs', 'tests/reported_percentages_controller.test.cjs', 'tasks/todo.md', 'static/phone/index.html', 'scripts/export_phone.py', 'static/phone/share-demo.html', 'static/media-context.js'}
with zipfile.ZipFile(artifacts[-1]['path']) as archive:
    manifest = json.loads(archive.read('SOURCE_MANIFEST.json'))['files']
changed = []
for row in manifest:
    if digest(root / row['path']) != row['sha256']:
        changed.append(row['path'])
assert set(changed) == allowed, changed
record = {
    'previous_artifacts': len(artifacts), 'original_files': len(original['original_source_evidence']),
    'protected_files_unchanged_relative_v33': len(prior['protected_files']),
    'v34_manifest_entries': len(manifest), 'unchanged_entries': len(manifest) - len(changed),
    'intentional_existing_changes': sorted(changed), 'artifacts': artifacts,
    'phone_export': 'Pocket v35 cache v30; source receipt records separate current phone hash and offline evidence.',
}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record, indent=2))
print(json.dumps({key: value for key, value in record.items() if key != 'artifacts'}, indent=2))
