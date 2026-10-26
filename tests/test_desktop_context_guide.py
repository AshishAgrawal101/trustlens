"""Shared fixed guide outside Pocket scope; no actual network or browser."""
import asyncio
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import httpx
import pytest
from app.main import app
from app.pocket_workspaces import render_desktop_context

STATIC=Path(__file__).parents[1]/'static'

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

def request(path,method='GET'):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
            return await client.request(method,path)
    return asyncio.run(run())

def test_same_five_cards_and_fragments_with_desktop_navigation_and_no_input_or_scripts():
    source=(STATIC/'phone/context.html').read_text(encoding='utf-8');text=render_desktop_context();page=Page(text)
    assert [a['id'] for tag,a in page.tags if tag=='details']==['sources','captions','quotations','numbers','ads']
    assert 'TrustLens Pocket — Context checks' not in text
    assert '<small>LOCAL GUIDE</small>' in text
    assert not any(tag in {'input','form','textarea','select','script','iframe','base'} for tag,_ in page.tags)
    hrefs=[a['href'] for tag,a in page.tags if tag=='a']
    assert '/static/claim-review.html' in hrefs and '/static/numbers-context.html' in hrefs and '/static/quote-context.html' in hrefs
    assert '/phone/workspace/' not in text
    for tag,a in Page(source).tags:
        if tag=='a' and a['href'].startswith('#'):assert a['href'] in hrefs
    assert all(href.startswith('#') or href in {'/','/static/tools.html','/static/claim-review.html','/static/claim-review.html#example=endorsement','/static/numbers-context.html','/static/quote-context.html','/phone/','/phone/context.html'} for href in hrefs)
    for marker in ['Writing style cannot reliably establish','does not detect fake reviews','5 percentage points higher','Nothing is transferred automatically']:assert marker in text
    original_cards=re.findall(r'<details id="[^"]+" class="card">.*?</details>',source,re.S)
    desktop_cards=re.findall(r'<details id="[^"]+" class="card">.*?</details>',text,re.S)
    for original,rendered in zip(original_cards,desktop_cards,strict=True):
        for tool,filename in [('claims','claim-review'),('numbers','numbers-context'),('quotes','quote-context')]:
            original=original.replace('/phone/workspace/'+tool+'.html','/static/'+filename+'.html')
        assert rendered==original

def test_desktop_availability_and_early_meta_policy_do_not_claim_prepared_offline_access():
    text=render_desktop_context();page=Page(text)
    assert 'This desktop view requires the local launcher' in text
    assert 'not the prepared Pocket offline copy' in text
    assert 'Works offline after Pocket preparation has completed successfully' not in text
    assert 'English · Fixed context checks · Desktop launcher required' in text
    policies=[(i,a['content']) for i,(tag,a) in enumerate(page.tags) if tag=='meta' and a.get('http-equiv','').lower()=='content-security-policy']
    assert len(policies)==1
    for directive in ["connect-src 'none'","form-action 'none'","base-uri 'none'"]:assert directive in policies[0][1]
    assert policies[0][0]<next(i for i,(tag,_) in enumerate(page.tags) if tag=='link')

def test_render_reads_trusted_current_source_instead_of_duplicate_template(tmp_path):
    (tmp_path/'phone').mkdir();source=(STATIC/'phone/context.html').read_text(encoding='utf-8')
    (tmp_path/'phone/context.html').write_text(source.replace('</main>','<p>TRUSTED_TEMPLATE_MARKER</p></main>'),encoding='utf-8')
    assert 'TRUSTED_TEMPLATE_MARKER' in render_desktop_context(static_dir=tmp_path)
    assert 'TRUSTED_TEMPLATE_MARKER' not in render_desktop_context()

def test_fixed_route_outside_worker_scope_is_no_store_and_ignores_private_query():
    first=request('/context-guide.html');query=request('/context-guide.html?claim=PRIVATE_QUERY&url=https://PRIVATE/')
    assert first.status_code==query.status_code==200
    assert first.text==query.text==render_desktop_context()
    assert 'PRIVATE' not in query.text
    assert first.headers['cache-control']=='no-store'
    assert first.headers['content-type'].startswith('text/html')
    assert "frame-ancestors 'none'" in first.headers['content-security-policy']
    assert '/context-guide.html' not in (STATIC/'phone/sw.js').read_text(encoding='utf-8')

@pytest.mark.parametrize('path',['/context-guide','/context-guide/PRIVATE.html','/context-guide-private.html'])
def test_no_dynamic_alias_or_path_input(path):
    response=request(path+'?PRIVATE_QUERY=1');assert response.status_code==404
    assert 'PRIVATE' not in response.text

def test_post_unavailable_and_canonical_phone_changes_only_by_fixed_example_link():
    original=(STATIC/'phone/context.html').read_bytes();digest=hashlib.sha256(original).hexdigest()
    before=json.loads((STATIC.parent/'verification/desktop-context-20261024/canonical-before.json').read_text(encoding='utf-8-sig'))
    import re
    prior,count=re.subn(rb'<p><a href="/phone/workspace/claims.html#example=endorsement">[^<]*</a>[^<]*</p>',b'',original)
    assert count==1 and hashlib.sha256(prior).hexdigest()==before['Hash'].lower()
    assert request('/context-guide.html',method='POST').status_code==405
    assert request('/phone/context.html').content==original
    render_desktop_context()
    assert hashlib.sha256((STATIC/'phone/context.html').read_bytes()).hexdigest()==digest
