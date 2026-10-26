"""Fixed Pocket views of the existing browser-only workspace templates."""
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / 'static'
PAGES = {
    'claims': 'claim-review.html',
    'numbers': 'numbers-context.html',
    'quotes': 'quote-context.html',
}
ASSETS = (
    '/static/claim-review.css',
    '/static/claim-review.js',
    '/static/numbers-context.css',
    '/static/numbers-context.js',
    '/static/quote-context.css',
    '/static/quote-context.js',
    '/static/source-context.js',
    '/static/unicode-notice.js',
)


def render_pocket_workspace(tool, static_dir=STATIC):
    """Render only a known template; static_dir is trusted server/export configuration."""
    if not isinstance(tool, str) or tool not in PAGES:
        raise ValueError('Unknown Pocket workspace.')
    html = (Path(static_dir) / PAGES[tool]).read_text(encoding='utf-8')
    html = html.replace('<head>', '<head><meta http-equiv="Content-Security-Policy" content="connect-src \'none\'; form-action \'none\'; base-uri \'none\'">', 1)
    for original, replacement in (
        ('href="/"', 'href="/phone/"'),
        ('href="/static/tools.html"', 'href="/phone/context.html"'),
        ('href="/static/claim-review.html"', 'href="/phone/workspace/claims.html"'),
        ('aria-label="TrustLens home"', 'aria-label="TrustLens Pocket home"'),
        ('LOCAL EDITION', 'POCKET WORKSPACE'),
        ('— TrustLens</title>', '— TrustLens Pocket</title>'),
        ('← Back to the checker', '← Back to Pocket'),
        ('Return to the local checker →', 'Return to Pocket →'),
        ('Return to the checker', 'Return to Pocket'),
        ('return to the checker', 'return to Pocket'),
        ('← All local tools', '← Pocket context guide'),
        ('Explore all local tools →', 'Pocket context guide →'),
        ('Open other tools (new tab)', 'Open context guide (new tab)'),
        ('return to the local tools', 'return to the Pocket context guide'),
        ('<span class="local">Local workspace</span>', '<span class="local">Pocket workspace</span>'),
    ):
        html = html.replace(original, replacement)
    return html.replace('<div class="facts">', '<div class="facts"><span>Pocket workspace</span><span>Offline after Pocket preparation</span>', 1)


def render_desktop_context(static_dir=STATIC):
    """Serve the same fixed guide outside Pocket scope; no request data is used."""
    html = (Path(static_dir) / 'phone' / 'context.html').read_text(encoding='utf-8')
    html = html.replace('<head>', '<head><meta http-equiv="Content-Security-Policy" content="connect-src \'none\'; form-action \'none\'; base-uri \'none\'">', 1)
    for original, replacement in (
        ('TrustLens Pocket — Context checks', 'TrustLens — Context checks'),
        ('<small>POCKET</small>', '<small>LOCAL GUIDE</small>'),
        ('href="/phone/"', 'href="/"'),
        ('href="/phone/workspace/claims.html"', 'href="/static/claim-review.html"'),
        ('href="/phone/workspace/claims.html#example=endorsement"', 'href="/static/claim-review.html#example=endorsement"'),
        ('href="/phone/workspace/numbers.html"', 'href="/static/numbers-context.html"'),
        ('href="/phone/workspace/quotes.html"', 'href="/static/quote-context.html"'),
        ('Return to Pocket’s message guide →', 'Return to the local checker →'),
        ('English · Fixed context checks · Offline after successful Pocket preparation', 'English · Fixed context checks · Desktop launcher required'),
        ('Actual physical-phone behavior remains untested. <a href="/">Back to Pocket</a>', '<a href="/static/tools.html">Explore all local tools →</a>'),
    ):
        html = html.replace(original, replacement)
    return html.replace(
        'Works offline after Pocket preparation has completed successfully and included this guide. Open <a href="/">Pocket</a>, prepare offline access, then disconnect and test this page before relying on it. Browser storage can be removed. Physical-phone use has not been verified in this build.',
        'This desktop view requires the local launcher and is not the prepared Pocket offline copy. For offline use, open <a href="/phone/">Pocket</a>, complete preparation for the current version, then disconnect and test its <a href="/phone/context.html">canonical context guide</a>. Browser storage can be removed; physical-phone behavior remains untested.',
    )
