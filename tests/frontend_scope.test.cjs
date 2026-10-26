const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
function text(x){return x.ids['coverage-checked'].textContent+' '+x.ids['coverage-unverified'].textContent;}
async function report(x,kind,extra={}){x.state.fetch=async()=>({ok:true,json:async()=>({...fixture.report(),kind,...extra})});await x.submit();}
test('fixed source-specific scope explains unverified identity and avoids private content',async()=>{
  for(const [mode,checked,limit] of [['text',/submitted wording/,/sender.*hidden link/],['url',/address structure/,/Neither address was visited/],['email',/headers/,/Attachments were not opened or scanned/],['call',/transcript/,/No audio was checked/],['image',/components ran.*unavailable/,/cannot verify the depicted story/]]){
    const x=fixture.setup();await x.mode(mode);x.ids.content.value='PRIVATE SOURCE';if(mode==='image')await x.file();await report(x,mode,{summary:'PRIVATE SUMMARY',evidence:[{...fixture.report().evidence[0],detail:'PRIVATE EVIDENCE'}]});
    assert.match(x.ids['coverage-checked'].textContent,checked);assert.match(x.ids['coverage-unverified'].textContent,limit);assert.doesNotMatch(text(x),/PRIVATE/);assert.equal(x.ids['print-summary'].textContent,'Input-free summary');await x.ids.copy.fire('click');assert.equal(x.clipboard[0],'Input-free summary');
  }
});
test('screenshot and QR scopes follow reviewed extraction, never first-stage extraction alone',async()=>{
  for(const mode of ['screenshot','qr']){
    const x=fixture.setup();await x.mode(mode);await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'PRIVATE EXTRACT',notice:'Review',review_required:true})});await x.submit();assert.equal(text(x),' ');
    x.ids.reviewed.checked=true;await report(x,'text');assert.match(x.ids['coverage-checked'].textContent,mode==='qr'?/decoded text you reviewed/:/reviewed after screenshot extraction/);assert.doesNotMatch(text(x),/PRIVATE/);
  }
});
test('image report takes precedence over a reviewed screenshot source and does not assert model execution',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'Reviewed',notice:'Review'})});await x.submit();x.ids.reviewed.checked=true;await report(x,'image',{model_ran:false,content_credentials:{status:'unavailable',detail:'Unavailable'}});
  assert.match(x.ids['coverage-checked'].textContent,/image-origin report/);assert.doesNotMatch(x.ids['coverage-checked'].textContent,/screenshot|detector ran|credentials verified/);assert.match(x.ids['coverage-unverified'].textContent,/No claim is made that every image component ran/);
});
test('incomplete link evidence adds an explicit scope caveat without replacing useful coverage',async()=>{
  const x=fixture.setup();await report(x,'text',{evidence:[{...fixture.report().evidence[0],id:'analysis:links_incomplete'}]});assert.match(text(x),/submitted wording/);assert.match(text(x),/Some links remain unchecked/);
});
test('edits, mode changes, Clear, page lifecycle and malformed retry erase coverage',async()=>{
  for(const reset of ['input','mode','clear','pagehide','pageshow','malformed']){
    const x=fixture.setup();await report(x,'text');assert.ok(text(x).length>1);
    if(reset==='input')await x.ids.content.fire('input');else if(reset==='mode')await x.mode('call');else if(reset==='clear')await x.ids.clear.fire('click');else if(reset==='malformed'){x.state.fetch=async()=>({ok:true,json:async()=>({kind:'text'})});await x.submit();}else for(const fn of x.windowEvents[reset])fn({persisted:true});
    assert.equal(text(x),' ',reset);assert.equal(x.ids.result.hidden,true);
  }
});
test('a pending dismissed result cannot restore old coverage',async()=>{
  const x=fixture.setup();let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();await x.ids.cancel.fire('click');resolve({ok:true,json:async()=>fixture.report()});await pending;assert.equal(text(x),' ');assert.equal(x.ids.result.hidden,true);
});
