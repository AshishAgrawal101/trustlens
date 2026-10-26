from email.message import EmailMessage
import pytest

from app.analyzers.email import analyze_email_bytes
from app.guidance import add_guidance


@pytest.mark.parametrize('body', ['', 'The library meeting is tomorrow.'])
def test_input_free_email_export_keeps_unscanned_content_limit(body):
    message = EmailMessage()
    message['Subject'] = 'PRIVATE-SUBJECT'
    if body:
        message.set_content(body)
    message.add_attachment(b'PRIVATE-ATTACHMENT', maintype='application', subtype='pdf', filename='PRIVATE-NAME.pdf')
    report = add_guidance(analyze_email_bytes(message.as_bytes()))
    assert 'Attachment or unsupported MIME content was not scanned.' in report.share_summary
    assert 'PRIVATE' not in report.share_summary
    assert any(e.id == 'email:incomplete' for e in report.evidence) == (not body)
