// Offline controller tests with a minimal DOM double. These do not verify browser rendering.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'static/index.template.html'),'utf8');
const source=fs.readFileSync(path.join(root,'static/app.js'),'utf8');

function setup(){
  let document;
  class Element {
    constructor(tag='div'){this.tagName=tag;this.children=[];this.events={};this.dataset={};this.attributes={};this.hidden=false;this.value='';this.files=[];this.checked=false;this.required=false;this.open=false;this._text='';}
    get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
    set textContent(s){this._text=String(s);this.children=[];}
    append(...children){this.children.push(...children);}
    replaceChildren(...children){this._text='';this.children=children;}
    addEventListener(name,fn){(this.events[name]??=[]).push(fn);}
    async fire(name,init={}){await Promise.all((this.events[name]||[]).map(fn=>fn({preventDefault(){},...init})));}
    setCustomValidity(message){this.validationMessage=String(message);this.validity??={};this.validity.customError=message!=='';}
    reportValidity(){this.validityChecks=(this.validityChecks||0)+1;return this.valid!==false;}
    requestSubmit(){return this.fire('submit');}
    setAttribute(k,v){this.attributes[k]=v;}
    removeAttribute(k){delete this.attributes[k];if(k==='src')delete this.src;}
    focus(){document.activeElement=this;}
    scrollIntoView(options){this.scrollOptions=options;}
    showModal(){this.open=true;}
    close(){this.open=false;this.fire('close');}
    click(){return this.fire('click');}
    remove(){}
    get firstElementChild(){return this.children[0];}
  }
  const ids={},all=[];
  for(const match of html.matchAll(/<(\w+)\b([^>]*)>/g)){
    const [,tag,attrs]=match,e=new Element(tag);
    for(const a of attrs.matchAll(/([\w-]+)="([^"]*)"/g)){
      const [,k,v]=a;e.attributes[k]=v;
      if(k==='id')ids[v]=e;
      if(k.startsWith('data-'))e.dataset[k.slice(5)]=v;
    }
    e.hidden=/\bhidden\b/.test(attrs);e.required=/\brequired\b/.test(attrs);
    if(/\bdata-recovery\b/.test(attrs))e.dataset.recovery='';
    all.push(e);
  }
  document={body:new Element('body'),activeElement:null,getElementById(id){assert.ok(ids[id],`Missing element ${id}`);return ids[id];},createElement:tag=>new Element(tag),createTextNode(text){const e=new Element('#text');e.textContent=text;return e;},querySelectorAll(selector){const key=selector.slice(6,-1);return all.filter(e=>Object.hasOwn(e.dataset,key));}};
  const windowEvents={};
  const timers=new Map(),requests=[],clipboard=[],blobs=[],revoked=[];let nextTimer=0;
  const state={fetch:async()=>({ok:true,json:async()=>report()}),clipboardError:false};
  const context=vm.createContext({PocketGuide:require(path.join(root,'static/phone/guide.js')),document,window:{innerWidth:1200,addEventListener(name,fn){(windowEvents[name]??=[]).push(fn);},print(){state.prints=(state.prints||0)+1;}},navigator:{clipboard:{async writeText(text){if(state.writeText)return state.writeText(text);if(state.clipboardError)throw new Error();clipboard.push(text);}}},AbortController,AbortSignal,Blob,
    URL:{createObjectURL(blob){blobs.push(blob);return 'blob:fixture';},revokeObjectURL(url){revoked.push(url);}},FormData:class{append(){}},
    setTimeout(fn){timers.set(++nextTimer,fn);return nextTimer;},clearTimeout(id){timers.delete(id);},
    async fetch(url,options){requests.push({url,options});return state.fetch(url,options);}});
  vm.runInContext(source,context);
  if(ids['practice-dialog'])vm.runInContext(fs.readFileSync(path.join(root,'static/learning-practice.js'),'utf8'),context);
  return {ids,state,requests,clipboard,timers,document,blobs,revoked,windowEvents,topics:all.filter(e=>Object.hasOwn(e.dataset,'topic')),
    async demo(name){await all.find(e=>e.dataset.demo===name).fire('click');},
    async mode(name){await all.find(e=>e.dataset.mode===name).fire('click');},
    async submit(){await ids['check-form'].fire('submit');},
    async file(){ids.file.files=[{type:'image/png',size:200,name:'demo.png'}];await ids.file.fire('change');},
    async recovery(){await all.find(e=>Object.hasOwn(e.dataset,'recovery')).fire('click');}};
}
function report(){return {kind:'text',risk_level:'high',summary:'Pause.',evidence:[{weight:.8,evidence_class:'inferred',title:'Code request',detail:'Constructed text',source:'Test'}],actions:[{title:'Verify independently',detail:'Use a known contact.'}],limitations:['Not proof.'],share_summary:'Input-free summary'};}

