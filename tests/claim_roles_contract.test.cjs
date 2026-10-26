'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {evaluate,HASH}=require('../verification/evidence-roles/evaluate.cjs');
const retained=require('../verification/evidence-roles/results.json'),result=evaluate();
for(const row of result.rows)test('frozen human-role contract: '+row.id,()=>assert.deepEqual(row.failures,[]));
test('role contract bytes, row identities and network guard remain intact',()=>{
 assert.equal(result.contract_sha256,HASH);assert.equal(retained.contract_sha256,HASH);assert.equal(result.rows.length,18);assert.equal(result.network_calls,0);
 assert.deepEqual(result.rows.map(r=>r.id),retained.rows.map(r=>r.id));
});
test('labels describe interpretation rather than detected findings and no-source labels explain exclusion',()=>{
 for(const row of result.rows.filter(r=>r.result))for(const label of row.result.labels){
  if(label.id.endsWith(':missing'))assert.match(label.text,/not counted as an account/);
  else assert.match(label.text,/your interpretation, not a detected finding/);
 }
 for(const id of ['both-inactive-roles','date-only-is-not-account'])assert.equal(result.rows.find(r=>r.id===id).active_role_ids.length,0);
});
test('opposed roles do not produce balance, resolution or automated support claims',()=>{
 for(const id of ['support-and-challenge','same-host-opposed-roles']){
  const r=result.rows.find(r=>r.id===id).result;
  assert.match(r.nextStep,/keeping the claim unresolved/);
  assert.match(r.questions.find(q=>q.id==='labels:human_judgment').text,/has not checked relevance, reliability, factual support or source independence/);
 }
 for(const row of result.rows.filter(r=>r.result))for(const q of row.result.questions.filter(q=>q.id.startsWith('coverage:')))assert.match(q.text,/do not require equal weight/);
 assert.match(result.plan,/not a truth verdict/);
});
