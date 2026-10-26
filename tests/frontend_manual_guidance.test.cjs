// Offline DOM regressions reuse the main controller harness and the actual fixed Pocket guidance.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const guide=require('../static/phone/guide.js');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
async function select(x,...topics){for(const topic of topics)x.topics.find(input=>input.dataset.topic===topic).checked=true;await x.ids['manual-form'].fire('submit');}
test('manual guidance is communication-only and requires explicit topics and submit',async()=>{
  const x=fixture.setup();assert.equal(x.ids['manual-panel'].hidden,true);await x.submit();assert.equal(x.ids['manual-panel'].hidden,false);
  await x.ids['manual-form'].fire('submit');assert.match(x.ids['manual-status'].textContent,/Choose at least one/);assert.equal(x.ids['manual-result'].hidden,true);
  x.topics[0].checked=true;await x.topics[0].fire('change');assert.equal(x.ids['manual-result'].hidden,true);
  await x.ids['manual-form'].fire('submit');assert.equal(x.ids['manual-result'].hidden,false);assert.equal(x.document.activeElement,x.ids['manual-heading']);
  assert.match(x.ids['manual-steps'].textContent,/Pause before paying/);assert.equal(x.requests.length,1);
  x.state.fetch=async()=>({ok:true,json:async()=>({...fixture.report(),kind:'image'})});await x.submit();assert.equal(x.ids['manual-panel'].hidden,true);assert.equal(x.ids['manual-result'].hidden,true);assert.ok(x.topics.every(input=>!input.checked));
});
test('all four user-selected topics render fixed steps without changing report or detected evidence',async()=>{
  const x=fixture.setup(),data=fixture.report(),before=JSON.stringify(data);x.ids.content.value='PRIVATE source text';x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  const evidence=x.ids.evidence.textContent,actions=x.ids.actions.textContent,verdict=x.ids.verdict.textContent;
  await select(x,'money','code','device','secret');assert.equal(x.ids['manual-steps'].children.length,5);
  for(const phrase of ['Pause before paying','Keep account access private','Keep control of your device','Bring in someone you trust','Verify independently'])assert.match(x.ids['manual-steps'].textContent,new RegExp(phrase));
  assert.equal(JSON.stringify(data),before);assert.equal(x.ids.evidence.textContent,evidence);assert.equal(x.ids.actions.textContent,actions);assert.equal(x.ids.verdict.textContent,verdict);assert.equal(x.ids['print-summary'].textContent,data.share_summary);
  await x.ids.copy.fire('click');assert.equal(x.clipboard[0],data.share_summary);assert.doesNotMatch(x.ids['manual-steps'].textContent,/PRIVATE/);
});
test('manual copy and download export the exact fixed summary separately from original exports',async()=>{
  const x=fixture.setup();x.ids.content.value='PRIVATE https://private.test code 12345';await x.submit();await select(x,'code');
  await x.ids['manual-copy'].fire('click');await x.ids['manual-download'].fire('click');const expected=guide.summary(['code']);
  assert.equal(x.clipboard[0],expected);assert.equal(await x.blobs[0].text(),expected);assert.doesNotMatch(expected,/PRIVATE|private.test|12345/);assert.match(expected,/User-selected request topics; no automatic scam verdict/);
  assert.equal(x.document.body.children[0].download,'trustlens-user-selected-steps.txt');[...x.timers.values()][0]();assert.equal(x.revoked[0],'blob:fixture');
  await x.ids.download.fire('click');assert.equal(await x.blobs[1].text(),'Input-free summary');assert.equal(x.ids['print-summary'].textContent,'Input-free summary');
});
test('manual topic edits invalidate pending copy and require rebuilding selected steps',async()=>{
  const x=fixture.setup();await x.submit();await select(x,'money');let resolve;x.state.writeText=()=>new Promise(r=>resolve=r);const copying=x.ids['manual-copy'].fire('click');
  x.topics[0].checked=false;x.topics[1].checked=true;await x.topics[1].fire('change');await x.ids['manual-form'].fire('submit');resolve();await copying;
  assert.equal(x.ids['manual-status'].textContent,'');assert.match(x.ids['manual-steps'].textContent,/Keep account access private/);assert.doesNotMatch(x.ids['manual-steps'].textContent,/Pause before paying/);
});
test('manual clipboard timeout is actionable and source edits/mode/page exit erase selected guidance',async()=>{
  for(const reset of ['input','mode','exit']){
    const x=fixture.setup();await x.submit();await select(x,'device');x.state.writeText=()=>new Promise(()=>{});const copying=x.ids['manual-copy'].fire('click');[...x.timers.values()][0]();await copying;
    assert.match(x.ids['manual-status'].textContent,/Download selected steps/);
    if(reset==='input')await x.ids.content.fire('input');else if(reset==='mode')await x.mode('email');else for(const fn of x.windowEvents.pagehide)fn({});
    assert.ok(x.topics.every(input=>!input.checked));assert.equal(x.ids['manual-panel'].hidden,true);assert.equal(x.ids['manual-result'].hidden,true);assert.equal(x.ids['manual-steps'].textContent,'');assert.equal(x.ids['manual-status'].textContent,'');
    await x.ids['manual-download'].fire('click');assert.equal(x.blobs.length,0);
  }
});
test('manual markup identifies user choice, separates exports, and loads the shared local guide first',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');assert.match(html,/USER-SELECTED · NOT A DETECTED FINDING/);assert.match(html,/do not change the detected evidence or risk/);
  assert.ok(html.indexOf('/phone/guide.js')<html.indexOf('/static/app.js'));assert.equal((html.match(/data-topic=/g)||[]).length,4);
});
test('missing shared guide fails honestly without breaking the original report or exports',async()=>{
  const withoutGuide=harness.replace("PocketGuide:require(path.join(root,'static/phone/guide.js')),",'');
  const local={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(withoutGuide+'\nthis.setup=setup;',local);
  const x=local.setup();await x.submit();await select(x,'money');assert.match(x.ids['manual-status'].textContent,/could not load/);
  assert.equal(x.ids['manual-result'].hidden,true);assert.equal(x.ids.result.hidden,false);await x.ids.copy.fire('click');assert.equal(x.clipboard[0],'Input-free summary');
});
