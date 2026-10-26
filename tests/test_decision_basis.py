"""Rule-only communication reports must not claim learned-model execution."""
import pytest
from test_community import request


@pytest.mark.parametrize('kind,payload', [
    ('text', {'text': 'Send me your verification code.'}),
    ('call', {'transcript': 'Please transfer $20.'}),
    ('email', {'raw_email': 'From: example@example.invalid\nSubject: Reminder\n\nMeet at noon.'}),
    ('url', {'url': 'https://example.invalid/'}),
])
def test_rule_only_report_metadata(kind, payload):
    response = request('POST', '/api/analyze/' + kind, json=payload)
    assert response.status_code == 200
    assert response.json()['decision_basis'] == 'rules'
    assert response.json()['model_ran'] is False
