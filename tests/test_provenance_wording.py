"""Provenance outcomes must not promise that an optional detector runs."""
import io
import json
import sys
from types import SimpleNamespace

import pytest
from app.analyzers import content_credentials_worker as worker
from app.analyzers import provenance
from app.models import ContentCredentials


@pytest.mark.parametrize('error_type,message,status,detail', [
    ('remote', 'remote', 'external', 'External Content Credentials were not fetched.'),
    ('generic', 'Remote: must fetch remote manifests from url https://private.example/', 'external', 'External Content Credentials were not fetched.'),
    ('generic', 'validation failed', 'invalid', 'Content Credentials could not be validated.'),
])
def test_verifier_error_reports_only_its_actual_outcome(monkeypatch,error_type,message,status,detail):
    class SdkError(Exception): pass
    class Missing(SdkError): pass
    class Remote(SdkError): pass
    SdkError.ManifestNotFound = Missing
    SdkError.RemoteManifest = Remote
    def fail(_):
        raise (Remote if error_type == 'remote' else SdkError)(message)
    monkeypatch.setitem(sys.modules, 'c2pa', SimpleNamespace(C2paError=SdkError, Context=SimpleNamespace(from_dict=fail)))
    answer = worker.verify(b'not-an-image', 'image/png', [('test', {})])
    assert answer == {'status': status, 'detail': detail}
    # No real image decode or model is needed to compose the unavailable result.
    monkeypatch.setattr(provenance,'decode_image',lambda _:SimpleNamespace(size=(1,1),close=lambda:None))
    monkeypatch.setattr(provenance,'read_credentials',lambda _:ContentCredentials(**answer))
    def unavailable(_): raise provenance.ImageModelUnavailable('not installed')
    monkeypatch.setattr(provenance,'analyze_image',unavailable)
    report = provenance.analyze_image_with_credentials(b'not-an-image')
    assert report.model_ran is False
    assert report.content_credentials.status == status
    assert report.content_credentials.detail == detail
    assert 'will analyze' not in ' '.join(e.detail for e in report.evidence)


def test_worker_main_failure_does_not_promise_detector(monkeypatch):
    monkeypatch.setattr(sys,'stdin',SimpleNamespace(buffer=io.BytesIO(b'')))
    monkeypatch.setattr(sys,'argv',['worker','unsupported'])
    output = io.StringIO()
    monkeypatch.setattr(sys,'stdout',output)
    worker.main()
    assert json.loads(output.getvalue()) == {'status':'unavailable','detail':'Content Credentials verification is unavailable.'}
