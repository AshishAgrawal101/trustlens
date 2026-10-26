"""Reject ambiguous browser numeric syntax instead of asserting a false host."""
import asyncio
import httpx
import pytest
from app.analyzers.url import parse_address,analyze_url
from app.analyzers.url_details import inspect_url
from app.analyzers.text import analyze_text
from app.analyzers.email import analyze_email
from app.main import app

BAD=['https:/example.org/path','http:example.org','https:example.org','http:/example.org','https://0x7f000001/','https://0x7f.0.0.1/','https://example.0x1/','https://example.09/','https://example.123/','https://0x/','https://１２７．０．０．０ｘ１/','https://[fe80::1%25eth0]/']

@pytest.mark.parametrize('value',BAD)
def test_ambiguous_explicit_or_numeric_hosts_rejected(value):
    with pytest.raises(ValueError):parse_address(value)
    with pytest.raises(ValueError):inspect_url(value)
    with pytest.raises(ValueError):analyze_url('https://ordinary.example',known_website=value)


@pytest.mark.parametrize('value,host',[('example.org:8080','example.org'),('localhost:80','localhost'),('https://127.0.0.1/','127.0.0.1'),('https://[::1]:0/','::1'),('https://[2001:db8::1]/','2001:db8::1'),('https://name.0xgg/','name.0xgg'),('https://123.example/','123.example'),('https://straße.example/','xn--strae-oqa.example')])
def test_unambiguous_existing_hosts_preserved(value,host):
    assert parse_address(value)[1]==host


def test_reviewed_qr_text_and_email_do_not_make_false_host_claim():
    url='https://0x7f000001/'
    report=analyze_text(url)
    assert any(e.id=='url:malformed:0' for e in report.evidence)
    assert not any(e.id=='url:host:0' for e in report.evidence)
    report=analyze_email('Content-Type:text/html\n\n<a href="'+url+'">https://bank.example</a>')
    assert not any(e.id.startswith('email:link_mismatch') for e in report.evidence)


@pytest.mark.parametrize('path',['/api/analyze/url','/api/inspect/url'])
def test_actual_url_routes_fixed_private_400(path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
            return await client.post(path,json={'url':'https://0x7f000001/PRIVATE'})
    response=asyncio.run(run())
    assert response.status_code==400 and 'PRIVATE' not in response.text
