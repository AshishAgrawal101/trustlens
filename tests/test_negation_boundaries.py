"""Paired advice-boundary acceptance, separate from the FTC-pattern diagnostic."""
import json
from pathlib import Path
import time

import pytest
from app.analyzers.text import request_evidence, analyze_text
from app.analyzers.email import analyze_email

CASES=json.loads((Path(__file__).parents[1]/'verification/desktop-negation/frozen-acceptance.json').read_text())

@pytest.mark.parametrize('case',CASES,ids=lambda case:case['id'])
def test_original_offset_negative_scope_preserves_direct_and_live_requests(case):
    actual=sorted(e.id.removeprefix('request:') for e in request_evidence(case['text']) if e.weight>0)
    assert actual==sorted(case['expected_requests'])

@pytest.mark.parametrize('kind',['text','call','email'])
def test_negative_advice_fix_reaches_communication_modes(kind):
    text='Do not visit example.com and install AnyDesk.'
    report=analyze_email('Subject: Safety advice\n\n'+text) if kind=='email' else analyze_text(text,kind)
    assert not any(e.weight>0 for e in report.evidence)
    assert report.risk_index is None and report.confidence=='low'


def test_maximum_text_negative_scopes_have_bounded_work():
    text=('Do not send $1.00 or buy gift cards.\n'*900)[:30000]
    started=time.perf_counter()
    assert not any(e.weight>0 for e in request_evidence(text))
    assert time.perf_counter()-started < 5 # loose guard against unbounded rescanning, not a benchmark


@pytest.mark.parametrize('text', [
    'There was never a problem at example.com and install AnyDesk.',
    'Never mind Mr. Smith and install AnyDesk.',
])
def test_negative_word_without_supported_prohibition_cannot_hide_live_request(text):
    assert 'request:remote' in {e.id for e in request_evidence(text) if e.weight>0}
