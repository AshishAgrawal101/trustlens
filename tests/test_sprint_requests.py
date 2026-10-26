"""Constructed wording regressions; no population-accuracy claim."""
import pytest

from app.analyzers.text import request_evidence


@pytest.mark.parametrize('text,key', [
    ('Please wire $480 to this account.', 'payment'),
    ("Don't send money to strangers, but transfer $900 to this account.", 'payment'),
    ("Please wire this month's invoice payment to our new bank account.", 'payment'),
    ('Read me the one-time passcode we just sent to your phone.', 'code'),
    ('Reply with your full card number, expiry date and the digits on the back.', 'personal'),
    ('Tell me your Social Security number and date of birth.', 'personal'),
    ('Open the screen-sharing app and choose allow remote control.', 'remote'),
    ('Send me 500 dollars before the meeting.', 'payment'),
    ('Share your passcode with our agent.', 'code'),
    ('Never wire $10, but transfer $25 to this account.', 'payment'),
])
def test_explicit_sensitive_requests(text, key):
    assert 'request:' + key in {item.id for item in request_evidence(text)}


@pytest.mark.parametrize('text', [
    'Do not wire $480 to this account.',
    'Never transfer $900 to this account.',
    'Do not buy gift cards or wire money to an unexpected caller.',
    'Never wire $10 or transfer $25 to this account.',
    "Do not wire this month's invoice payment to a new account without checking.",
    'Never read anyone your one-time passcode.',
    'Never reply with your full card number.',
    'Do not tell callers your Social Security number.',
    'Never open the screen-sharing app for an unexpected caller.',
    'Do not send me 500 dollars.',
    'We will never ask you to share your passcode.',
    'Please send me the invoice for $500.',
    'Please send the source code for the library app.',
    'Tell me about Social Security benefits at the workshop.',
    'The six-digit order number is 482163. Quote it at the collection desk.',
    'Please bring your name badge to the meeting.',
])
def test_advice_and_ordinary_requests_stay_unflagged(text):
    assert not request_evidence(text)
