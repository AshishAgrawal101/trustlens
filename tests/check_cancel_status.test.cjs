const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
const ACK='Stopped waiting for this check. Your input is kept here. Local processing may continue.';
async function pending(mode,reviewed=false){
  const x=fixture.setup();await x.mode(mode);
  if(['screenshot','qr','image'].includes(mode))await x.file();else x.ids.content.value='Constructed private draft.';
  if(reviewed){x.state.fetch=async()=>({ok:true,json:async()=>({text:'Constructed reviewed draft.',notice:'Review first.',review_required:true})});await x.submit();x.ids.reviewed.checked=true;await x.ids.reviewed.fire('change');}
  let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const task=x.submit();return {x,task,resolve,request:x.requests.at(-1)};
}
for(const [mode,reviewed]of [['text',false],['screenshot',false],['qr',true],['image',false]])test(mode+(reviewed?' reviewed':'')+' cancel acknowledges dismissal retains input and rejects late completion',async()=>{
  const {x,task,resolve,request}=await pending(mode,reviewed),draft=x.ids.content.value,preview=x.ids.preview.src;
  await x.ids.cancel.fire('click');assert.equal(x.ids['check-status'].textContent,ACK);assert.equal(request.options.signal.aborted,true);
  assert.equal(x.ids.content.value,draft);assert.equal(x.ids.preview.src,preview);assert.equal(x.revoked.length,0);assert.equal(x.ids.reviewed.checked,reviewed);
  assert.equal(x.ids.result.hidden,true);assert.equal(x.ids.loading.hidden,true);assert.equal(x.ids.submit.disabled,false);assert.equal(x.ids['check-form'].attributes['aria-busy'],'false');
  assert.equal(x.document.activeElement,x.ids[mode==='text'||reviewed?'content':'file']);
  resolve({ok:true,json:async()=>fixture.report()});await task;assert.equal(x.ids['check-status'].textContent,ACK);assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,preview?1:0);
});
test('cancel acknowledgement clears on retry edits Clear mode change exit and persisted Back',async()=>{
  for(const action of ['retry','input','clear','mode','pagehide','pageshow']){
    const {x,task,resolve}=await pending('text');await x.ids.cancel.fire('click');assert.equal(x.ids['check-status'].textContent,ACK);
    if(action==='retry'){x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.submit();assert.equal(x.ids.result.hidden,false);}
    else if(action==='input')await x.ids.content.fire('input');else if(action==='clear')await x.ids.clear.fire('click');else if(action==='mode')await x.mode('email');else for(const fn of x.windowEvents[action])fn({persisted:true});
    assert.equal(x.ids['check-status'].textContent,'',action);resolve({ok:true,json:async()=>fixture.report()});await task;assert.equal(x.ids['check-status'].textContent,'',action);
  }
});
