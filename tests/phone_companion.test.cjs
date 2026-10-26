const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const guide=require('../static/phone/guide.js');
const {receiveSharedText,sharedPage}=require('../static/phone/share.js');
const root=path.join(__dirname,'../static/phone');
const share=text=>new Request('https://local.test/phone/share',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({text})});

test('user choices give fixed actions without copying private input',()=>{
  assert.equal(guide.nextSteps([]).length,1);
  assert.equal(guide.nextSteps(['money','money','code']).length,3);
  assert.match(guide.summary(['money']),/Pause before paying/);
  assert.doesNotMatch(guide.summary(['PRIVATE-TEXT']),/PRIVATE-TEXT/);
  assert.match(guide.summary([]),/no automatic scam verdict/);
});
test('host inspection exposes userinfo without visiting or exporting addresses',()=>{
  const rows=guide.hosts('Check https://trusted.test@elsewhere.test/pay?token=PRIVATE now.');
  assert.equal(rows[0].host,'elsewhere.test');
  assert.match(rows[0].notes.join(' '),/before @/);
  assert.doesNotMatch(JSON.stringify(rows),/PRIVATE/);
  assert.equal(guide.hosts('No URL here').length,0);
  assert.equal(guide.hosts(Array(20).fill('https://example.test').join(' ')).length,12);
  assert.throws(()=>guide.hosts('a'.repeat(30001)));
});
test('shared form accepts bounded text and rejects duplicates, empty, files and oversize',async()=>{
  assert.equal(await receiveSharedText(share('Read me a code.')),'Read me a code.');
  await assert.rejects(()=>receiveSharedText(share(' ')));
  await assert.rejects(()=>receiveSharedText(share('a'.repeat(30001))));
  await assert.rejects(()=>receiveSharedText(share('a'.repeat(256001))));
  const duplicate=new Request('https://local.test/phone/share',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body:'text=a&text=b'});
  await assert.rejects(()=>receiveSharedText(duplicate));
  await assert.rejects(()=>receiveSharedText(new Request('https://local.test/phone/share',{method:'POST',body:new FormData()})));
  await assert.rejects(()=>receiveSharedText(new Request('https://local.test/phone/share',{method:'POST',headers:{'content-type':'application/x-www-form-urlencodedevil'},body:'text=message'})));
});
test('shared payload cannot escape textarea or interpret replacement tokens',()=>{
  const shell=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const result=sharedPage(shell,'</textarea><script>alert(1)</script>$&');
  assert.match(result,/&lt;\/textarea&gt;&lt;script&gt;alert\(1\)&lt;\/script&gt;\$&/);
  assert.doesNotMatch(result,/<script>alert/);
  assert.throws(()=>sharedPage('changed shell','text'));
});
test('service worker handles shares without network or caching any shared text',async()=>{
  const handlers={},puts=[]; let network=0;
  const shell=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const self={location:{origin:'https://local.test'},clients:{claim:async()=>{}},skipWaiting:async()=>{},addEventListener:(name,fn)=>handlers[name]=fn};
  const cache={addAll:async urls=>puts.push(...urls),match:async()=>new Response(shell)};
  const context={self,caches:{open:async()=>cache,keys:async()=>[]},Response,URL,receiveSharedText,sharedPage,importScripts:()=>{},fetch:async()=>{network++;throw new Error('Network forbidden');}};
  vm.runInNewContext(fs.readFileSync(path.join(root,'sw.js'),'utf8'),context);
  let install; handlers.install({waitUntil:p=>install=p}); await install;
  let response; handlers.fetch({request:share('PRIVATE-SHARE'),respondWith:p=>response=p});
  const received=await response; assert.equal(received.status,200);
  assert.match(await received.text(),/PRIVATE-SHARE/);
  assert.equal(received.headers.get('cache-control'),'no-store');
  assert.equal(network,0); assert.equal(puts.some(x=>x.includes('PRIVATE-SHARE')),false);
  assert.equal(puts.some(x=>x.includes('/api/')),false);
  let intercepted=false; handlers.fetch({request:new Request('https://other.test/phone/'),respondWith:()=>intercepted=true});
  assert.equal(intercepted,false);
});
test('every declared offline shell asset exists and manifest uses body sharing',()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.webmanifest'),'utf8'));
  assert.equal(manifest.share_target.method,'POST');
  assert.equal(manifest.scope,'/phone/');
  for(const icon of manifest.icons) assert.ok(fs.existsSync(path.join(root,path.basename(icon.src))));
});

