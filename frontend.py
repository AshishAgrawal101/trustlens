"""Build a self-contained page, including for older file-serving launchers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / 'static'


def render_frontend() -> str:
    html = (STATIC / 'index.template.html').read_text(encoding='utf-8')
    css = (STATIC / 'styles.css').read_text(encoding='utf-8')
    script = (STATIC / 'app.js').read_text(encoding='utf-8')
    guide = (STATIC / 'phone/guide.js').read_text(encoding='utf-8')
    details = (STATIC / 'link-details.js').read_text(encoding='utf-8')
    transfer = (STATIC / 'draft-transfer.js').read_text(encoding='utf-8')
    primary = (STATIC / 'primary-flow.js').read_text(encoding='utf-8')
    original = (STATIC / 'original-preview.js').read_text(encoding='utf-8')
    verification = (STATIC / 'verification-plan.js').read_text(encoding='utf-8')
    route = (STATIC / 'mode-route.js').read_text(encoding='utf-8')
    practice = (STATIC / 'learning-practice.js').read_text(encoding='utf-8')
    fx = (STATIC / 'fx.js').read_text(encoding='utf-8')
    practice_css = (STATIC / 'learning-practice.css').read_text(encoding='utf-8')
    return html.replace(
        '<link rel="stylesheet" href="/static/styles.css" />', f'<style>{css}</style>'
    ).replace('<script src="/phone/guide.js"></script>', f'<script>{guide}</script>').replace('<script src="/static/app.js"></script>', f'<script>{script}</script>').replace('<script src="/static/original-preview.js"></script>', f'<script>{original}</script>').replace('<script src="/static/link-details.js"></script>', f'<script>{details}</script>').replace('<script src="/static/draft-transfer.js"></script>', f'<script>{transfer}</script>').replace('<script src="/static/primary-flow.js"></script>', f'<script>{primary}</script>').replace('<script src="/static/verification-plan.js"></script>', f'<script>{verification}</script>').replace('<script src="/static/mode-route.js"></script>', f'<script>{route}</script>').replace('<script src="/static/learning-practice.js"></script>', f'<script>{practice}</script>').replace('<script src="/static/fx.js"></script>', f'<script>{fx}</script>').replace('<link rel="stylesheet" href="/static/learning-practice.css" />', f'<style>{practice_css}</style>')


def build_frontend() -> Path:
    # Atomic replacement also lets an already-running FileResponse serve the fix.
    destination = STATIC / 'index.html'
    temporary = destination.with_suffix('.html.tmp')
    temporary.write_text(render_frontend(), encoding='utf-8')
    temporary.replace(destination)
    return destination


if __name__ == '__main__':
    print(build_frontend())
