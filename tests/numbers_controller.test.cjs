// Actual controller in the established DOM double; not a browser-rendering test.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0]
 .replace('static/index.template.html','static/numbers-context.html').replace('static/app.js','static/numbers-context.js');
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
const fields=['count-a','total-a','count-b','total-b'];
function values(x,items=['20','100','30','200']){fields.forEach((id,index)=>x.ids[id].value=items[index]);}
async function compare(x){values(x);await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,false);}
function result(x){return x.ids['numbers-facts'].textContent+x.ids['numbers-questions'].textContent;}

test('numbers require explicit submit; construction and typing send nothing',async()=>{
 const x=fixture.setup();assert.equal(x.ids['numbers-submit'].disabled,false);assert.equal(x.ids['numbers-result'].hidden,true);
 values(x);await x.ids['count-a'].fire('input');assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(x.requests.length,0);
 await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,false);assert.equal(x.document.activeElement,x.ids['numbers-result-title']);assert.equal(x.ids['numbers-result-title'].scrollOptions?.block,'start');assert.equal(x.requests.length,0);assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);
});

test('all four edits remove old facts/questions and errors while retaining drafts',async()=>{
 for(const id of fields){const x=fixture.setup();await compare(x);const draft=x.ids[id].value;await x.ids[id].fire('input');assert.equal(x.ids['numbers-result'].hidden,true,id);assert.equal(result(x),'');assert.equal(x.ids[id].value,draft);assert.equal(x.ids['numbers-error'].hidden,true);}
});

test('Clear, exit and persisted Back remove every supplied number and result',async()=>{
 for(const reset of ['clear','pagehide','pageshow']){const x=fixture.setup();await compare(x);if(reset==='clear')await x.ids['numbers-clear'].fire('click');else for(const fn of x.windowEvents[reset])fn({persisted:true});for(const id of fields)assert.equal(x.ids[id].value,'',reset+id);assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(result(x),'');assert.equal(x.requests.length,0);}
});

test('loading constructed example clears previous output and waits for submit',async()=>{
 const x=fixture.setup();await compare(x);await x.ids['numbers-example'].fire('click');assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(result(x),'');assert.ok(fields.every(id=>x.ids[id].value!==''));assert.equal(x.requests.length,0);await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,false);
});

test('bad or native-invalid values cannot retain a previous calculation',async()=>{
 for(const items of [['101','100','30','200'],['0','0','30','200'],['0.5','100','30','200'],['9007199254740992','9007199254740992','30','200'],['','100','30','200']]){const x=fixture.setup();await compare(x);values(x,items);await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(result(x),'');assert.equal(x.requests.length,0);}
 const x=fixture.setup();await compare(x);x.ids['numbers-form'].valid=false;await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(result(x),'');
});

test('zero baseline is an undefined relative change rather than an infinity or causal claim',async()=>{
 const x=fixture.setup();values(x,['0','100','1','100']);await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,false);assert.doesNotMatch(x.ids['numbers-facts'].textContent,/Infinity|NaN|caused|statistically significant|claim is true/);assert.match(x.ids['numbers-facts'].textContent,/Undefined.*rate is zero/);assert.match(x.ids['numbers-questions'].textContent,/do not establish statistical significance, causation, data quality or whether a claim is true/);assert.equal(x.requests.length,0);
});

test('empty guidance follows the explicit comparison lifecycle',async()=>{
 const x=fixture.setup();assert.equal(x.ids['numbers-empty'].hidden,false);await compare(x);assert.equal(x.ids['numbers-empty'].hidden,true);await x.ids['count-a'].fire('input');assert.equal(x.ids['numbers-empty'].hidden,false);await compare(x);await x.ids['numbers-clear'].fire('click');assert.equal(x.ids['numbers-empty'].hidden,false);
});
