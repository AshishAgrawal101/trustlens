"""Duplicate MIME interpretation headers limit a check; they are not extra evidence of safety."""
import pytest
from app.analyzers.email import analyze_email, analyze_email_bytes
from app.guidance import add_guidance

@pytest.mark.parametrize('name,values', [('Content-Type', ['text/plain; charset=utf-8', 'text/html; charset=utf-8']), ('Content-Transfer-Encoding', ['7bit','8bit'])])
@pytest.mark.parametrize('reverse',[False,True])
@pytest.mark.parametrize('nested',[False,True])
def test_duplicate_mime_headers_mark_incomplete_and_preserve_readable_requests(name,values,reverse,nested):
    ordered=list(reversed(values)) if reverse else values
    headers='\n'.join(name+': '+value for value in ordered)
    if name!='Content-Type': headers='Content-Type: text/plain; charset=utf-8\n'+headers
    body=headers+'\n\nSend your password.'
    raw='MIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=parts\n\n--parts\n'+body+'\n--parts--\n' if nested else body
    report=add_guidance(analyze_email(raw))
    assert any(e.id=='email:incomplete' and name in e.detail for e in report.evidence)
    assert any(e.id=='request:code' for e in report.evidence)
    assert report.risk_level=='high' and 'could not be fully interpreted' in report.summary
    assert 'This email check was incomplete.' in report.share_summary

@pytest.mark.parametrize('reverse',[False,True])
def test_conflicting_transfer_encodings_do_not_silently_look_complete(reverse):
    values=['7bit','base64'];values.reverse() if reverse else None
    raw='Content-Type: text/plain; charset=utf-8\n'+''.join('Content-Transfer-Encoding: '+v+'\n' for v in values)+'\nU2VuZCB5b3VyIHBhc3N3b3JkLg=='
    for report in [analyze_email(raw),analyze_email_bytes(raw.encode())]:
        assert any(e.id=='email:incomplete' and 'Content-Transfer-Encoding' in e.detail for e in report.evidence)
        assert report.risk_level!='low'

def test_duplicate_mime_headers_in_skipped_attachment_do_not_contaminate_readable_body():
    raw='Content-Type: multipart/mixed; boundary=p\n\n--p\nContent-Type: text/plain\n\nMeeting notes.\n--p\nContent-Disposition: attachment\nContent-Type: text/plain\nContent-Type: text/html\n\nSend your password.\n--p--\n'
    report=analyze_email(raw)
    assert any(e.id=='email:unscanned' for e in report.evidence)
    assert not any(e.id in {'email:incomplete','request:code'} for e in report.evidence)
