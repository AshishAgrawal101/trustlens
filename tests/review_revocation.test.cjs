const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/verification-plan.js'),'utf8'),context);");
harness=harness.replace('async demo(name)',"routes:all.filter(e=>Object.hasOwn(e.dataset,'route')),async demo(name)");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
async function extracted(mode){
  const x=fixture.setup();await x.mode(mode);await x.file();
  x.state.fetch=async()=>({ok:true,json:async()=>({text:'Constructed request: send a code.',notice:'Review every word.',review_required:true})});
  await x.submit();x.ids.reviewed.checked=true;await x.ids.reviewed.fire('change');
  x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});return x;
}
function retained(x){
  assert.equal(x.ids.content.value,'Constructed request: send a code.');
  assert.equal(x.ids['preview-wrap'].hidden,false);assert.equal(x.ids.preview.src,'blob:fixture');
  assert.equal(x.revoked.length,0);assert.equal(x.ids['ocr-review'].hidden,false);assert.equal(x.ids.reviewed.required,true);
}
async function noExports(x){
  const copied=x.clipboard.length,blobs=x.blobs.length,prints=x.state.prints||0;
  for(const id of ['copy','download','print','manual-copy','manual-download','verification-copy','verification-download'])await x.ids[id].fire('click');
  assert.equal(x.clipboard.length,copied);assert.equal(x.blobs.length,blobs);assert.equal(x.state.prints||0,prints);
}
for(const mode of ['screenshot','qr']){
  test(mode+' withdrawing review clears completed output and all export/plan state but retains the draft and original',async()=>{
    const x=await extracted(mode);await x.submit();
    await x.routes[0].fire('click');x.topics[0].checked=true;await x.ids['manual-form'].fire('submit');
    assert.equal(x.ids.result.hidden,false);assert.equal(x.ids['verification-choice'].hidden,false);assert.equal(x.ids['manual-result'].hidden,false);
    x.ids.reviewed.checked=false;await x.ids.reviewed.fire('change');
    assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.ids['coverage-checked'].textContent,'');
    assert.equal(x.ids['verification-choice'].hidden,true);assert.equal(x.ids['verification-steps'].textContent,'');assert.equal(x.ids['manual-result'].hidden,true);assert.equal(x.ids['manual-steps'].textContent,'');
    retained(x);await noExports(x);
    const count=x.requests.length;await x.submit();assert.equal(x.requests.length,count);assert.match(x.ids.error.textContent,/confirm/);
    x.ids.reviewed.checked=true;await x.ids.reviewed.fire('change');assert.equal(x.requests.length,count);assert.equal(x.ids.result.hidden,true);
    await x.submit();assert.equal(x.ids.result.hidden,false);assert.equal(x.requests.at(-1).url,'/api/analyze/text');
  });
  test(mode+' withdrawing review aborts a pending check and rejects its late success even after rechecking',async()=>{
    const x=await extracted(mode);let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);
    const pending=x.submit(),request=x.requests.at(-1);assert.equal(x.ids.loading.hidden,false);
    x.ids.reviewed.checked=false;await x.ids.reviewed.fire('change');assert.equal(request.options.signal.aborted,true);
    assert.equal(x.ids.loading.hidden,true);assert.equal(x.ids.submit.disabled,false);retained(x);
    x.ids.reviewed.checked=true;await x.ids.reviewed.fire('change');const count=x.requests.length;
    resolve({ok:true,json:async()=>fixture.report()});await pending;
    assert.equal(x.requests.length,count);assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');await noExports(x);
  });
  test(mode+' late clipboard completion cannot restore feedback after review is withdrawn',async()=>{
    const x=await extracted(mode);await x.submit();let finish;x.state.writeText=()=>new Promise(resolve=>finish=resolve);
    const copying=x.ids.copy.fire('click');x.ids.reviewed.checked=false;await x.ids.reviewed.fire('change');finish();await copying;
    assert.equal(x.ids['copy-status'].textContent,'');assert.equal(x.ids.result.hidden,true);retained(x);
  });
}
