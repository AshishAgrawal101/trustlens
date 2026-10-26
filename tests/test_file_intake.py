"""Real native QR fixtures and byte-preserving local mail intake."""
import asyncio
from email import policy
from email.message import EmailMessage
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from fastapi import FastAPI
import httpx
from PIL import Image
import pytest

from app.intake import router
from app.analyzers import qr
from app.analyzers.email import analyze_email, analyze_email_bytes, MAX_EMAIL_BYTES
from app.analyzers.image import InvalidImage

app=FastAPI()
app.include_router(router)


def request(path, content, name='fixture.png'):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
            return await client.post(path,files={'file':(name,content,'application/octet-stream')})
    return asyncio.run(run())


def png(image):
    output=io.BytesIO()
    image.save(output,format='PNG')
    return output.getvalue()


def qr_fixture(*values):
    cv2=pytest.importorskip('cv2')
    images=[]
    for value in values:
        matrix=cv2.QRCodeEncoder_create().encode(value)
        image=Image.fromarray(matrix)
        images.append(image.resize((image.width*10,image.height*10),Image.Resampling.NEAREST))
    canvas=Image.new('L',(sum(i.width for i in images)+80*(len(images)+1),max(i.height for i in images)+160),255)
    x=80
    for image in images:
        canvas.paste(image,(x,80))
        x+=image.width+80
    return png(canvas)


def test_native_single_qr_is_review_only_and_temporary_image_is_removed(monkeypatch):
    subprocess_run=qr.subprocess.run
    paths=[]
    def run(args,**kwargs):
        paths.append(Path(args[-2]))
        assert paths[-1].is_file() and kwargs['timeout']==15
        return subprocess_run(args,**kwargs)
    monkeypatch.setattr(qr.subprocess,'run',run)
    response=request('/api/extract/qr',qr_fixture('https://example.org/review-only'))
    assert response.status_code==200,response.text
    result=response.json()
    assert result['codes']==['https://example.org/review-only']
    assert result['text']=='https://example.org/review-only' and result['review_required'] is True
    assert 'No address was opened' in result['notice'] and 'risk_level' not in result
    assert paths and all(not p.exists() for p in paths)


def test_native_multiple_qr_codes_are_retained_without_destination_visits():
    result=qr.extract_qr(qr_fixture('https://example.org/one','https://example.net/two'))
    assert set(result['codes'])=={'https://example.org/one','https://example.net/two'}
    assert set(result['text'].splitlines())==set(result['codes'])


def test_native_plain_text_payload_is_not_assumed_to_be_a_url():
    result=qr.extract_qr(qr_fixture('Call the library at its known number.'))
    assert result['text']=='Call the library at its known number.' and result['review_required']


def test_native_control_payload_is_rejected_without_a_verdict():
    with pytest.raises(InvalidImage,match='control characters'):
        qr.extract_qr(qr_fixture('\x1b[31mHidden terminal control'))


def test_native_active_scheme_is_only_extracted_as_reviewable_text():
    result=qr.extract_qr(qr_fixture('javascript:alert(1)'))
    assert result['text']=='javascript:alert(1)' and result['review_required']
    assert 'No address was opened' in result['notice']


def test_native_blank_and_malformed_images_fail_without_a_verdict():
    response=request('/api/extract/qr',png(Image.new('RGB',(200,200),'white')))
    assert response.status_code==400 and 'No readable QR' in response.json()['detail']
    response=request('/api/extract/qr',b'not an image')
    assert response.status_code==400 and 'image' in response.json()['detail']


def test_qr_timeout_cleans_temporary_file_and_releases_lock(monkeypatch):
    paths=[]
    def timeout(args,**kwargs):
        paths.append(Path(args[-2]))
        raise subprocess.TimeoutExpired(args,15)
    monkeypatch.setattr(qr.subprocess,'run',timeout)
    with pytest.raises(qr.QrUnavailable,match='timed out'):
        qr.extract_qr(png(Image.new('RGB',(20,20),'white')))
    assert not qr._lock.locked() and paths and all(not p.exists() for p in paths)


def test_real_timeout_transport_kills_and_reaps_worker(monkeypatch):
    real_run=qr.subprocess.run
    real_popen=qr.subprocess.Popen
    workers=[];paths=[]
    def popen(*args,**kwargs):
        worker=real_popen(*args,**kwargs)
        workers.append(worker)
        return worker
    def sleeping_worker(args,**kwargs):
        paths.append(Path(args[-2]))
        assert kwargs['timeout']==15
        return real_run([sys._base_executable,'-c','import time; time.sleep(60)'],
            **dict(kwargs,timeout=.2))
    monkeypatch.setattr(qr.subprocess,'Popen',popen)
    monkeypatch.setattr(qr.subprocess,'run',sleeping_worker)
    with pytest.raises(qr.QrUnavailable,match='timed out'):
        qr.extract_qr(png(Image.new('RGB',(20,20),'white')))
    assert len(workers)==1 and workers[0].poll() is not None
    assert not qr._lock.locked() and all(not p.exists() for p in paths)


def test_qr_busy_does_not_decode_or_launch_worker():
    qr._lock.acquire()
    try:
        with pytest.raises(qr.QrUnavailable,match='Another QR'):
            qr.extract_qr(b'bad')
    finally:
        qr._lock.release()


