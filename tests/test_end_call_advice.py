"""Examined PR06 development regression and paired refusal/live controls."""
import pytest

from app.analyzers.text import analyze_text, request_evidence
from app.guidance import add_guidance


def test_examined_end_call_advice_is_unknown_not_a_live_request():
    text = "If the caller asks you to install a remote-control program or read a verification code aloud, end the call. Find the housing office's number on your tenancy papers and call that number yourself."
    report = add_guidance(analyze_text(text, 'call'))
    context = next(item for item in report.evidence if item.id == 'context:code')
    assert (context.evidence_class, context.severity, context.weight) == ('unknown', 'info', 0)
    assert not any(item.weight > 0 for item in report.evidence)
    assert report.risk_index is None and report.confidence == 'low'
    assert 'does not verify' in report.summary
    assert 'End the call and call back independently' in {action.title for action in report.actions}


@pytest.mark.parametrize('subject', ['the caller', 'someone'])
@pytest.mark.parametrize('refusal', ['end the call', 'stop', 'hang up'])
def test_exact_subject_and_refusal_variants(subject, refusal):
    evidence = request_evidence(f'If {subject} asks you to read a verification code, {refusal}.')
    assert {item.id for item in evidence} == {'context:code'}
    assert all(item.weight == 0 and item.evidence_class == 'unknown' for item in evidence)


@pytest.mark.parametrize('ending', [
    'comply',
    'end the call now and read me your verification code',
    'end the call and read me your verification code',
    'stop worrying and do it',
])
def test_refusal_prefix_without_delimiter_cannot_suppress_request(ending):
    evidence = request_evidence('If the caller asks you to read a verification code, ' + ending + '.')
    assert 'request:code' in {item.id for item in evidence if item.weight > 0}
    assert 'context:code' not in {item.id for item in evidence}


@pytest.mark.parametrize('separator', ['; ', ', but ', '. '])
@pytest.mark.parametrize('later,key', [
    ('read me your verification code', 'code'),
    ('install TeamViewer for me', 'remote'),
    ('send $75 to this account', 'payment'),
])
def test_later_independent_request_survives_end_call_advice(separator, later, key):
    evidence = request_evidence('If the caller asks you to read a verification code, end the call' + separator + later + '.')
    assert 'context:code' in {item.id for item in evidence}
    assert 'request:' + key in {item.id for item in evidence if item.weight > 0}


@pytest.mark.parametrize('text', [
    'The caller asks you to read a verification code.',
    "The caller says 'read me a verification code' and is waiting.",
    'If the caller is ready, read me your verification code.',
])
def test_present_requests_remain_warnings(text):
    assert 'request:code' in {item.id for item in request_evidence(text) if item.weight > 0}


def test_no_broader_remote_program_detection_was_added():
    assert not request_evidence('Install a remote-control program.')
