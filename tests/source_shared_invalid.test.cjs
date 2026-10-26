const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/quote-context.html').replace('static/app.js','static/quote-context.js');
harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);vm.runInContext(fs.readFileSync(path.join(root,'static/unicode-notice.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function pageTwo(){const x=fixture.setup();x.ids['quote-original'].value='PRIVATE\u200b';x.ids['quote-revised'].value='PRIVATE revised';x.ids['source-passage'].value=('Before PRIVATE\u200b after. ').repeat(12);await x.ids['source-form'].fire('submit');await x.ids['source-next'].fire('click');assert.match(x.ids['source-page-status'].textContent,/6–10 of 12/);assert.equal(x.ids['source-formatting'].hidden,false);return x;}
async function invalid(x,target){for(const fn of x.ids['quote-form'].events.invalid||[])await fn({target:x.ids[target],preventDefault(){}});}
test('shared Original native invalid clears later source windows and pager without erasing drafts or IO',async()=>{
 const x=await pageTwo(),drafts=['quote-original','quote-revised','source-passage'].map(id=>x.ids[id].value);await invalid(x,'quote-original');
 assert.equal(x.ids['source-result'].hidden,true);assert.equal(x.ids['source-formatting'].hidden,true);assert.equal(x.ids['source-paging'].hidden,true);
 for(const id of ['source-matches','source-status','source-page-status'])assert.equal(x.ids[id].textContent,'');for(const id of ['source-prev','source-next'])assert.equal(x.ids[id].disabled,true);
 assert.deepEqual(['quote-original','quote-revised','source-passage'].map(id=>x.ids[id].value),drafts);assert.equal(x.requests.length+x.blobs.length+x.clipboard.length,0);
 await x.ids['source-form'].fire('submit');assert.match(x.ids['source-page-status'].textContent,/1–5 of 12/);
});
test('Revised native invalid preserves independent later source page and formatting notice',async()=>{
 const x=await pageTwo(),before=x.ids['source-matches'].textContent;await invalid(x,'quote-revised');assert.equal(x.ids['source-result'].hidden,false);assert.equal(x.ids['source-formatting'].hidden,false);assert.equal(x.ids['source-matches'].textContent,before);assert.match(x.ids['source-page-status'].textContent,/6–10 of 12/);assert.equal(x.requests.length+x.blobs.length+x.clipboard.length,0);
});