@pytest.mark.parametrize('output',[
    b'not-json',b'\xff',b'{"codes": "wrong"}',b'{"codes": [null]}',b'{}',b'null',b'[]',
])
def test_worker_bad_output_is_unavailable(monkeypatch,output):
    monkeypatch.setattr(qr.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=output))
    response=request('/api/extract/qr',png(Image.new('RGB',(20,20),'white')))
    assert response.status_code==503 and 'unavailable' in response.json()['detail']


@pytest.mark.parametrize('codes',[[str(i) for i in range(17)],['x'*30001]])
def test_qr_result_bounds(monkeypatch,codes):
    import json
    monkeypatch.setattr(qr.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=json.dumps({'codes':codes}).encode()))
    with pytest.raises(InvalidImage,match='Too many'):
        qr.extract_qr(png(Image.new('RGB',(20,20),'white')))


@pytest.mark.parametrize('code',['https://example.org/\x00hidden','\x1b[31mtext','https://example.org/\u202eevil'])
def test_qr_hidden_control_text_requires_manual_entry(monkeypatch,code):
    import json
    monkeypatch.setattr(qr.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=json.dumps({'codes':[code]}).encode()))
    response=request('/api/extract/qr',png(Image.new('RGB',(20,20),'white')))
    assert response.status_code==400 and 'control characters' in response.json()['detail']


def test_worker_size_rejection_is_actionable_and_no_partial_codes_return(monkeypatch):
    monkeypatch.setattr(qr.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=b'{"codes": [], "too_large": true}'))
    response=request('/api/extract/qr',png(Image.new('RGB',(20,20),'white')))
    assert response.status_code==400 and 'Crop to one code' in response.json()['detail']


def test_qr_rejects_over_pixel_limit_before_native_worker(monkeypatch):
    import app.analyzers.image as images
    monkeypatch.setattr(images,'MAX_PIXELS',100)
    with pytest.raises(InvalidImage,match='20 million'):
        qr.extract_qr(png(Image.new('RGB',(11,10),'white')))


@pytest.mark.parametrize('charset,cte',[('utf-8','base64'),('iso-8859-1','quoted-printable')])
def test_eml_mime_encoding_preserves_body_and_encoded_subject(charset,cte):
    message=EmailMessage(policy=policy.SMTP)
    message['From']='René <office@example.org>'
    message['Subject']='Réunion'
    message.set_content('Café meeting. Send me your password.',charset=charset,cte=cte)
    content=message.as_bytes()
    report=analyze_email_bytes(content)
    assert any(e.id=='request:code' for e in report.evidence)
    assert not any(e.id=='email:incomplete' for e in report.evidence)
    response=request('/api/analyze/email-file',content,'meeting.eml')
    assert response.status_code==200,response.text
    assert response.json()['kind']=='email' and response.json()['actions']
    assert any('Attachments are not scanned' in text for text in response.json()['limitations'])


def test_eml_attachments_and_forwarded_messages_remain_unscanned():
    message=EmailMessage()
    message.set_content('Meeting notes attached.')
    attached=EmailMessage()
    attached.set_content('Send me your password.')
    message.add_attachment(attached,filename='forwarded.eml')
    message.add_attachment(b'Send gift cards now',maintype='application',subtype='octet-stream',filename='notes.bin')
    report=analyze_email_bytes(message.as_bytes())
    assert not any(e.id.startswith('request:') for e in report.evidence)
    assert any('Attachments are not scanned' in text for text in report.limitations)


def test_eml_matches_existing_plain_text_behavior():
    raw='From: office@example.org\nReply-To: other@elsewhere.example\nSubject: Hello\n\nSend me your password.'
    assert analyze_email_bytes(raw.encode()).model_dump()==analyze_email(raw).model_dump()


@pytest.mark.parametrize('content',[b'',b' \r\n',b'x'*(MAX_EMAIL_BYTES+1)],ids=['empty','whitespace','oversize'])
def test_eml_empty_and_oversize_have_actionable_errors(content):
    response=request('/api/analyze/email-file',content,'message.eml')
    assert response.status_code==400 and '.eml' in response.json()['detail']


def test_eml_binary_upload_is_not_reported_as_a_clean_message():
    response=request('/api/analyze/email-file',b'\x89PNG\r\n\x00binary','not-really-mail.eml')
    assert response.status_code==400 and 'binary content' in response.json()['detail']


def test_eml_unknown_charset_is_explicitly_incomplete():
    response=request('/api/analyze/email-file',b'Content-Type: text/plain; charset=unknown-encoding\r\n\r\nHello','message.eml')
    assert response.status_code==200
    assert any(e['id']=='email:incomplete' for e in response.json()['evidence'])
    assert response.json()['actions'][0]['title']=='Review the original email'


def test_eml_invalid_declared_encoding_keeps_readable_warnings_but_is_partial():
    report=analyze_email_bytes(b'Content-Type: text/plain; charset=utf-8\r\n\r\nSend me your password.\xff')
    assert any(e.id=='request:code' for e in report.evidence)
    assert any(e.id=='email:incomplete' for e in report.evidence)
    assert report.risk_level=='high'


def test_deep_mime_is_rejected_in_byte_and_pasted_entrypoints():
    raw=''.join(f'Content-Type: multipart/mixed; boundary=b{i}\r\n\r\n--b{i}\r\n' for i in range(1100))
    raw+='Content-Type: text/plain\r\n\r\nMeeting notes.\r\n'
    raw+=''.join(f'--b{i}--\r\n' for i in reversed(range(1100)))
    for value,analyzer in [(raw,analyze_email),(raw.encode(),analyze_email_bytes)]:
        with pytest.raises(ValueError,match='structure could not be read'):
            analyzer(value)
