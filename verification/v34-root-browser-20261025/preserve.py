"""Read-only baseline comparison; write a separate v34 preservation record."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((root / 'verification/final-integration-20261024/preservation-final.json').read_text())
artifacts = prior['artifacts'] + [{
    'path': str(root.parent / 'TrustLens-professional-20261024-passage-jumps-v33-review.zip'),
    'sha256': '0e474b6478ac98e32032ed8701ab559d87309b39127c3aec74935adfad21f1e3',
}]
for row in artifacts:
    assert digest(Path(row['path'])) == row['sha256'], row['path']
original = json.loads((root / 'verification/model-next-integration/preservation-final.json').read_text())
for row in original['original_source_evidence']:
    assert digest(root.parent / 'neighborhood_hacks_20261021' / row['path']) == row['expected_sha256'], row['path']
for row in prior['protected_files']:
    assert digest(root / row['path']) == row['sha256'], row['path']
allowed = {
    'README.md', 'tasks/todo.md', 'scripts/package.py', 'app/analyzers/email.py',
    'static/media-context.js', 'static/media-context.html', 'static/index.template.html',
    'tests/media_context.test.cjs', 'tests/media_controller_extra.test.cjs',
}
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
    'v33_manifest_entries': len(manifest), 'unchanged_entries': len(manifest) - len(changed),
    'intentional_existing_changes': sorted(changed), 'artifacts': artifacts,
    'phone_export': 'Unchanged v33 Pocket remains current; this desktop-only slice does not rebuild it.',
}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record, indent=2))
print(json.dumps({key: value for key, value in record.items() if key != 'artifacts'}, indent=2))
