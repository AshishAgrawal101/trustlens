// Reuse the existing offline DOM double; rendering is checked separately by the coordinator.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);

test('availability is explicit, reports configuration only, and sends no private input',async()=>{
  const x=fixture.setup();x.ids.content.value='PRIVATE MESSAGE';
  assert.equal(x.requests.length,0);
  x.state.fetch=async()=>({ok:true,json:async()=>({message_rules:true,screenshot_ocr:{configured:true,detail:'Windows OCR'},image_detector:{configured:false,detail:'No model'},content_credentials:{configured:true,detail:'Local trust snapshot'}})});
  await x.ids['capability-refresh'].fire('click');
  assert.equal(x.requests[0].url,'/api/capabilities');assert.equal(x.requests[0].options.body,undefined);
  assert.match(x.ids['capability-list'].textContent,/runtime not verified/);
  assert.match(x.ids['capability-list'].textContent,/not configured/);
  assert.doesNotMatch(x.ids['capability-list'].textContent,/PRIVATE/);
  assert.equal(x.ids['capability-refresh'].disabled,false);
});
test('failed or malformed availability replaces stale configuration with unknown and permits retry',async()=>{
  const x=fixture.setup();x.state.fetch=async()=>({ok:true,json:async()=>({message_rules:true})});
  await x.ids['capability-refresh'].fire('click');assert.match(x.ids['capability-list'].textContent,/unknown/);
  x.state.fetch=async()=>{throw new TypeError('offline');};await x.ids['capability-refresh'].fire('click');
  assert.match(x.ids['capability-status'].textContent,/still try/);assert.equal(x.ids['capability-refresh'].disabled,false);
});
test('intake guidance distinguishes screenshot review from image origin',async()=>{
  const x=fixture.setup();await x.mode('image');assert.match(x.ids['mode-guide'].textContent,/cannot tell you/);
  await x.mode('screenshot');assert.match(x.ids['mode-guide'].textContent,/Two steps/);
  await x.mode('email');assert.match(x.ids['mode-guide'].textContent,/hidden HTML links/);
});
test('request failure focuses the actionable error and releases busy state',async()=>{
  const x=fixture.setup();let reject;
  x.state.fetch=()=>new Promise((resolve,r)=>reject=r);const pending=x.submit();
  assert.equal(x.ids['check-form'].attributes['aria-busy'],'true');
  reject(new TypeError('offline'));await pending;
  assert.equal(x.document.activeElement,x.ids.error);assert.equal(x.ids['check-form'].attributes['aria-busy'],'false');
  assert.match(x.ids.error.textContent,/offline/);assert.equal(x.ids.submit.disabled,false);
  await x.ids.clear.fire('click');assert.equal(x.ids.error.hidden,true);
});
test('phone companion is a visible normal link with honest scope',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');
  assert.match(html,/href="\/phone\/">Open phone companion/);
  assert.match(html,/Prepare Pocket while connected for offline use/);
  assert.match(html,/sharing stay manual; file analysis needs the desktop app/);
});

test('availability refresh restores disabled-button focus without taking it from another field',async()=>{
  const x=fixture.setup();let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);
  x.ids['capability-refresh'].focus();const first=x.ids['capability-refresh'].fire('click');
  x.document.activeElement=x.document.body;resolve({ok:false});await first;
  assert.equal(x.document.activeElement,x.ids['capability-refresh']);
  const second=x.ids['capability-refresh'].fire('click');x.ids.content.focus();resolve({ok:false});await second;
  assert.equal(x.document.activeElement,x.ids.content);
});

test('visual model results show the release caveat and restore communication safety wording',async()=>{
  const x=fixture.setup();const data=fixture.report();data.kind='image';data.model_ran=true;
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.equal(x.ids['result-safety'].hidden,false);assert.match(x.ids['result-safety'].textContent,/not passed release requirements/);
  data.model_ran=false;await x.submit();assert.equal(x.ids['result-safety'].hidden,true);
  data.kind='text';await x.submit();assert.match(x.ids['result-safety'].textContent,/no warning does not prove safety/);
});

test('unexamined links have an incomplete headline rather than no warning reassurance',async()=>{
  const x=fixture.setup();const data=fixture.report();data.risk_level='low';data.evidence=[{id:'analysis:links_incomplete',weight:0,evidence_class:'unknown',title:'Link review incomplete',detail:'9 found;8 inspected',source:'Bounded coverage'}];
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids.verdict.textContent,'Some links still need review.');
  data.risk_level='high';await x.submit();assert.equal(x.ids.verdict.textContent,'Pause; some links remain unchecked.');
});


