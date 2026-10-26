// New dashboard controls use the existing DOM double; visual review belongs in the real browser.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
test('Ctrl/Cmd Enter checks native validity and does not submit twice while pending',async()=>{
  const x=fixture.setup(),form=x.ids['check-form'];form.valid=false;let prevented=0;
  await form.fire('keydown',{key:'Enter',ctrlKey:true,preventDefault(){prevented++;}});
  assert.equal(form.validityChecks,1);assert.equal(prevented,1);assert.equal(x.requests.length,0);
  form.valid=true;x.ids.content.value='Please verify independently.';await form.fire('keydown',{key:'Enter',metaKey:true});assert.equal(x.requests.length,1);
  let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=form.fire('keydown',{key:'Enter',ctrlKey:true});
  await form.fire('keydown',{key:'Enter',ctrlKey:true});assert.equal(x.requests.length,2);resolve({ok:true,json:async()=>fixture.report()});await pending;
});
test('ordinary Enter, composition and alternate modifier shortcuts leave typing alone',async()=>{
  const x=fixture.setup();
  for(const event of [{key:'Enter'},{key:'Enter',ctrlKey:true,isComposing:true},{key:'Enter',ctrlKey:true,altKey:true},{key:'Enter',metaKey:true,shiftKey:true},{key:'x',ctrlKey:true}]){
    await x.ids['check-form'].fire('keydown',{...event,preventDefault(){assert.fail('Typing should be left alone');}});
  }
  assert.equal(x.requests.length,0);assert.equal(x.ids['check-form'].validityChecks,undefined);
});
test('character count follows typing, examples, mode limits, extraction and Clear',async()=>{
  const x=fixture.setup();x.ids.content.value='Some text';await x.ids.content.fire('input');assert.equal(x.ids['input-count'].textContent,'9 / 30,000 characters');
  await x.demo('code');assert.match(x.ids['input-count'].textContent,/^\d[\d,]* \/ 30,000 characters$/);assert.doesNotMatch(x.ids['input-count'].textContent,/^9 /);
  await x.mode('url');assert.equal(x.ids['input-count'].textContent,'0 / 4,096 characters');await x.ids.example.fire('click');assert.doesNotMatch(x.ids['input-count'].textContent,/^0 /);
  await x.mode('qr');assert.equal(x.ids['input-meta'].hidden,true);await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'https://example.org',review_required:true,notice:'Review this.'})});await x.submit();
  assert.equal(x.ids['input-meta'].hidden,false);assert.equal(x.ids['input-count'].textContent,'19 / 30,000 characters');await x.ids.clear.fire('click');assert.equal(x.ids['input-count'].textContent,'0 / 30,000 characters');
});
test('Cancel preserves the input and chosen file while rejecting a late response',async()=>{
  const x=fixture.setup();x.ids.content.value='PRIVATE DRAFT';let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();
  await x.ids.cancel.fire('click');assert.equal(x.ids.content.value,'PRIVATE DRAFT');assert.equal(x.ids.submit.disabled,false);assert.equal(x.ids.loading.hidden,true);assert.equal(x.document.activeElement,x.ids.content);
  assert.equal(x.requests[0].options.signal.aborted,true);resolve({ok:true,json:async()=>fixture.report()});await pending;assert.equal(x.ids.result.hidden,true);
  await x.mode('qr');await x.file();x.state.fetch=()=>new Promise(r=>resolve=r);const extraction=x.submit();await x.ids.cancel.fire('click');
  assert.equal(x.ids['file-name'].textContent,'demo.png');assert.equal(x.ids['preview-wrap'].hidden,false);assert.equal(x.document.activeElement,x.ids.file);
  resolve({ok:true,json:async()=>({text:'PRIVATE QR',review_required:true})});await extraction;assert.equal(x.ids.content.value,'');assert.equal(x.ids['ocr-review'].hidden,true);
});
test('visual tool selection opens its disclosure and returning to communication collapses it',async()=>{
  const x=fixture.setup();for(const mode of ['screenshot','image','qr']){await x.mode(mode);assert.equal(x.ids['visual-modes'].open,true);}
  await x.mode('text');assert.equal(x.ids['visual-modes'].open,false);assert.equal(x.requests.length,0);
});
