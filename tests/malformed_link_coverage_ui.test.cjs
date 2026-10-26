const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
function malformed(id){return {id,weight:0,evidence_class:'unknown',title:'Address could not be parsed',detail:'This address needs manual review.',source:'Literal address parser'};}
async function show(x,kind,id,risk='low'){
  const data={...fixture.report(),kind,risk_level:risk,evidence:[malformed(id)],summary:'Server coverage summary',share_summary:'SERVER INPUT-FREE EXPORT'};
  if(risk==='high')data.evidence.push({...fixture.report().evidence[0],id:'text:code'});
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();return data;
}
test('exact and indexed malformed address evidence makes a low check incomplete without inventing risk or export content',async()=>{
  for(const id of ['url:malformed','url:malformed:0','url:malformed:12','url:malformed:future-key']){
    const x=fixture.setup();x.ids.content.value='CONSTRUCTED PRIVATE https://[invalid';await show(x,'text',id);
    assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids['verdict-tag'].className,'verdict-tag low');assert.equal(x.ids.verdict.textContent,'Some links still need review.');
    assert.match(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);assert.doesNotMatch(x.ids['coverage-unverified'].textContent,/PRIVATE|first 8|first eight/);
    assert.equal(x.ids['result-summary'].textContent,'Server coverage summary');assert.equal(x.ids['print-summary'].textContent,'SERVER INPUT-FREE EXPORT');
    await x.ids.copy.fire('click');await x.ids.download.fire('click');assert.equal(x.clipboard[0],'SERVER INPUT-FREE EXPORT');assert.equal(await x.blobs[0].text(),'SERVER INPUT-FREE EXPORT');
  }
});
test('a malformed address does not suppress a separate high code warning or its styling',async()=>{
  const x=fixture.setup();await show(x,'text','url:malformed:1','high');
  assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');assert.equal(x.ids['verdict-tag'].className,'verdict-tag high');assert.equal(x.ids.verdict.textContent,'Pause; some links remain unchecked.');
  assert.match(x.ids.evidence.textContent,/Code request/);assert.match(x.ids.actions.textContent,/Verify independently/);
});
test('malformed evidence retains source-specific screenshot QR email call and link scope',async()=>{
  for(const [mode,kind,scope]of [['screenshot','text',/screenshot extraction/],['qr','text',/decoded text/],['email','email',/email wording/],['call','call',/transcript wording/],['url','url',/address structure/]]){
    const x=fixture.setup();await x.mode(mode);
    if(['screenshot','qr'].includes(mode)){await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'Constructed extracted wording.',notice:'Review first.',review_required:true})});await x.submit();x.ids.reviewed.checked=true;await x.ids.reviewed.fire('change');}
    await show(x,kind,'url:malformed:2');assert.match(x.ids['coverage-checked'].textContent,scope);assert.match(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');
    await x.ids.clear.fire('click');assert.equal(x.ids['coverage-unverified'].textContent,'');assert.equal(x.ids['print-summary'].textContent,'');
  }
});
test('valid and lookalike evidence IDs keep existing unverified behavior while the existing budget marker still works',async()=>{
  for(const id of ['url:parsed','url:malformedness','url:malformed_extra','other:url:malformed:1',undefined,null,42,{}]){
    const x=fixture.setup();await show(x,'text',id);assert.equal(x.ids['verdict-tag'].textContent,'STILL UNVERIFIED');assert.equal(x.ids.verdict.textContent,'This request is still unverified.');assert.doesNotMatch(x.ids['coverage-unverified'].textContent,/Some links remain unchecked/);
  }
  const x=fixture.setup();await show(x,'text','analysis:links_incomplete');assert.equal(x.ids['verdict-tag'].textContent,'CHECK INCOMPLETE');
});
