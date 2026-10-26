"""Frozen HTML href contracts; no destinations are opened."""
import asyncio
from email.message import EmailMessage
import httpx
import pytest
from app.analyzers.email import analyze_email,analyze_email_bytes,VisibleText
from app.main import app

def report(body,as_bytes=False):
    message=EmailMessage();message.set_content(body,subtype='html',charset='utf-8')
    return analyze_email_bytes(message.as_bytes()) if as_bytes else analyze_email(message.as_string())
def partial(r):return [e for e in r.evidence if e.id=='email:links_incomplete']
def mismatches(r):return [e for e in r.evidence if e.id.startswith('email:link_mismatch')]

@pytest.mark.parametrize('as_bytes',[False,True])
@pytest.mark.parametrize('label,href,expected',[('https://bank.example','//evil.example/path?PRIVATE=1',True),('bank.example','//BANK.EXAMPLE./path',False),('straße.example','//xn--strae-oqa.example/',False),('bank.example','//bank.example@evil.example/',True)])
def test_protocol_relative_literal_host_only(label,href,expected,as_bytes):
    r=report(f'<a href="{href}">{label}</a>',as_bytes)
    assert bool(mismatches(r)) is expected and not partial(r)
    # A literal https label is still ordinary visible body text, independently
    # checked. Only the synthetic destination must stay out of body URL rules.
    assert not any(e.id.startswith('url:host') and e.detail=='evil.example' for e in r.evidence)
    assert not any(e.id.startswith('url:http') for e in r.evidence)
    parser=VisibleText();parser.feed(f'<a href="{href}">{label}</a>');parser.finish_anchor()
    assert parser.links==[]
    assert 'PRIVATE' not in ' '.join(e.detail for e in r.evidence)
    if expected:assert 'evil.example' in mismatches(r)[0].detail

@pytest.mark.parametrize('href',['///evil.example','//:443','//0x7f000001','\t//bank.example','//bank.\u200bexample','//bank.example/\u202e','/login','../notice','?ticket=PRIVATE','javascript:PRIVATE','data:PRIVATE','ftp:/PRIVATE','https:/PRIVATE'])
def test_unsupported_targets_count_unknown_without_private_target(href):
    r=report(f'<a href="{href}">Open</a>');rows=partial(r)
    assert len(rows)==1 and rows[0].weight==0 and rows[0].severity=='info' and rows[0].evidence_class=='unknown'
    assert '1' in rows[0].detail and 'PRIVATE' not in rows[0].detail
    assert not mismatches(r)

def test_aggregate_counts_not_distinct_target_or_raw_values():
    r=report('<a href="/PRIVATE">Open</a><a href="/PRIVATE">Again</a><a href="?PRIVATE">Third</a>')
    assert len(partial(r))==1 and '3' in partial(r)[0].detail and 'PRIVATE' not in partial(r)[0].detail

@pytest.mark.parametrize('anchor',['<a>Label</a>','<a href="">Label</a>','<a href="   ">Label</a>','<a href="#section">Label</a>'])
def test_nondestination_anchor_policy(anchor):assert not partial(report(anchor))

def test_hidden_fragment_not_silently_stripped():assert partial(report('<a href="\t#section">Label</a>'))
def test_script_and_style_anchors_not_counted():assert not partial(report('<script><a href="/PRIVATE">X</a></script><style><a href="data:PRIVATE">X</a></style><p>Hello</p>'))

def test_inline_block_and_http_control():
    assert mismatches(report('<a href="//evil.example">bank.<b>example</b></a>'))
    assert not mismatches(report('<a href="//evil.example">bank.<br>example</a>'))
    assert mismatches(report('<a href="https://bank.example@evil.example">bank.example</a>'))

def test_mailto_primary_scope_and_malformed_target():
    assert mismatches(report('<a href="mailto:a@evil.example?cc=PRIVATE">a@bank.example</a>'))
    assert partial(report('<a href="mailto:a@[">a@bank.example</a>'))
    assert not partial(report('<a href="mailto:a@evil.example">Send email</a>'))

def test_parts_aggregate_and_existing_http_cap_remain_separate():
    m=EmailMessage();m.make_mixed()
    for body in ['<a href="/one">A</a>','<a href="ftp:/two">B</a>'+''.join(f'<a href="https://a{i}.example">Open</a>' for i in range(9))]:
        p=EmailMessage();p.set_content(body,subtype='html');m.attach(p)
    r=analyze_email_bytes(m.as_bytes())
    assert len(partial(r))==1 and '2' in partial(r)[0].detail
    assert any(e.id=='analysis:links_incomplete' for e in r.evidence)

def test_warning_retained_and_mismatch_detail_cap():
    r=report('<p>Read me your verification code.</p><a href="/PRIVATE">Open</a>'+''.join(f'<a href="//a{i}.example">bank.example</a>' for i in range(10)))
    assert any(e.id=='request:code' for e in r.evidence) and partial(r)
    assert len(mismatches(r))==8

def test_malformed_absolute_web_target_retains_existing_unknown_link_evidence():
    r=report('<a href="https://-invalid.example">Open</a>')
    assert partial(r) and any(e.id.startswith('url:malformed') for e in r.evidence)

@pytest.mark.parametrize('path',['/api/analyze/email','/api/analyze/email-file'])
def test_actual_api_evidence_shape(path):
    text='Content-Type:text/html\n\n<a href="/PRIVATE">Open</a>'
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as c:
            return await c.post(path,json={'raw_email':text}) if path.endswith('/email') else await c.post(path,files={'file':('constructed.eml',text.encode(),'message/rfc822')})
    response=asyncio.run(run());assert response.status_code==200
    row=next(e for e in response.json()['evidence'] if e['id']=='email:links_incomplete')
    assert row['weight']==0 and row['evidence_class']=='unknown' and 'PRIVATE' not in row['detail']
