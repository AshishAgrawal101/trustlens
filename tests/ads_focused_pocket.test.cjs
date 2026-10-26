const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const frozen=require('../verification/next-scope-v31-20261024/focused-contract.json');
const {cases}=require('../static/phone/practice.js');
function setup(){const text=fs.readFileSync(require.resolve('./pocket_context_practice.test.cjs'),'utf8').split("test('")[0],box={require,__dirname};vm.runInNewContext(text+'\nthis.setup=setup;',box);return box.setup();}
test('focused Pocket session uses both exact frozen ad cases and repeats only that session',()=>{
 assert.equal(crypto.createHash('sha256').update(JSON.stringify(cases)).digest('hex'),frozen.pocket.sha256);
 const x=setup();x.ids['practice-ads-start'].fire('click');
 for(const [i,c]of frozen.pocket.ads.entries()){
  assert.equal(x.ids['practice-text'].textContent,c.text);assert.match(x.ids['practice-progress'].textContent,new RegExp((i+1)+' of 2'));
  assert.equal(x.active,x.ids['practice-title']);x.next();assert.equal(x.ids['practice-text'].textContent,c.text);
  const stale=x.ids['practice-options'].children[0];x.answer(c.best);const feedback=x.ids['practice-feedback'].textContent;stale.fire('click');assert.equal(x.ids['practice-feedback'].textContent,feedback);
  assert.equal(x.ids['practice-next'].textContent,i===1?'Practice again':'Next scenario');x.next();stale.fire('click');assert.equal(x.ids['practice-feedback'].textContent,'');
 }
 assert.equal(x.ids['practice-text'].textContent,frozen.pocket.ads[0].text);assert.match(x.ids['practice-progress'].textContent,/1 of 2/);
 x.start();assert.equal(x.ids['practice-text'].textContent,cases[0].text);assert.match(x.ids['practice-progress'].textContent,/1 of 12/);
});
test('switching sessions and close/exit/Back reject old focused callbacks and erase content',()=>{
 for(const event of ['toggle','pagehide','pageshow']){
  const x=setup();x.ids['practice-ads-start'].fire('click');const old=x.ids['practice-options'].children[0];x.answer(0);
  if(event==='toggle'){x.ids.practice.open=false;x.ids.practice.fire('toggle');}else for(const fn of x.events[event])fn({persisted:true});
  assert.equal(x.ids['practice-session'].hidden,true);assert.equal(x.ids['practice-options'].children.length,0);
  for(const id of ['practice-progress','practice-title','practice-text','practice-feedback'])assert.equal(x.ids[id].textContent,'');
  x.ids.practice.open=true;x.start();old.fire('click');assert.equal(x.ids['practice-feedback'].textContent,'');
  const prior=x.ids['practice-options'].children[0];x.ids['practice-ads-start'].fire('click');prior.fire('click');assert.equal(x.ids['practice-feedback'].textContent,'');assert.match(x.ids['practice-progress'].textContent,/1 of 2/);
 }
 const x=setup();x.ids.practice.open=false;x.ids['practice-ads-start'].fire('click');assert.equal(x.ids['practice-session'].hidden,true);
});
test('both Pocket start actions fail closed until setup and focused practice adds no input or export access',()=>{
 const html=fs.readFileSync(require.resolve('../static/phone/index.html'),'utf8');for(const id of ['practice-start','practice-ads-start'])assert.match(html,new RegExp('<button[^>]*id="'+id+'"[^>]*disabled'));
 const x=setup();assert.equal(x.ids['practice-start'].disabled,false);assert.equal(x.ids['practice-ads-start'].disabled,false);
 const source=fs.readFileSync(require.resolve('../static/phone/practice.js'),'utf8');assert.doesNotMatch(source,/fetch\(|localStorage|sessionStorage|clipboard|createObjectURL|location\.|get\(['"](?:message|content|file)/);
});
