import asyncio

import httpx
import pytest

from app.analyzers.url import analyze_url
from app.guidance import add_guidance
from app.main import app


@pytest.mark.parametrize('url,known,matched', [
    ('https://BANK.example./private?secret=123', 'bank.example', True),
    ('https://login.bank.example', 'bank.example', False),
    ('https://bank.example.evil.test', 'bank.example', False),
    ('https://bank.example@evil.test', 'bank.example', False),
    ('https://bücher.example', 'xn--bcher-kva.example', True),
    ('https://[2001:db8::1]/', '[2001:db8::1]', True),
])
def test_comparison_is_exact_and_does_not_claim_ownership(url, known, matched):
    report = add_guidance(analyze_url(url, known_website=known))
    comparison = next(e for e in report.evidence if e.id == 'url:comparison')
    assert ('matches' in comparison.title) == matched
    assert comparison.weight == 0
    assert 'safety remain unverified' in comparison.detail
    assert '123' not in comparison.detail
    assert known not in report.share_summary
    assert report.risk_index is None


@pytest.mark.parametrize('known', ['https://bank.example@evil.test', 'javascript:alert(1)', 'bank.example other.test', 'https://bank.example\\@evil.test'])
def test_invalid_reference_is_rejected(known):
    with pytest.raises(ValueError, match='known HTTP'):
        analyze_url('https://bank.example', known_website=known)


def test_comparison_endpoint_accepts_reference_and_preserves_userinfo_warning():
    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1') as client:
            return await client.post('/api/analyze/url', json={'url':'https://bank.example@evil.test','known_website':'https://bank.example/private?secret=REF'})
    response = asyncio.run(check())
    assert response.status_code == 200
    report = response.json()
    assert report['risk_level'] == 'high'
    assert {'url:userinfo', 'url:comparison'} <= {e['id'] for e in report['evidence']}
    assert 'REF' not in str(report)
