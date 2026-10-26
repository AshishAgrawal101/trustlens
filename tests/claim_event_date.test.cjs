const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),vm=require('node:vm');
const claim=require('../static/claim-review.js');
const root=path.join(__dirname,'..'),baseline=JSON.parse(fs.readFileSync(path.join(root,'verification/event-context-20261024/old-output-contract.json'),'utf8'));
test('omitted and blank event date preserve frozen old outputs and PLAN bytes',()=>{
  for(const row of baseline)for(const event of [{},{eventDate:''}]){const input={...row.input,...event};assert.deepEqual(claim.review(input,row.today),row.review);assert.deepEqual(claim.analyze(input,row.today),row.analyze);}
  assert.equal(crypto.createHash('sha256').update(claim.PLAN).digest('hex'),fs.readFileSync(path.join(root,'verification/event-context-20261024/plan-before.sha256'),'utf8').trim());
});
test('event chronology observes leap-year year-boundary same-day and after without a truth judgment',()=>{
  for(const [eventDate,aDate,relation,gap]of [['2024-03-01','2024-02-28','before',2],['2024-01-01','2023-12-31','before',1],['2024-03-01','2024-03-01','same',0],['2024-03-01','2024-03-03','after',2]]){
    const result=claim.review({claim:'Constructed claim.',eventDate,aDate,aQuote:'Supplied account.'},'2024-03-04');
    const row=result.observations.find(row=>row.id==='dates:a:'+relation);assert.ok(row,relation);
    assert.match(row.text,/supplied|unverified/i);if(gap)assert.match(row.text,new RegExp(gap+' calendar days? '+relation));else assert.match(row.text,/same calendar date/);
    assert.doesNotMatch(row.text,/proves|credible|corroborated|authentic|is false/i);if(relation==='before')assert.match(row.text,/announcement/);
  }
  const result=claim.review({claim:'Claim',eventDate:'2024-03-01',aDate:'2024-02-28',aQuote:'A',bDate:'2024-03-03',bUrl:'https://b.example/'},'2024-03-04');assert.ok(result.observations.some(row=>row.id==='dates:b:after'));
});
test('missing publication and date-only inputs never create dated source accounts or invented gaps',()=>{
  const missing=claim.review({claim:'Claim',eventDate:'2024-03-01',aQuote:'Account'},'2024-03-04');assert.ok(missing.questions.some(row=>row.id==='source:a:missing_date'));assert.ok(!missing.observations.some(row=>/^dates:[ab]:/.test(row.id)));
  const alone=claim.review({claim:'Claim',eventDate:'2024-03-01',aDate:'2024-02-28',bDate:'2024-03-03'},'2024-03-04');assert.ok(alone.observations.some(row=>row.id==='sources:zero'));assert.ok(!alone.observations.some(row=>/^dates:[ab]:/.test(row.id)));
});
test('invalid event dates reject with fixed private feedback',()=>{
  for(const eventDate of ['2023-02-29','2024-13-01','2024-03','PRIVATE-DATE-SECRET',42,null,{},'2024-03-01 '])assert.throws(()=>claim.review({claim:'Claim',eventDate},'2024-03-04'),error=>error instanceof Error&&!/PRIVATE|SECRET/.test(error.message));
});

let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/claim-review.html').replace('static/app.js','static/claim-review.js');
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function review(x){x.ids['claim-text'].value='Constructed claim.';x.ids['claim-event-date'].value='2024-03-01';x.ids['source-a-quote'].value='Source account.';x.ids['source-a-date'].value='2024-02-28';await x.ids['claim-form'].fire('submit');}
test('event field is optional unnamed and bounded; explicit review renders then exports only the existing fixed plan',async()=>{
  const html=fs.readFileSync(path.join(root,'static/claim-review.html'),'utf8'),tag=html.match(/<input\b[^>]*id="claim-event-date"[^>]*>/)?.[0];assert.ok(tag);assert.match(tag,/type="date"/);assert.doesNotMatch(tag,/\sname=|\srequired(?:\s|>)/);assert.match(html,/<label\b[^>]*for="claim-event-date"/);
  const x=fixture.setup();await review(x);assert.equal(x.ids['claim-result'].hidden,false);assert.match(x.ids['claim-observations'].textContent,/2 calendar days before/);assert.equal(x.requests.length,0);
  await x.ids['claim-copy-plan'].fire('click');await x.ids['claim-download-plan'].fire('click');assert.equal(x.clipboard[0],claim.PLAN);assert.equal(await x.blobs[0].text(),claim.PLAN);assert.doesNotMatch(claim.PLAN,/2024-03-01|Constructed claim/);
});
test('event edits examples Clear exit and persisted Back invalidate and erase as appropriate',async()=>{
  for(const action of ['input','change','clear','example','pagehide','pageshow']){
    const x=fixture.setup();await review(x);
    if(['input','change'].includes(action))await x.ids['claim-event-date'].fire(action);else if(action==='clear')await x.ids['claim-clear'].fire('click');else if(action==='example'){const examples=x.document.querySelectorAll('[data-claim-example]');examples[0].getAttribute=k=>examples[0].attributes[k];await examples[0].fire('click');}else for(const fn of x.windowEvents[action])fn({persisted:true});
    assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.ids['claim-observations'].textContent,'');assert.equal(x.ids['claim-copy-plan'].disabled,true);assert.equal(x.ids['claim-event-date'].value,['input','change'].includes(action)?'2024-03-01':action==='example'?'2024-06-15':'');assert.equal(x.requests.length,0);
  }
});
test('event date change prevents pending copy feedback from reviving after invalidation',async()=>{
  const x=fixture.setup();await review(x);let finish;x.state.writeText=()=>new Promise(resolve=>finish=resolve);const copy=x.ids['claim-copy-plan'].fire('click');
  x.ids['claim-event-date'].value='2024-03-02';await x.ids['claim-event-date'].fire('change');finish();await copy;
  assert.equal(x.ids['claim-copy-status'].textContent,'');assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.ids['claim-copy-plan'].disabled,true);
});
