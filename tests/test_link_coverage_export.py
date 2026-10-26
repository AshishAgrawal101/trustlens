from app.analyzers.text import analyze_text
from app.guidance import add_guidance


def test_incomplete_link_export_keeps_coverage_and_omits_all_private_addresses():
    text = ' '.join(f'https://PRIVATE-{i}.example/path' for i in range(9))
    report = add_guidance(analyze_text(text))
    assert report.share_summary.startswith('TrustLens — private-input-free summary\nLink review was incomplete.')
    assert 'PRIVATE' not in report.share_summary
    assert any(a.title == 'Review the remaining links independently' for a in report.actions)
    assert 'first 8 unique literal links' in report.share_summary
