const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/quote-context.html').replace('static/app.js','static/quote-context.js');
harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);vm.runInContext(fs.readFileSync(path.join(root,'static/unicode-notice.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
test('native invalid without submit clears comparison and formatting while preserving drafts and doing no IO',async()=>{
 const x=fixture.setup(),original='PRIVATE\u200b wording',revised='PRIVATE wording';
 x.ids['quote-original'].value=original;x.ids['quote-revised'].value=revised;await x.ids['quote-form'].fire('submit');
 assert.equal(x.ids['quote-result'].hidden,false);assert.equal(x.ids['quote-formatting'].hidden,false);
 // A native invalid event suppresses submit; no synthetic submit or input is sent.
 x.ids['quote-form'].valid=false;await x.ids['quote-form'].fire('invalid');
 assert.equal(x.ids['quote-result'].hidden,true);assert.equal(x.ids['quote-formatting'].hidden,true);
 for(const id of ['quote-diff','quote-status','quote-error'])assert.equal(x.ids[id].textContent,'');
 assert.equal(x.ids['quote-original'].value,original);assert.equal(x.ids['quote-revised'].value,revised);
 assert.equal(x.ids['quote-empty'].hidden,false);assert.equal(x.requests.length,0);assert.equal(x.blobs.length,0);assert.equal(x.clipboard.length,0);
});
