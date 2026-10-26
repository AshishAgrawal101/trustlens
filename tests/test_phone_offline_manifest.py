"""The exported companion must contain every fixed offline-shell asset."""
import ast,re,zipfile
from scripts.export_phone import build_phone_bundle, WORKSPACE_ASSETS

def test_export_contains_every_declared_offline_asset(tmp_path):
    destination=tmp_path/'pocket.zip'
    build_phone_bundle(destination)
    with zipfile.ZipFile(destination) as archive:
        source=archive.read('phone/sw.js').decode()
        match=re.search(r'const SHELL = (\[[^;]+\]);',source)
        assert match is not None
        paths=ast.literal_eval(match.group(1))
        assert '/phone/context.html' in paths
        for url in paths:
            assert (url.startswith('/phone/') or url in WORKSPACE_ASSETS) and '?' not in url
            name='phone/index.html' if url=='/phone/' else url.lstrip('/')
            assert name in archive.namelist(),f'Offline asset missing from export: {url}'
        assert b'Five short guides' in archive.read('phone/context.html')
