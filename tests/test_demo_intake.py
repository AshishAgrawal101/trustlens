from pathlib import Path
import pytest

from app.analyzers.email import analyze_email_bytes
from app.analyzers.qr import extract_qr
from app.guidance import add_guidance
from frontend import render_frontend


ROOT = Path(__file__).resolve().parents[1]


def test_downloadable_qr_sample_decodes_only_to_reserved_constructed_address():
    pytest.importorskip('cv2')
    result = extract_qr((ROOT/'static/demo-qr.png').read_bytes())
    assert result['codes'] == ['https://community-library.example/meeting?demo=constructed']
    assert result['review_required'] is True
    assert 'risk_level' not in result


def test_downloadable_email_sample_preserves_html_link_difference_without_executing_it():
    report = add_guidance(analyze_email_bytes((ROOT/'static/demo-email.eml').read_bytes()))
    mismatch = next(e for e in report.evidence if e.id.startswith('email:link_mismatch:'))
    assert 'community.example' in mismatch.detail and 'account-review.example' in mismatch.detail
    assert 'account-review.example' not in report.share_summary


def test_rendered_page_includes_shared_fixed_guide_before_controller():
    html = render_frontend()
    assert '<script src="/phone/guide.js">' not in html
    assert html.index('const PocketGuide =') < html.index('const MODES =')
