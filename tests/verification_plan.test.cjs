const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace('vm.runInContext(source,context);', "vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/verification-plan.js'),'utf8'),context);");
harness=harness.replace('async demo(name)', "routes:all.filter(e=>Object.hasOwn(e.dataset,'route')),async demo(name)");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
async function choose(x,key){await x.routes.find(button=>button.dataset.route===key).fire('click');}

test('verification plan requires a communication result and an explicit route choice',async()=>{
 const x=fixture.setup();assert.equal(x.ids['verification-plan'].hidden,true);await choose(x,'app');assert.equal(x.ids['verification-choice'].hidden,true);assert.equal(x.requests.length,0);
 x.ids.content.value='CONSTRUCTED PRIVATE https://private.test/?token=123';await x.submit();assert.equal(x.ids['verification-plan'].hidden,false);assert.equal(x.ids['verification-choice'].hidden,true);await choose(x,'app');assert.equal(x.requests.length,1);assert.equal(x.document.activeElement,x.ids['verification-heading']);assert.match(x.ids['verification-steps'].textContent,/supplied link/);assert.doesNotMatch(x.ids['verification-steps'].textContent,/CONSTRUCTED|private.test|123/);
});
test('each route exports only fixed input-free guidance without changing detected evidence',async()=>{
 for(const key of ['app','number','person']){const x=fixture.setup();x.ids.content.value='CONSTRUCTED PRIVATE';await x.submit();const verdict=x.ids.verdict.textContent,evidence=x.ids.evidence.textContent,original=x.ids['print-summary'].textContent;await choose(x,key);await x.ids['verification-copy'].fire('click');assert.match(x.clipboard[0],/user-selected verification plan/);assert.match(x.clipboard[0],/not completed verification/);assert.doesNotMatch(x.clipboard[0],/CONSTRUCTED PRIVATE/);await x.ids['verification-download'].fire('click');assert.equal(await x.blobs[0].text(),x.clipboard[0]);assert.equal(x.ids.verdict.textContent,verdict);assert.equal(x.ids.evidence.textContent,evidence);assert.equal(x.ids['print-summary'].textContent,original);}
});
test('image reports never offer a communication verification plan',async()=>{
 const x=fixture.setup();await x.submit();await choose(x,'person');x.state.fetch=async()=>({ok:true,json:async()=>({...fixture.report(),kind:'image'})});await x.submit();assert.equal(x.ids['verification-plan'].hidden,true);await x.ids['verification-copy'].fire('click');await choose(x,'app');assert.equal(x.clipboard.length,0);assert.equal(x.ids['verification-choice'].hidden,true);
});
test('edits Clear examples mode changes rechecks and page exit erase selected plans',async()=>{
 const invalidate=[async x=>x.ids.content.fire('input'),async x=>x.ids.clear.fire('click'),async x=>x.ids.example.fire('click'),async x=>x.mode('call'),async x=>x.submit(),async x=>{for(const fn of x.windowEvents.pagehide)await fn({});},async x=>{for(const fn of x.windowEvents.pageshow)await fn({persisted:true});}];
 for(const reset of invalidate){const x=fixture.setup();await x.submit();await choose(x,'number');await reset(x);assert.equal(x.ids['verification-choice'].hidden,true);assert.equal(x.ids['verification-steps'].textContent,'');assert.equal(x.ids['verification-heading'].textContent,'');await x.ids['verification-copy'].fire('click');assert.equal(x.clipboard.length,0);}
});
test('clipboard timeout gives a download fallback and late old choices cannot label a newer plan',async()=>{
 const x=fixture.setup();await x.submit();await choose(x,'app');let resolve;x.state.writeText=()=>new Promise(r=>resolve=r);const pending=x.ids['verification-copy'].fire('click');await choose(x,'person');resolve();await pending;assert.equal(x.ids['verification-status'].textContent,'');
 x.state.writeText=()=>new Promise(()=>{});const timeout=x.ids['verification-copy'].fire('click');[...x.timers.values()][0]();await timeout;assert.match(x.ids['verification-status'].textContent,/Download plan/);assert.equal(x.timers.size,0);
});
