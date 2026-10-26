from pathlib import Path

from app import capabilities
from test_community import request


def test_capabilities_are_configuration_only_and_do_not_expose_paths(monkeypatch, tmp_path):
    monkeypatch.setenv('TRUSTLENS_CLIP_CACHE', str(tmp_path / 'PRIVATE-CACHE'))
    monkeypatch.setenv('TRUSTLENS_COMMUNITY_WEIGHTS', str(tmp_path / 'PRIVATE-WEIGHTS'))
    monkeypatch.setattr(capabilities, 'credential_python', lambda: None)
    response = request('GET', '/api/capabilities')
    assert response.status_code == 200
    data = response.json()
    assert data['message_rules'] is True
    assert data['image_detector']['configured'] is False
    assert data['content_credentials']['configured'] is False
    assert 'PRIVATE' not in response.text
    assert 'not readiness' in data['notice']
    assert response.headers['cache-control'] == 'no-store'


def test_phone_shell_and_share_fallback_never_echo_input():
    assert request('GET', '/phone/').status_code == 200
    manifest = request('GET', '/phone/manifest.webmanifest').json()
    assert manifest['share_target']['method'] == 'POST'
    response = request('POST', '/phone/share', data={'text': 'PRIVATE-MESSAGE'})
    assert response.status_code == 409
    assert 'PRIVATE-MESSAGE' not in response.text
    assert response.headers['cache-control'] == 'no-store'
    assert request('POST', '/phone/share', headers={'origin': 'https://other.test'}).status_code == 403


def test_capabilities_follow_runtime_default_asset_locations(monkeypatch, tmp_path):
    root = tmp_path / 'project' / 'app'
    (root / 'models').mkdir(parents=True)
    (root / 'models/image_pipeline.json').write_text('{}')
    clip = tmp_path / 'work/clip-weights'
    clip.mkdir(parents=True)
    (clip / 'open_clip_model.safetensors').touch()
    community = tmp_path / 'work/community-forensics'
    community.mkdir()
    (community / 'model.safetensors').touch()
    monkeypatch.setattr(capabilities, 'ROOT', root)
    monkeypatch.delenv('TRUSTLENS_CLIP_CACHE', raising=False)
    monkeypatch.delenv('TRUSTLENS_COMMUNITY_WEIGHTS', raising=False)
    monkeypatch.setattr(capabilities.importlib.util, 'find_spec', lambda _: object())
    monkeypatch.setattr(capabilities, 'credential_python', lambda: None)
    assert capabilities.configured_capabilities()['image_detector']['configured'] is True