test('screenshot requires a separate reviewed-text submission and clears safely',async()=>{
  const x=setup();await x.mode('screenshot');await x.file();
  x.state.fetch=async()=>({ok:true,json:async()=>({text:'Send your verification code.',notice:'Review first.'})});
  await x.submit();assert.equal(x.requests.length,1);assert.equal(x.requests[0].url,'/api/extract/screenshot');
  assert.equal(x.ids.content.hidden,false);assert.equal(x.ids['ocr-review'].hidden,false);assert.equal(x.ids.reviewed.required,true);
  await x.submit();assert.equal(x.requests.length,1);assert.match(x.ids.error.textContent,/confirm/);
  x.ids.reviewed.checked=true;x.state.fetch=async()=>({ok:true,json:async()=>report()});await x.submit();
  assert.equal(x.requests[1].url,'/api/analyze/text');assert.equal(x.ids.result.hidden,false);assert.equal(x.ids['result-recovery'].hidden,false);
  await x.ids.clear.fire('click');assert.equal(x.ids.content.value,'');assert.equal(x.ids.reviewed.required,false);assert.equal(x.ids['result-recovery'].hidden,true);
});
test('blank OCR invites manual text and editing requires review again',async()=>{
  const x=setup();await x.mode('screenshot');await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'',notice:'Review the recognized text.',review_required:true})});await x.submit();
  assert.match(x.ids['ocr-notice'].textContent,/No readable text/);assert.equal(x.ids.content.required,true);
  x.ids.reviewed.checked=true;x.ids.content.value='A correction';await x.ids.content.fire('input');assert.equal(x.ids.reviewed.checked,false);
  await x.mode('url');assert.equal(x.ids.reviewed.required,false);assert.equal(x.ids['ocr-review'].hidden,true);assert.equal(x.ids.file.required,false);
});
test('response after Clear cannot repopulate private content or results',async()=>{
  const x=setup();let resolve;
  x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();await x.ids.clear.fire('click');
  resolve({ok:true,json:async()=>report()});await pending;assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['empty'].hidden,false);
});
test('failed requests and explicit timeout recover controls',async()=>{
  const x=setup();x.state.fetch=async()=>{throw new Error('Connection failed');};await x.submit();assert.equal(x.ids.error.hidden,false);assert.equal(x.ids.submit.disabled,false);
  x.state.fetch=(_,opts)=>new Promise((resolve,reject)=>opts.signal.addEventListener('abort',()=>{const e=new Error();e.name='AbortError';reject(e);}));
  const pending=x.submit();[...x.timers.values()][0]();await pending;assert.match(x.ids.error.textContent,/too long/);assert.equal(x.ids.submit.disabled,false);
});
test('clipboard denial is actionable and copies only report summary',async()=>{
  const x=setup();await x.submit();x.state.clipboardError=true;await x.ids.copy.fire('click');assert.match(x.ids['copy-status'].textContent,/Download/);
  x.state.clipboardError=false;await x.ids.copy.fire('click');assert.deepEqual(x.clipboard,['Input-free summary']);
});
test('recovery is available without analysis and exports a fixed checklist',async()=>{
  const x=setup();x.state.fetch=async()=>({ok:true,json:async()=>({plans:[{id:'paid',label:'I sent money',title:'Contact your provider',steps:['Use a known number.','Keep records.']}]})});
  await x.recovery();assert.equal(x.requests[0].url,'/api/recovery');assert.equal(x.requests[0].options.signal.aborted,false);
  await x.ids['recovery-options'].children[0].fire('click');assert.equal(x.ids['recovery-plan'].hidden,false);await x.ids['recovery-copy'].fire('click');assert.match(x.clipboard[0],/Recovery is not guaranteed/);
  await x.ids['recovery-dialog'].close();await x.recovery();assert.equal(x.ids['recovery-plan'].hidden,true);
});
test('invalid image selection clears the preview and reports its limit',async()=>{
  const x=setup();await x.mode('screenshot');x.ids.file.files=[{type:'text/html',size:20}];await x.ids.file.fire('change');assert.equal(x.ids.error.hidden,false);assert.equal(x.ids['preview-wrap'].hidden,true);assert.equal(x.requests.length,0);
});

