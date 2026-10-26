"""HTML presentation boundaries and ambiguous subjects must not rewrite request meaning."""
import json
from pathlib import Path
import pytest
from app.analyzers.email import analyze_email, analyze_email_bytes, VisibleText
from app.guidance import add_guidance

CASES=json.loads((Path(__file__).parents[1]/'verification/next-wave-communication/frozen-cases.json').read_text())['cases']

@pytest.mark.parametrize('bytes_input',[False,True],ids=['paste','eml'])
@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
def test_new_frozen_email_pairs(case,bytes_input):
    report=analyze_email_bytes(case['raw'].encode()) if bytes_input else analyze_email(case['raw'])
    if 'expected' in case:
        assert sorted(e.id for e in report.evidence if e.weight>0)==sorted(case['expected'])
    assert any(e.id=='email:incomplete' for e in report.evidence)==case.get('expected_incomplete',False)
    if case.get('expected_incomplete'):
        assert any(e.id=='request:code' for e in report.evidence)
        assert any(a.title=='Review the original email' for a in add_guidance(report).actions)

@pytest.mark.parametrize('body,expected',[
    ('<p>Se<span>nd</span> me your password.</p>',['request:code']),
    ('<p>Se<br>nd me your password.</p>',[]),
    ('<div>Send me your verifi</div><div>cation code.</div>',[]),
    ('<p>Do not share your password.</p><p>Install AnyDesk.</p>',['request:remote']),
    ('<p>Send me your password.</p><p>Never install AnyDesk.</p>',['request:code']),
    ('<p>Never buy gift cards.</p><script>Send me your password.</script><style>Install AnyDesk.</style>',[]),
])
def test_inline_and_block_controls_keep_distinct_meaning(body,expected):
    report=analyze_email('Content-Type: text/html\n\n'+body)
    assert sorted(e.id for e in report.evidence if e.weight>0)==expected


def test_split_inline_anchor_label_and_destination_still_compared():
    report=analyze_email('Content-Type: text/html\n\n<a href="https://other.example">https://bank.<b>example</b></a>')
    assert sum(e.id.startswith('email:link_mismatch:') for e in report.evidence)==1


def test_html_does_not_invent_spaces_between_adjacent_inline_text_nodes():
    parser=VisibleText();parser.feed('read<span>me</span>');parser.close()
    assert ''.join(parser.parts)=='readme'


def test_duplicate_subject_guidance_export_excludes_all_subject_content():
    report=add_guidance(analyze_email('Subject: PRIVATE-FIRST\nSubject: PRIVATE-SECOND send me your password.\n\nHello.'))
    assert 'PRIVATE' not in report.share_summary
    assert 'incomplete' in report.share_summary
