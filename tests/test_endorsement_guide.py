"""One fixed constructed example link follows its own desktop/Pocket workspace."""
from pathlib import Path
from app.pocket_workspaces import render_desktop_context

ROOT=Path(__file__).resolve().parents[1]


def test_endorsement_guide_link_stays_in_the_correct_workspace_scope():
    pocket=(ROOT/'static/phone/context.html').read_text(encoding='utf-8')
    desktop=render_desktop_context()
    for html,prefix in [(pocket,'/phone/workspace/claims.html'),(desktop,'/static/claim-review.html')]:
        card=html.split('<details id="ads" class="card">',1)[1].split('</details>',1)[0]
        assert f'href="{prefix}#example=endorsement"' in card
        assert 'constructed endorsement' in card and 'Review' in card
        assert '<form' not in card and '<script' not in card
    assert '/phone/workspace/claims.html#example=endorsement' not in desktop
    assert '/static/claim-review.html#example=endorsement' not in pocket
