"""Read-only baseline comparison; write a separate v36 preservation record."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((root / 'verification/final-integration-20261024/preservation-final.json').read_text())
artifacts = json.loads((root / 'verification/v35-root-browser-20261025/preservation.json').read_text())['artifacts'] + [{'path': str(root.parent / 'TrustLens-Pocket-iphone-test-v35.zip'), 'sha256': '0775eae01a5351ca6639408f2795be895f5cc912579b7ca3225cc32faf2289b4'}, {
    'path': str(root.parent / 'TrustLens-professional-20261025-drafts-resource-v35-review.zip'),
    'sha256': 'f0496d4a42b22be3868e39c3a99104867c787f6a837d43102414540e23c83e5f',
}]
for row in artifacts:
    assert digest(Path(row['path'])) == row['sha256'], row['path']
original = json.loads((root / 'verification/model-next-integration/preservation-final.json').read_text())
for row in original['original_source_evidence']:
    assert digest(root.parent / 'neighborhood_hacks_20261021' / row['path']) == row['expected_sha256'], row['path']
for row in prior['protected_files']:
    assert digest(root / row['path']) == row['sha256'], row['path']
allowed = {'README.md', 'tasks/todo.md', 'scripts/package.py', 'app/models.py', 'static/app.js'}
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
    'v35_manifest_entries': len(manifest), 'unchanged_entries': len(manifest) - len(changed),
    'intentional_existing_changes': sorted(changed), 'artifacts': artifacts,
    'phone_export': 'Pocket v35 cache v30 unchanged by desktop-only URL slice.',
}
Path(__file__).with_name('preservation.json').write_text(json.dumps(record, indent=2))
print(json.dumps({key: value for key, value in record.items() if key != 'artifacts'}, indent=2))
