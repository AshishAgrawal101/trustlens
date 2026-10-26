"""Offline aliases reuse trusted templates; no model, browser or external network."""
import asyncio
import hashlib
from html.parser import HTMLParser
from pathlib import Path

import httpx
import pytest
from app.pocket_workspaces import PAGES, ASSETS, render_pocket_workspace
from app.main import app

STATIC=Path(__file__).parents[1]/'static'
EXPECTED={'claims':'claim-review.html','numbers':'numbers-context.html','quotes':'quote-context.html'}
EXPECTED_ASSETS={
 '/static/claim-review.css','/static/claim-review.js','/static/numbers-context.css','/static/numbers-context.js',
 '/static/quote-context.css','/static/quote-context.js','/static/source-context.js','/static/unicode-notice.js',
}
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tags=[];self.text=[];self.feed(text)
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
 def handle_data(self,data):self.text.append(data)
 def attrs(self,tag):return [a for t,a in self.tags if t==tag]
 def ids(self):return [a['id'] for _,a in self.tags if 'id' in a]

def request(url):
 async def run():
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:return await client.get(url)
 return asyncio.run(run())

def test_closed_page_and_asset_allowlists():
 assert PAGES==EXPECTED
 assert isinstance(ASSETS,tuple) and len(ASSETS)==8 and set(ASSETS)==EXPECTED_ASSETS
 assert all((STATIC/path.removeprefix('/static/')).is_file() for path in ASSETS)

@pytest.mark.parametrize('tool',['../numbers','../../PRIVATE','claims.html','claims?PRIVATE','/PRIVATE','<script>PRIVATE</script>','',None])
def test_unknown_key_and_traversal_fail_with_fixed_private_message(tool):
 with pytest.raises(ValueError) as error:render_pocket_workspace(tool)
 assert str(error.value)=='Unknown Pocket workspace.'

@pytest.mark.parametrize('tool',EXPECTED)
def test_reuse_ids_controllers_and_pocket_only_fixed_navigation(tool):
 original=Page((STATIC/EXPECTED[tool]).read_text(encoding='utf-8'));text=render_pocket_workspace(tool);page=Page(text)
 assert set(original.ids())<=set(page.ids())
 assert len(page.ids())==len(set(page.ids()))
 assert [a['src'] for a in page.attrs('script') if 'src' in a]==[a['src'] for a in original.attrs('script') if 'src' in a]
 links=[a.get('href','') for a in page.attrs('a')]
 assert all(href.startswith('#') or href in {'/phone/','/phone/context.html','/phone/workspace/claims.html'} for href in links)
 assert '/phone/' in links and '/phone/context.html' in links
 for a in original.attrs('a'):
  if a.get('href','').startswith('#'):assert a['href'] in links
 assert 'local edition' not in ' '.join(page.text).lower()
 assert 'pocket' in text.lower() and 'offline' in text.lower() and 'prepar' in text.lower()

@pytest.mark.parametrize('tool',EXPECTED)
def test_early_meta_csp_stops_content_connections_forms_and_base_changes(tool):
 text=render_pocket_workspace(tool);page=Page(text)
 policies=[a['content'] for a in page.attrs('meta') if a.get('http-equiv','').lower()=='content-security-policy']
 assert len(policies)==1
 for directive in ["connect-src 'none'","form-action 'none'","base-uri 'none'"]:assert directive in policies[0]
 csp_position=next(i for i,(tag,attrs) in enumerate(page.tags) if tag=='meta' and attrs.get('http-equiv','').lower()=='content-security-policy')
 first_asset=next(i for i,(tag,_) in enumerate(page.tags) if tag in ('link','script'))
 assert csp_position<first_asset
 assert not page.attrs('base')

@pytest.mark.parametrize('tool',EXPECTED)
def test_trusted_source_template_edits_propagate_without_second_html_copy(tool,tmp_path):
 source=(STATIC/EXPECTED[tool]).read_text(encoding='utf-8')
 (tmp_path/EXPECTED[tool]).write_text(source.replace('</main>','<p id="trusted-template-marker">TEMPLATE_MARKER</p></main>'),encoding='utf-8')
 output=render_pocket_workspace(tool,static_dir=tmp_path)
 assert 'TEMPLATE_MARKER' in output and 'trusted-template-marker' in output
 assert output!=render_pocket_workspace(tool)

@pytest.mark.parametrize('tool',EXPECTED)
def test_asgi_html_alias_and_query_input_never_echoed(tool):
 normal=request('/phone/workspace/'+tool+'.html');query=request('/phone/workspace/'+tool+'.html?claim=PRIVATE_QUERY&url=https://PRIVATE/');
 assert normal.status_code==query.status_code==200
 assert normal.headers['content-type'].startswith('text/html')
 assert normal.text==query.text==render_pocket_workspace(tool)
 assert 'PRIVATE' not in query.text

@pytest.mark.parametrize('path',['/phone/workspace/PRIVATE.html','/phone/workspace/claims%2FPRIVATE.html','/phone/workspace/%2e%2e%2fPRIVATE.html'])
def test_asgi_unknown_alias_is_fixed_404_without_echo(path):
 response=request(path+'?PRIVATE_QUERY=1');assert response.status_code==404
 assert 'PRIVATE' not in response.text
 if path=='/phone/workspace/PRIVATE.html':assert response.json()=={'detail':'Unknown Pocket workspace.'}


def test_original_desktop_templates_and_phone_ios_remain_byte_identical():
 paths=[*(STATIC/name for name in EXPECTED.values()),STATIC/'phone/ios.html']
 before={path:hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
 for tool,name in EXPECTED.items():
  render_pocket_workspace(tool);response=request('/static/'+name)
  assert response.status_code==200 and response.content==(STATIC/name).read_bytes()
 response=request('/phone/ios.html');assert response.status_code==200 and response.content==(STATIC/'phone/ios.html').read_bytes()
 assert before=={path:hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
