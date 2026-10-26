const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(){
  const events={},ids={},timers=new Map(),requests=[];let id=0;
  class Element{
    constructor(){this.events={};this.value='';this.hidden=false;this.children=[];this.text='';}
    addEventListener(name,fn){(this.events[name]??=[]).push(fn);}
    async fire(name){for(const fn of this.events[name]||[])await fn({persisted:true});}
    focus(){document.activeElement=this;}
    replaceChildren(){this.children=[];this.text='';}append(...children){this.children.push(...children);}
    set textContent(value){this.text=value;this.children=[];}get textContent(){return this.text+this.children.map(c=>c.textContent).join(' ');}
  }
  for(const name of ['link-details-open','link-details-result','link-details-status','known-website-wrap','content','known-website','clear','example'])ids[name]=new Element();
  const mode=new Element();let reply=async()=>({ok:true,json:async()=>data()});
  const document={body:new Element(),getElementById:name=>ids[name],createElement:()=>new Element(),querySelectorAll:()=>[mode]};
  vm.runInNewContext(fs.readFileSync(require.resolve('../static/link-details.js'),'utf8'),{document,window:{addEventListener:(name,fn)=>events[name]=fn},AbortController,setTimeout:fn=>{timers.set(++id,fn);return id;},clearTimeout:key=>timers.delete(key),fetch:async(url,options)=>{requests.push({url,options});return reply();}});
  return {ids,events,mode,timers,requests,document,setReply:fn=>reply=fn};
}
function data(){return{scheme:'https',scheme_assumed:false,ascii_host:'other.test',display_unicode_host:'other.test',port:8443,username_present:true,path_segment_count:2,query_parameter_count:3,fragment_present:true,reference_comparison:{ascii_host:'bank.test',exact_host_match:false,same_scheme:true,same_port:false},notice:'Literal local inspection only; private components omitted.'};}

test('address anatomy is opt-in, local, structured and contains no original private values',async()=>{
  const p=setup();p.ids.content.value='https://PRIVATE@other.test:8443/private/SECRET?token=PRIVATE#HIDDEN';p.ids['known-website'].value='bank.test';
  assert.equal(p.requests.length,0);await p.ids['link-details-open'].fire('click');assert.equal(p.requests.length,1);
  assert.equal(p.requests[0].url,'/api/inspect/url');assert.equal(p.requests[0].options.method,'POST');
  assert.equal(JSON.parse(p.requests[0].options.body).known_website,'bank.test');
  const text=p.ids['link-details-result'].textContent;assert.match(text,/8443/);assert.match(text,/Different hostname/);assert.doesNotMatch(text,/PRIVATE|SECRET|HIDDEN|token/);
  assert.equal(p.ids['link-details-result'].hidden,false);assert.equal(p.timers.size,0);
});

test('edit, mode change, Clear and exit abort stale anatomy and erase its output',async()=>{
  for(const invalidate of [p=>p.ids.content.fire('input'),p=>p.ids['known-website'].fire('input'),p=>p.ids.clear.fire('click'),p=>p.mode.fire('click'),p=>p.events.pagehide()]){
    const p=setup();let resolve;p.setReply(()=>new Promise(r=>resolve=r));const pending=p.ids['link-details-open'].fire('click');
    await invalidate(p);assert.equal(p.requests[0].options.signal.aborted,true);resolve({ok:true,json:async()=>data()});await pending;
    assert.equal(p.ids['link-details-result'].textContent,'');assert.equal(p.ids['link-details-status'].textContent,'');assert.equal(p.ids['link-details-open'].disabled,false);
  }
});

test('failed or malformed inspection never presents stale components and releases controls',async()=>{
  const p=setup();await p.ids['link-details-open'].fire('click');p.setReply(async()=>({ok:false,json:async()=>({detail:'Check the known website.'})}));
  await p.ids['link-details-open'].fire('click');assert.equal(p.ids['link-details-result'].hidden,true);assert.match(p.ids['link-details-status'].textContent,/known website/);
  p.setReply(async()=>({ok:true,json:async()=>({...data(),port:'PRIVATE'})}));await p.ids['link-details-open'].fire('click');assert.equal(p.ids['link-details-result'].hidden,true);assert.doesNotMatch(p.ids['link-details-status'].textContent,/PRIVATE/);
  assert.equal(p.ids['link-details-open'].disabled,false);
  p.ids['known-website-wrap'].hidden=true;const count=p.requests.length;await p.ids['link-details-open'].fire('click');assert.equal(p.requests.length,count);
});

test('inspection restores disabled-button focus without taking it from an edited field',async()=>{
  for(const moved of [false,true]){
    const p=setup();let resolve;p.setReply(()=>new Promise(r=>resolve=r));p.ids['link-details-open'].focus();
    const pending=p.ids['link-details-open'].fire('click');p.document.activeElement=moved?p.ids.content:p.document.body;
    resolve({ok:true,json:async()=>data()});await pending;
    assert.equal(p.document.activeElement,moved?p.ids.content:p.ids['link-details-open']);
  }
});

test('raw URL and reference controls reach strict producer validation unchanged', async()=>{
  for (const control of ['\uFEFF','\t']) {
    for (const field of ['content','known-website']) {
      const p=setup(); p.ids.content.value='https://example.org'; p.ids['known-website'].value='https://example.org';
      p.ids[field].value=control+p.ids[field].value;
      p.setReply(async()=>({ok:false,json:async()=>({detail:'This address contains hidden characters.'})}));
      await p.ids['link-details-open'].fire('click');
      const body=JSON.parse(p.requests[0].options.body);
      assert.equal(body[field==='content'?'url':'known_website'],p.ids[field].value);
      assert.equal(p.ids['link-details-result'].hidden,true);
      assert.match(p.ids['link-details-status'].textContent,/hidden characters/);
    }
    const p=setup(); p.ids.content.value='https://example.org'; p.ids['known-website'].value=control;
    await p.ids['link-details-open'].fire('click');
    assert.equal(JSON.parse(p.requests[0].options.body).known_website,control);
  }
});

test('ordinary edge spaces remain raw while empty or space-only optional references are omitted',async()=>{
  for (const reference of ['', '   ', '  https://example.org  ']) {
    const p=setup(); p.ids.content.value='  https://example.org  '; p.ids['known-website'].value=reference;
    await p.ids['link-details-open'].fire('click');
    const body=JSON.parse(p.requests[0].options.body);
    assert.equal(body.url,p.ids.content.value);
    if(reference.includes('https:')) assert.equal(body.known_website,reference);
    else assert.equal(Object.hasOwn(body,'known_website'),false);
    assert.equal(p.requests[0].url,'/api/inspect/url');
  }
});
