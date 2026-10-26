const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const frozen=require('../verification/ads-context-20261024/frozen-cases.json');
const desktop=require('../static/learning-practice.js').cases,pocket=require('../static/phone/practice.js').cases;
function fixture(file){const text=fs.readFileSync(path.join(__dirname,file),'utf8').split("test('")[0],box={require,__dirname};vm.runInNewContext(text+'\nthis.setup=setup;',box);return box.setup();}
test('previous cases retain exact order and bytes while two frozen constructed cases are added to both practice flows',()=>{
  for(const [name,cases]of [['desktop',desktop],['pocket',pocket]]){
    const prior=frozen.preservation[name];assert.equal(cases.length,prior.count+2);assert.equal(crypto.createHash('sha256').update(JSON.stringify(cases.slice(0,prior.count))).digest('hex'),prior.sha256);
    for(const [i,row]of frozen.cases.entries()){const actual=cases[prior.count+i];for(const key of ['text','choices','why'])assert.deepEqual(actual[key],row[key]);assert.equal(name==='desktop'?actual.answer:actual.best,row.answer);}
  }
});
test('desktop complete ten-case journey includes ads feedback and retry/reset without stale callbacks or I/O',()=>{
  const x=fixture('learning_practice.test.cjs');x.open();let stale;
  for(const [i,c]of desktop.entries()){if(i===8)stale=x.ids.choices.children[0];x.answer(i===8?0:c.answer);x.next();}
  assert.equal(x.ids['practice-progress'].value,10);assert.equal(x.ids['practice-complete'].hidden,false);assert.match(x.ids['practice-recap'].textContent,/Ads|Endorsements/);
  x.ids['practice-again-missed'].fire('click');assert.equal(x.ids['practice-progress'].max,1);assert.equal(x.ids.scenario.textContent,frozen.cases[0].text);stale.fire('click');assert.equal(x.ids['practice-answer'].hidden,true);
  x.answer(frozen.cases[0].answer);x.next();x.ids['practice-restart'].fire('click');assert.equal(x.ids['practice-progress'].max,10);assert.equal(x.ids['practice-progress'].value,0);
  for(const fn of x.events.pagehide)fn({});assert.equal(x.ids['practice-dialog'].open,false);assert.equal(x.ids.choices.children.length,0);
});
test('Pocket twelve-case journey reaches both constructed examples and clears on close and Back',()=>{
  const x=fixture('pocket_context_practice.test.cjs');x.start();let old;
  for(const [i,c]of pocket.entries()){if(i===10){assert.equal(x.ids['practice-text'].textContent,frozen.cases[0].text);old=x.ids['practice-options'].children[0];}x.answer(c.best);assert.match(x.ids['practice-feedback'].textContent,/useful next check/i);x.next();}
  assert.match(x.ids['practice-progress'].textContent,/1 of 12/);old.fire('click');assert.equal(x.ids['practice-feedback'].textContent,'');
  x.ids.practice.open=false;x.ids.practice.fire('toggle');assert.equal(x.ids['practice-session'].hidden,true);assert.equal(x.ids['practice-options'].children.length,0);
  x.ids.practice.open=true;x.start();for(const fn of x.events.pageshow)fn({persisted:true});assert.equal(x.ids['practice-text'].textContent,'');assert.equal(x.ids['practice-options'].children.length,0);
});
test('new guide card uses native disclosure fixed checks and only passive internal worksheet navigation',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../static/phone/context.html'),'utf8'),card=html.match(/<details id="ads" class="card">([\s\S]*?)<\/details>/)?.[1];assert.ok(card);
  assert.equal((card.match(/<li>/g)||[]).length,3);assert.match(card,/<h3>Constructed example<\/h3>/);assert.match(card,/not.*fake|does not.*fake/i);assert.match(card,/href="\/phone\/workspace\/claims.html"/);assert.match(card,/Nothing is transferred automatically/);
  assert.doesNotMatch(card,/<script|<input|<form|https?:\/\//);assert.match(html,/href="#ads"/);
});
