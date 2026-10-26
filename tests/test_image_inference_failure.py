"""A failed cross-check cannot become an origin result; no real model is loaded."""
import io
import asyncio
import httpx
import pytest
from PIL import Image
from app.analyzers import image, provenance
from app.models import ContentCredentials
from app.main import app


def png():
    buffer = io.BytesIO()
    Image.new('RGB', (20, 24)).save(buffer, format='PNG')
    return buffer.getvalue()


class Pipeline:
    threshold = .35
    robustness = None
    metadata = {'evaluation': {'accuracy': .95, 'n': 670,
                              'accuracy_wilson_95_interval': [.93, .96]}}


@pytest.mark.parametrize('failure', [RuntimeError, MemoryError, ValueError, IndexError, AttributeError, OSError])
def test_inference_failure_preserves_provenance_without_origin_or_private_error(monkeypatch, failure):
    class Broken(Pipeline):
        def score(self, _):
            raise failure('PRIVATE IMAGE PATH AND RUNTIME DETAIL')
    monkeypatch.setattr(image, 'load_runtime', lambda: Broken())
    monkeypatch.setattr(provenance, 'read_credentials', lambda _: ContentCredentials(status='absent', detail='No embedded credentials.'))
    report = provenance.analyze_image_with_credentials(png())
    assert report.model_ran is False and report.risk_index is None
    assert report.content_credentials.status == 'absent'
    assert not any(e.id in {'image:model', 'image:clip', 'image:community'} for e in report.evidence)
    assert 'PRIVATE' not in report.model_dump_json()


@pytest.mark.parametrize('score,threshold', [(float('nan'), .35), (float('inf'), .35), (-.1, .35), (1.1, .35), (.4, float('nan')), (.4, 0), (.4, 1), (True, .35)])
def test_invalid_scalar_or_threshold_is_unavailable(monkeypatch, score, threshold):
    class Broken(Pipeline):
        def score(self, _): return score
    instance = Broken()
    instance.threshold = threshold
    monkeypatch.setattr(image, 'load_runtime', lambda: instance)
    with pytest.raises(image.ImageModelUnavailable):
        image.analyze_image(png())


@pytest.mark.parametrize('details', [None, {}, {'combined': .4}, {'combined': .4, 'clip_probe': float('nan'), 'community': .2}, {'combined': .4, 'clip_probe': True, 'community': .2}])
def test_incomplete_or_invalid_branch_scores_cannot_claim_cross_verification(monkeypatch, details):
    class Broken(Pipeline):
        def score_details(self, _): return details
        def score(self, _): pytest.fail('Do not run another scoring attempt')
    monkeypatch.setattr(image, 'load_runtime', lambda: Broken())
    with pytest.raises(image.ImageModelUnavailable):
        image.analyze_image(png())


def test_invalid_upload_remains_an_input_error_not_a_model_fallback(monkeypatch):
    monkeypatch.setattr(image, 'load_runtime', lambda: pytest.fail('No model for invalid upload'))
    with pytest.raises(image.InvalidImage):
        provenance.analyze_image_with_credentials(b'not an image')


def test_failed_detector_api_keeps_signed_history_but_no_pattern_result(monkeypatch):
    class Broken(Pipeline):
        def score(self, _): raise RuntimeError('PRIVATE RUNTIME DETAIL')
    monkeypatch.setattr(image, 'load_runtime', lambda: Broken())
    monkeypatch.setattr(provenance, 'read_credentials', lambda _: ContentCredentials(status='verified', detail='Signed edit is asset-bound.', declaration='edited'))
    async def request():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1') as client:
            return await client.post('/api/analyze/image', files={'file': ('constructed.png', png(), 'image/png')})
    response = asyncio.run(request())
    assert response.status_code == 200
    report = response.json()
    assert report['content_credentials']['status'] == 'verified'
    assert report['model_ran'] is False and report['risk_index'] is None
    assert [e['id'] for e in report['evidence']] == ['image:credentials']
    assert 'PRIVATE' not in response.text
    assert 'AI patterns detected' not in report['share_summary']
    assert 'Photograph patterns detected' not in report['share_summary']
