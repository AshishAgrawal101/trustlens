// Reuse the existing controller DOM double, including browser lifecycle and clipboard hooks.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
function lifecycle(x,type,persisted=false){for(const fn of x.windowEvents[type])fn({persisted});}
const plans={plans:[{id:'paid',label:'I sent money',title:'Contact your provider',steps:['Use a known number.','Keep records.']}]};
async function recovery(x){x.state.fetch=async()=>({ok:true,json:async()=>plans});await x.recovery();await x.ids['recovery-options'].children[0].fire('click');}
test('ordinary pageshow preserves the draft and report; persisted Back clears all private output',async()=>{
  const x=fixture.setup();x.ids.content.value='PRIVATE MESSAGE';const data=fixture.report();data.evidence[0].detail='PRIVATE EVIDENCE';
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();lifecycle(x,'pageshow',false);
  assert.equal(x.ids.content.value,'PRIVATE MESSAGE');assert.equal(x.ids.result.hidden,false);
  x.ids['known-website'].value='private.test';lifecycle(x,'pageshow',true);
  for(const id of ['content','known-website'])assert.equal(x.ids[id].value,'');
  for(const id of ['evidence','result-summary','credentials','actions','limits','print-summary','copy-status'])assert.equal(x.ids[id].textContent,'');
  assert.equal(x.ids.result.hidden,true);await x.ids.copy.fire('click');await x.ids.download.fire('click');await x.ids.print.fire('click');
  assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);assert.equal(x.state.prints,undefined);
});
test('page exit revokes previews and clears file inputs, OCR review and filenames',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();x.ids.content.value='PRIVATE OCR';x.ids['ocr-notice'].textContent='PRIVATE OCR NOTICE';x.ids.reviewed.checked=true;
  lifecycle(x,'pagehide');assert.equal(x.ids.file.value,'');assert.equal(x.ids['file-name'].textContent,'');assert.equal(x.ids['preview-wrap'].hidden,true);
  assert.equal(x.ids.preview.src,undefined);assert.deepEqual(Array.from(x.revoked),['blob:fixture']);assert.equal(x.ids.content.value,'');assert.equal(x.ids.reviewed.checked,false);assert.equal(x.ids['ocr-notice'].textContent,'');
  await x.mode('email');x.ids['email-file'].files=[{name:'PRIVATE.eml',size:100}];await x.ids['email-file'].fire('change');
  lifecycle(x,'pagehide');assert.equal(x.ids['email-file'].value,'');assert.equal(x.ids['email-file-name'].textContent,'');assert.equal(x.ids.content.hidden,false);
});
test('page exit aborts a pending content check and late results cannot return on Back',async()=>{
  const x=fixture.setup();let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();lifecycle(x,'pagehide');
  assert.equal(x.requests[0].options.signal.aborted,true);resolve({ok:true,json:async()=>fixture.report()});await pending;
  lifecycle(x,'pageshow',true);assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.ids.submit.disabled,false);
});
test('page exit erases recovery selection and prevents delayed checklist loading from reopening it',async()=>{
  const x=fixture.setup();await recovery(x);lifecycle(x,'pagehide');
  assert.equal(x.ids['recovery-dialog'].open,false);assert.equal(x.ids['recovery-plan'].hidden,true);
  for(const id of ['recovery-options','recovery-heading','recovery-steps','recovery-status','recovery-copy-status'])assert.equal(x.ids[id].textContent,'');
  await x.ids['recovery-copy'].fire('click');assert.equal(x.clipboard.length,0);
  const y=fixture.setup();let resolve;y.state.fetch=()=>new Promise(r=>resolve=r);const pending=y.recovery();lifecycle(y,'pagehide');
  resolve({ok:true,json:async()=>plans});await pending;assert.equal(y.ids['recovery-options'].children.length,0);assert.equal(y.ids['recovery-dialog'].open,false);assert.equal(y.ids['recovery-status'].textContent,'');
});
test('main clipboard prompt times out with download fallback and late completion cannot label a new report',async()=>{
  const x=fixture.setup();await x.submit();x.state.writeText=()=>new Promise(()=>{});const pending=x.ids.copy.fire('click');[...x.timers.values()][0]();await pending;
  assert.match(x.ids['copy-status'].textContent,/Download/);assert.equal(x.timers.size,0);
  let resolve;x.state.writeText=()=>new Promise(r=>resolve=r);const copying=x.ids.copy.fire('click');await x.submit();resolve();await copying;
  assert.equal(x.ids.result.hidden,false);assert.equal(x.ids['copy-status'].textContent,'');
});
test('recovery clipboard timeout offers text fallback; reselecting the same plan invalidates old status',async()=>{
  const x=fixture.setup();await recovery(x);x.state.writeText=()=>new Promise(()=>{});const pending=x.ids['recovery-copy'].fire('click');[...x.timers.values()][0]();await pending;
  assert.match(x.ids['recovery-copy-status'].textContent,/select and copy/);
  let reject;x.state.writeText=()=>new Promise((resolve,r)=>reject=r);const copying=x.ids['recovery-copy'].fire('click');await x.ids['recovery-options'].children[0].fire('click');
  reject(new Error('denied'));await copying;assert.equal(x.ids['recovery-copy-status'].textContent,'');
});
test('page exit invalidates both pending clipboard statuses',async()=>{
  const x=fixture.setup();await x.submit();await recovery(x);const resolvers=[];x.state.writeText=()=>new Promise(r=>resolvers.push(r));
  const main=x.ids.copy.fire('click'),help=x.ids['recovery-copy'].fire('click');lifecycle(x,'pagehide');resolvers.forEach(resolve=>resolve());await Promise.all([main,help]);
  assert.equal(x.ids['copy-status'].textContent,'');assert.equal(x.ids['recovery-copy-status'].textContent,'');assert.equal(x.timers.size,0);
});

