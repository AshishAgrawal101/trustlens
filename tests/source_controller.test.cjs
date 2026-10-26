// Combined quote/source controllers, using existing DOM double rather than a second implementation.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0]
 .replace('static/index.template.html','static/quote-context.html').replace('static/app.js','static/quote-context.js');
harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function find(x,quote='PRIVATE wording',source='Before PRIVATE wording after.'){x.ids['quote-original'].value=quote;x.ids['source-passage'].value=source;await x.ids['source-form'].fire('submit');}
const output=x=>x.ids['source-status'].textContent+x.ids['source-matches'].textContent;

test('source finding is explicit, literal text including markup and never sends or exports input',async()=>{
 const x=fixture.setup();x.ids['quote-original'].value='<script>x</script>';x.ids['source-passage'].value='Before <script>x</script> after.';await x.ids['source-passage'].fire('input');assert.equal(x.ids['source-result'].hidden,true);await x.ids['source-form'].fire('submit');assert.equal(x.ids['source-result'].hidden,false);assert.match(output(x),/1 non-overlapping exact match/);assert.match(output(x),/<script>x<\/script>/);const item=x.ids['source-matches'].children[0];assert.equal(item.tagName,'article');assert.equal(item.children[1].children[1].tagName,'mark');assert.equal(x.document.activeElement,x.ids['source-result']);assert.equal(x.requests.length,0);assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);
});

test('editing either dependency removes old matches; revised wording is independent of source finding',async()=>{
 for(const id of ['quote-original','source-passage']){const x=fixture.setup();await find(x);await x.ids[id].fire('input');assert.equal(x.ids['source-result'].hidden,true);assert.equal(output(x),'');assert.notEqual(x.ids['source-passage'].value,'');}
 const x=fixture.setup();await find(x);x.ids['quote-revised'].value='Another revised version';await x.ids['quote-revised'].fire('input');assert.equal(x.ids['source-result'].hidden,false);
});

test('source-only Clear preserves supplied versions while main Clear erases every private field/result',async()=>{
 const x=fixture.setup();x.ids['quote-revised'].value='Revised private';await find(x);await x.ids['source-clear'].fire('click');assert.equal(x.ids['source-passage'].value,'');assert.equal(x.ids['quote-original'].value,'PRIVATE wording');assert.equal(x.ids['quote-revised'].value,'Revised private');assert.equal(output(x),'');assert.equal(x.document.activeElement,x.ids['source-passage']);await find(x);await x.ids['quote-clear'].fire('click');for(const id of ['quote-original','quote-revised','source-passage'])assert.equal(x.ids[id].value,'');assert.equal(output(x),'');assert.equal(x.document.activeElement,x.ids['quote-original']);
});

test('constructed example replacement clears old source text and its result',async()=>{
 const x=fixture.setup();await find(x);await x.ids['quote-example'].fire('click');assert.match(x.ids['quote-original'].value,/park/);assert.equal(x.ids['source-result'].hidden,true);assert.equal(x.ids['source-passage'].value,'');assert.equal(output(x),'');
});

test('exit and persisted Back cannot restore long passage or source match context',async()=>{
 for(const event of ['pagehide','pageshow']){const x=fixture.setup();await find(x);for(const fn of x.windowEvents[event])fn({persisted:true});for(const id of ['quote-original','quote-revised','source-passage'])assert.equal(x.ids[id].value,'');assert.equal(output(x),'');assert.equal(x.ids['source-result'].hidden,true);}
});

test('errors cannot leave old or partial output, echo inputs or destroy drafts',async()=>{
 for(const bad of ['quote','source','native']){const x=fixture.setup();await find(x);if(bad==='quote')x.ids['quote-original'].value='PRIVATE'.repeat(600);else if(bad==='source')x.ids['source-passage'].value='PRIVATE'.repeat(5000);else x.ids['source-form'].valid=false;await x.ids['source-form'].fire('submit');assert.equal(output(x),'');assert.equal(x.ids['source-result'].hidden,true);assert.notEqual(x.ids['source-passage'].value,'');assert.doesNotMatch(x.ids['source-error'].textContent,/PRIVATE/);if(bad!=='native')assert.equal(x.document.activeElement,x.ids['source-error']);}
});

test('no-match remains unresolved and long repetitive passage renders only five windows with the full count',async()=>{
 const x=fixture.setup();await find(x,'Changed wording','This is other wording.');assert.match(output(x),/does not prove a quotation is fabricated/);assert.equal(x.ids['source-matches'].children.length,0);assert.equal(x.ids['source-window-note'].hidden,true);await find(x,'x','x'.repeat(30000));assert.match(output(x),/30000 non-overlapping exact matches/);assert.equal(x.ids['source-page-status'].textContent,'Matches 1–5 of 30000');assert.equal(x.ids['source-next'].disabled,false);assert.equal(x.ids['source-matches'].children.length,5);assert.equal(x.ids['source-window-note'].hidden,false);assert.match(output(x),/does not authenticate/);
});

test('cropped context windows visibly disclose omissions at their edges',async()=>{
 const x=fixture.setup();await find(x,'QUOTED','a'.repeat(200)+'QUOTED'+'b'.repeat(200));const context=x.ids['source-matches'].children[0].children[1].textContent;assert.ok(context.startsWith('…'));assert.ok(context.endsWith('…'));assert.ok(context.includes('QUOTED'));
});
