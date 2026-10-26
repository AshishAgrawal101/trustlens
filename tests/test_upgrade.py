import io
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw, ImageFont
from app.analyzers import screenshot
from app.analyzers.text import request_evidence, analyze_text
from app.guidance import add_guidance
from test_community import request

CASES = json.loads((Path(__file__).parent/'fixtures/request_cases.json').read_text())


@pytest.mark.parametrize('case', CASES, ids=lambda c:c['text'][:60])
def test_labeled_request_cases(case):
    assert sorted(e.id.removeprefix('request:') for e in request_evidence(case['text'])) == sorted(case['keys'])


def image_bytes(blank=False):
    image=Image.new('RGB',(1100,350),'white')
    if not blank:
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',38)
        ImageDraw.Draw(image).multiline_text((35,35),'BANK ALERT\nSend the verification code immediately.\nDo not call your bank.',font=font,fill='black',spacing=18)
    buffer=io.BytesIO();image.save(buffer,format='PNG');return buffer.getvalue()


def test_specific_actions_and_input_free_exports():
    report=add_guidance(analyze_text('PRIVATE Jane, move your savings to a safe account.'))
    assert report.actions[0].title=='Pause the payment'
    assert 'PRIVATE' not in report.share_summary and 'Jane' not in report.share_summary
    report=add_guidance(analyze_text('Please share the source code.'))
    assert not any('security codes' in a.title.lower() for a in report.actions)
    report=add_guidance(analyze_text('Return the difference after the check arrives.'))
    assert report.actions[0].title=='Do not return the difference yet'


def test_recovery_catalog_has_all_paths_and_source():
    response=request('GET','/api/recovery')
    data=response.json()
    assert {p['id'] for p in data['plans']}=={'paid','account','device','clicked'}
    assert 'consumer.ftc.gov/' in data['source']
    assert all(len(p['steps'])>=2 for p in data['plans'])
    assert response.headers['cache-control']=='no-store'


def test_screenshot_rejects_non_image():
    assert request('POST','/api/extract/screenshot',files={'file':('x.png',b'bad','image/png')}).status_code==400


def test_screenshot_worker_temporary_file_removed(monkeypatch):
    paths=[]
    def run(args,**kwargs):
        path=Path(args[-1]);paths.append(path);assert path.is_file()
        assert kwargs['timeout']==30
        return SimpleNamespace(returncode=0,stdout=b'{"text":"review me", "language":"en-US"}')
    monkeypatch.setattr(screenshot.subprocess,'run',run)
    if os.name!='nt': pytest.skip('Windows worker path')
    data=screenshot.extract_screenshot(image_bytes(True))
    assert data['review_required'] is True and data['text']=='review me'
    assert paths and all(not p.exists() for p in paths)


def test_screenshot_timeout_releases_lock_and_temp_file(monkeypatch):
    if os.name!='nt': pytest.skip('Windows worker path')
    paths=[]
    def timeout(args,**kwargs):
        paths.append(Path(args[-1]));raise subprocess.TimeoutExpired(args,30)
    monkeypatch.setattr(screenshot.subprocess,'run',timeout)
    with pytest.raises(screenshot.OcrUnavailable,match='timed out'):
        screenshot.extract_screenshot(image_bytes(True))
    assert not screenshot._lock.locked() and all(not p.exists() for p in paths)


def test_screenshot_busy_does_not_start_worker():
    if os.name!='nt': pytest.skip('Windows worker path')
    screenshot._lock.acquire()
    try:
        with pytest.raises(screenshot.OcrUnavailable,match='Another screenshot'):
            screenshot.extract_screenshot(image_bytes(True))
    finally:
        screenshot._lock.release()


def test_screenshot_unavailable_is_actionable(monkeypatch):
    import app.main
    def unavailable(_):raise screenshot.OcrUnavailable('Paste the message instead.')
    monkeypatch.setattr(app.main,'extract_screenshot',unavailable)
    response=request('POST','/api/extract/screenshot',files={'file':('x.png',image_bytes(True),'image/png')})
    assert response.status_code==503 and 'Paste' in response.json()['detail']


@pytest.mark.skipif(os.environ.get('TRUSTLENS_TEST_NATIVE_OCR')!='1',reason='Opt in to real Windows OCR integration')
def test_real_native_ocr_then_reviewed_message_analysis():
    response=request('POST','/api/extract/screenshot',files={'file':('demo.png',image_bytes(),'image/png')})
    assert response.status_code==200,response.text
    data=response.json();assert data['review_required'] and data['language']=='en-US'
    assert 'verification code' in data['text'].lower()
    # The OCR endpoint never returns a verdict or invokes the classifier.
    assert 'risk_level' not in data
    checked=request('POST','/api/analyze/text',json={'text':data['text']}).json()
    assert any(e['id']=='request:code' for e in checked['evidence'])
    blank=request('POST','/api/extract/screenshot',files={'file':('blank.png',image_bytes(True),'image/png')})
    assert blank.status_code==200 and blank.json()['text']==''