function phonePage(writeText=async()=>{}, serviceWorker,hash='') {
  const ids={},inputs=[],windowEvents={},timers=new Map(); let timerId=0;
  const document={getElementById:id=>ids[id],querySelectorAll:()=>inputs,createElement:()=>new Element()};
  class Element {
    constructor(){this.attributes={};this.children=[];this.events={};this.value='';this.dataset={};this.checked=false;this.hidden=false;this.text='';}
    getAttribute(name){return this.attributes[name];}
    set textContent(value){this.text=value;this.children=[];}
    get textContent(){return this.text+this.children.map(c=>c.textContent).join('');}
    append(...children){this.children.push(...children);}
    replaceChildren(){this.children=[];this.text='';}
    addEventListener(name,fn){this.events[name]=fn;}
    fire(name,event={preventDefault(){}}){return this.events[name]?.(event);}
    focus(){document.activeElement=this;}
    querySelector(){return this.strong??=new Element();}
  }
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  for(const match of html.matchAll(/<\w+\b([^>]*)>/g)){
    const attrs=match[1],element=new Element(),id=attrs.match(/id="([^"]+)"/);
    if(id) ids[id[1]]=element;
    for(const attr of attrs.matchAll(/([\w-]+)="([^"]*)"/g))element.attributes[attr[1]]=attr[2];
    element.hidden=/\bhidden\b/.test(attrs);
    if(/name="request"/.test(attrs)){element.value=attrs.match(/value="([^"]+)"/)[1];inputs.push(element);}
  }
  if(!ids['pocket-version']){ids['pocket-version']=new Element();ids['pocket-version'].attributes.content='trustlens-pocket-v35';}
  class MessageChannel {
    constructor(){
      this.port1={close(){},onmessage:null};
      this.port2={close(){},postMessage:data=>this.port1.onmessage?.({data})};
    }
  }
  if(serviceWorker){const register=serviceWorker.register;serviceWorker={...serviceWorker,register:async(...args)=>{const registration=await register(...args);return Object.assign({update:async()=>{}},registration);}};}
  const context={MessageChannel,document,window:{location:{hash,reload(){}},isSecureContext:!!serviceWorker,addEventListener:(name,fn)=>windowEvents[name]=fn},navigator:{clipboard:{writeText},...(serviceWorker?{serviceWorker}:{})},PocketGuide:guide,history:{replaceState(){}},URL,Blob,
    setTimeout:fn=>{timers.set(++timerId,fn);return timerId;},clearTimeout:id=>timers.delete(id)};
  vm.runInNewContext(fs.readFileSync(path.join(root,'phone.js'),'utf8'),context);
  return {ids,inputs,timers,windowEvents,document,navigator:context.navigator};
}
test('phone edits and page exit remove private text, topics and stale results',()=>{
  const p=phonePage();p.ids.message.value='PRIVATE-MESSAGE';p.inputs[0].checked=true;p.ids.guide.fire('submit');
  assert.equal(p.ids.result.hidden,false);assert.match(p.ids.actions.textContent,/Pause before paying/);
  p.ids.message.fire('input');assert.equal(p.ids.result.hidden,true);
  p.ids.guide.fire('submit');p.windowEvents.pagehide();
  assert.equal(p.ids.message.value,'');assert.equal(p.inputs[0].checked,false);assert.equal(p.ids.actions.textContent,'');
});
test('pending clipboard permission times out with download fallback and respects Clear',async()=>{
  const p=phonePage(()=>new Promise(()=>{}));p.ids.guide.fire('submit');
  const pending=p.ids.copy.fire('click');[...p.timers.values()][0]();await pending;
  assert.match(p.ids['copy-status'].textContent,/Use Download/);
  const second=p.ids.copy.fire('click');p.ids.clear.fire('click');[...p.timers.values()][0]();await second;
  assert.equal(p.ids['copy-status'].textContent,'');assert.equal(p.ids.result.hidden,true);
});
const settle=async()=>{for(let i=0;i<24;i++)await Promise.resolve();};
function offlineWorker(state='installing') {
  const listeners=new Set();
  return {state,listeners,postMessage(message,ports){ports[0].postMessage({cache:'trustlens-pocket-v35',ready:true});},addEventListener(name,fn){listeners.add(fn);},removeEventListener(name,fn){listeners.delete(fn);},change(state){this.state=state;for(const fn of listeners)fn();}};
}
test('new offline worker must activate even when ready already points to an older worker',async()=>{
  const old=offlineWorker('activated'),next=offlineWorker();
  const p=phonePage(undefined,{register:async()=>({active:old,installing:next}),ready:Promise.resolve({active:old})});
  await settle();assert.equal(p.ids.prepare.disabled,true);assert.doesNotMatch(p.ids['offline-status'].textContent,/shell prepared/);
  next.change('installed');await settle();assert.equal(p.ids.prepare.disabled,true);
  next.change('activated');await settle();assert.match(p.ids['offline-status'].textContent,/shell prepared/);
  assert.equal(p.ids.prepare.disabled,false);assert.equal(p.timers.size,0);assert.equal(next.listeners.size,0);
});
test('failed worker update does not claim readiness from old active worker and permits retry',async()=>{
  const next=offlineWorker();let attempts=0;
  const p=phonePage(undefined,{register:async()=>{attempts++;return {active:offlineWorker('activated'),installing:attempts===1?next:null};}});
  await settle();next.change('redundant');await settle();assert.match(p.ids['offline-status'].textContent,/failed/);
  assert.equal(next.listeners.size,0);await p.ids.prepare.fire('click');assert.match(p.ids['offline-status'].textContent,/shell prepared/);
});
test('registration timeout releases controls and ignores late resolution',async()=>{
  let resolve;const worker=offlineWorker();
  const p=phonePage(undefined,{register:()=>new Promise(r=>resolve=r)});
  [...p.timers.values()][0]();await settle();assert.equal(p.ids.prepare.disabled,false);assert.match(p.ids['offline-status'].textContent,/failed/);
  resolve({installing:worker});await settle();assert.equal(worker.listeners.size,0);assert.match(p.ids['offline-status'].textContent,/failed/);
});
test('worker activation timeout removes state listeners and does not overwrite a retry',async()=>{
  const worker=offlineWorker();let attempts=0;
  const p=phonePage(undefined,{register:async()=>({installing:++attempts===1?worker:offlineWorker('activated')})});
  await settle();[...p.timers.values()][0]();await settle();assert.equal(worker.listeners.size,0);
  await p.ids.prepare.fire('click');worker.change('activated');await settle();assert.match(p.ids['offline-status'].textContent,/shell prepared/);
});
test('clipboard success or failure from a prior result cannot label a rebuilt result',async()=>{
  for(const fail of [false,true]){
    let resolve,reject;const p=phonePage(()=>new Promise((a,b)=>{resolve=a;reject=b;}));
    p.inputs[0].checked=true;p.ids.guide.fire('submit');const pending=p.ids.copy.fire('click');
    p.inputs[0].checked=false;p.inputs[1].checked=true;p.ids.guide.fire('submit');
    if(fail)reject(new Error('denied'));else resolve();await pending;
    assert.equal(p.ids.result.hidden,false);assert.equal(p.ids['copy-status'].textContent,'');assert.match(p.ids.actions.textContent,/Keep account access private/);
  }
});
test('offline readiness requires exact shell version and a complete cache',async()=>{
  for(const status of [{cache:'trustlens-pocket-v3',ready:true},{cache:'trustlens-pocket-v35',ready:false}]){
    const worker=offlineWorker('activated');worker.postMessage=(message,ports)=>{assert.equal(message.type,'POCKET_STATUS');ports[0].postMessage(status);};
    const p=phonePage(undefined,{register:async()=>({active:worker})});await settle();
    assert.match(p.ids['offline-status'].textContent,status.ready?/different companion version/:/failed/);assert.equal(p.ids['reload-companion'].hidden,!status.ready);assert.equal(p.ids.prepare.disabled,false);assert.equal(p.timers.size,0);
  }
});
test('offline status handshake is bounded and a missing reply never claims readiness',async()=>{
  const worker=offlineWorker('activated');worker.postMessage=()=>{};
  const p=phonePage(undefined,{register:async()=>({active:worker})});await settle();
  assert.equal(p.ids.prepare.disabled,true);[...p.timers.values()][0]();await settle();
  assert.match(p.ids['offline-status'].textContent,/failed/);assert.equal(p.ids.prepare.disabled,false);
});


