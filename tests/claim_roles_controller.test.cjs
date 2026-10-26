// Reuse the existing actual-controller harness rather than duplicating the controller.
const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const prefix=fs.readFileSync(path.join(__dirname,'claim_controller.test.cjs'),'utf8').split("test('review is explicit")[0];
const shared={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;',shared);
async function labelled(x){x.ids['claim-text'].value='PRIVATE CLAIM';x.ids['source-a-url'].value='https://private.example/path?secret';x.ids['source-a-quote'].value='PRIVATE QUOTE';x.ids['source-a-role'].value='supports';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-result'].hidden,false);}
test('select change alone invalidates labels, priority feedback and exports without network',async()=>{
 for(const id of ['source-a-role','source-b-role']){const x=shared.setup();await labelled(x);assert.match(x.ids['claim-labels'].textContent,/supporting the claim/);assert.match(x.ids['claim-review-status'].textContent,/challenge your interpretation/);x.ids[id].value='challenges';await x.ids[id].fire('change');assert.equal(x.ids['claim-result'].hidden,true);for(const node of ['claim-labels','claim-review-status','claim-copy-status'])assert.equal(x.ids[node].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,true);assert.equal(x.ids['claim-download-plan'].disabled,true);assert.equal(x.requests.length,0);}
});
test('Clear, page exit and persisted Back reset both source roles and wipe label/status content',async()=>{
 for(const reset of ['clear','pagehide','pageshow']){const x=shared.setup();await labelled(x);x.ids['source-b-role'].value='challenges';if(reset==='clear')await x.ids['claim-clear'].fire('click');else for(const fn of x.windowEvents[reset])fn({persisted:true});for(const id of ['source-a-role','source-b-role'])assert.equal(x.ids[id].value,'unsure');assert.equal(x.ids['claim-labels'].textContent,'');assert.equal(x.ids['claim-review-status'].textContent,'');assert.equal(x.ids['claim-result'].hidden,true);}
});
test('late copy after a role change cannot label a new review as copied',async()=>{
 const x=shared.setup();await labelled(x);let resolve;x.state.writeText=()=>new Promise(r=>resolve=r);const pending=x.ids['claim-copy-plan'].fire('click');x.ids['source-a-role'].value='challenges';await x.ids['source-a-role'].fire('change');await x.ids['claim-form'].fire('submit');assert.match(x.ids['claim-labels'].textContent,/challenging the claim/);resolve();await pending;assert.equal(x.ids['claim-copy-status'].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,false);
});
test('roles do not change PLAN bytes and private source details never enter labels or exports',async()=>{
 const x=shared.setup();await labelled(x);await x.ids['claim-copy-plan'].fire('click');const plan=x.clipboard[0];assert.doesNotMatch(plan,/PRIVATE|private\.example|supporting the claim/);assert.doesNotMatch(x.ids['claim-labels'].textContent,/PRIVATE|private\.example/);assert.match(x.ids['claim-labels'].textContent,/not a detected finding/);
 x.ids['source-a-role'].value='challenges';await x.ids['source-a-role'].fire('change');await x.ids['claim-form'].fire('submit');await x.ids['claim-copy-plan'].fire('click');assert.equal(x.clipboard[1],plan);await x.ids['claim-download-plan'].fire('click');assert.equal(await x.blobs[0].text(),plan);
});
test('unknown injected role fails closed without exposing its value or enabling exports',async()=>{
 const x=shared.setup();await labelled(x);x.ids['source-a-role'].value='<PRIVATE>';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-result'].hidden,true);assert.match(x.ids['claim-error'].textContent,/available source labels/);assert.doesNotMatch(x.ids['claim-error'].textContent,/PRIVATE/);assert.equal(x.ids['claim-labels'].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,true);
});
