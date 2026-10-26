"""Narrow credential-privacy/refusal regression pairs; no fraud classification."""
from email.message import EmailMessage
import time
import pytest
from app.analyzers.text import request_evidence, analyze_text
from app.analyzers.email import analyze_email

def ids(text):return {e.id for e in request_evidence(text) if e.weight>0}

@pytest.mark.parametrize('prefix',['Do not','Never',"Don't",'You must not','You should not'])
@pytest.mark.parametrize('credential',['your password','your verification code','your security code','your passcode','your PIN'])
def test_explicit_tell_anyone_credential_privacy_is_not_secret_pressure(prefix,credential):
    text=prefix+' tell anyone '+credential+'.'
    assert not ids(text)
    assert ids(text+' Send me your verification code.')=={'request:code'}
    assert ids(text+' Do not call your bank.')=={'request:secrecy'}

@pytest.mark.parametrize('space',[' ','  ','\t','\u00a0'])
@pytest.mark.parametrize('prefix',['Do{h}not','You must{h}not','You should{h}not'])
def test_consistent_secrecy_spacing_and_modal_forms_preserve_privacy(space,prefix):
    prohibition=prefix.format(h=space)
    assert ids(prohibition+' tell anyone about this transfer.')=={'request:secrecy'}
    assert not ids(prohibition+' tell anyone your password.')

@pytest.mark.parametrize('text',[
 'Do not tell anyone that I asked for your password.',
 'Do not tell your bank your password.',
 'Never tell anyone about this payment or your password.',
 'Never tell anyone your password, but do not call your bank.',
 'Do not tell anyone your password after you send it to me.',
 'Never tell anyone your password, only tell me.',
 'Never tell anyone your password; only tell me.',
])
def test_sensitive_word_presence_cannot_hide_independent_or_ambiguous_secrecy(text):
    assert 'request:secrecy' in ids(text)

@pytest.mark.parametrize('prefix',['I will not',"I won't",'I won’t'])
@pytest.mark.parametrize('action,key',[('share my password','code'),('buy gift cards','payment'),('install TeamViewer','remote'),('send my card number','personal')])
def test_adjacent_first_person_refusal_is_not_a_live_request(prefix,action,key):
    assert not ids(prefix+' '+action+'.')
    assert ids(prefix+' '+action+'. Send me your verification code.')=={'request:code'}
    assert 'request:'+key in ids('Please '+action+'.')

@pytest.mark.parametrize('text',[
 'I will not only share my password but also provide my PIN.',
 "I won't only share my password but also provide my PIN.",
 'I will not hesitate to share my password.',
 "I won't hesitate to share my password.",
 'They will not share your password.',
])
def test_refusal_guard_is_adjacent_and_first_person_only(text):
    assert 'request:code' in ids(text)

@pytest.mark.parametrize('separator',['. ','; ', ', but '])
def test_later_same_family_positive_clause_survives(separator):
    assert ids('I will not share my password'+separator+'send me your verification code.')=={'request:code'}

@pytest.mark.parametrize('boundary',['\n','\r','\u2028','\u2029'])
def test_no_refusal_or_privacy_guard_bridges_hard_lines(boundary):
    assert ids('I will not'+boundary+'share my password.')=={'request:code'}
    assert ids('Never tell anyone'+boundary+'your password.')=={'request:secrecy'}

@pytest.mark.parametrize('kind',['text','call','email'])
def test_shared_modes_keep_uncertainty_and_original_input(kind):
    text='Do\u00a0not tell anyone your password.'
    message=EmailMessage();message['Subject']='Advice';message.set_content(text)
    report=analyze_email(message.as_string()) if kind=='email' else analyze_text(text,kind)
    assert not any(e.weight>0 for e in report.evidence)
    assert report.risk_index is None and report.confidence=='low' and not report.model_ran

def test_maximum_privacy_advice_input_is_bounded():
    text=('Never tell anyone your password.\n'*1000)[:30000]
    start=time.perf_counter();assert not ids(text);assert time.perf_counter()-start<5

@pytest.mark.parametrize('space',[' ','\t','\u00a0','  '])
def test_first_person_refusal_horizontal_spacing_and_original_positive_excerpt(space):
    assert not ids('I'+space+'will'+space+'not'+space+'share my password.')
    text='You must'+space+'not tell anyone about this transfer.'
    item=next(e for e in request_evidence(text) if e.id=='request:secrecy')
    assert ('must'+space+'not') in item.detail

def test_compound_privacy_with_later_live_requests_remains_conservative():
    text='Never tell anyone your password; send me your verification code.'
    assert 'request:code' in ids(text)
