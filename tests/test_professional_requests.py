import pytest
from app.analyzers.text import analyze_text, request_evidence
from app.guidance import add_guidance

@pytest.mark.parametrize('text', ['Please settle your balance.', 'Settle the outstanding balance using this link.'])
def test_balance_request_is_a_scoped_warning(text):
    report = add_guidance(analyze_text(text))
    assert 'request:balance' in {e.id for e in report.evidence}
    assert report.risk_level == 'guarded'
    assert report.risk_index is None and report.confidence == 'low'
    assert any(a.title == 'Pause the payment' for a in report.actions)

@pytest.mark.parametrize('text', ['Do not settle your balance through an unexpected text.',
    'Never settle the outstanding balance through that link.',
    'If someone asks you to settle your balance, hang up.',
    'Your balance is available in your monthly statement.',
    'We settled the balance yesterday.'])
def test_balance_advice_and_statements_are_not_requests(text):
    assert not any(e.weight > 0 for e in request_evidence(text))

def test_balance_warning_does_not_expose_input_in_share_summary():
    report = add_guidance(analyze_text('PRIVATE-NAME, settle your balance at https://private.example/token.'))
    assert 'PRIVATE-NAME' not in report.share_summary
    assert 'private.example' not in report.share_summary

