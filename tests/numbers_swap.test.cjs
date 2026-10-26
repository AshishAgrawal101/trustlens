const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const prefix=fs.readFileSync(path.join(__dirname,'numbers_controller.test.cjs'),'utf8').split("test('numbers require")[0],fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;',fixture);
const counts=['count-a','total-a','count-b','total-b'],percent=['percentage-a','percentage-b'];
const baseSetup=fixture.setup;fixture.setup=()=>{const x=baseSetup();for(const id of [...counts,...percent])x.ids[id].validity={badInput:false};return x;};
async function enter(x,ids,values){for(const [i,id]of ids.entries()){x.ids[id].value=values[i];await x.ids[id].fire('input');}}
async function method(x,value){x.ids['numbers-method'].value=value;await x.ids['numbers-method'].fire('change');}
const values=(x,ids)=>ids.map(id=>x.ids[id].value),facts=x=>x.ids['numbers-facts'].textContent;
test('swap is initially disabled native button and preserves pure math bytes and mobile target layout',()=>{
  const x=fixture.setup();assert.ok(x.ids['numbers-swap']);assert.equal(x.ids['numbers-swap'].disabled,true);assert.equal(x.ids['numbers-input-status'].textContent,'');
  const html=fs.readFileSync(path.join(__dirname,'../static/numbers-context.html'),'utf8'),tag=html.match(/<button\b[^>]*id="numbers-swap"[^>]*>/)?.[0];assert.ok(tag);assert.match(tag,/type="button"/);assert.match(tag,/\sdisabled(?:\s|>)/);assert.match(html,/id="numbers-input-status"[^>]*role="status"/);
  const css=fs.readFileSync(path.join(__dirname,'../static/numbers-context.css'),'utf8');assert.match(css,/#numbers-swap\{[^}]*min-height:48px/);assert.match(css,/\.submit-row\{[^}]*flex-wrap:wrap/);
  const source=fs.readFileSync(path.join(__dirname,'../static/numbers-context.js'),'utf8');assert.equal(crypto.createHash('sha256').update(source.split("if(typeof document!=='undefined')")[0]).digest('hex'),require('../verification/next-product-v29-20261024/swap-before.json').pureSha256);
});
test('count reversal swaps pairs clears old result and recalculates asymmetric baseline only on explicit Compare',async()=>{
  const x=fixture.setup();await enter(x,counts,['20','100','30','200']);await x.ids['numbers-form'].fire('submit');assert.match(facts(x),/About -25%/);
  x.ids['numbers-swap'].focus();await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,counts),['30','200','20','100']);assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(facts(x),'');assert.equal(x.document.activeElement,x.ids['numbers-swap']);assert.match(x.ids['numbers-input-status'].textContent,/baseline.*Compare proportions/);
  await x.ids['numbers-form'].fire('submit');assert.match(facts(x),/About 33\.3333%/);assert.equal(x.ids['numbers-input-status'].textContent,'');assert.equal(x.requests.length,0);
});
test('double swap preserves raw count strings and partial invalid drafts without silently validating',async()=>{
  for(const input of [['00020','00100','00030','00200'],['','100','3',''],['bad','100','2','100']]){
    const x=fixture.setup();await enter(x,counts,input);await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,counts),[input[2],input[3],input[0],input[1]]);await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,counts),input);assert.equal(x.ids['numbers-result'].hidden,true);
    if(input[0]==='bad'){await x.ids['numbers-form'].fire('submit');assert.equal(x.ids['numbers-result'].hidden,true);assert.equal(x.ids['numbers-error'].hidden,false);}
  }
});
test('percentage swap preserves exact strings active method and hidden inactive fields without denominator invention',async()=>{
  const x=fixture.setup();await method(x,'percentages');const input=['.000000000000000000000000000001','1.000000000000000000000000000001'];await enter(x,percent,input);x.ids['count-a'].value='UNTOUCHED';await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,percent),[input[1],input[0]]);assert.equal(x.ids['count-a'].value,'UNTOUCHED');assert.equal(x.ids['numbers-method'].value,'percentages');assert.equal(x.ids['count-a'].disabled,true);assert.equal(x.ids['percentage-a'].disabled,false);await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,percent),input);
  assert.doesNotMatch(x.ids['numbers-input-status'].textContent,/UNTOUCHED|000000/);assert.equal(x.requests.length+x.clipboard.length+x.blobs.length,0);
});
test('browser unparsed numeric entry is kept in place rather than assigning an unreadable empty value over it',async()=>{
  const x=fixture.setup();await enter(x,counts,['','100','2','100']);x.ids['count-a'].validity.badInput=true;const original=values(x,counts);await x.ids['numbers-swap'].fire('click');assert.deepEqual(values(x,counts),original);assert.match(x.ids['numbers-input-status'].textContent,/Finish the number entries/);assert.equal(x.ids['numbers-result'].hidden,true);
});
test('swapping the zero baseline changes orientation without changing Undefined arithmetic policy',async()=>{
  const x=fixture.setup();await method(x,'percentages');await enter(x,percent,['0','1']);await x.ids['numbers-form'].fire('submit');assert.match(facts(x),/Undefined: Group A’s rate is zero/);
  await x.ids['numbers-swap'].fire('click');assert.equal(x.ids['numbers-result'].hidden,true);await x.ids['numbers-form'].fire('submit');assert.match(facts(x),/About -100%/);assert.doesNotMatch(facts(x),/Undefined/);
  await x.ids['numbers-swap'].fire('click');await x.ids['numbers-form'].fire('submit');assert.match(facts(x),/Undefined: Group A’s rate is zero/);assert.equal(x.requests.length,0);
});
test('status readiness and stale results reset on every normal boundary without changing lifecycle defaults',async()=>{
  for(const action of ['input','submit','clear','example','method','invalid','pagehide','pageshow']){
    const x=fixture.setup();await method(x,'percentages');await enter(x,percent,['0','1']);await x.ids['numbers-swap'].fire('click');assert.ok(x.ids['numbers-input-status'].textContent);
    if(action==='input')await x.ids['percentage-a'].fire('input');else if(action==='submit')await x.ids['numbers-form'].fire('submit');else if(action==='clear'||action==='example')await x.ids['numbers-'+action].fire('click');else if(action==='method')await method(x,'counts');else if(action==='invalid')await x.ids['numbers-form'].fire('invalid');else for(const fn of x.windowEvents[action])fn({persisted:true});
    assert.equal(x.ids['numbers-input-status'].textContent,'',action);if(['clear','method','pagehide','pageshow'].includes(action))assert.equal(x.ids['numbers-swap'].disabled,true);if(action==='example')assert.equal(x.ids['numbers-swap'].disabled,false);if(action==='clear')assert.equal(x.ids['numbers-method'].value,'percentages');if(action==='pagehide'||action==='pageshow')assert.equal(x.ids['numbers-method'].value,'counts');assert.equal(x.requests.length,0);
  }
});
