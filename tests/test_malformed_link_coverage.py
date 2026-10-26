"""Failed literal link parsing is incomplete coverage, never a fraud score."""
import hashlib
import json
from pathlib import Path
import pytest
from app.analyzers.text import analyze_text, communication_report
from app.analyzers.email import analyze_email
from app.analyzers.url import analyze_url
from app.guidance import add_guidance
from app.models import Evidence

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'verification/sprint4h-20261024/malformed-acceptance.json'
CASES=json.loads(CONTRACT.read_text())['cases']
ACTION='Review unreadable link addresses independently'


def malformed(report):
    return [e for e in report.evidence if e.id=='url:malformed' or e.id.startswith('url:malformed:')]


def test_frozen_malformed_contract_checksum():
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==CONTRACT.with_suffix('.sha256').read_text().strip()


@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
@pytest.mark.parametrize('kind',['text','email','call'])
def test_failed_links_propagate_partial_coverage_without_risk_change(case,kind):
    report=analyze_email('Subject: PRIVATE\n\n'+case['text']) if kind=='email' else analyze_text(case['text'],kind)
    bad=malformed(report);assert len(bad)==case['parse_failures']
    assert all(e.evidence_class=='unknown' and e.weight==0 for e in bad)
    assert 'could not be parsed' in report.summary
    assert any(f"{case['parse_failures']} link address(es) could not be parsed" in s for s in report.limitations)
    assert ('Only the first 8' in '\n'.join(report.limitations))==case['over_limit']
    before=report.model_dump(exclude={'actions','share_summary'})
    result=add_guidance(report)
    assert result.model_dump(exclude={'actions','share_summary'})==before
    assert ACTION in [a.title for a in result.actions]
    assert f"{case['parse_failures']} link address(es) could not be parsed" in result.share_summary
    assert ('Only the first 8' in result.share_summary)==case['over_limit']
    assert not any(x in result.share_summary for x in ['PRIVATE','SECRET','private.example','https://s0.example'])
    if 'Send me' in case['text']:
        assert result.risk_level=='high'
        assert 'request:code' in {e.id for e in result.evidence}
        assert 'Keep security codes and passwords private' in [a.title for a in result.actions]
    else:
        assert result.risk_level=='low'
    assert result.risk_index is None and result.model_ran is False and result.confidence=='low'
    if kind=='call':assert result.actions[0].title=='End the call and call back independently'


@pytest.mark.parametrize('count',[1,8])
@pytest.mark.parametrize('kind',['text','email','call'])
def test_valid_links_keep_existing_complete_report(count,kind):
    text=' '.join(f'https://site{i}.example/path' for i in range(count))
    report=analyze_email('Subject: Notes\n\n'+text) if kind=='email' else analyze_text(text,kind)
    assert not malformed(report)
    assert report.summary=='No strong warning signs matched. That does not verify who sent this or make it safe.'
    assert not any('could not be parsed' in s for s in report.limitations)
    result=add_guidance(report)
    assert ACTION not in [a.title for a in result.actions]
    assert 'could not be parsed' not in result.share_summary


def test_ambiguous_email_keeps_failed_parse_reason_when_summary_overridden():
    result=add_guidance(analyze_email('From: PRIVATE-A@example.org\nFrom: PRIVATE-B@example.org\n\nhttps://private.example:bad/SECRET'))
    assert result.summary.startswith('This email could not be fully interpreted.')
    assert any('1 link address(es) could not be parsed' in x for x in result.limitations)
    assert '1 link address(es) could not be parsed' in result.share_summary
    assert ACTION in [a.title for a in result.actions]
    assert 'Review the original email' in [a.title for a in result.actions]
    assert 'PRIVATE' not in result.share_summary and 'SECRET' not in result.share_summary


@pytest.mark.parametrize('eid,expected',[('url:malformed',True),('url:malformed:0',True),('url:malformedness',False),('noturl:malformed:0',False)])
def test_only_authoritative_exact_or_colon_prefix_ids_trigger_notice(eid,expected):
    evidence=[Evidence(id=eid,evidence_class='unknown',severity='medium',title='PRIVATE',detail='PRIVATE',source='test')]
    result=add_guidance(communication_report('text',evidence))
    assert ('could not be parsed' in result.summary)==expected
    assert (ACTION in [a.title for a in result.actions])==expected
    assert ('could not be parsed' in result.share_summary)==expected
    assert 'PRIVATE' not in result.share_summary


@pytest.mark.parametrize('value',['https://private.example:bad/SECRET','https://[PRIVATE/SECRET'])
def test_direct_url_validation_still_rejects(value):
    with pytest.raises(ValueError):analyze_url(value)
