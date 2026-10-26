"""C06/C07 regressions from the examined first challenge, not the held-back set."""
import pytest

from app.analyzers.text import analyze_text, request_evidence
from app.guidance import add_guidance


@pytest.mark.parametrize('text', [
    "You are right never to share your code. In this case, though, read out the code we just sent because I'm the security supervisor.",
    'Read out the code we just sent to finish the account check.',
    'Never read us a verification code, but send the code we just sent for the security check.',
])
def test_delivered_code_with_security_context_is_a_request(text):
    report = add_guidance(analyze_text(text, 'call'))
    assert 'request:code' in {item.id for item in report.evidence}
    assert any(action.title == 'Keep security codes and passwords private' for action in report.actions)


@pytest.mark.parametrize('text', [
    'Do not read out the code we just sent to complete your account check.',
    'We will never ask you to share the code we just sent for account security.',
    'Share the source code we just sent for the security app.',
    'Please share the discount code we just sent.',
    'Read the code of conduct we just sent.',
    'Share the code we just sent for the crossword.',
])
def test_negated_and_ordinary_code_requests_stay_unflagged(text):
    assert not request_evidence(text)


@pytest.mark.parametrize('text,key', [
    ('If someone asks you to buy gift cards, hang up. Do not send them money or read out the card numbers. Call a trusted person instead.', 'payment'),
    ('If someone asks you to read a verification code, stop.', 'code'),
    ('If a caller asks you to install AnyDesk, hang up.', 'remote'),
])
def test_explicit_stop_advice_is_context_unknown(text, key):
    report = add_guidance(analyze_text(text, 'call'))
    context = next(item for item in report.evidence if item.id == 'context:' + key)
    assert context.evidence_class == 'unknown' and context.weight == 0
    assert not any(item.weight > 0 for item in report.evidence)
    assert not any(action.title == 'Pause the payment' for action in report.actions)
    assert 'does not verify' in report.summary


@pytest.mark.parametrize('text,key', [
    ('If someone asks you to buy gift cards, hang up, but send bitcoin to my agent.', 'payment'),
    ('If someone asks you to buy gift cards, stop. Transfer $75 to this account.', 'payment'),
    ('If someone asks you to read a verification code, stop; give me your password.', 'code'),
])
def test_later_independent_request_survives_safety_advice(text, key):
    evidence = request_evidence(text)
    assert 'context:' + key in {item.id for item in evidence}
    assert 'request:' + key in {item.id for item in evidence if item.weight > 0}


@pytest.mark.parametrize('text', [
    'If you have time, buy gift cards for my agent.',
    'If someone asks you to buy gift cards, comply.',
    'If someone asks you to buy gift cards, stop worrying and do it.',
    "The caller says 'buy gift cards' and is waiting for payment.",
])
def test_other_conditionals_and_live_quotes_are_not_suppressed(text):
    assert 'request:payment' in {item.id for item in request_evidence(text) if item.weight > 0}


def test_independent_secrecy_request_survives_safety_advice():
    evidence = request_evidence('If someone asks you to buy gift cards, hang up. Do not tell your family.')
    assert 'request:secrecy' in {item.id for item in evidence if item.weight > 0}


def test_amount_alone_does_not_assert_an_unusual_payment_method():
    report = add_guidance(analyze_text('Please send me $30 for our shared lunch.'))
    payment = next(item for item in report.evidence if item.id == 'request:payment')
    assert payment.title == 'Payment request to verify'
    assert 'Verify through a separate route' in {action.title for action in report.actions}
    assert not any(item.id in ('request:urgency', 'request:secrecy') for item in report.evidence)
