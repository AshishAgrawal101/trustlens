const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);

test('malformed reports never expose partial results, exports or private decoder errors',async()=>{
  const mutations=[()=>null,()=>[],r=>({...r,actions:null}),r=>({...r,evidence:[{...r.evidence[0],weight:NaN}]}),r=>({...r,limitations:[{private:'PRIVATE'}]}),r=>({...r,share_summary:null}),r=>({...r,content_credentials:{status:'verified',detail:{private:'PRIVATE'}}}),r=>({...r,risk_level:'invented'})];
  for(const mutate of mutations){const x=fixture.setup();await x.submit();assert.equal(x.ids.result.hidden,false);x.ids.content.value='PRIVATE DRAFT';x.state.fetch=async()=>({ok:true,json:async()=>mutate(fixture.report())});await x.submit();assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');assert.equal(x.ids.submit.disabled,false);assert.equal(x.ids['check-form'].attributes['aria-busy'],'false');assert.equal(x.ids.content.value,'PRIVATE DRAFT');assert.match(x.ids.error.textContent,/response|report/);assert.doesNotMatch(x.ids.error.textContent,/PRIVATE|TypeError|properties/);await x.ids.copy.fire('click');assert.equal(x.clipboard.length,0);}
});
test('unreadable success and error responses use fixed feedback and can be retried',async()=>{
 for(const ok of [false,true]){const x=fixture.setup();x.state.fetch=async()=>({ok,json:async()=>{throw new SyntaxError('PRIVATE DECODER BODY');}});await x.submit();assert.doesNotMatch(x.ids.error.textContent,/PRIVATE/);assert.match(x.ids.error.textContent,/unreadable response/);x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.submit();assert.equal(x.ids.result.hidden,false);assert.equal(x.ids.error.hidden,true);}
});
test('malformed extraction notice cannot enter editable review or be stringified',async()=>{
 const x=fixture.setup();await x.mode('screenshot');await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'PRIVATE EXTRACT',notice:{private:'PRIVATE'},review_required:true})});await x.submit();assert.equal(x.ids['ocr-review'].hidden,true);assert.equal(x.ids.content.value,'');assert.doesNotMatch(x.ids.error.textContent,/PRIVATE/);assert.equal(x.ids.submit.disabled,false);
});

test('practice moves focus from a disabled answer to readable feedback',async()=>{const x=fixture.setup();await x.ids['practice-open'].fire('click');const choice=x.ids.choices.children[1];choice.focus();await choice.fire('click');assert.equal(choice.disabled,true);assert.equal(x.document.activeElement,x.ids['practice-answer']);assert.equal(x.ids['practice-answer'].hidden,false);assert.equal(x.ids['practice-next'].hidden,false);await x.ids['practice-next'].fire('click');assert.equal(x.document.activeElement,x.ids.choices.children[0]);});

test('a result without matched concerns leads with unresolved verification',async()=>{const x=fixture.setup(),data=fixture.report();data.risk_level='low';data.evidence=[];x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();assert.equal(x.ids.verdict.textContent,'This request is still unverified.');assert.match(x.ids['result-safety'].textContent,/no warning does not prove safety/);});
