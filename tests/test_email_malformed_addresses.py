"""Tiny stdlib parser failure and literal HTML label regressions."""
import asyncio
import httpx
import pytest
from app.analyzers.email import analyze_email, analyze_email_bytes
from app.main import app


@pytest.mark.parametrize('header',['From: "','Reply-To: "','From: a@[','Reply-To: a@['])
@pytest.mark.parametrize('parser',[analyze_email,analyze_email_bytes])
def test_known_lazy_header_failures_controlled(header,parser):
    text=header+'\r\n\r\nPRIVATE ordinary message.'
    with pytest.raises(ValueError) as error:parser(text if parser is analyze_email else text.encode())
    assert 'PRIVATE' not in str(error.value) and 'could not be read' in str(error.value)


@pytest.mark.parametrize('path',['/api/analyze/email','/api/analyze/email-file'])
@pytest.mark.parametrize('header',['From: "','Reply-To: a@['])
def test_actual_route_returns_private_fixed_400(path,header):
    text=header+'\r\n\r\nPRIVATE body'
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://127.0.0.1') as c:
            if path.endswith('/email'):return await c.post(path,json={'raw_email':text})
            return await c.post(path,files={'file':('PRIVATE.eml',text.encode(),'message/rfc822')})
    r=asyncio.run(run());assert r.status_code==400 and 'PRIVATE' not in r.text


@pytest.mark.parametrize('label,href',[('a@[','mailto:a@example.org'),('a@example.org','mailto:a@[')])
def test_malformed_mailto_skipped_without_discarding_readable_warning(label,href):
    raw='Content-Type: text/html\r\n\r\n<p>Read me your verification code.</p><a href="'+href+'">'+label+'</a>'
    for parser,value in [(analyze_email,raw),(analyze_email_bytes,raw.encode())]:
        report=parser(value)
        assert any(e.id=='request:code' for e in report.evidence)
        assert not any(e.id.startswith('email:link_mismatch') for e in report.evidence)


@pytest.mark.parametrize('label',['https://bank.<br>example','https://bank.<div>example</div>','https://bank.<p>example</p>'])
def test_block_split_label_does_not_fabricate_literal_host(label):
    report=analyze_email('Content-Type:text/html\n\n<a href="https://evil.example">'+label+'</a>')
    assert not any(e.id.startswith('email:link_mismatch') for e in report.evidence)


def test_inline_label_still_compares_and_normal_sender_still_available():
    report=analyze_email('From: Person <a@example.org>\nContent-Type:text/html\n\n<a href="https://evil.example">https://bank.<strong>example</strong></a>')
    assert any(e.id.startswith('email:link_mismatch') for e in report.evidence)
    assert any(e.id=='email:sender' and e.detail=='a@example.org' for e in report.evidence)
