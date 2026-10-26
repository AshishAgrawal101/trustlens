'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {evaluate,CONTRACT_SHA}=require('../verification/scope-expansion/evaluate.cjs');
const retained=require('../verification/scope-expansion/results.json');
const result=evaluate();
for(const row of result.rows)test('frozen worksheet contract: '+row.id,()=>assert.deepEqual(row.failures,[]));
test('contract lineage, complete row coverage and network guard remain explicit',()=>{
 assert.equal(result.contract_sha256,CONTRACT_SHA);assert.equal(retained.contract_sha256,CONTRACT_SHA);
 assert.equal(result.rows.length,25);assert.equal(new Set(result.rows.map(x=>x.id)).size,25);
 assert.deepEqual(result.rows.map(x=>x.id),retained.rows.map(x=>x.id));assert.equal(result.network_calls,0);
});
test('host comparisons cannot establish independence and quote comparisons stay unresolved',()=>{
 for(const row of result.rows.filter(x=>x.result)){
  for(const obs of row.result.observations.filter(x=>x.id.startsWith('hosts:')))assert.match(obs.text,/does not establish independent reporting/);
  for(const q of row.result.questions.filter(x=>x.id==='quotes:compare'))assert.match(q.text,/factual meaning have not been checked/);
  for(const obs of row.result.observations.filter(x=>x.id==='quotes:identical'))assert.match(obs.text,/does not corroborate truth/);
  assert.equal(row.result.steps.length,4);assert.equal(Object.hasOwn(row.result,'confidence'),false);
 }
});
test('fixed plan and chronology never certify claim truth or include private inputs',()=>{
 assert.match(result.plan,/not a truth verdict/);assert.match(result.plan,/No source was visited or verified/);
 assert.doesNotMatch(result.plan,/PRIVATE_|library\.example|2026-10-22|09:00/);
 const future=result.rows.find(x=>x.id==='future-date');assert.match(future.result.questions.find(x=>x.id==='source:b:future_date').text,/does not disprove the claim/);
});
