"""Only bounded passive conditional requests ending in bare refusal are contextual."""
import hashlib
from pathlib import Path
import pytest
from app.analyzers.text import request_evidence,analyze_text
from app.analyzers.email import analyze_email
from app.guidance import add_guidance

CONTRACT=Path(__file__).resolve().parents[1]/'verification/next-communication-v29-20261024/passive-refusal-acceptance.json'
ACTIONS=[('share your password','code'),('install TeamViewer','remote'),('provide your card number','personal'),('buy gift cards','payment'),('settle your balance','balance'),('return the overpayment','overpayment'),('pay the fee to receive the prize','advance_fee')]
def positive(text):return [e.id for e in request_evidence(text) if e.weight>0]
def frame(action,cue='refuse'):return 'If you are asked to '+action+', '+cue


def test_frozen_passive_refusal_contract():assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('action,key',ACTIONS)
def test_advice_unknown_context_and_direct_active_pair(action,key):
    rows=request_evidence(frame(action)+'.')
    assert not any(e.weight>0 for e in rows)
    marker=next(e for e in rows if e.id=='context:passive_refusal:'+key)
    assert marker.evidence_class=='unknown' and marker.severity=='info' and marker.weight==0
    assert 'refus' in marker.detail and 'current request exists is unknown' in marker.detail
    assert 'request:'+key in positive('You are asked to '+action+'; please do it.')


@pytest.mark.parametrize('action,key',ACTIONS)
@pytest.mark.parametrize('separator',[', ','; ','. ','\n','\u2028'])
def test_independent_later_same_family_request_remains_positive(action,key,separator):
    rows=request_evidence(frame(action)+separator+action.capitalize()+'.')
    assert 'request:'+key in [e.id for e in rows if e.weight>0]
    assert any(e.id=='context:passive_refusal:'+key for e in rows)


@pytest.mark.parametrize('cue',['refuse to refuse','refuse nothing','refuse politely','refuse and call support','refused','do not refuse'])
def test_not_bare_terminal_refusal_never_becomes_context(cue):
    assert positive(frame('share your password',cue)+'.')==['request:code']


@pytest.mark.parametrize('text',[
    "If you're asked to share your password, refuse.",
    'If you’re asked to share your password, refuse.',
    'If you are told to share your password, refuse.',
    'If you are asked to share your password; refuse.',
    'The words "if you are asked to" are quoted; share your password, refuse.',
    'If you are asked to do another task, share your password, refuse.',
])
def test_unrecognized_nonadjacent_or_embedded_delimiters_remain_positive(text):
    assert positive(text)==['request:code']


def test_only_request_span_gets_context_even_with_second_action_before_cue():
    text='If you are asked to share your password, send me your verification code, refuse.'
    assert positive(text)==['request:code']


@pytest.mark.parametrize('length,context',[(179,True),(180,True),(181,False)])
def test_request_character_bound_includes_whitespace_without_unbounded_scope(length,context):
    tail=' share your password';request=' '+'x'*(length-len(tail)-1)+tail
    assert len(request)==length
    text='If you are asked to'+request+', refuse.'
    rows=request_evidence(text)
    assert any(e.id=='context:passive_refusal:code' for e in rows)==context
    assert bool([e for e in rows if e.weight>0]) is not context


@pytest.mark.parametrize('separator',['\n','\r','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029'])
def test_hard_break_inside_prefix_or_request_is_not_joined(separator):
    assert positive('If you are asked to'+separator+'share your password, refuse.')==['request:code']


def test_original_soft_hyphen_excerpt_offsets_and_horizontal_spaces_are_preserved():
    text='If\u00a0you are as\u00adked to send your verifi\u00adcation code, refuse.'
    rows=request_evidence(text);assert not any(e.weight>0 for e in rows)
    marker=next(e for e in rows if e.id=='context:passive_refusal:code')
    assert text[:-1] in marker.detail and '\u00ad' in marker.detail and '\u00a0' in marker.detail
    assert positive('If you are as\u200bked to share your password, refuse.')==['request:code']


def test_existing_active_conditional_behavior_and_copy_stay_exact():
    text='If someone asks you to share your password, hang up.'
    row=request_evidence(text)[0]
    assert row.model_dump()=={'id':'context:code','evidence_class':'unknown','severity':'info','weight':0.0,'title':'Conditional safety advice','detail':'This wording gives advice to stop or hang up: “If someone asks you to share your password, hang up”. Whether a current request exists is unknown.','source':'Local wording and context rules'}


@pytest.mark.parametrize('mode',['text','call','email'])
def test_shared_modes_keep_unknown_sender_null_risk_and_input_free_export(mode):
    text=frame('provide your card number')+'. PRIVATE-INCIDENT'
    report=analyze_email(text) if mode=='email' else analyze_text(text,mode)
    report=add_guidance(report)
    assert report.risk_level=='low' and report.risk_index is None and report.model_ran is False
    assert not any(e.weight>0 for e in report.evidence)
    assert 'PRIVATE' not in report.share_summary


def test_maximum_input_keeps_context_bounded_and_later_live_code():
    import time
    phrase='If you are asked to share your password, refuse. '
    tail='Send me your verification code.'
    prefix=phrase*((30000-len(tail))//len(phrase))
    text=prefix+' '*(30000-len(prefix)-len(tail))+tail
    start=time.perf_counter();rows=request_evidence(text)
    assert len(text)==30000 and [e.id for e in rows if e.weight>0]==['request:code']
    assert any(e.id=='context:passive_refusal:code' for e in rows)
    assert time.perf_counter()-start<1.0
