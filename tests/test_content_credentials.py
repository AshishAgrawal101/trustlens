import io
import json
import hashlib
from pathlib import Path
import subprocess

from test_community import request
from PIL import Image
import pytest

from app.main import app
from app.analyzers import provenance
from app.analyzers.content_credentials_worker import summarize
from app.models import ContentCredentials


@pytest.fixture(scope='module')
def crypto(tmp_path_factory):
    python = provenance.credential_python()
    if python is None: pytest.skip('Optional C2PA CPU verifier is not installed')
    destination = tmp_path_factory.mktemp('credentials')
    source = destination/'source.png'
    Image.new('RGB',(32,32),(20,60,90)).save(source)
    subprocess.run([python,str(Path(__file__).with_name('credentials_crypto_check.py')),
                    str(source),str(destination)],check=True,capture_output=True,timeout=30)
    return destination,json.loads((destination/'results.json').read_text())


def test_real_signatures_trust_and_file_binding(crypto):
    directory, checks = crypto
    assert checks['trusted']['status'] == 'verified'
    assert checks['trusted']['signer'] == 'Test Generator ONLY'
    assert checks['trusted']['tool'] == 'Test AI Tool ONLY'
    assert checks['trusted']['declaration'] == 'generated'
    assert checks['untrusted']['status'] == 'untrusted'
    assert checks['untrusted']['trust_list'] is None
    assert checks['tampered']['status'] == 'invalid'
    assert 'assertion.dataHash.mismatch' in checks['tampered']['validation_codes']
    assert Image.open(directory/'tampered.png').size == (32,32)
    assert checks['absent']['status'] == 'absent'
    assert checks['edited']['declaration'] == 'edited'
    assert checks['conventional_edit']['declaration'] is None
    assert checks['no_tool']['tool'] is None  # manifest writer is not the generation tool
    assert checks['external']['status'] == 'external'


def test_trusted_generation_skips_model_without_a_fabricated_score(crypto,monkeypatch):
    directory, checks = crypto
    monkeypatch.setattr(provenance,'read_credentials',lambda _:ContentCredentials(**checks['trusted']))
    def unexpected(_): pytest.fail('The model must not run for an explicit trusted generation declaration')
    monkeypatch.setattr(provenance,'analyze_image',unexpected)
    response = request('POST','/api/analyze/image',files={'file':('signed.png',(directory/'signed.png').read_bytes(),'image/png')})
    assert response.status_code == 200
    report = response.json()
    assert report['model_ran'] is False
    assert report['risk_index'] is None
    assert report['decision_basis'] == 'content_credentials'
    assert 'Test Generator ONLY' in report['summary']


@pytest.mark.parametrize('state', ['untrusted','tampered','absent','edited','conventional_edit'])
def test_other_credentials_keep_the_frozen_model_decision(crypto,monkeypatch,state):
    directory, checks = crypto
    monkeypatch.setattr(provenance,'read_credentials',lambda _:ContentCredentials(**checks[state]))
    class Pipeline:
        threshold = .35
        metadata = {'evaluation':{'accuracy':.9507462687,'n':670,'accuracy_wilson_95_interval':[.9316,.9647]}}
        robustness = None
        def score(self,image): return .4
    monkeypatch.setattr('app.analyzers.image.load_runtime',lambda:Pipeline())
    report = provenance.analyze_image_with_credentials((directory/'signed.png').read_bytes())
    assert report.model_ran is True
    assert report.risk_index == 40
    assert report.risk_level == 'high'
    assert 'AI patterns detected' in report.summary


def test_actual_worker_has_no_trust_in_test_root(crypto):
    directory, _ = crypto
    assert provenance.read_credentials((directory/'signed.png').read_bytes()).status == 'untrusted'


def test_upload_through_actual_cpu_verifier_reports_signer_and_tool(crypto,tmp_path,monkeypatch):
    directory, _ = crypto
    # Exercise the shipped subprocess and upload endpoint against an isolated
    # test trust store. The app's production certificates remain untouched.
    worker=tmp_path/'isolated-verifier/app/analyzers/content_credentials_worker.py'
    worker.parent.mkdir(parents=True)
    worker.write_bytes(provenance.WORKER.read_bytes())
    trust=worker.parents[1]/'trust'; trust.mkdir()
    root=(directory/'test-root.pem').read_bytes()
    materials={'c2pa-trust-list.pem':root, 'interim-anchors.pem':root,
               'interim-allowed.txt':b'', 'interim-config.txt':b''}
    snapshot=[]
    for name,data in materials.items():
        (trust/name).write_bytes(data)
        snapshot.append({'name':name,'sha256':hashlib.sha256(data).hexdigest()})
    (trust/'snapshot.json').write_text(json.dumps({'sources':snapshot}))
    monkeypatch.setattr(provenance,'WORKER',worker)
    def unexpected(_): pytest.fail('A trusted AI-generation declaration must skip inference')
    monkeypatch.setattr(provenance,'analyze_image',unexpected)
    response = request('POST','/api/analyze/image',files={'file':('signed.png',(directory/'signed.png').read_bytes(),'image/png')})
    assert response.status_code==200
    report=response.json()
    assert report['model_ran'] is False and report['risk_index'] is None
    assert report['content_credentials']['status']=='verified'
    assert report['content_credentials']['signer']=='Test Generator ONLY'
    assert report['content_credentials']['tool']=='Test AI Tool ONLY'
    (directory/'verified_api_report.json').write_text(json.dumps(report),encoding='utf-8')


def test_unknown_signer_through_actual_upload_does_not_skip_model(crypto,monkeypatch):
    directory, _ = crypto
    class Pipeline:
        threshold=.35
        metadata={'evaluation':{'accuracy':.9507462687,'n':670,'accuracy_wilson_95_interval':[.9316,.9647]}}
        robustness=None
        def score(self,image): return .4
    monkeypatch.setattr('app.analyzers.image.load_runtime',lambda:Pipeline())
    response = request('POST','/api/analyze/image',files={'file':('untrusted.png',(directory/'signed.png').read_bytes(),'image/png')})
    assert response.status_code==200
    report=response.json()
    assert report['model_ran'] is True and report['risk_index']==40
    assert report['decision_basis']=='model'
    assert report['content_credentials']['status']=='untrusted'


def test_unknown_verifier_and_timeout_fall_back(monkeypatch):
    monkeypatch.setattr(provenance,'credential_python',lambda:None)
    assert provenance.read_credentials(b'asset').status == 'unavailable'
    monkeypatch.setattr(provenance,'credential_python',lambda:'python')
    def timeout(*args,**kwargs): raise subprocess.TimeoutExpired('verifier',15)
    monkeypatch.setattr(provenance.subprocess,'run',timeout)
    assert provenance.read_credentials(b'asset').status == 'unavailable'


def test_signature_without_asset_binding_or_active_claim_is_not_verified():
    store = {'active_manifest':'active','validation_state':'Trusted','manifests':{'active':{'assertions':[]}},
             'validation_results':{'activeManifest':{'success':[{'code':'signingCredential.trusted'},
                {'code':'claimSignature.validated'}],'failure':[]}}}
    assert summarize(store,'test')['status'] == 'invalid'
    store['active_manifest'] = 'missing'
    assert summarize(store,'test')['status'] == 'invalid'
