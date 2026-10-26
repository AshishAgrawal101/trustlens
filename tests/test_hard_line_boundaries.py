"""Copied-text hard boundary regression; separate from accuracy diagnostics."""
import json
from pathlib import Path
import time
from email.message import EmailMessage
import pytest
from app.analyzers.text import request_evidence, analyze_text
from app.analyzers.email import analyze_email

CASES = json.loads((Path(__file__).parents[1] / "verification/desktop-next-communication/hard-separator-acceptance.json").read_text())["cases"]

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_hard_line_separator_preserves_clause_independence(case):
    assert sorted(e.id for e in request_evidence(case["text"]) if e.weight > 0) == case["expected_requests"]

@pytest.mark.parametrize("kind", ["text", "email", "call"])
def test_shared_analyzer_does_not_borrow_sensitive_words_across_unicode_line(kind):
    text = "Please send the meeting notes\u2028Your verification code is 847261."
    message = EmailMessage()
    message["Subject"] = "Meeting notes"
    message.set_content(text)
    report = analyze_email(message.as_string()) if kind == "email" else analyze_text(text, kind)
    assert not any(e.weight > 0 for e in report.evidence)
    assert report.risk_index is None and report.confidence == "low"

def test_maximum_input_has_bounded_separator_work():
    text = ("Please send the meeting notes\u2028Your verification code is 847261.\r" * 600)[:30000]
    start = time.perf_counter()
    assert not any(e.weight > 0 for e in request_evidence(text))
    assert time.perf_counter() - start < 5

def test_evidence_keeps_original_unicode_and_no_newline_joining():
    text = "Read me your verification code.\u2028Send us the\nverification code."
    evidence = [e for e in request_evidence(text) if e.weight > 0]
    assert len(evidence) == 1
    assert "Read me your verification code" in evidence[0].detail
    assert not request_evidence("Send us the\nverification code.")
