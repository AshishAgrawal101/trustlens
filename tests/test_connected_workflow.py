"""Native explicit new-tab worksheet continuations; no persistence or transfer."""
from html.parser import HTMLParser
from pathlib import Path
import pytest
from app.pocket_workspaces import render_pocket_workspace

STATIC=Path(__file__).parents[1]/'static'
class Links(HTMLParser):
 def __init__(self,html):super().__init__();self.links=[];self.current=None;self.feed(html)
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.current={'attrs':dict(attrs),'text':''};self.links.append(self.current)
 def handle_data(self,text):
  if self.current is not None:self.current['text']+=text
 def handle_endtag(self,tag):
  if tag=='a':self.current=None

def check(html,href,label):
 links=Links(html).links
 actions=[a for a in links if a['attrs'].get('target')=='_blank']
 assert len(actions)==1
 a=actions[0];assert a['attrs']['href']==href
 assert 'noopener' in a['attrs'].get('rel','').split()
 assert a['text']==label
 assert 'Return using your browser tabs' in html
 assert 'Keep this worksheet open' in html
 assert 'Closing, reloading or leaving this page clears its entries' in html
 assert 'No input is transferred' in html
 for a in links:
  if a['attrs'].get('target')!='_blank':assert 'target' not in a['attrs']
 assert any(a['attrs'].get('href') in ('/','/phone/') and 'target' not in a['attrs'] for a in links)

@pytest.mark.parametrize('page',['quote-context.html','numbers-context.html','media-context.html'])
def test_desktop_continuations_are_explicit_native_safe_links(page):
 check((STATIC/page).read_text(),'/static/claim-review.html','Open Claim & context (new tab)')

def test_claim_separate_tools_action_keeps_normal_navigation():
 check((STATIC/'claim-review.html').read_text(),'/static/tools.html','Open other tools (new tab)')

@pytest.mark.parametrize('tool',['claims','numbers','quotes'])
def test_shared_pocket_render_keeps_canonical_destinations_and_labels(tool):
 check(render_pocket_workspace(tool),'/phone/context.html' if tool=='claims' else '/phone/workspace/claims.html',
       'Open context guide (new tab)' if tool=='claims' else 'Open Claim & context (new tab)')
 assert '/static/tools.html' not in render_pocket_workspace(tool)
