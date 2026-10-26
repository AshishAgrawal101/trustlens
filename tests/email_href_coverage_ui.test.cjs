const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
function unknown(id){return {id,weight:0,evidence_class:'unknown',title:'Link coverage incomplete',detail:'Some supplied targets need manual review.',source:'Email link extraction'};}
async function email(x,ids,risk='low'){
  await x.mode('email');x.ids.content.value='CONSTRUCTED PRIVATE EMAIL';
  const report={...fixture.report(),kind:'email',risk_level:risk,evidence:ids.map(unknown),summary:'Server summary only',share_summary:'SERVER FIXED EXPORT'};
  if(risk==='high')report.evidence.push({...fixture.report().evidence[0],id:'text:code'});
  x.state.fetch=async()=>({ok:true,json:async()=>report});await x.submit();
}
test('unsupported email target coverage is incomplete without becoming a positive warning or invented hostname',async()=>{
  const x=fixture.setup();await email(x,['email:links_incomplete']);
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids['verdict-tag'].className,'verdict-tag low');assert.equal(x.ids.verdict.textContent,'Some links still need review.');
  assert.match(x.ids['coverage-checked'].textContent,/email wording/);assert.match(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);
  assert.match(x.ids.evidence.textContent,/Still unknown/);assert.doesNotMatch(x.ids.evidence.textContent,/Warning signs to review|Observed facts/);
  assert.doesNotMatch(x.ids['coverage-unverified'].textContent+x.ids.verdict.textContent,/PRIVATE|https?:|hostname|first eight|first 8/);
  assert.equal(x.ids['result-summary'].textContent,'Server summary only');assert.equal(x.ids['print-summary'].textContent,'SERVER FIXED EXPORT');
  await x.ids.copy.fire('click');await x.ids.download.fire('click');assert.equal(x.clipboard[0],'SERVER FIXED EXPORT');assert.equal(await x.blobs[0].text(),'SERVER FIXED EXPORT');
});
test('readable high code warning keeps high style pause and warning evidence beside incomplete target coverage',async()=>{
  const x=fixture.setup();await email(x,['email:links_incomplete'],'high');
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids['verdict-tag'].className,'verdict-tag high');assert.equal(x.ids.verdict.textContent,'Pause; some links remain unchecked.');
  assert.match(x.ids.evidence.textContent,/Warning signs to review/);assert.match(x.ids.evidence.textContent,/Code request/);assert.match(x.ids.actions.textContent,/Verify independently/);
});
test('MIME and both link coverage flags coexist without replacing the email manual-check headline',async()=>{
  const x=fixture.setup();await email(x,['email:incomplete','email:links_incomplete','analysis:links_incomplete'],'high');
  assert.equal(x.ids.verdict.textContent,'This email needs a manual check.');assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids['verdict-tag'].className,'verdict-tag high');
  assert.equal((x.ids['coverage-unverified'].textContent.match(/Some links remain unchecked/g)||[]).length,1);assert.match(x.ids.evidence.textContent,/Code request/);
  await x.ids.clear.fire('click');assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.ids['coverage-unverified'].textContent,'');assert.equal(x.ids.result.hidden,true);
});
test('new email coverage marker is exact while existing MIME behavior remains distinct',async()=>{
  for(const id of ['email:links_incomplete:1','email:links_incomplete_extra','other:email:links_incomplete','email:links_complete']){
    const x=fixture.setup();await email(x,[id]);assert.equal(x.ids['verdict-tag'].textContent,'STILL UNVERIFIED');assert.doesNotMatch(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);
  }
  const x=fixture.setup();await email(x,['email:incomplete']);assert.equal(x.ids.verdict.textContent,'This email needs a manual check.');assert.doesNotMatch(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);
});
