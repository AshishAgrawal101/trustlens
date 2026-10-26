"""Constructed parser regressions, not a real-world phishing accuracy estimate."""
import pytest
from app.analyzers.email import analyze_email
from app.analyzers.url import analyze_url
from app.analyzers.text import analyze_text
from app.guidance import add_guidance
from test_community import request


def email(body):
    return 'From: Sender <sender@example.org>\nContent-Type: text/html; charset=utf-8\n\n'+body


def mismatches(report):
    return [e for e in report.evidence if e.id.startswith('email:link_mismatch:')]


@pytest.mark.parametrize('label,href', [
    ('https://bank.example', 'https://review.example/login'),
    ('bank.example', 'https://review.example'),
    ('https://bank.<strong>example</strong>', 'https://review.example'),
    ('https://bank.example/account', 'HTTPS://review.example/path?a=1&amp;b=2'),
    ('https://bank.example', 'https://bank.example@review.example'),
])
def test_link_destination_compared_with_displayed_host(label,href):
    report=analyze_email(email(f'<a href="{href}">{label}</a>'))
    found=mismatches(report)
    assert len(found)==1
    assert 'bank.example' in found[0].detail and 'review.example' in found[0].detail
    assert found[0].evidence_class=='verified' and 'Legitimate tracking' in found[0].detail
    assert 'neither destination was visited' in found[0].source


@pytest.mark.parametrize('label,href', [
    ('https://bank.example', 'https://BANK.EXAMPLE./account'),
    ('https://bank.example/a', 'https://bank.example/b'),
    ('Open your account', 'https://bank.example'),
    ('https://bücher.example', 'https://xn--bcher-kva.example'),
    ('https://[::1]', 'https://[0:0:0:0:0:0:0:1]/a'),
    ('not..valid', 'https://bank.example'),
    ('https://bank.example', 'https://-invalid.example'),
])
def test_no_invented_mismatch(label,href):
    assert not mismatches(analyze_email(email(f'<a href="{href}">{label}</a>')))


def test_plain_text_does_not_invent_missing_destination():
    report=analyze_email('Subject: A link\n\nhttps://bank.example')
    assert not mismatches(report)
    assert any('Pasted plain text' in s for s in report.limitations)


def test_hidden_script_and_style_content_not_used():
    report=analyze_email(email('<script><a href="https://evil.example">https://bank.example</a></script><style>.x{}</style><p>Hello</p>'))
    assert not mismatches(report)
    assert not any('evil.example' in e.detail for e in report.evidence)


def test_unclosed_anchor_and_duplicates_are_bounded():
    body='<a href="https://other.example">https://bank.example</a>'*20
    assert len(mismatches(analyze_email(email(body))))==1
    body=''.join(f'<a href="https://other{i}.example">https://bank.example</a>' for i in range(20))
    assert len(mismatches(analyze_email(email(body))))==8
    assert len(mismatches(analyze_email(email('<a href="https://other.example">https://bank.example'))))==1


def test_link_guidance_and_summary_do_not_export_private_hosts_or_tokens():
    raw=email('<a href="https://private-review.example/login?token=SECRET">https://private-bank.example</a>')
    response=request('POST','/api/analyze/email',json={'raw_email':raw})
    assert response.status_code==200
    data=response.json()
    assert data['risk_level']=='guarded' and data['risk_index'] is None
    assert data['actions'][0]['title']=='Use a known address instead of this link'
    for private in ('private-review','private-bank','SECRET','sender@example'):
        assert private not in data['share_summary']
    assert 'does not prove fraud' in data['share_summary']


def test_embedded_userinfo_receives_link_action_and_ipv6_stays_parseable():
    report=add_guidance(analyze_text('Visit https://bank.example@other.example.'))
    assert report.actions[0].title=='Use a known address instead of this link'
    report=analyze_text('Server: https://[::1]')
    assert any(e.detail=='::1' for e in report.evidence)


@pytest.mark.parametrize('value', [
    'https://a..example', 'https://-bank.example', 'https://bank-.example',
    'https://bank.example..', 'https://127.1', 'https://999.1.1.1',
    'https://'+'a'*64+'.example', 'https://bank_example', 'https://a:443:123',
])
def test_malformed_host_is_rejected_at_api_boundary(value):
    assert request('POST','/api/analyze/url',json={'url':value}).status_code==400


@pytest.mark.parametrize('value,host', [
    ('example.org','example.org'), ('HTTPS://BANK.EXAMPLE.','bank.example'),
    ('https://bücher.example','xn--bcher-kva.example'),
    ('http://192.0.2.1:8080','192.0.2.1'), ('https://[2001:db8::1]','2001:db8::1'),
    ('https://a-b.example','a-b.example'),
])
def test_valid_hosts_remain_accepted(value,host):
    assert analyze_url(value).evidence[0].detail==host
