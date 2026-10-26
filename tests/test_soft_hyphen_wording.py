"""Source-faithful soft-hyphen equivalence regressions, not model evaluation."""
import json
import time
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import patch
import pytest
from app.analyzers.text import request_evidence, analyze_text
from app.analyzers.email import analyze_email
from app.models import AnalysisReport

CASES=json.loads((Path(__file__).parents[1]/"verification/model-next-communication/soft-hyphen-acceptance.json").read_text())["cases"]
@pytest.mark.parametrize("case",CASES,ids=lambda c:c["id"])
def test_source_wording_and_context(case):
    assert sorted(e.id for e in request_evidence(case["text"]))==case["expected_ids"]

@pytest.mark.parametrize("text",[
    "Se\u00adnd me your veri\u00adfication code.",
    "If someone asks you to se\u00adnd a veri\u00adfication code, hang up.",
])
def test_displayed_excerpt_is_exact_original_slice(text):
    item=request_evidence(text)[0]
    excerpt=item.detail.split("“",1)[1].split("”",1)[0]
    assert excerpt in text and "\u00ad" in excerpt
    assert "\u00ad" in text # analyzer never replaces caller input

@pytest.mark.parametrize("kind",["text","call","email"])
def test_normalized_negation_propagates_without_confidence_change(kind):
    text="Do n\u00adot share your password."
    message=EmailMessage(); message["Subject"]="Advice"; message.set_content(text)
    report=analyze_email(message.as_string()) if kind=="email" else analyze_text(text,kind)
    assert not any(e.weight>0 for e in report.evidence)
    assert report.risk_index is None and report.confidence=="low" and not report.model_ran

def test_url_parser_receives_literal_original_address():
    url="https://exa\u00admple.test/account"
    dummy=AnalysisReport(kind="url",risk_index=None,risk_level="low",confidence="low",summary="",model_ran=False,decision_basis="rules",evidence=[],limitations=[])
    with patch("app.analyzers.text.analyze_url",return_value=dummy) as parser:
        analyze_text("Meeting notes "+url)
    parser.assert_called_once_with(url)

def test_max_input_many_soft_hyphens_has_bounded_work():
    text=("Do n\u00adot share your veri\u00adfication code.\n"*900)[:30000]
    start=time.perf_counter()
    assert not any(e.weight>0 for e in request_evidence(text))
    assert time.perf_counter()-start<5

@pytest.mark.parametrize("text",["ab\u00adcd", "\u00adab\u00adcd\u00ad", "a\u00ad\u00adb", "a\u00ad1", "a\u00ad\nb", "α\u00adβ", ""])
def test_source_map_is_monotonic_and_every_nonempty_span_is_source_faithful(text):
    from app.analyzers.text import _wording_view, _source_excerpt
    view,indices=_wording_view(text)
    source=list(range(len(text))) if indices is None else indices
    assert source==sorted(set(source))
    assert view=="".join(text[i] for i in source)
    for start in range(len(view)):
        for end in range(start+1,len(view)+1):
            assert _source_excerpt(text,indices,start,end)==text[source[start]:source[end-1]+1].strip()
    assert _source_excerpt(text,indices,0,0)==""
