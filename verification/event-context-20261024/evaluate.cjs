// Independent calendar oracle fixed in acceptance.json; no Date arithmetic here.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const bytes=fs.readFileSync(path.join(__dirname,'acceptance.json')),frozen=JSON.parse(bytes);
assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),'aba8c337a0b253ed7fb7eaf9e35316d53bd6c5d87a06bfdc94a0ba813c487b52');
const original=fs.readFileSync(path.join(__dirname,'baseline-v23-claim-review.js.txt'));
assert.equal(crypto.createHash('sha256').update(original).digest('hex'),fs.readFileSync(path.join(__dirname,'baseline-v23-claim-review.sha256'),'utf8').trim().split(/\s+/)[0]);
const context={module:{exports:{}},URL};vm.runInNewContext(original.toString(),context);const baseline=context.module.exports;
const current=require('../../static/claim-review.js');
assert.equal(current.PLAN,baseline.PLAN,'fixed PLAN unchanged');
const normalize=value=>JSON.parse(JSON.stringify(value));
let branches=0,asserted=0;
for(const row of frozen.cases){
 branches++;
 if(row.values){for(const value of row.values){assert.throws(()=>current.review({...frozen.base_input,eventDate:value},'2026-10-24'));asserted++;}continue;}
 const input={...frozen.base_input};for(const key of ['eventDate','aDate','bDate','aUrl','aQuote','bUrl','bQuote'])if(Object.hasOwn(row,key))input[key]=row[key];
 const result=current.review(input,'2026-10-24');
 if(!row.expected_observations){assert.deepEqual(normalize(result),normalize(baseline.review(input,'2026-10-24')),row.id+' old outputs preserved');}
 else{
  const dates=result.observations.filter(x=>/^dates:[ab]:/.test(x.id));
  assert.deepEqual(dates.map(x=>x.id).sort(),row.expected_observations.map(x=>x.id).sort(),row.id+' relations');
  for(const expected of row.expected_observations){const observed=dates.find(x=>x.id===expected.id);assert.match(observed.text,/unverified/i);if(expected.calendar_day_gap===0)assert.match(observed.text,/same calendar date/i);else assert.match(observed.text,new RegExp(expected.calendar_day_gap+' calendar day'));}
  assert.ok(result.questions.some(x=>/event/i.test(x.text)&&/supplied|unverified/i.test(x.text)),row.id+' event caveat');
 }
 assert.deepEqual(Object.keys(current.analyze(input,'2026-10-24')).sort(),['observations','questions','steps']);asserted++;
}
console.log(JSON.stringify({frozen_branches:branches,executed_inputs:asserted,plan_unchanged:true,passed:true}));