test('Prepare explicitly checks for updates and retains a verified cached shell when offline',async()=>{
  for(const offline of [false,true]){
    let updates=0;const worker=offlineWorker('activated');
    const p=phonePage(undefined,{register:async()=>({active:worker,update:async()=>{updates++;if(offline)throw new Error('server stopped');}})});
    await settle();assert.equal(updates,1);assert.match(p.ids['offline-status'].textContent,/shell prepared/);assert.equal(p.ids['reload-companion'].hidden,true);
  }
});


test('installed app shortcuts open only known fixed panels and focus their summaries',()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.webmanifest'),'utf8'));
  assert.deepEqual(manifest.shortcuts.map(item=>item.url),['/phone/#recovery','/phone/#practice']);
  for(const id of ['recovery','practice']){const p=phonePage(undefined,undefined,'#'+id);assert.equal(p.ids[id].open,true);assert.equal(p.document.activeElement,p.ids[id].strong);assert.equal(p.ids.message.value,'');}
  const p=phonePage(undefined,undefined,'#untrusted-value');assert.equal(p.ids.recovery.open,undefined);assert.equal(p.ids.practice.open,undefined);
});


test('phone navigation reopens a manually closed panel even when its hash is unchanged',()=>{
  for(const id of ['recovery','practice']){const p=phonePage(undefined,undefined,'#'+id);p.ids[id].open=false;let prevented=false;p.ids['nav-'+id].fire('click',{preventDefault:()=>{prevented=true;}});assert.equal(prevented,true);assert.equal(p.ids[id].open,true);assert.equal(p.document.activeElement,p.ids[id].strong);}
  const p=phonePage(undefined,undefined,'#android');assert.equal(p.ids.android.open,true);p.ids['nav-review'].fire('click');assert.equal(p.document.activeElement,p.ids.message);
});
