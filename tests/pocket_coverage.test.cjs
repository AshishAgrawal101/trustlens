const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const guide=require('../static/phone/guide.js');
const first=Array.from({length:12},(_,i)=>'https://site'+i+'.test');

test('Pocket reports uninspected addresses without parsing or exposing them',()=>{
  let parses=0;const scope={URL:class extends URL{constructor(value){super(value);parses++;}},module:{exports:{}}};
  vm.runInNewContext(fs.readFileSync(require.resolve('../static/phone/guide.js'),'utf8'),scope);
  const result=scope.module.exports.hostCoverage([...first,'https://PRIVATE@uninspected.test/SECRET','https://later.test'].join(' '));
  assert.equal(parses,12);assert.equal(result.items.length,12);assert.equal(result.remaining,2);
  assert.doesNotMatch(JSON.stringify(result),/PRIVATE|SECRET|uninspected|later/);
  assert.equal(guide.hostCoverage(first.join(' ')).remaining,0);
  assert.equal(guide.compareHosts([...first,'https://later.test'].join(' '),'site0.test').remaining,1);
});

test('incomplete Pocket address notice clears on edits and is absent from fixed exports',()=>{
  const harness=fs.readFileSync(path.join(__dirname,'phone_companion.test.cjs'),'utf8');
  const prelude=harness.slice(harness.indexOf('function phonePage('),harness.indexOf("test('phone edits"));
  const scope={fs,path,vm,root:path.join(__dirname,'../static/phone'),guide,URL,Blob};
  vm.runInNewContext(prelude+'\nthis.phonePage=phonePage;',scope);
  const p=scope.phonePage();p.ids.message.value=[...first,'https://PRIVATE@uninspected.test/SECRET'].join(' ');
  p.ids.guide.fire('submit');assert.match(p.ids['host-coverage'].textContent,/incomplete/);assert.match(p.ids['host-coverage'].textContent,/not inspected: 1/);
  assert.doesNotMatch(p.ids.hosts.textContent,/PRIVATE|SECRET|uninspected/);
  assert.doesNotMatch(guide.summary([]),/PRIVATE|uninspected|site0/);
  p.ids.message.fire('input');assert.equal(p.ids['host-coverage'].textContent,'');assert.equal(p.ids.hosts.textContent,'');
});
