"""One complete negative-urgency declaration is context, never sender verification."""
import hashlib
import json
from pathlib import Path
from email.message import EmailMessage
import pytest
from app.analyzers.text import RULES,request_evidence,analyze_text
from app.analyzers.email import analyze_email,analyze_email_bytes
from app.guidance import add_guidance

CONTRACT=Path(__file__).resolve().parents[1]/'verification/negative-urgency-v32-20261024/acceptance.json'
SPEC=json.loads(CONTRACT.read_text(encoding='utf-8'))


def test_frozen_contract_and_all_old_rules_unchanged():
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()
    assert hashlib.sha256(json.dumps(RULES,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()==SPEC['rules_sha256']


@pytest.mark.parametrize('case',SPEC['cases'],ids=lambda c:c['id'])
def test_exact_declarative_scope_and_adversarial_controls(case):
    rows=request_evidence(case['text'])
    assert set(e.id for e in rows if e.weight>0)==set(case['expected_positive_ids'])
    context=[e for e in rows if e.id=='context:negative_urgency']
    assert bool(context)==case['context']
    if context:
        row=context[0];assert (row.evidence_class,row.severity,row.weight)==('unknown','info',0)
        assert 'not urgent' in row.title.lower()
        assert 'does not verify' in row.detail.lower() and 'safety' in row.detail.lower()
        assert '\ufffd' not in row.detail
        if '\u00ad' in case['text']:assert 'ur\u00adgent' in row.detail


@pytest.mark.parametrize('text',['This\u00a0is\t not\u2009urgent\u00a0; send me your verification code.','  THIS  IS  NOT  URGENT  '])
def test_existing_horizontal_space_and_case_policy(text):
    rows=request_evidence(text);assert any(e.id=='context:negative_urgency' for e in rows)
    assert not any(e.id=='request:urgency' for e in rows)


@pytest.mark.parametrize('mode',['call','email-paste','eml'])
def test_representative_shared_callers_keep_live_code_and_input_free_exports(mode):
    text='This is not ur\u00adgent. Send me your verification code. PRIVATE-NOTE'
    if mode=='eml':
        m=EmailMessage();m.set_content(text,charset='utf-8');report=analyze_email_bytes(m.as_bytes())
    elif mode=='email-paste':report=analyze_email(text)
    else:report=analyze_text(text,mode)
    assert {e.id for e in report.evidence if e.weight>0}=={'request:code'}
    assert any(e.id=='context:negative_urgency' for e in report.evidence)
    assert report.risk_level=='high' and report.risk_index is None and report.model_ran is False
    result=add_guidance(report);assert 'PRIVATE' not in result.share_summary and '\u00ad' not in result.share_summary
