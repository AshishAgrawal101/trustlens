"""Fixed guidance must not discard an already detected action domain."""
import hashlib
import json
from pathlib import Path
import pytest
from app.analyzers.text import analyze_text, communication_report
from app.analyzers.email import analyze_email
from app.guidance import add_guidance, REQUEST_ACTIONS, VERIFY
from app.models import Evidence

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'verification/sprint4h-20261024/guidance-acceptance.json'
CASES=json.loads(CONTRACT.read_text())['cases']


def snapshot(report):
    return report.model_dump(exclude={'actions','share_summary'})


def test_frozen_guidance_acceptance_checksum():
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
@pytest.mark.parametrize('kind',['text','email','call'])
def test_all_detected_action_domains_survive(case,kind):
    text=case['input']+' PRIVATE-INCIDENT https://private.example/SECRET'
    report=analyze_email('Subject: PRIVATE-SUBJECT\n\n'+text) if kind=='email' else analyze_text(text,kind)
    before=snapshot(report)
    result=add_guidance(report)
    expected=[REQUEST_ACTIONS[k].title for k in case['expected_action_keys']]+[VERIFY.title]
    if kind=='call':
        expected.insert(0,'End the call and call back independently')
    assert [a.title for a in result.actions]==expected
    assert snapshot(result)==before
    assert result.risk_index is None and result.model_ran is False and result.confidence=='low'
    for action in result.actions:
        assert action.title in result.share_summary and action.detail in result.share_summary
    assert not any(v in result.share_summary for v in ['PRIVATE','private.example','SECRET','$50'])


def test_incomplete_email_and_link_review_cannot_be_displaced():
    raw=('From: PRIVATE-A@example.org\nFrom: PRIVATE-B@example.org\nContent-Type: text/html\n\n'
         '<p>Send $50. Return the overpayment. Send me your verification code.</p>'
         '<a href="https://other.example/PRIVATE">https://bank.example</a>')
    report=analyze_email(raw);before=snapshot(report);result=add_guidance(report)
    assert [a.title for a in result.actions]==[
        REQUEST_ACTIONS['payment'].title,REQUEST_ACTIONS['overpayment'].title,REQUEST_ACTIONS['code'].title,
        'Use a known address instead of this link','Review the original email',VERIFY.title]
    assert snapshot(result)==before
    assert 'This email check was incomplete.' in result.share_summary
    assert 'Review the original email' in result.share_summary
    assert 'PRIVATE' not in result.share_summary and 'bank.example' not in result.share_summary


def test_repeated_evidence_and_balance_alias_keep_stable_unique_actions():
    evidence=[Evidence(id='request:'+key,evidence_class='inferred',severity='high',title='PRIVATE',detail='PRIVATE',source='test',weight=.8)
              for key in ['code','payment','balance','overpayment','code','payment']]
    result=add_guidance(communication_report('text',evidence))
    assert [a.title for a in result.actions]==[REQUEST_ACTIONS[k].title for k in ['payment','overpayment','code']]+[VERIFY.title]
    assert 'PRIVATE' not in result.share_summary


def test_all_fixed_action_templates_have_a_finite_bound_and_no_duplicates():
    evidence=[Evidence(id='request:'+key,evidence_class='unknown',severity='info',title='PRIVATE',detail='PRIVATE',source='test') for key in REQUEST_ACTIONS]
    evidence += [Evidence(id=key,evidence_class='unknown',severity='info',title='PRIVATE',detail='PRIVATE',source='test') for key in ['email:incomplete','email:link_mismatch:0']]
    result=add_guidance(communication_report('call',evidence));titles=[a.title for a in result.actions]
    assert titles[0]=='End the call and call back independently'
    assert titles[1:8]==[a.title for a in REQUEST_ACTIONS.values()]
    assert titles[8:]==['Use a known address instead of this link','Review the original email',VERIFY.title]
    assert len(titles)==11 and len(set(titles))==11
    assert 'PRIVATE' not in result.share_summary
