"""Do not reinterpret malformed explicit schemes as bare hostnames."""
import asyncio
import httpx
import pytest
from app.analyzers.url import parse_address,analyze_url
from app.analyzers.url_details import inspect_url
from app.analyzers.text import analyze_text
from app.analyzers.email import analyze_email
from app.main import app

@pytest.mark.parametrize('value',['ftp:/example.com','FTP:example.com','mailto:user@example.com','custom+v1:payload','custom.foo-bar:/PRIVATE','javascript:alert(1)','ftp://example.com'])
def test_explicit_unsupported_schemes_not_inferred_as_host(value):
    for call in [lambda:parse_address(value),lambda:inspect_url(value),lambda:analyze_url('https://example.com',known_website=value)]:
        with pytest.raises(ValueError):call()

@pytest.mark.parametrize('value,host',[('ftp:80','ftp'),('intranet:8080/path','intranet'),('intranet:8080?x=1','intranet'),('intranet:8080#fragment','intranet'),('example.com:443','example.com'),('bücher.example:443','xn--bcher-kva.example'),('[::1]:8080','::1'),('127.0.0.1:0','127.0.0.1')])
def test_bare_decimal_ports_preserved(value,host):
    assert parse_address(value)[1]==host

def test_nonhttp_text_is_not_web_link_and_mailto_label_parsing_preserved():
    report=analyze_text('ftp:/example.com')
    assert not any(e.id.startswith('url:host') for e in report.evidence)
    report=analyze_email('Content-Type:text/html\n\n<a href="mailto:a@evil.example">a@bank.example</a>')
    assert any(e.id.startswith('email:link_mismatch') for e in report.evidence)

@pytest.mark.parametrize('path',['/api/analyze/url','/api/inspect/url'])
def test_api_fixed_400_does_not_echo_payload(path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as c:
            return await c.post(path,json={'url':'ftp:/PRIVATE'})
    r=asyncio.run(run());assert r.status_code==400 and 'PRIVATE' not in r.text
