"""Create and verify a source-only handoff; never include local configuration or weights."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ('app', 'ai_detector', 'models', 'static', 'tests', 'docs', 'submission', 'tasks', 'scripts', 'verification', 'experiments/results/external_cf1006')
ROOT_FILES = ('README.md', '.gitignore', 'frontend.py', 'serve.py', 'Start-TrustLens.cmd', 'requirements.txt', 'requirements-ai.txt', 'requirements-credentials.txt', 'requirements-qr.txt')


def main():
    files = [ROOT / name for name in ROOT_FILES]
    for folder in DIRECTORIES:
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts
                     and p.suffix != '.pyc' and p != ROOT / 'static/index.html')
    files = sorted(set(files))
    destination = ROOT.parent / 'TrustLens-professional-20261025-input-recovery-v42-review.zip'
    if destination.exists():
        raise FileExistsError('Preserve the existing review archive; choose a new version name before packaging.')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'files': [
        {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
         'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files:
            archive.write(p, p.relative_to(ROOT).as_posix())
        archive.writestr('SOURCE_MANIFEST.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
        names = archive.namelist()
        assert not any(name.startswith(('artifacts/', '.git/')) or name in ('local-runtime.json', 'local-python.cmd') for name in names)
        assert not any(name.endswith(('.safetensors', '.pt', '.pth')) for name in names)
        assert 'app/main.py' in names and 'static/app.js' in names and 'tests/test_community.py' in names
    receipt = {'path': str(destination), 'files': len(files)+1, 'bytes': destination.stat().st_size,
               'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(), 'verified': True}
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    (ROOT / 'artifacts/package-receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
