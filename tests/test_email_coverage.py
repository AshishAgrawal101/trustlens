"""Unscanned parts are coverage limits, never fraud evidence or a clean result."""
from email.message import EmailMessage
from email.contentmanager import raw_data_manager

import pytest

from app.analyzers.email import analyze_email, analyze_email_bytes, unscanned_parts_count
from app.guidance import add_guidance
from test_community import request


PRIVATE_NAME='Private-person-finances-12345.pdf'
PRIVATE_BODY='PRIVATE ATTACHMENT: Send me your password and buy gift cards.'


def inventory(report):
    return next(e for e in report.evidence if e.id=='email:unscanned')


def assert_private_metadata_not_echoed(report):
    serialized=report.model_dump_json()
    assert PRIVATE_NAME not in serialized and PRIVATE_BODY not in serialized


def test_attachment_only_mail_is_explicitly_incomplete_with_no_fraud_weight():
    message=EmailMessage()
    message.add_attachment(PRIVATE_BODY.encode(),maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    report=add_guidance(analyze_email_bytes(message.as_bytes()))
    item=inventory(report)
    assert item.evidence_class=='unknown' and item.weight==0 and item.severity=='info'
    assert '1 attachment or unsupported' in item.detail
    assert report.risk_level=='guarded' and 'could not be fully interpreted' in report.summary
    assert any(e.id=='email:incomplete' for e in report.evidence)
    assert report.actions[0].title=='Review the original email'
    assert 'incomplete' in report.share_summary
    assert not any(e.id.startswith('request:') for e in report.evidence)
    assert_private_metadata_not_echoed(report)


def test_nontext_only_inline_image_is_unknown_coverage_not_clean_headline():
    message=EmailMessage()
    message.set_content(b'not-decoded-image-data',maintype='image',subtype='png',disposition='inline')
    report=analyze_email_bytes(message.as_bytes())
    assert inventory(report).weight==0
    assert report.risk_level=='guarded' and 'could not be fully interpreted' in report.summary


def test_readable_body_and_attachments_keep_warning_and_explicit_body_only_coverage():
    message=EmailMessage()
    message.set_content('Send me your password.')
    message.add_attachment(PRIVATE_BODY.encode(),maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    report=analyze_email_bytes(message.as_bytes())
    assert report.risk_level=='high' and any(e.id=='request:code' for e in report.evidence)
    assert 'Only readable subject and message-body' in inventory(report).detail
    assert report.summary.startswith('Only readable subject and message-body content was checked;')
    assert not any(e.id=='email:incomplete' for e in report.evidence)
    assert_private_metadata_not_echoed(report)


def test_subject_only_mail_with_attachment_is_still_incomplete():
    message=EmailMessage()
    message['Subject']='Meeting agenda'
    message.add_attachment(b'not-scanned',maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    report=analyze_email_bytes(message.as_bytes())
    assert 'Only readable subject' in inventory(report).detail
    assert any(e.id=='email:incomplete' for e in report.evidence)
    assert report.risk_level=='guarded' and 'could not be fully interpreted' in report.summary


def test_normal_multipart_alternative_has_no_false_unscanned_inventory():
    message=EmailMessage()
    message.set_content('The library meeting is tomorrow.')
    message.add_alternative('<p>The library meeting is tomorrow.</p>',subtype='html')
    report=analyze_email_bytes(message.as_bytes())
    assert not any(e.id in ('email:unscanned','email:incomplete') for e in report.evidence)


def test_inline_image_is_counted_without_decoding_and_attached_forward_subtree_skipped(monkeypatch):
    message=EmailMessage()
    message.set_content('The library meeting is tomorrow.')
    message.add_related(b'private-image',maintype='image',subtype='png',cid='<private>',filename=PRIVATE_NAME,disposition='inline')
    forward=EmailMessage()
    forward.set_content(PRIVATE_BODY)
    forward.add_attachment(b'private binary',maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    message.add_attachment(forward,filename='private-forward.eml')
    assert unscanned_parts_count(message)==2
    original=raw_data_manager.get_content
    def read_only_body(part,*args,**kwargs):
        assert part.get_content_type() in ('text/plain','text/html')
        assert part.get_content_disposition()!='attachment'
        return original(part,*args,**kwargs)
    monkeypatch.setattr(raw_data_manager,'get_content',read_only_body)
    report=analyze_email_bytes(message.as_bytes())
    assert '2 attachment or unsupported' in inventory(report).detail
    assert not any(e.id.startswith('request:') for e in report.evidence)
    assert_private_metadata_not_echoed(report)


def test_attached_multipart_counts_as_one_unscanned_subtree():
    part=EmailMessage()
    part.set_content(PRIVATE_BODY)
    part.add_alternative('<p>Private attached HTML</p>',subtype='html')
    part['Content-Disposition']='attachment; filename="private-alternative.eml"'
    assert unscanned_parts_count(part)==1
    report=analyze_email_bytes(part.as_bytes())
    assert inventory(report).weight==0 and report.risk_level=='guarded'
    assert not any(e.id.startswith('request:') for e in report.evidence)


@pytest.mark.parametrize('mode',['paste','file'])
def test_attachment_only_routes_return_guided_unknown_without_filename_echo(mode):
    message=EmailMessage()
    message.add_attachment(b'private data',maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    if mode=='paste':
        response=request('POST','/api/analyze/email',json={'raw_email':message.as_string()})
    else:
        response=request('POST','/api/analyze/email-file',files={'file':('message.eml',message.as_bytes(),'message/rfc822')})
    assert response.status_code==200,response.text
    data=response.json()
    assert data['risk_level']=='guarded' and data['actions'][0]['title']=='Review the original email'
    assert PRIVATE_NAME not in response.text


def test_plain_paste_and_file_analysis_share_inventory_without_changing_body_rules():
    message=EmailMessage()
    message.set_content('Meeting notes are attached.')
    message.add_attachment(b'private data',maintype='application',subtype='pdf',filename=PRIVATE_NAME)
    assert analyze_email(message.as_string()).model_dump()==analyze_email_bytes(message.as_bytes()).model_dump()
