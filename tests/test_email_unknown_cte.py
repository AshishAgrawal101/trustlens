"""Unsupported MIME transfer mechanisms remain opaque, not implicitly identity."""
import base64
import pytest
from app.analyzers.email import analyze_email, analyze_email_bytes
from app.guidance import add_guidance

@pytest.fixture(params=['paste','eml'])
def check(request):
    return lambda raw: add_guidance(analyze_email(raw) if request.param=='paste' else analyze_email_bytes(raw.encode('ascii')))

def message(cte,body='Send me your verification code.',subject=''):
    return ('Subject: '+subject+'\n' if subject else '')+'MIME-Version: 1.0\nContent-Type: text/plain; charset=ascii\n'+('Content-Transfer-Encoding: '+cte+'\n' if cte is not None else '')+'\n'+body

def ids(report): return {e.id for e in report.evidence}

@pytest.mark.parametrize('cte',['x-private','','base64; bogus=yes','x-PRIVATE'])
@pytest.mark.parametrize('body',['Send me your verification code.',base64.b64encode(b'Send me your verification code.').decode()])
def test_unknown_body_not_interpreted_and_fixed_incomplete_export(check,cte,body):
    report=check(message(cte,body))
    assert 'email:incomplete' in ids(report)
    assert 'request:code' not in ids(report)
    assert report.risk_level=='guarded' and 'could not be fully interpreted' in report.summary
    assert 'This email check was incomplete.' in report.share_summary
    assert body not in report.share_summary and 'x-private' not in report.share_summary.lower()
    assert report.risk_index is None and report.model_ran is False

@pytest.mark.parametrize('cte',[None,'7bit','8bit','binary','  7BiT  ','BASE64','quoted-printable'])
def test_supported_default_case_and_whitespace_preserve_requests(check,cte):
    body=base64.b64encode(b'Send me your verification code.').decode() if cte=='BASE64' else 'Send me your verification code.'
    report=check(message(cte,body))
    assert 'request:code' in ids(report) and 'email:incomplete' not in ids(report)

@pytest.mark.parametrize('subject',['Send me your verification code.','Meeting notes'])
def test_unknown_leaf_preserves_independent_subject_and_known_sibling(check,subject):
    raw='Subject: '+subject+'\nContent-Type: multipart/mixed; boundary=p\n\n--p\nContent-Type: text/plain\nContent-Transfer-Encoding: x-private\n\nSend money by wire.\n--p\nContent-Type: text/plain\nContent-Transfer-Encoding: 7bit\n\nSend me your verification code.\n--p--\n'
    report=check(raw)
    assert 'email:incomplete' in ids(report) and 'request:code' in ids(report)
    assert 'request:payment' not in ids(report) and report.risk_level=='high'

def test_unknown_container_skips_children_but_preserves_subject(check):
    raw='Subject: Send me your verification code.\nContent-Type: multipart/mixed; boundary=p\nContent-Transfer-Encoding: x-private\n\n--p\nContent-Type: text/plain\n\nSend money by wire.\n--p--\n'
    report=check(raw)
    assert {'email:incomplete','request:code'} <= ids(report)
    assert 'request:payment' not in ids(report)

@pytest.mark.parametrize('values',[['7bit','x-private'],['x-private','7bit']])
def test_unsupported_duplicate_is_opaque_in_either_order(check,values):
    raw=message(values[0]).replace('\n\n','\nContent-Transfer-Encoding: '+values[1]+'\n\n',1)
    report=check(raw)
    assert 'email:incomplete' in ids(report) and 'request:code' not in ids(report)

def test_unknown_attachment_does_not_contaminate_readable_body(check):
    raw='Content-Type: multipart/mixed; boundary=p\n\n--p\nContent-Type: text/plain\n\nMeeting notes.\n--p\nContent-Disposition: attachment\nContent-Type: text/plain\nContent-Transfer-Encoding: x-private\n\nSend me your verification code.\n--p--\n'
    report=check(raw)
    assert 'email:unscanned' in ids(report)
    assert not {'email:incomplete','request:code'} & ids(report)

@pytest.mark.parametrize('space',['\u00a0','\u2003'])
@pytest.mark.parametrize('position',['before','after'])
def test_nonascii_cte_whitespace_is_opaque_for_paste_and_bytes(space,position):
    cte=(space+'base64') if position=='before' else ('base64'+space)
    raw=message(cte,base64.b64encode(b'Send me your verification code.').decode())
    for report in [analyze_email(raw),analyze_email_bytes(raw.encode('utf-8'))]:
        assert 'email:incomplete' in ids(report)
        assert 'request:code' not in ids(report)
        assert report.risk_level=='guarded'

@pytest.mark.parametrize('cte',['\tBaSe64\t','\n base64\n '])
def test_ascii_header_folding_still_decodes(check,cte):
    report=check(message(cte,base64.b64encode(b'Send me your verification code.').decode()))
    assert 'request:code' in ids(report) and 'email:incomplete' not in ids(report)
