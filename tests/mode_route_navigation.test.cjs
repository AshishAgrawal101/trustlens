const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const base=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
function setup(hash=''){
  let harness=base.replace('setAttribute(k,v){this.attributes[k]=v;}','setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k];}');
  harness=harness.replace('window:{innerWidth:1200,',`window:{location:{hash:${JSON.stringify(hash)}},innerWidth:1200,`);
  harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);for(const script of ['primary-flow.js','mode-route.js'])vm.runInContext(fs.readFileSync(path.join(root,'static',script),'utf8'),context);");
  harness=harness.replace('return {ids,state,','return {async route(hash){context.window.location.hash=hash;for(const fn of windowEvents.hashchange||[])await fn({});},ids,state,');
  const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);return fixture.setup();
}
const current=x=>x.document.querySelectorAll('[data-mode]').find(b=>b.getAttribute('aria-pressed')==='true').dataset.mode;
test('same-document tool fragments select all seven modes through the normal controller without requests',async()=>{
  const x=setup();for(const mode of ['email','url','call','screenshot','qr','image','text']){
    await x.route('#check='+mode);assert.equal(current(x),mode);assert.equal(x.requests.length,0);assert.equal(x.ids.content.value,'');assert.equal(x.document.activeElement,x.ids.workspace);assert.equal(x.ids.workspace.scrollOptions.block,'start');
    assert.equal(x.ids['visual-modes'].open,['url','email','call','qr','image'].includes(mode));
  }
});
test('same-mode explicit route retains a completed result draft and exports without resubmitting or clicking',async()=>{
  const x=setup('#check=email');x.ids.content.value='Constructed private draft';await x.submit();const before=x.ids['print-summary'].textContent;
  const button=x.document.querySelectorAll('[data-mode]').find(b=>b.dataset.mode==='email');let clicks=0;button.addEventListener('click',()=>clicks++);
  await x.route('#check=email');assert.equal(clicks,0);assert.equal(x.requests.length,1);assert.equal(x.ids.result.hidden,false);assert.equal(x.ids.content.value,'Constructed private draft');assert.equal(x.ids['print-summary'].textContent,before);assert.equal(x.document.activeElement,x.ids.workspace);
});
test('same-mode route preserves pending work while a different valid mode aborts it and rejects stale output',async()=>{
  const x=setup();x.ids.content.value='Constructed private draft';let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit(),request=x.requests[0];
  await x.route('#check=text');assert.equal(request.options.signal.aborted,false);assert.equal(x.ids.content.value,'Constructed private draft');
  await x.route('#check=email');assert.equal(request.options.signal.aborted,true);assert.equal(current(x),'email');assert.equal(x.ids.content.value,'');assert.equal(x.ids.loading.hidden,true);
  resolve({ok:true,json:async()=>({kind:'text',risk_level:'low',summary:'Old',evidence:[],actions:[],limitations:[],share_summary:'Old export'})});await pending;assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.requests.length,1);
});
test('unknown partial encoded and input-bearing fragments leave drafts mode focus and requests untouched',async()=>{
  const x=setup('#check=call');x.ids.content.value='Constructed private draft';x.ids.content.focus();
  for(const hash of ['','#workspace','#check=admin','#check=email&text=PRIVATE','#check=%65mail','#check=Email','#check=image?file=PRIVATE','#check=email\n']){
    await x.route(hash);assert.equal(current(x),'call');assert.equal(x.ids.content.value,'Constructed private draft');assert.equal(x.document.activeElement,x.ids.content);assert.equal(x.requests.length,0);
  }
});
