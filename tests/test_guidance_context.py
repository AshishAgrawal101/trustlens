"""Post-entry fixed-copy regressions; no detection-performance claim."""
import pytest

from app.analyzers.text import analyze_text
from app.guidance import add_guidance


@pytest.mark.parametrize('text', [
    'The school office asks me to check a timetable.',
    'The repair service asks me to confirm an appointment.',
])
def test_independent_verification_guidance_covers_nonbank_organizations(text):
    report = add_guidance(analyze_text(text))
    action = next(action for action in report.actions if action.title == 'Verify through a separate route')
    assert 'school, service-provider or organization record' in action.detail
    assert 'already know' in action.detail
    assert 'Do not use contact details supplied in the message.' in action.detail
    assert report.risk_index is None and report.decision_basis == 'rules' and report.model_ran is False


def test_payment_guidance_does_not_invent_an_account_protection_story():
    text = 'Send $75 for the PRIVATE-REPAIR-CHARGE.'
    report = add_guidance(analyze_text(text))
    assert [action.title for action in report.actions] == ['Pause the payment', 'Verify through a separate route']
    payment = report.actions[0]
    assert 'Confirm the amount, reason and payment instructions' in payment.detail
    assert 'protect your account' not in payment.detail and 'bank independently' not in payment.detail
    assert 'route you already trust' in payment.detail
    assert 'Do not use contact details supplied in the message.' in payment.detail
    assert 'PRIVATE-REPAIR-CHARGE' not in report.share_summary and '$75' not in report.share_summary
    assert 'request:payment' in {item.id for item in report.evidence if item.weight > 0}


def test_mixed_payment_and_device_actions_keep_existing_order():
    report = add_guidance(analyze_text('Send $75 for the repair. Install TeamViewer.'))
    assert [action.title for action in report.actions] == [
        'Pause the payment', 'Keep control of your device', 'Verify through a separate route']
    assert report.risk_level == 'high' and report.confidence == 'low' and report.risk_index is None
