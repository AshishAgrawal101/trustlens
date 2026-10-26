const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'../static/phone');
const guide=require('../static/phone/guide.js');
const harness=fs.readFileSync(path.join(__dirname,'phone_companion.test.cjs'),'utf8');
const source=harness.slice(harness.indexOf('function phonePage('),harness.indexOf("test('phone edits"));
function setup(){const scope={fs,path,vm,root,guide,URL,Blob};vm.runInNewContext(source+';this.setup=phonePage;',scope);return scope.setup();}

test('native sharing needs explicit click and includes only fixed selected guidance',async()=>{
  const p=setup(),calls=[];p.navigator.share=async data=>calls.push(data);
  await p.ids['share-steps'].fire('click');assert.equal(calls.length,0);
  p.ids.message.value='PRIVATE-NAME code 123456 https://private.example/SECRET';p.inputs[0].checked=true;p.inputs[1].checked=true;p.ids.guide.fire('submit');
  assert.equal(calls.length,0);await p.ids['share-steps'].fire('click');assert.equal(calls.length,1);
  assert.equal(calls[0].text,guide.summary(['money','code']));assert.doesNotMatch(JSON.stringify(calls),/PRIVATE|123456|SECRET|private.example/);
  assert.match(p.ids['copy-status'].textContent,/Delivery is not verified/);assert.equal(p.ids['share-steps'].disabled,false);
});

test('unsupported, cancelled and rejected shares offer actionable alternatives',async()=>{
  const p=setup();p.ids.guide.fire('submit');await p.ids['share-steps'].fire('click');assert.match(p.ids['copy-status'].textContent,/Copy or Download/);
  p.navigator.share=async()=>{throw Object.assign(new Error(),{name:'AbortError'});};await p.ids['share-steps'].fire('click');assert.match(p.ids['copy-status'].textContent,/cancelled/);
  p.navigator.share=async()=>{throw new Error('private device error');};await p.ids['share-steps'].fire('click');assert.match(p.ids['copy-status'].textContent,/did not complete/);assert.doesNotMatch(p.ids['copy-status'].textContent,/private device error/);
});

test('Clear invalidates a pending device share and newer export invalidates old clipboard status',async()=>{
  const p=setup();p.ids.guide.fire('submit');let resolve;p.navigator.share=()=>new Promise(r=>resolve=r);
  const pending=p.ids['share-steps'].fire('click');assert.equal(p.ids['share-steps'].disabled,true);p.ids.clear.fire('click');resolve();await pending;
  assert.equal(p.ids['copy-status'].textContent,'');assert.equal(p.ids['share-steps'].disabled,false);
  let copied;const q=setup();q.navigator.clipboard.writeText=()=>new Promise(r=>copied=r);q.navigator.share=async()=>{};q.ids.guide.fire('submit');
  const copy=q.ids.copy.fire('click');await q.ids['share-steps'].fire('click');copied();await copy;assert.match(q.ids['copy-status'].textContent,/Share request/);
});

test('recovery shares only a selected fixed plan and page exit rejects its late status',async()=>{
  const p=setup(),calls=[];let resolve;p.navigator.share=data=>{calls.push(data);return new Promise(r=>resolve=r);};
  await p.ids['share-recovery'].fire('click');assert.equal(calls.length,0);
  p.ids.message.value='PRIVATE-INCIDENT';p.ids['recovery-account'].fire('click');const pending=p.ids['share-recovery'].fire('click');
  assert.match(calls[0].text,/Secure the affected account/);assert.doesNotMatch(calls[0].text,/PRIVATE-INCIDENT/);
  p.windowEvents.pagehide();resolve();await pending;assert.equal(p.ids['recovery-status'].textContent,'');assert.equal(p.ids['share-recovery'].disabled,false);
});
