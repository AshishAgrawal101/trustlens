"""Regressions discovered by exercising the normal-reminder demo."""
import pytest
from app.analyzers.text import request_evidence


@pytest.mark.parametrize('prefix', [
    'We will never ask you to', 'We never ask you to', 'We will not ask you to',
    "We won't ever ask you to", 'We do not ask you to', "We don't ask you to",
])
def test_explicit_not_asking_is_not_a_code_request(prefix):
    assert not request_evidence(prefix+' read us a verification code.')


@pytest.mark.parametrize('sentence,key', [
    ('We never ask you to read a verification code, but send us your password.','code'),
    ('Never buy gift cards, but send bitcoin to our agent.','payment'),
    ('Never install AnyDesk, but enable remote access for our agent.','remote'),
    ('Never share your social security number, but provide your card number.','personal'),
    ('Never return the difference, but refund the extra money.','overpayment'),
    ('Never pay a fee to claim a prize, but send a deposit to unlock a loan.','advance_fee'),
])
def test_negated_first_request_does_not_hide_a_later_positive_one(sentence,key):
    assert key in {e.id.removeprefix('request:') for e in request_evidence(sentence)}


def test_complete_demo_reminder_has_no_matched_warning():
    assert not request_evidence('Your one-time code is 123456. Do not share it with anyone. We will never ask you to read us a verification code.')
