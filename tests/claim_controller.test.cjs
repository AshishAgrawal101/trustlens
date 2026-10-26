// Actual worksheet controller with the established minimal DOM double; no browser-rendering claim.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0]
 .replace('static/index.template.html','static/claim-review.html').replace('static/app.js','static/claim-review.js')
 .replace('setAttribute(k,v){','getAttribute(k){return this.attributes[k]??null;}\n    setAttribute(k,v){')
 .replace("URL:{createObjectURL(blob){blobs.push(blob);return 'blob:fixture';},revokeObjectURL(url){revoked.push(url);}},","URL:class extends (require('node:url').URL){static createObjectURL(blob){blobs.push(blob);return 'blob:fixture';}static revokeObjectURL(url){revoked.push(url);}},");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function review(x){x.ids['claim-text'].value='PRIVATE CLAIM';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-result'].hidden,false);}

test('review is explicit, fixed output receives focus, and no network request occurs',async()=>{
 const x=fixture.setup();assert.equal(x.ids['claim-review-submit'].disabled,false);x.ids['claim-text'].value='PRIVATE CLAIM';await x.ids['claim-text'].fire('input');assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.requests.length,0);
 await review(x);assert.equal(x.document.activeElement,x.ids['claim-result-title']);assert.equal(x.ids['claim-result-title'].scrollOptions?.block,'start');assert.doesNotMatch(x.ids['claim-observations'].textContent+x.ids['claim-questions'].textContent,/PRIVATE/);assert.equal(x.requests.length,0);
});

test('every input change invalidates prior output and disables exports',async()=>{
 for(const id of ['claim-text','claim-context','source-a-url','source-a-quote','source-a-date','source-b-url','source-b-quote','source-b-date']){
  const x=fixture.setup();await review(x);await x.ids[id].fire('input');assert.equal(x.ids['claim-result'].hidden,true,id);assert.equal(x.ids['claim-observations'].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,true);assert.equal(x.ids['claim-download-plan'].disabled,true);
 }
});

test('validation preserves drafts, suppresses private error text and cannot export a completed review',async()=>{
 const x=fixture.setup();await review(x);x.ids['source-a-url'].value='javascript:PRIVATE';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-text'].value,'PRIVATE CLAIM');assert.equal(x.ids['source-a-url'].value,'javascript:PRIVATE');assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.ids['claim-error'].hidden,false);assert.doesNotMatch(x.ids['claim-error'].textContent,/PRIVATE/);assert.equal(x.document.activeElement,x.ids['claim-error']);
 await x.ids['claim-copy-plan'].fire('click');await x.ids['claim-download-plan'].fire('click');assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);assert.equal(x.requests.length,0);
});

test('Clear, page exit and persisted Back erase all private fields and prior output',async()=>{
 for(const reset of ['clear','pagehide','pageshow']){const x=fixture.setup();await review(x);x.ids['claim-context'].value='PRIVATE';x.ids['source-a-quote'].value='PRIVATE';if(reset==='clear')await x.ids['claim-clear'].fire('click');else for(const fn of x.windowEvents[reset])fn({persisted:true});for(const id of ['claim-text','claim-context','source-a-url','source-a-quote','source-a-date','source-b-url','source-b-quote','source-b-date'])assert.equal(x.ids[id].value,'',id);assert.equal(x.ids['claim-result'].hidden,true);}
});

test('copy and download export a fixed plan; late copy completion cannot revive cleared output',async()=>{
 const x=fixture.setup();await review(x);await x.ids['claim-copy-plan'].fire('click');assert.equal(x.clipboard.length,1);assert.doesNotMatch(x.clipboard[0],/PRIVATE/);assert.match(x.clipboard[0],/not a truth verdict/);
 await x.ids['claim-download-plan'].fire('click');assert.equal(await x.blobs[0].text(),x.clipboard[0]);assert.equal(x.revoked.length,0);for(const fn of x.timers.values())fn();assert.equal(x.revoked[0],'blob:fixture');
 let resolve;x.state.writeText=()=>new Promise(r=>resolve=r);const pending=x.ids['claim-copy-plan'].fire('click');await x.ids['claim-clear'].fire('click');resolve();await pending;assert.equal(x.ids['claim-copy-status'].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,true);assert.equal(x.requests.length,0);
});

test('clipboard timeout offers download without exposing input',async()=>{
 const x=fixture.setup();await review(x);x.state.writeText=()=>new Promise(()=>{});const pending=x.ids['claim-copy-plan'].fire('click');for(const fn of x.timers.values())fn();await pending;assert.match(x.ids['claim-copy-status'].textContent,/Download the plan/);assert.equal(x.ids['claim-copy-plan'].disabled,false);
});
