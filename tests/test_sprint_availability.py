"""Image service availability contracts; no native worker or model scoring."""
import io

import pytest
from PIL import Image

from app.analyzers import provenance
from app.analyzers.image import ImageModelUnavailable
from app.models import AnalysisReport, ContentCredentials
from test_community import request


@pytest.fixture
def image_upload():
    buffer = io.BytesIO()
    Image.new('RGB', (20, 20)).save(buffer, format='PNG')
    return {'file': ('PRIVATE-FILENAME.png', buffer.getvalue(), 'image/png')}


def missing_model(_):
    raise ImageModelUnavailable('not installed')


def test_both_image_services_unavailable_is_not_a_completed_check(monkeypatch, image_upload):
    monkeypatch.setattr(provenance, 'credential_python', lambda: None)
    monkeypatch.setattr(provenance, 'analyze_image', missing_model)
    response = request('POST', '/api/analyze/image', files=image_upload)
    assert response.status_code == 200
    report = response.json()
    assert report['model_ran'] is False and report['risk_index'] is None
    assert report['content_credentials']['status'] == 'unavailable'
    assert report['summary'].startswith('Image checks unavailable.')
    assert 'Message mode' in report['summary'] and 'README.md' in report['summary']
    assert 'will analyze' not in report['content_credentials']['detail']
    assert any('README' in text and 'Message' in text for text in report['limitations'])
    assert 'PRIVATE-FILENAME' not in report['share_summary']


@pytest.mark.parametrize('status', ['absent', 'invalid', 'untrusted', 'external'])
def test_missing_model_preserves_the_available_credentials_result(monkeypatch, image_upload, status):
    monkeypatch.setattr(provenance, 'read_credentials', lambda _: ContentCredentials(status=status, detail='Fixture credentials result'))
    monkeypatch.setattr(provenance, 'analyze_image', missing_model)
    response = request('POST', '/api/analyze/image', files=image_upload)
    assert response.status_code == 200
    report = response.json()
    assert report['model_ran'] is False and report['risk_index'] is None
    assert report['content_credentials']['status'] == status
    assert report['summary'] == 'Image detector unavailable. Only the Content Credentials check is shown.'
    assert report['evidence'][0]['detail'] == 'Fixture credentials result'


def test_available_model_survives_unavailable_credentials(monkeypatch, image_upload):
    monkeypatch.setattr(provenance, 'credential_python', lambda: None)
    model = AnalysisReport(kind='image', risk_index=40, risk_level='guarded', confidence='low',
        summary='Fixture model result', evidence=[], limitations=['Fixture limitation'])
    monkeypatch.setattr(provenance, 'analyze_image', lambda _: model)
    response = request('POST', '/api/analyze/image', files=image_upload)
    assert response.status_code == 200
    report = response.json()
    assert report['model_ran'] is True and report['risk_index'] == 40
    assert report['summary'] == 'Fixture model result'
    assert report['content_credentials']['status'] == 'unavailable'
    assert 'will analyze' not in report['content_credentials']['detail']


def test_trusted_generation_declaration_still_skips_the_model(monkeypatch, image_upload):
    monkeypatch.setattr(provenance, 'read_credentials', lambda _: ContentCredentials(
        status='verified', detail='Fixture trusted declaration', declaration='generated', signer='Fixture signer'))
    monkeypatch.setattr(provenance, 'analyze_image', lambda _: pytest.fail('Trusted generation must skip the model'))
    response = request('POST', '/api/analyze/image', files=image_upload)
    assert response.status_code == 200
    report = response.json()
    assert report['model_ran'] is False and report['risk_index'] is None
    assert report['content_credentials']['status'] == 'verified'
    assert report['summary'] == 'Fixture signer signed this image and declared it AI-generated.'
