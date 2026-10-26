"""Header-free decoded text pastes are not wire-MIME byte payloads."""
import hashlib
import json
from pathlib import Path
from email import policy
from email.parser import Parser
from email.message import EmailMessage
import pytest
from app.analyzers.email import analyze_email,analyze_email_bytes
from app.guidance import add_guidance

CONTRACT=Path(__file__).resolve().parents[1]/'verification/sprint4h-20261024/unicode-paste-acceptance.json'
CASES=json.loads(CONTRACT.read_text(encoding='utf-8'))['cases']
def weighted(report):return [e.id for e in report.evidence if e.weight>0]
def incomplete(report):return any(e.id=='email:incomplete' for e in report.evidence)


def test_frozen_decoded_paste_contract():
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('case',[c for c in CASES if c['id']!='colon-invalid-header'],ids=lambda c:c['id'])
def test_header_free_paste_preserves_unicode_and_supported_wording(case):
    parsed=Parser(policy=policy.default).parsestr(case['text']);assert not parsed.keys()
    report=analyze_email(case['text'])
    assert weighted(report)==case['expected_weighted_ids']
    assert not incomplete(report)
    if '\u00ad' in case['text']:
        assert any('\u00ad' in e.detail for e in report.evidence if e.id=='request:code')
    assert '\ufffd' not in ''.join(e.detail for e in report.evidence)
    result=add_guidance(report)
    assert case['text'] not in result.share_summary
    assert result.risk_index is None and result.model_ran is False


@pytest.mark.parametrize('text',['',' ','\n','\n\n'])
def test_empty_paste_still_has_no_readable_body(text):
    assert incomplete(analyze_email(text))


@pytest.mark.parametrize('prefix',['Subject: Reminder\n\n','Content-Type: text/plain; charset=utf-8\n\n','Content-Type: text/plain; charset=us-ascii\n\n','Content-Type: text/plain; charset=utf-8\nContent-Transfer-Encoding: 8bit\n\n'])
def test_headerful_raw_unicode_retains_explicit_mime_partial_check(prefix):
    assert incomplete(analyze_email(prefix+'You must\u00a0not share your password.'))


@pytest.mark.parametrize('text',['Note: Send me your verification code.','Subject: Send me your verification code.','Note:\nSend me your verification code.'])
def test_genuine_header_looking_lines_are_not_reinterpreted_as_body(text):
    parsed=Parser(policy=policy.default).parsestr(text);assert parsed.keys()
    assert incomplete(analyze_email(text))


def test_byte_entry_does_not_receive_decoded_paste_override():
    r=analyze_email_bytes(b'You must\xa0not share your password.')
    assert incomplete(r)
    assert 'request:code' in weighted(r)


@pytest.mark.parametrize('surrogate',['\ud800','\udfff'])
def test_lone_surrogate_paste_rejects_without_echo_or_silent_sanitization(surrogate):
    with pytest.raises(ValueError) as error:analyze_email('PRIVATE '+surrogate+' Send me your password.')
    assert 'PRIVATE' not in str(error.value) and surrogate not in str(error.value)


@pytest.mark.parametrize('charset',['utf-8','iso-8859-1'])
@pytest.mark.parametrize('cte',['quoted-printable','base64','8bit'])
def test_proper_encoded_mime_string_and_bytes_remain_identical(charset,cte):
    message=EmailMessage();message.set_content('You must\u00a0not share your password.',charset=charset,cte=cte)
    byte=analyze_email_bytes(message.as_bytes());string=analyze_email(message.as_string())
    assert not incomplete(byte) and not incomplete(string)
    assert byte.model_dump()==string.model_dump()
    assert weighted(byte)==[]


@pytest.mark.parametrize('cte',['base64','quoted-printable'])
def test_invalid_unicode_transfer_payload_is_not_accepted_as_decoded_paste(cte):
    r=analyze_email('Content-Type: text/plain; charset=utf-8\nContent-Transfer-Encoding: '+cte+'\n\nYou must\u00a0not share your password.')
    assert incomplete(r)


def test_invalid_colon_header_keeps_existing_discarded_payload_and_defect_policy():
    case=next(c for c in CASES if c['id']=='colon-invalid-header')
    parsed=Parser(policy=policy.default).parsestr(case['text'])
    assert parsed.get_payload(decode=False)=='' and parsed.defects
    result=analyze_email(case['text'])
    assert incomplete(result) and weighted(result)==[]


def test_normal_astral_unicode_and_first_line_colon_in_body_are_not_sanitized():
    result=analyze_email('Hello 😀\nReminder: Send me your verifi\u00adcation code.')
    assert not incomplete(result) and weighted(result)==['request:code']
    assert any('\u00ad' in e.detail for e in result.evidence)
