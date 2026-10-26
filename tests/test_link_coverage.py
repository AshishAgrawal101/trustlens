"""The bounded literal-link review must disclose unexamined addresses."""
import pytest
from app.analyzers import text as analyzer
from app.analyzers.email import analyze_email
from app.guidance import add_guidance

LINKS = [f'https://site{i}.example/path' for i in range(8)]
NINTH = 'https://PRIVATE-bank.example@unexamined.example/SECRET'

@pytest.mark.parametrize('links', [LINKS, LINKS * 2, LINKS + [LINKS[0]] * 20])
def test_eight_unique_literal_links_keep_existing_result(links):
    report = analyzer.analyze_text(' '.join(links))
    assert 'analysis:links_incomplete' not in {e.id for e in report.evidence}
    assert len([e for e in report.evidence if e.id.startswith('url:host:')]) == 8
    assert report.summary.startswith('No strong warning signs matched.')

@pytest.mark.parametrize('kind', ['text','call','email'])
def test_ninth_link_is_disclosed_but_not_analyzed(monkeypatch,kind):
    actual = analyzer.analyze_url
    checked = []
    def track(url):
        checked.append(url)
        return actual(url)
    monkeypatch.setattr(analyzer,'analyze_url',track)
    content = ' '.join(LINKS + [NINTH, NINTH])
    report = analyze_email('Subject: Links\n\n'+content) if kind == 'email' else analyzer.analyze_text(content,kind)
    assert checked == LINKS
    coverage = next(e for e in report.evidence if e.id == 'analysis:links_incomplete')
    assert coverage.evidence_class == 'unknown' and coverage.weight == 0
    assert '9' in coverage.detail and '8' in coverage.detail and '1' in coverage.detail
    assert 'http' not in coverage.detail and 'PRIVATE' not in coverage.detail
    assert not any(e.id.startswith('url:userinfo') for e in report.evidence)
    assert 'incomplete' in report.summary.lower()
    assert any('first 8 unique literal HTTP(S)' in limit for limit in report.limitations)
    assert report.risk_index is None and report.confidence == 'low'
    shared = add_guidance(report).share_summary
    assert 'PRIVATE' not in shared and 'SECRET' not in shared
    assert 'unexamined.example' not in shared


def test_excess_links_do_not_hide_real_first_eight_warning():
    report = analyzer.analyze_text(' '.join(['https://bank.example@first.example'] + LINKS))
    assert report.risk_level == 'high'
    assert 'analysis:links_incomplete' in {e.id for e in report.evidence}
    assert 'Pause before responding.' in report.summary
