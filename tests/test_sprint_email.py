"""Malformed supplied mail must not be mistaken for a complete clean check."""
import pytest
from app.analyzers.email import analyze_email
from app.guidance import add_guidance
from test_community import request


@pytest.mark.parametrize('headers', [
    'From: first@bank.example\nFrom: second@elsewhere.example',
    'From: first@bank.example\nReply-To: one@bank.example\nReply-To: two@elsewhere.example',
])
def test_ambiguous_address_headers_are_reported_without_selecting_a_winner(headers):
    report=analyze_email(headers+'\n\nHello there.')
    assert any(e.id=='email:incomplete' and 'Multiple' in e.detail for e in report.evidence)
    assert not any(e.id=='email:reply' for e in report.evidence)
    if headers.count('From:')>1: assert not any(e.id=='email:sender' for e in report.evidence)
    assert 'could not be fully interpreted' in report.summary
    assert report.risk_level=='guarded'


@pytest.mark.parametrize('raw', [
    'Content-Type: text/plain\nContent-Transfer-Encoding: base64\n\n@@@aGVsbG8=!!!',
    'Content-Type: text/plain; charset=unknown-character-set\n\nHello',
    'Content-Type: multipart/mixed; boundary=missing\n\nHello without a boundary',
])
def test_mime_and_decode_failures_are_explicit_partial_results(raw):
    response=request('POST','/api/analyze/email',json={'raw_email':raw})
    assert response.status_code==200
    data=response.json()
    assert any(e['id']=='email:incomplete' for e in data['evidence'])
    assert 'could not be fully interpreted' in data['summary']
    assert data['risk_index'] is None


@pytest.mark.parametrize('raw', [
    'Hello, the library meeting is at six.',
    'Subject: Meeting\n\nBring the notes.',
    'From: office@example.org\nContent-Type: text/plain\nContent-Transfer-Encoding: base64\n\nSGVsbG8=',
])
def test_normal_body_only_or_encoded_mail_is_not_marked_incomplete(raw):
    assert not any(e.id=='email:incomplete' for e in analyze_email(raw).evidence)


def test_readable_request_is_not_lost_when_headers_are_ambiguous():
    report=add_guidance(analyze_email('From: private-a@example.org\nFrom: private-b@example.org\n\nSend me your password.'))
    assert report.risk_level=='high'
    assert any(e.id=='request:code' for e in report.evidence)
    assert any('passwords private' in a.title for a in report.actions)
    assert 'private-a' not in report.share_summary and 'private-b' not in report.share_summary
    assert 'This email check was incomplete.' in report.share_summary


def test_incomplete_email_gets_manual_review_action():
    report=add_guidance(analyze_email('Content-Type: text/plain; charset=unknown-encoding\n\nHello'))
    assert report.actions[0].title=='Review the original email'


def test_unscanned_attached_email_does_not_contaminate_body_findings():
    from email.message import EmailMessage
    outer=EmailMessage();outer.set_content('Meeting notes attached.')
    attached=EmailMessage();attached['Content-Type']='text/plain; charset=bad-encoding';attached.set_payload('Send me your password.')
    outer.add_attachment(attached,filename='forwarded.eml')
    report=analyze_email(outer.as_string())
    assert not any(e.id in ('email:incomplete','request:code') for e in report.evidence)
