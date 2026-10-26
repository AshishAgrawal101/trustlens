"""Literal mailto domain mismatch and privacy regressions; no address contacted."""
import pytest
from test_link_evidence import email, mismatches
from app.analyzers.email import analyze_email
from app.guidance import add_guidance


@pytest.mark.parametrize('label,target', [
    ('billing@bank.example','mailto:collections@other.example'),
    ('billing@bank.example','MAILTO:collections%40other.example?subject=Hello'),
    ('billing@<b>bank.example</b>','mailto:collections@other.example'),
])
def test_primary_recipient_domain_mismatch(label,target):
    report=add_guidance(analyze_email(email(f'<a href="{target}">{label}</a>')))
    found=mismatches(report)
    assert len(found)==1 and found[0].evidence_class=='verified'
    assert 'bank.example' in found[0].detail and 'other.example' in found[0].detail
    assert 'legitimate' in found[0].detail
    assert report.risk_level=='guarded' and report.risk_index is None
    assert report.actions[0].title=='Use a known address instead of this link'
    assert all(private not in report.share_summary for private in ('billing','collections','bank.example','other.example'))


@pytest.mark.parametrize('label,target', [
    ('billing@bank.example','mailto:billing@BANK.EXAMPLE'),
    ('billing@bücher.example','mailto:billing@xn--bcher-kva.example'),
    ('billing@bank.example','mailto:alternate@bank.example'),
    ('Contact support','mailto:support@bank.example'),
    ('bad@@bank.example','mailto:support@other.example'),
    ('billing@bank.example','mailto:one@other.example,two@third.example'),
    ('billing@bank.example','mailto:bad%0Aaddress@other.example'),
    ('billing@bank.example','mailto:bad%FF@other.example'),
])
def test_no_invented_recipient_domain_mismatch(label,target):
    assert not mismatches(analyze_email(email(f'<a href="{target}">{label}</a>')))


def test_mailto_query_is_not_treated_as_visible_message_text():
    report=analyze_email(email('<a href="mailto:billing@bank.example?body=share%20your%20password">billing@bank.example</a>'))
    assert not any(e.id=='request:code' for e in report.evidence)
    assert any('additional query recipients' in limitation for limitation in report.limitations)