test('demo choices change mode but never submit without Check',async()=>{
  const x=setup();await x.mode('screenshot');await x.file();
  await x.demo('link');assert.match(x.ids.content.value,/Content-Type: text\/html/);assert.match(x.ids.content.value,/href=/);
  assert.equal(x.ids['example-note'].hidden,false);assert.equal(x.ids.file.required,false);assert.equal(x.ids['preview-wrap'].hidden,true);assert.equal(x.requests.length,0);
  await x.submit();assert.equal(x.requests[0].url,'/api/analyze/email');
  await x.demo('ordinary');assert.match(x.ids.content.value,/Do not share/);assert.equal(x.ids.result.hidden,true);assert.equal(x.requests.length,1);
  await x.demo('code');assert.match(x.ids.content.value,/Send us the verification code/);assert.equal(x.document.activeElement,x.ids.content);
});

test('results distinguish concerns, observations and unknowns without hiding evidence',async()=>{
  const x=setup();const data=report();data.evidence=[
    {weight:0,evidence_class:'unknown',title:'Sender',detail:'Unverified',source:'Pasted'},
    {weight:0,evidence_class:'verified',title:'Host',detail:'example.org',source:'Parsed'},
    ...data.evidence];
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.deepEqual(x.ids.evidence.children.map(g=>g.children[0].textContent),['Warning signs to review','Observed facts','Still unknown']);
  assert.equal(x.ids.evidence.children.reduce((n,g)=>n+g.children.length-1,0),3);
  assert.equal(x.ids['result-safety'].hidden,false);assert.match(x.ids.actions.textContent,/Verify independently/);
  assert.ok(html.indexOf('id="actions"')<html.indexOf('id="evidence"'));
  data.kind='image';data.content_credentials={status:'absent',detail:'No manifest'};await x.submit();
  assert.equal(x.ids['result-safety'].hidden,true);assert.equal(x.ids['result-recovery'].hidden,true);
  assert.equal(x.ids.evidence.children[0].children[0].textContent,'Image and provenance evidence');
});

test('Clear erases private result nodes as well as input, and disables stale exports',async()=>{
  const x=setup();const data=report();data.summary='PRIVATE_SUMMARY';data.evidence[0].detail='PRIVATE_QUOTE';
  data.content_credentials={status:'untrusted',detail:'PRIVATE_SIGNER'};
  x.ids.content.value='PRIVATE_INPUT';x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.match(x.ids.evidence.textContent,/PRIVATE_QUOTE/);await x.ids.clear.fire('click');
  for(const id of ['content','result-summary','evidence','credentials','actions','limits'])assert.equal(id==='content'?x.ids[id].value:x.ids[id].textContent,'');
  await x.ids.copy.fire('click');await x.ids.download.fire('click');assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);
});

test('download contains only the safe summary and releases its temporary URL',async()=>{
  const x=setup();x.ids.content.value='PRIVATE_INPUT';await x.submit();await x.ids.download.fire('click');
  assert.equal(await x.blobs[0].text(),'Input-free summary');
  assert.equal(x.document.body.children[0].download,'trustlens-safe-summary.txt');
  [...x.timers.values()][0]();assert.deepEqual(x.revoked,['blob:fixture']);
});

