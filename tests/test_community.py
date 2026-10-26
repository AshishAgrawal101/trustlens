import asyncio
import io
import httpx
import pytest
from PIL import Image
from app.main import app
from app.analyzers.text import analyze_text
from app.analyzers.email import analyze_email
from app.analyzers.url import analyze_url
from app.analyzers import provenance
from app.analyzers.image import ImageModelUnavailable
from app.models import ContentCredentials
from app.guidance import add_guidance


def request(method,path,**kwargs):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
            return await client.request(method,path,**kwargs)
    return asyncio.run(run())


@pytest.mark.parametrize('text,key',[
    ('Read me the verification code.','code'),
    ('Buy gift cards to pay this bill.','payment'),
    ('Please install AnyDesk.','remote'),
    ('Do not tell your family about this.','secrecy'),
    ('Act now or your account will be suspended.','threat'),
])
def test_dangerous_requests(text,key):
    assert 'request:'+key in {e.id for e in analyze_text(text).evidence}


@pytest.mark.parametrize('text',[
    'Your one-time code is 123456. Do not share it with anyone.',
    'Never share your password. Do not send gift cards.',
    "We won't ask you to read us a verification code.",
    'The library meeting is at 6 pm. Please bring a notebook.',
])
def test_benign_or_negated_requests(text):
    assert not any(e.weight>0 for e in analyze_text(text).evidence)


def test_sender_code_and_link_never_enter_shared_summary():
    report=add_guidance(analyze_text('Alice Jones, send code 943178 to alice@example.net or https://secret.example/?token=PRIVATE and call 312-555-9911.'))
    for private in ['Alice','943178','alice@example','secret.example','PRIVATE','312-555']:
        assert private not in report.share_summary
    assert report.risk_index is None


def test_link_host_not_userinfo():
    report=analyze_url('https://bank.example@evil.example/login')
    assert report.evidence[0].detail=='evil.example'
    assert any(e.id=='url:userinfo' for e in report.evidence)
    assert report.risk_level=='high'


@pytest.mark.parametrize('url',['javascript:alert(1)','file:///etc/passwd','https://[broken','https://example.com:bad','https://exa mple.com','https://example.com\\@evil.example'])
def test_bad_url_is_client_error(url):
    response=request('POST','/api/analyze/url',json={'url':url})
    assert response.status_code==400


def test_email_auth_untrusted_and_html_body_analyzed():
    raw='From: A <a@example.org>\nAuthentication-Results: forged; spf=pass; dkim=pass\nContent-Type: text/html\n\n<p>Send me your password.</p><script>ignored()</script><a href="https://bank.example@evil.example">bank</a>'
    report=analyze_email(raw)
    auth=next(e for e in report.evidence if e.id=='email:auth')
    assert auth.evidence_class=='unknown' and auth.weight==0
    assert any(e.id=='request:code' for e in report.evidence)
    assert any(e.detail=='evil.example' for e in report.evidence)


def test_attached_email_body_is_not_silently_scanned():
    from email.message import EmailMessage
    outer=EmailMessage(); outer.set_content('Here are the meeting notes.')
    attached=EmailMessage(); attached.set_content('Send me your password.')
    outer.add_attachment(attached,filename='example.eml')
    report=analyze_email(outer.as_string())
    assert not any(e.id=='request:code' for e in report.evidence)


@pytest.mark.parametrize('kind,key,text',[
    ('text','text','Send me the code.'),('url','url','https://example.org'),
    ('email','raw_email','Subject: Hello\n\nMeet at the library.'),('call','transcript','Install AnyDesk.')])
def test_public_endpoints(kind,key,text):
    response=request('POST','/api/analyze/'+kind,json={key:text})
    assert response.status_code==200
    data=response.json()
    assert data['kind']==kind and data['actions'] and data['share_summary']
    assert response.headers['cache-control']=='no-store'
    if kind=='call': assert 'End the call' in data['actions'][0]['title']


def test_whitespace_and_oversize_rejected():
    for value in ['   ','x'*30001]:
        assert request('POST','/api/analyze/text',json={'text':value}).status_code==422


def test_missing_model_retains_credential_result(monkeypatch):
    monkeypatch.setattr(provenance,'read_credentials',lambda _:ContentCredentials(status='absent',detail='No embedded credentials found.'))
    def unavailable(_): raise ImageModelUnavailable('missing')
    monkeypatch.setattr(provenance,'analyze_image',unavailable)
    image=io.BytesIO();Image.new('RGB',(20,20)).save(image,format='PNG')
    response=request('POST','/api/analyze/image',files={'file':('image.png',image.getvalue(),'image/png')})
    assert response.status_code==200
    report=response.json()
    assert report['model_ran'] is False and report['risk_index'] is None
    assert report['content_credentials']['status']=='absent'
    assert 'unavailable' in report['summary']


def test_invalid_image_rejected():
    assert request('POST','/api/analyze/image',files={'file':('x.png',b'not an image','image/png')}).status_code==400


def test_page_no_external_scripts_or_untrusted_markup():
    response=request('GET','/')
    assert response.status_code==200
    assert 'frame-ancestors' in response.headers['content-security-policy']
    assert '<script src="https://' not in response.text
    assert 'innerHTML' not in response.text


def test_other_sites_cannot_submit_to_local_api():
    assert request('POST','/api/analyze/text',json={'text':'Hi'},headers={'Origin':'https://outside.example'}).status_code==403
    assert request('GET','/',headers={'Host':'outside.example'}).status_code==400
    assert request('POST','/api/analyze/text',json={'text':'Hi'},headers={'Origin':'http://127.0.0.1'}).status_code==200
