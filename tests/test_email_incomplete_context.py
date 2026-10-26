"""Incomplete source interpretation must stay visible without losing readable wording."""
import pytest
from app.analyzers.email import analyze_email, analyze_email_bytes
from app.guidance import add_guidance

@pytest.mark.parametrize('raw',[
 'From: office@example.org\nSubject: Constructed meeting\n\n',
 'Content-Type: text/plain; charset=utf-8\nSubject: Constructed meeting\n\n   ',
 'Content-Type: text/html\n\n<style>body{color:red}</style><script>ignored()</script>',
])
@pytest.mark.parametrize('as_bytes',[False,True])
def test_missing_visible_body_is_incomplete_even_when_subject_or_headers_exist(raw,as_bytes):
    report=analyze_email_bytes(raw.encode()) if as_bytes else analyze_email(raw)
    assert any(e.id=='email:incomplete' and 'No readable message body' in e.detail for e in report.evidence)
    assert report.risk_level=='guarded'

@pytest.mark.parametrize('outer_body',['Meeting notes.','Send your password.'])
def test_nested_malformed_container_defect_is_checked_but_readable_part_remains(outer_body):
    raw='Content-Type: multipart/mixed; boundary=a\n\n--a\nContent-Type: text/plain\n\n'+outer_body+'\n--a\nContent-Type: multipart/alternative; boundary=absent\n\nPreamble only.\n--a--\n'
    report=analyze_email(raw)
    assert any(e.id=='email:incomplete' for e in report.evidence)
    assert report.risk_level==('high' if 'password' in outer_body else 'guarded')
    if 'password' in outer_body: assert any(e.id=='request:code' for e in report.evidence)

@pytest.mark.parametrize('subject',['=?utf-8?b?/w==?=','=?unknown-charset?b?SGVsbG8=?='])
@pytest.mark.parametrize('body',['Meeting notes.','Send your password.'])
def test_invalid_encoded_subject_is_incomplete_without_hiding_body_requests(subject,body):
    report=add_guidance(analyze_email('Subject: '+subject+'\nContent-Type: text/plain\n\n'+body))
    assert any(e.id=='email:incomplete' and 'subject' in e.detail.lower() for e in report.evidence)
    assert report.risk_level==('high' if 'password' in body else 'guarded')
    assert 'This email check was incomplete.' in report.share_summary
    if 'password' in body: assert any(e.id=='request:code' for e in report.evidence)

@pytest.mark.parametrize('raw',['Meeting notes.','Subject: =?utf-8?b?SGVsbG8=?=\n\nMeeting notes.'])
def test_body_only_and_valid_encoded_subject_are_still_complete(raw):
    assert not any(e.id=='email:incomplete' for e in analyze_email(raw).evidence)

def test_defective_attached_multipart_and_subject_are_still_not_read():
    raw='Content-Type: multipart/mixed; boundary=a\n\n--a\nContent-Type: text/plain\n\nMeeting notes.\n--a\nContent-Disposition: attachment\nContent-Type: multipart/alternative; boundary=absent\nSubject: =?utf-8?b?/w==?=\n\nSend your password.\n--a--\n'
    report=analyze_email(raw)
    assert not any(e.id in {'email:incomplete','request:code'} for e in report.evidence)
    assert any(e.id=='email:unscanned' for e in report.evidence)
