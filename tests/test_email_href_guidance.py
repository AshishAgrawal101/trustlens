"""Consume exact HTML-link coverage evidence without parsing or exporting its detail."""
import pytest
from app.models import Evidence
from app.analyzers.text import communication_report, analyze_text
from app.analyzers.email import analyze_email
from app.guidance import add_guidance

ACTION='Review unsupported email links in the original message'
HTML_REASON='HTML link review was incomplete; some supplied HTML link targets were not inspected.'


def evidence(eid,detail='PRIVATE detail must not be parsed as a count'):
    return Evidence(id=eid,evidence_class='unknown',severity='info',weight=0,title='PRIVATE',detail=detail,source='test')


def test_exact_html_coverage_id_is_unknown_not_a_fraud_score():
    items=[evidence('email:links_incomplete')]
    report=communication_report('email',items)
    assert report.summary.startswith('HTML link review is incomplete.')
    assert any('HTML link targets could not be inspected locally' in x for x in report.limitations)
    assert report.risk_level=='low' and report.risk_index is None and report.confidence=='low'
    before=report.model_dump(exclude={'actions','share_summary'})
    result=add_guidance(report)
    assert result.model_dump(exclude={'actions','share_summary'})==before
    assert ACTION in [a.title for a in result.actions]
    assert HTML_REASON in result.share_summary
    action=next(a for a in result.actions if a.title==ACTION)
    assert 'trusted mail app' in action.detail and 'already trust' in action.detail
    assert 'PRIVATE' not in result.share_summary


@pytest.mark.parametrize('eid',['email:links_incomplete:0','email:links_incomplete_extra','notemail:links_incomplete'])
def test_similar_ids_do_not_trigger_html_notice(eid):
    result=add_guidance(communication_report('email',[evidence(eid)]))
    assert 'HTML link review is incomplete' not in result.summary
    assert ACTION not in [a.title for a in result.actions]
    assert HTML_REASON not in result.share_summary


@pytest.mark.parametrize('detail',['0','99999999','PRIVATE https://private.example/SECRET','not a number'])
def test_detail_is_not_interpreted_or_echoed_in_export(detail):
    result=add_guidance(communication_report('email',[evidence('email:links_incomplete',detail)]))
    assert HTML_REASON in result.share_summary
    assert ACTION in [a.title for a in result.actions]
    control=add_guidance(communication_report('email',[evidence('email:links_incomplete','CONTROL')]))
    assert result.share_summary==control.share_summary


def test_all_coverage_reasons_remain_distinct_without_displacing_live_advice():
    report=analyze_text('Send me your verification code.')
    report=communication_report('email',report.evidence+[
        evidence('email:links_incomplete'),evidence('analysis:links_incomplete'),evidence('url:malformed:0'),evidence('email:incomplete')])
    assert 'HTML link review is incomplete' in report.summary
    assert '1 link address(es) could not be parsed' in report.summary
    assert any('first 8 unique literal HTTP(S)' in x for x in report.limitations)
    assert any('HTML link targets could not be inspected locally' in x for x in report.limitations)
    result=add_guidance(report);titles=[a.title for a in result.actions]
    assert result.risk_level=='high'
    for title in ['Keep security codes and passwords private','Review the original email',ACTION,'Review unreadable link addresses independently','Review the remaining links independently']:
        assert titles.count(title)==1 and title in result.share_summary
    for reason in [HTML_REASON,'1 link address(es) could not be parsed','Only the first 8 unique literal links','This email check was incomplete.']:
        assert reason in result.share_summary
    assert 'PRIVATE' not in result.share_summary


def test_normal_email_report_remains_unchanged():
    result=add_guidance(analyze_email('Subject: Notes\n\nMeeting tomorrow.'))
    assert result.summary=='No strong warning signs matched. That does not verify who sent this or make it safe.'
    assert ACTION not in [a.title for a in result.actions]
    assert HTML_REASON not in result.share_summary


def test_actual_unsupported_html_href_propagates_integration_notice():
    result=add_guidance(analyze_email('Content-Type: text/html\n\n<a href="/PRIVATE-path">Review statement</a>'))
    assert any(e.id=='email:links_incomplete' for e in result.evidence)
    assert 'HTML link review is incomplete' in result.summary
    assert ACTION in [a.title for a in result.actions]
    assert HTML_REASON in result.share_summary
    assert 'PRIVATE' not in result.share_summary


def test_actual_email_combines_html_malformed_budget_and_mime_coverage():
    links=['https://private.example:bad/SECRET']+[f'https://site{i}.example/path' for i in range(8)]
    raw=('From: PRIVATE-A@example.org\nFrom: PRIVATE-B@example.org\nContent-Type: text/html\n\n'
         '<p>Send me your verification code.</p><p>'+' '.join(links)+'</p>'
         '<a href="/PRIVATE-relative">Open statement</a>')
    result=add_guidance(analyze_email(raw));ids={e.id for e in result.evidence}
    assert {'email:links_incomplete','email:incomplete','analysis:links_incomplete','url:malformed:0','request:code'}<=ids
    assert result.risk_level=='high'
    assert result.summary.startswith('This email could not be fully interpreted.')
    for reason in [HTML_REASON,'1 link address(es) could not be parsed','Only the first 8 unique literal links','This email check was incomplete.']:
        assert reason in result.share_summary
    assert ACTION in [a.title for a in result.actions]
    assert 'PRIVATE' not in result.share_summary and 'SECRET' not in result.share_summary
