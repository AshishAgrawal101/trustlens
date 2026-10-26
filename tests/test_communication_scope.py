"""English wording scope must survive custom communication limitations."""
import asyncio
import hashlib
from pathlib import Path
from email.message import EmailMessage
import httpx
import pytest
from app.analyzers.text import communication_report,analyze_text
from app.analyzers.email import analyze_email,analyze_email_bytes
from app.analyzers.url import analyze_url
from app.guidance import add_guidance
from app.main import app

SCOPE='English-language rules identify wording and link structure, not intent or sender identity.'
FALLBACK='A legitimate message can trigger a rule; a scam can avoid every rule. No links were visited.'
CONTRACT=Path(__file__).resolve().parents[1]/'verification/communication-fresh-20261024/scope-acceptance.json'


def test_frozen_scope_contract():assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('kind',['text','call'])
@pytest.mark.parametrize('limits',[None,[]])
def test_default_two_lines_are_exact_and_unchanged(kind,limits):
    r=communication_report(kind,[],limits)
    assert r.limitations==[SCOPE,FALLBACK]


def test_custom_limitations_keep_order_without_mutation_and_no_other_report_change():
    custom=['First supplied MIME limitation.','Second supplied attachment limitation.'];before=list(custom)
    evidence=analyze_text('Send me your verification code.').evidence
    report=communication_report('email',evidence,custom)
    assert report.limitations==[SCOPE]+before and custom==before
    report.limitations.append('Local report change.')
    assert custom==before
    baseline=communication_report('email',evidence)
    assert report.model_dump(exclude={'limitations'})==baseline.model_dump(exclude={'limitations'})
    assert add_guidance(report).share_summary==add_guidance(baseline).share_summary


@pytest.mark.parametrize('mode',['text','call','email-paste','eml'])
def test_all_communication_modes_disclose_scope_without_input_in_export(mode):
    body='Please send me your verification code. PRIVATE-INCIDENT'
    if mode=='eml':
        m=EmailMessage();m.set_content(body);r=analyze_email_bytes(m.as_bytes())
    elif mode=='email-paste':r=analyze_email('Subject: PRIVATE-SUBJECT\n\n'+body)
    else:r=analyze_text(body,mode)
    assert r.limitations[0]==SCOPE and r.limitations.count(SCOPE)==1
    assert r.risk_level=='high' and r.risk_index is None and r.model_ran is False
    assert 'request:code' in {e.id for e in r.evidence}
    r=add_guidance(r);assert 'PRIVATE' not in r.share_summary


@pytest.mark.parametrize('path',['/api/analyze/text','/api/analyze/call','/api/analyze/email','/api/analyze/email-file'])
def test_actual_communication_api_has_explicit_english_scope(path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
            body='Send me your verification code. PRIVATE-API'
            if path.endswith('/email-file'):
                m=EmailMessage();m.set_content(body)
                return await client.post(path,files={'file':('constructed.eml',m.as_bytes(),'message/rfc822')})
            key='transcript' if path.endswith('/call') else 'raw_email' if path.endswith('/email') else 'text'
            return await client.post(path,json={key:body})
    response=asyncio.run(run());assert response.status_code==200
    result=response.json();assert result['limitations'][0]==SCOPE
    assert result['risk_level']=='high' and result['risk_index'] is None
    assert 'PRIVATE' not in result['share_summary']
    assert result['share_summary'].splitlines().count(EXPORT_SCOPE)==1


def test_url_only_analysis_does_not_acquire_english_wording_scope():
    result=analyze_url('https://example.org')
    assert result.limitations==['No page, redirect, domain registry or reputation service was contacted.','HTTPS protects the connection; it does not prove that a site or offer is legitimate.']
    assert not any('English' in s for s in result.limitations)

EXPORT_SCOPE='Wording rules cover English; other-language warning signs may be missed.'


@pytest.mark.parametrize('body',['Bitte sende mir dein Passwort. PRIVATE-DE','Meeting tomorrow. PRIVATE-NOTES','Send me your verification code. PRIVATE-CODE'])
@pytest.mark.parametrize('mode',['text','call','email-paste','eml'])
def test_export_scope_is_fixed_for_every_communication_input(body,mode):
    if mode=='eml':
        m=EmailMessage();m.set_content(body,charset='utf-8');report=analyze_email_bytes(m.as_bytes())
    elif mode=='email-paste':report=analyze_email(body)
    else:report=analyze_text(body,mode)
    before=report.model_dump(exclude={'actions','share_summary'})
    result=add_guidance(report)
    assert result.share_summary.splitlines().count(EXPORT_SCOPE)==1
    assert result.model_dump(exclude={'actions','share_summary'})==before
    assert body not in result.share_summary and 'PRIVATE' not in result.share_summary


def test_url_and_image_exports_do_not_claim_an_english_wording_check():
    from app.models import AnalysisReport
    url=add_guidance(analyze_url('https://example.org'))
    image=add_guidance(AnalysisReport(kind='image',risk_index=None,risk_level='low',confidence='low',summary='Origin remains unresolved.',evidence=[],limitations=['Image origin does not establish a claim.']))
    for report in [url,image]:assert EXPORT_SCOPE not in report.share_summary


def test_coverage_and_count_export_reasons_survive_scope_line():
    from app.models import Evidence
    items=analyze_text('Send me your verification code.').evidence
    for eid in ['email:links_incomplete','analysis:links_incomplete','url:malformed:0','email:incomplete']:
        items.append(Evidence(id=eid,evidence_class='unknown',severity='info',title='PRIVATE',detail='PRIVATE',source='test'))
    result=add_guidance(communication_report('email',items))
    assert result.share_summary.splitlines().count(EXPORT_SCOPE)==1
    for reason in ['1 wording or address warning sign(s) matched.','Only the first 8 unique literal links','1 link address(es) could not be parsed','HTML link review was incomplete','This email check was incomplete.']:
        assert reason in result.share_summary
    assert 'PRIVATE' not in result.share_summary
