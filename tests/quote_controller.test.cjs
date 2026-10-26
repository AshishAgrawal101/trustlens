// Actual controller in the existing DOM double; browser rendering is checked separately.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0]
 .replace('static/index.template.html','static/quote-context.html').replace('static/app.js','static/quote-context.js');
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function compare(x,a='The park will close for repairs.',b='The park will close.'){
 x.ids['quote-original'].value=a;x.ids['quote-revised'].value=b;await x.ids['quote-form'].fire('submit');
}
test('explicit comparison labels changes with literal text and sends or exports nothing',async()=>{
 const x=fixture.setup();x.ids['quote-original'].value='<img src=x>';x.ids['quote-revised'].value='<script>alert(1)</script>';await x.ids['quote-original'].fire('input');assert.equal(x.ids['quote-result'].hidden,true);
 await x.ids['quote-form'].fire('submit');assert.equal(x.ids['quote-result'].hidden,false);assert.match(x.ids['quote-diff'].textContent,/\[Removed\].*<img src=x>.*\[Added\].*<script>/);assert.equal(x.document.activeElement,x.ids['quote-result-title']);assert.equal(x.ids['quote-result-title'].scrollOptions?.block,'start');assert.equal(x.requests.length,0);assert.equal(x.blobs.length,0);assert.equal(x.clipboard.length,0);assert.equal(x.ids['quote-empty'].hidden,true);
});
test('edits invalidate old diff and Clear/exit/Back remove both versions and output',async()=>{
 for(const id of ['quote-original','quote-revised']){const x=fixture.setup();await compare(x);await x.ids[id].fire('input');assert.equal(x.ids['quote-result'].hidden,true);assert.equal(x.ids['quote-diff'].textContent,'');assert.equal(x.ids['quote-empty'].hidden,false);assert.notEqual(x.ids[id].value,'');}
 for(const reset of ['clear','pagehide','pageshow']){const x=fixture.setup();await compare(x);if(reset==='clear')await x.ids['quote-clear'].fire('click');else for(const fn of x.windowEvents[reset])fn({persisted:true});for(const id of ['quote-original','quote-revised','quote-diff','quote-status','quote-error'])assert.equal(x.ids[id].value||x.ids[id].textContent,'');assert.equal(x.ids['quote-result'].hidden,true);assert.equal(x.requests.length,0);}
});
test('invalid retry never retains partial or old comparison; fixed error focuses without input echo',async()=>{
 for(const a of ['', ' '.repeat(5),'PRIVATE'.repeat(600),Array(401).fill('x').join(' ')]){const x=fixture.setup();await compare(x);await compare(x,a,'other');assert.equal(x.ids['quote-result'].hidden,true);assert.equal(x.ids['quote-diff'].textContent,'');assert.equal(x.ids['quote-error'].hidden,false);assert.equal(x.document.activeElement,x.ids['quote-error']);assert.doesNotMatch(x.ids['quote-error'].textContent,/PRIVATE/);}
 const x=fixture.setup();await compare(x);x.ids['quote-form'].valid=false;await x.ids['quote-form'].fire('submit');assert.equal(x.ids['quote-diff'].textContent,'');assert.equal(x.ids['quote-result'].hidden,true);
});
test('constructed example replaces drafts but waits for explicit comparison',async()=>{
 const x=fixture.setup();await compare(x);await x.ids['quote-example'].fire('click');assert.equal(x.ids['quote-result'].hidden,true);assert.match(x.ids['quote-original'].value,/for repairs/);assert.doesNotMatch(x.ids['quote-revised'].value,/for repairs/);assert.equal(x.requests.length,0);await x.ids['quote-form'].fire('submit');assert.equal(x.ids['quote-result'].hidden,false);
});
test('identical supplied versions are described without authenticating their source',async()=>{
 const x=fixture.setup();await compare(x,'same wording','same wording');assert.match(x.ids['quote-status'].textContent,/exactly identical/);assert.match(x.ids['quote-status'].textContent,/does not verify/);assert.equal(x.ids['quote-diff'].children.length,1);assert.equal(x.ids['quote-diff'].children[0].className,'same');
});
