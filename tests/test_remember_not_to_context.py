"""Only directly adjacent remember-not-to is a protective sensitive-action frame."""
import hashlib
from pathlib import Path
import pytest
from app.analyzers.text import request_evidence,analyze_text
from app.analyzers.email import analyze_email
from app.guidance import add_guidance

CONTRACT=Path(__file__).resolve().parents[1]/'verification/communication-fresh-20261024/reminder-acceptance.json'
ACTIONS=[('share your password','code'),('send your verification code','code'),('buy gift cards','payment'),('settle your balance','balance'),('return the overpayment','overpayment'),('pay the fee to receive the prize','advance_fee'),('provide your card number','personal'),('install TeamViewer','remote')]
def positive(text):return [e.id for e in request_evidence(text) if e.weight>0]


def test_frozen_reminder_contract_checksum():assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('action,key',ACTIONS)
def test_direct_protective_and_active_reminder_pair(action,key):
    assert positive('Please remember not to '+action+'.')==[]
    assert 'request:'+key in positive('Please remember to '+action+'.')


@pytest.mark.parametrize('text',[
    'Remember not only to share your password.',
    'Remember not to hesitate to share your password.',
    'Remember not to call support; share your password.',
    'Remember the word not; share your password.',
    'The words "remember not to" are quoted; share your password.',
    'Remember: do the other task, not this one; share your password.',
    'Do not forget to share your password.',
])
def test_nonadjacent_quoted_unrelated_or_nonprohibitive_words_do_not_suppress(text):
    assert positive(text)==['request:code']


@pytest.mark.parametrize('separator',['. ','; ','! ','\n'])
def test_later_independent_live_request_survives(separator):
    text='Remember not to share your password'+separator+'Send me your verification code.'
    assert positive(text)==['request:code']
    row=next(e for e in request_evidence(text) if e.id=='request:code')
    assert 'Send me your verification code' in row.detail


@pytest.mark.parametrize('space',[' ','  ','\t','\u00a0','\u2009'])
def test_horizontal_whitespace_follows_existing_policy(space):
    assert positive('Remember'+space+'not'+space+'to'+space+'share your password.')==[]


@pytest.mark.parametrize('separator',['\n','\r','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029'])
def test_reminder_does_not_join_hard_line_boundaries(separator):
    assert positive('Remember not to'+separator+'share your password.')==['request:code']


def test_only_existing_soft_hyphen_normalization_and_offsets_are_used():
    assert positive('Remem\u00adber not to share your password.')==[]
    assert positive('Remember\u200b not to share your password.')==['request:code']
    text='Remember not to share your password. Send me your verifi\u00adcation code.'
    row=next(e for e in request_evidence(text) if e.weight>0)
    assert row.id=='request:code' and 'verifi\u00adcation' in row.detail


@pytest.mark.parametrize('mode',['text','call','email'])
def test_shared_callers_and_input_free_guidance(mode):
    text='Please remember not to share your password with anyone. PRIVATE-NOTE'
    r=analyze_email(text) if mode=='email' else analyze_text(text,mode)
    assert not any(e.weight>0 for e in r.evidence)
    r=add_guidance(r);assert r.risk_level=='low' and r.risk_index is None and r.model_ran is False
    assert 'Keep security codes and passwords private' not in [a.title for a in r.actions]
    assert 'PRIVATE' not in r.share_summary


def test_maximum_text_keeps_later_live_request_without_unbounded_work():
    import time
    suffix='Send me your verification code.'
    prefix=('Remember not to share your password. '*850)
    text=(prefix[:30000-len(suffix)-1]+' '+suffix)
    assert len(text)==30000
    start=time.perf_counter();rows=request_evidence(text)
    assert [e.id for e in rows if e.weight>0]==['request:code']
    assert 'Send me your verification code' in next(e.detail for e in rows if e.weight>0)
    assert time.perf_counter()-start<1.0
