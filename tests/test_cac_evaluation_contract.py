"""Validate preregistered diagnostic integrity, never require perfect analyzer outcomes."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

FOLDER=Path(__file__).parents[1]/'verification/cac-evaluation'
FROZEN_SHA256='8e6125b637a6a5acc5f1d37eec63ed48ad3f72ef7bd0c631960773fdb47d2927'


def test_contract_frozen_bytes_balance_and_primary_source_lineage():
    path=FOLDER/'frozen-contract.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==FROZEN_SHA256
    contract=json.loads(path.read_text())
    assert len(contract['cases'])==36
    assert Counter(c['group'] for c in contract['cases'])=={'ordinary':9,'advice':9,'scam_pattern':9,'ambiguous':9}
    assert Counter(c['mode'] for c in contract['cases'])=={'text':12,'email':12,'call':12}
    assert len({c['id'] for c in contract['cases']})==36
    for case in contract['cases']:
        assert case['source_key'] in contract['sources']
        assert urlsplit(contract['sources'][case['source_key']]).hostname=='consumer.ftc.gov'
        assert len(case['text'])<=30000
        assert all(theme in contract['action_title_map'] for theme in case['expected_specific_actions'])
        assert case['expected_warning'] is None if case['group']=='ambiguous' else isinstance(case['expected_warning'],bool)


def test_results_preserve_ids_expectations_all_outcomes_and_unscored_ambiguity():
    contract=json.loads((FOLDER/'frozen-contract.json').read_text())
    results=json.loads((FOLDER/'results.json').read_text())
    assert results['contract_sha256']==FROZEN_SHA256
    assert results['source_unchanged_during_run'] is True
    assert results['repeatability_identical_excluding_timing'] is True
    assert [row['id'] for row in results['rows']]==[case['id'] for case in contract['cases']]
    for case,row in zip(contract['cases'],results['rows']):
        assert row['expected_warning']==case['expected_warning']
        assert row['expected_specific_actions']==case['expected_specific_actions']
        assert row['warning_alignment']==(None if case['expected_warning'] is None else row['warning']==case['expected_warning'])
        assert set(row['missing_action_themes'])<=set(case['expected_specific_actions'])
        assert row['latency_ms']>=0
    manual=json.loads((FOLDER/'manual-review.json').read_text())
    assert [row['id'] for row in manual]==[case['id'] for case in contract['cases']]
    assert all(row['action_usefulness_review'] for row in manual)
    assert (FOLDER/'results.html').is_file()
