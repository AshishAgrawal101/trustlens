"""Fresh typography/negation equivalence regressions, not diagnostic tuning."""
import time
import pytest
from app.analyzers.text import request_evidence

HORIZONTAL=[' ', '  ', '\t', '\u00a0', '\u2009']
def ids(text): return {e.id for e in request_evidence(text) if e.weight>0}

@pytest.mark.parametrize('space',HORIZONTAL)
@pytest.mark.parametrize('negative',['Do','You should','You must'])
def test_horizontal_negative_advice_does_not_hide_independent_live_request(space,negative):
    advice=negative+space+'not share your password.'
    assert not ids(advice)
    assert ids(advice+' Install TeamViewer.')=={'request:remote'}

@pytest.mark.parametrize('space',HORIZONTAL)
def test_original_offset_negative_clause_guard_uses_same_horizontal_phrases(space):
    assert not ids('Do'+space+'not send $1.00 or buy gift cards.')
    assert ids('Do'+space+'not send $1.00, but buy gift cards.')=={'request:payment'}

@pytest.mark.parametrize('space',HORIZONTAL)
def test_existing_sensitive_noun_phrases_keep_their_meaning(space):
    for phrase in ['social security number','bank account number','card number']:
        sensitive=phrase.replace(' ',space)
        assert ids('Send your '+sensitive+'.')=={'request:personal'}
        assert not ids('Do not send your '+sensitive+'.')
    assert not ids('Please send the meeting agenda.')

@pytest.mark.parametrize('hyphen',['-','\u2010','\u2011'])
@pytest.mark.parametrize('compound',['six{h}digit','6{h}digit','one{h}time'])
def test_existing_compound_code_phrases_accept_typographic_hyphens(hyphen,compound):
    phrase=compound.format(h=hyphen)+' code'
    assert ids('Read me the '+phrase+'.')=={'request:code'}
    assert not ids('Never read anyone the '+phrase+'.')
    assert not ids('The '+compound.format(h=hyphen)+' order number is on the receipt.')

@pytest.mark.parametrize('text',[
 'You should not hesitate to share your password.',
 'You must not hesitate to share your password.',
 'You should not only share your password but also provide your PIN.',
 'You should share your password.',
 'Never mind the instructions and share your password.',
])
def test_negative_words_without_direct_prohibition_cannot_hide_live_request(text):
    assert 'request:code' in ids(text)

@pytest.mark.parametrize('boundary',['\n','\r','\r\n','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029'])
def test_horizontal_repair_never_joins_hard_line_boundaries(boundary):
    assert ids('Do'+boundary+'not share your password.')=={'request:code'}
    assert not ids('Send your bank'+boundary+'account number.')
    assert ids('Do not'+boundary+'buy gift cards and install TeamViewer.')=={'request:payment','request:remote'}

def test_sensitive_excerpt_keeps_original_spacing():
    text='Send your bank\u00a0account\u00a0number.'
    evidence=request_evidence(text)
    assert len(evidence)==1 and 'bank\u00a0account\u00a0number' in evidence[0].detail

def test_max_input_horizontal_negation_has_bounded_work():
    text=('Do\u00a0not send $1.00 or buy gift cards.\n'*900)[:30000]
    start=time.perf_counter()
    assert not ids(text)
    assert time.perf_counter()-start<5

@pytest.mark.parametrize('space',HORIZONTAL)
@pytest.mark.parametrize('compound',['six{h}digit','6{h}digit','one{h}time'])
def test_known_code_compounds_accept_only_horizontal_word_spacing(space,compound):
    phrase=compound.format(h=space)+' code'
    assert ids('Read me the '+phrase+'.')=={'request:code'}
    assert not ids('Do not read anyone the '+phrase+'.')
