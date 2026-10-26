"""Constructed development regressions, not population accuracy measurements."""
import pytest

from app.analyzers.text import analyze_text, request_evidence
from app.guidance import add_guidance


PAIRS = [
    ('code', "At last week's safety class, the instructor displayed the example, ",
     'The support chat I am in right now says, ', 'Send me your verification code so I can protect the account.'),
    ('payment', 'For the workshop handout we used the invented line, ',
     'Someone has just sent me this message: ', 'Transfer $700 to this account before the office closes.'),
    ('remote', "In yesterday's training role-play, the actor said, ",
     'The person on the other line is telling me, ', 'Install TeamViewer and accept my connection.'),
    ('code', 'Our completed poster includes the fake example ',
     'Please review the message waiting in my inbox: ', 'Reply with your password to confirm the account.'),
]


@pytest.mark.parametrize('key,past,current,quote', PAIRS)
@pytest.mark.parametrize('opening,closing', [("'", "'"), ('"', '"'), ('“', '”'), ('‘', '’')])
def test_completed_teaching_quote_vs_current(key, past, current, quote, opening, closing):
    historical = request_evidence(past + opening + quote + closing)
    assert not [item for item in historical if item.weight > 0]
    context = next(item for item in historical if item.id == 'context:' + key)
    assert context.evidence_class == 'unknown' and context.weight == 0
    assert 'request:' + key in {item.id for item in request_evidence(current + opening + quote + closing)
                               if item.weight > 0}


@pytest.mark.parametrize('key,past,current,quote', PAIRS)
@pytest.mark.parametrize('separator', [' ', ' Now: ', '\n'])
def test_later_live_request_survives_same_family(key, past, current, quote, separator):
    evidence = request_evidence(past + "'" + quote + "'" + separator + current + "'" + quote + "'")
    assert {'context:' + key, 'request:' + key} <= {item.id for item in evidence}
    assert next(item for item in evidence if item.id == 'request:' + key).weight > 0


@pytest.mark.parametrize('prefix', [
    'Yesterday someone said, ',
    'This is an example: ',
    "At last week's safety class, a caller is now saying, ",
    'Our completed poster includes a current message: ',
    'An archived message still waiting for my response says, ',
])
def test_ambiguous_quote_retains_warning(prefix):
    evidence = request_evidence(prefix + "'Send me your verification code.'")
    assert 'request:code' in {item.id for item in evidence if item.weight > 0}


def test_unquoted_live_request_in_historical_sentence_survives():
    evidence = request_evidence("Our completed poster includes the fake example 'Reply with your password.' and now send me your verification code.")
    assert {'context:code', 'request:code'} <= {item.id for item in evidence}


def test_quote_boundary_and_other_family_survive():
    evidence = request_evidence("Our completed poster includes the fake example 'Reply with your password' and install TeamViewer now.")
    assert 'context:code' in {item.id for item in evidence}
    assert 'request:remote' in {item.id for item in evidence if item.weight > 0}


def test_negated_quote_remains_negative_control():
    assert not request_evidence("Our completed poster includes the fake example 'Never send a verification code.'")


@pytest.mark.parametrize('text,context,live', [
    ('If an unexpected caller asks you to install remote access software and approve their connection, stop. Contact support through your usual official route instead.', True, None),
    ('If an unexpected caller asks you to install remote access software, hang up.', True, None),
    ('If an unexpected caller asks you to install remote access software, comply.', False, 'remote'),
    ('If an unexpected caller asks you to install remote access software, stop worrying and do it.', False, 'remote'),
    ('If our support agent calls, install remote access software and approve their connection so they can fix the account.', False, 'remote'),
    ('If an unexpected caller asks you to install remote access software, stop; install TeamViewer for me.', True, 'remote'),
    ('If an unexpected caller asks you to install remote access software, stop. Send me your verification code.', True, 'code'),
])
def test_unexpected_caller_advice_and_live_request_falsifiers(text, context, live):
    report = add_guidance(analyze_text(text))
    contexts = [item for item in report.evidence if item.id == 'context:remote']
    assert bool(contexts) == context
    assert all(item.evidence_class == 'unknown' and item.weight == 0 for item in contexts)
    assert {item.id for item in report.evidence if item.weight > 0} == (
        {'request:' + live} if live else set())
    if live == 'code':
        assert 'Keep security codes and passwords private' in {action.title for action in report.actions}
