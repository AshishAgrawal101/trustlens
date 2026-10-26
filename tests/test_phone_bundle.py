import hashlib,json,zipfile,shutil
from pathlib import Path
import pytest
from scripts import export_phone
from scripts.export_phone import build_phone_bundle

def test_phone_bundle_contains_only_static_companion_and_verified_manifest(tmp_path,monkeypatch):
 source=export_phone.ROOT/'static/phone';shutil.copytree(source,tmp_path/'static/phone');(tmp_path/'static/phone/PRIVATE.txt').write_text('PRIVATE');monkeypatch.setattr(export_phone,'ROOT',tmp_path)
 for name in export_phone.PAGES.values():shutil.copyfile(source.parent/name,tmp_path/'static'/name)
 for name in export_phone.WORKSPACE_ASSETS:shutil.copyfile(source.parent/name.split('/')[-1],tmp_path/name.lstrip('/'))
 destination=tmp_path/'phone.zip';receipt=build_phone_bundle(destination)
 with zipfile.ZipFile(destination) as archive:
  assert archive.testzip() is None
  manifest=json.loads(archive.read('PHONE_TEST_MANIFEST.json'))
  assert 'phone/index.html' in archive.namelist() and 'phone/sw.js' in archive.namelist()
  assert len([item for item in manifest['files'] if item['path'].startswith('phone/')])==22
  for item in manifest['files']:assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
  assert all(name.startswith('phone/') or '/'+name in export_phone.WORKSPACE_ASSETS or name in ['README-IPHONE-TEST.md','PHONE_TEST_MANIFEST.json'] for name in archive.namelist())
  assert not any(name.endswith('.py') or 'local-runtime' in name or 'weights' in name for name in archive.namelist())
  assert 'HTTPS' in archive.read('README-IPHONE-TEST.md').decode()
 assert receipt['sha256']==hashlib.sha256(destination.read_bytes()).hexdigest()
 before=destination.read_bytes()
 with pytest.raises(FileExistsError):build_phone_bundle(destination)
 assert destination.read_bytes()==before
