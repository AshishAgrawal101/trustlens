// Load the actual controller first, then the transfer script in the same context.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace('setAttribute(k,v){this.attributes[k]=v;}', 'setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k];}dispatchEvent(event){return this.fire(event.type,event);}');
harness=harness.replace('AbortController,AbortSignal,Blob,','AbortController,AbortSignal,Blob,Event,');
harness=harness.replace('vm.runInContext(source,context);', "vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/draft-transfer.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob,Event};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
async function type(x,text){x.ids.content.value=text;await x.ids.content.fire('input');}
test('Message and Call transfer exact draft only after explicit click and never submit',async()=>{
  const x=fixture.setup();assert.equal(x.ids['draft-transfer'].hidden,true);const text='  Caller: Hello.\nMe: Please verify.\n';await type(x,text);
  assert.equal(x.ids['draft-transfer'].hidden,false);assert.match(x.ids['transfer-draft'].textContent,/call transcript/);assert.equal(x.requests.length,0);
  await x.ids['transfer-draft'].fire('click');assert.equal(x.ids.content.value,text);assert.equal(x.ids['input-label'].textContent,'What did the caller say?');
  assert.match(x.ids['transfer-draft'].textContent,/Use as message/);assert.equal(x.document.activeElement,x.ids.content);assert.match(x.ids['transfer-status'].textContent,/No analysis started/);
  assert.equal(x.ids['input-count'].textContent,text.length+' / 30,000 characters');assert.equal(x.requests.length,0);
  await x.ids['transfer-draft'].fire('click');assert.equal(x.ids['input-label'].textContent,'Paste the message');assert.equal(x.ids.content.value,text);assert.equal(x.requests.length,0);
});
test('transfer invalidates existing report and original exports until explicitly checked again',async()=>{
  const x=fixture.setup();await type(x,'Caller asks for a code.');await x.submit();assert.equal(x.ids.result.hidden,false);
  await x.ids['transfer-draft'].fire('click');assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');
  await x.ids.copy.fire('click');await x.ids.download.fire('click');assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);assert.equal(x.requests.length,1);
  await x.submit();assert.equal(x.requests[1].url,'/api/analyze/call');assert.deepEqual(JSON.parse(x.requests[1].options.body),{transcript:'Caller asks for a code.'});
});
test('transfer uses normal mode cancellation so a pending source response cannot reappear',async()=>{
  const x=fixture.setup();await type(x,'PRIVATE DRAFT');let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();
  await x.ids['transfer-draft'].fire('click');assert.equal(x.requests[0].options.signal.aborted,true);assert.equal(x.ids.content.value,'PRIVATE DRAFT');assert.equal(x.ids.submit.disabled,false);
  resolve({ok:true,json:async()=>fixture.report()});await pending;assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['result-summary'].textContent,'');
});
test('transfer preserves a constructed-demo label and later edits clear it normally',async()=>{
  const x=fixture.setup();await x.demo('code');assert.equal(x.ids['example-note'].hidden,false);const text=x.ids.content.value;
  await x.ids['transfer-draft'].fire('click');assert.equal(x.ids.content.value,text);assert.equal(x.ids['example-note'].hidden,false);
  await type(x,text+' Edited');assert.equal(x.ids['example-note'].hidden,true);assert.equal(x.ids['transfer-status'].textContent,'');
});
test('other modes and blank or oversized drafts cannot use transfer to bypass review',async()=>{
  const x=fixture.setup();
  for(const mode of ['url','email','screenshot','qr','image']){
    await x.mode(mode);x.ids.content.value='PRIVATE hidden text';await x.ids.content.fire('input');assert.equal(x.ids['draft-transfer'].hidden,true);
    await x.ids['transfer-draft'].fire('click');assert.equal(x.ids.content.value,'PRIVATE hidden text');assert.equal(x.requests.length,0);assert.equal(x.ids['transfer-status'].textContent,'');
  }
  await x.mode('text');for(const text of [' \n\t','x'.repeat(30001)]){await type(x,text);assert.equal(x.ids['draft-transfer'].hidden,true);await x.ids['transfer-draft'].fire('click');assert.equal(x.ids['input-label'].textContent,'Paste the message');}
});
test('Clear and page lifecycle remove transfer affordance and status without retaining a draft',async()=>{
  const x=fixture.setup();for(const reset of ['clear','pagehide','pageshow']){
    await type(x,'PRIVATE');await x.ids['transfer-draft'].fire('click');assert.ok(x.ids['transfer-status'].textContent);
    if(reset==='clear')await x.ids.clear.fire('click');else for(const fn of x.windowEvents[reset])fn({persisted:true});
    assert.equal(x.ids.content.value,'');assert.equal(x.ids['draft-transfer'].hidden,true);assert.equal(x.ids['transfer-status'].textContent,'');
  }
});