test('reselecting the active mode preserves drafts, results and active requests',async()=>{
  const x=setup();x.ids.content.value='Constructed draft';await x.mode('text');
  assert.equal(x.ids.content.value,'Constructed draft');
  let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();
  await x.mode('text');assert.equal(x.requests[0].options.signal.aborted,false);
  resolve({ok:true,json:async()=>report()});await pending;await x.mode('text');
  assert.equal(x.ids.result.hidden,false);assert.equal(x.ids.content.value,'Constructed draft');
  await x.mode('call');assert.equal(x.ids.content.value,'');assert.equal(x.ids.result.hidden,true);
});

test('reselecting Screenshot preserves corrected text and its review state',async()=>{
  const x=setup();await x.mode('screenshot');await x.file();
  x.state.fetch=async()=>({ok:true,json:async()=>({text:'Recognized text',notice:'Review first.'})});await x.submit();
  x.ids.content.value='Corrected text';await x.ids.content.fire('input');x.ids.reviewed.checked=true;
  await x.mode('screenshot');assert.equal(x.ids.content.value,'Corrected text');
  assert.equal(x.ids.reviewed.checked,true);assert.equal(x.ids['ocr-review'].hidden,false);
  assert.equal(x.ids['preview-wrap'].hidden,false);assert.equal(x.ids['file-name'].textContent,'demo.png');
});

test('same-mode demo replacement clears results and rejects the earlier response',async()=>{
  const x=setup();await x.demo('code');await x.submit();assert.equal(x.ids.result.hidden,false);
  await x.demo('ordinary');assert.equal(x.ids.result.hidden,true);assert.equal(x.requests.length,1);
  let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();
  await x.demo('code');assert.equal(x.requests[1].options.signal.aborted,true);
  resolve({ok:true,json:async()=>report()});await pending;
  assert.equal(x.ids.result.hidden,true);assert.match(x.ids.content.value,/Send us the verification code/);
});

test('preview cleanup erases filenames on Clear, mode changes and invalid replacement',async()=>{
  const x=setup();await x.mode('image');await x.file();await x.ids.clear.fire('click');
  assert.equal(x.ids['file-name'].textContent,'');assert.equal(x.ids.file.value,'');
  assert.equal(x.ids.preview.src,undefined);assert.equal(x.ids['preview-wrap'].hidden,true);
  assert.deepEqual(x.revoked,['blob:fixture']);
  await x.file();await x.mode('text');assert.equal(x.ids['file-name'].textContent,'');
  await x.mode('image');await x.file();
  x.ids.file.files=[{type:'text/html',size:20,name:'INVALID-FILENAME.html'}];await x.ids.file.fire('change');
  assert.equal(x.ids['file-name'].textContent,'');assert.equal(x.ids['preview-wrap'].hidden,true);
  await x.file();assert.equal(x.ids['file-name'].textContent,'demo.png');
});

test('image heading distinguishes unavailable checks from usable partial results',async()=>{
  const x=setup();await x.mode('image');await x.file();
  for(const [status,modelRan,title] of [
    ['unavailable',false,'Image checks unavailable'],
    ['absent',false,'Credentials check complete'],
    ['unavailable',true,'This image looks AI-generated'],
    ['verified',false,'This image looks AI-generated']]){
    const data=report();data.kind='image';data.model_ran=modelRan;data.content_credentials={status,detail:'Fixture status'};
    x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
    assert.equal(x.ids.verdict.textContent,title);assert.match(x.ids['verdict-tag'].textContent,/NOT A SCAM VERDICT/);
    assert.equal(x.ids['result-recovery'].hidden,true);
  }
});

test('incomplete email is explicit while retaining detected warnings and actions',async()=>{
  const x=setup();const data=report();data.kind='email';data.risk_level='low';
  data.evidence=[{id:'email:incomplete',weight:0,evidence_class:'unknown',title:'Incomplete email',detail:'Body could not be decoded.',source:'Email parser'}];
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');
  assert.equal(x.ids.verdict.textContent,'This email needs a manual check.');
  assert.match(x.ids.evidence.textContent,/Body could not be decoded/);
  data.risk_level='high';data.evidence.push(...report().evidence);await x.submit();
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');
  assert.equal(x.ids['verdict-tag'].className,'verdict-tag high');
  assert.match(x.ids.evidence.textContent,/Warning signs to review.*Code request/);
  assert.match(x.ids.actions.textContent,/Verify independently/);
});
