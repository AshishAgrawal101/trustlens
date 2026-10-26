'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {evaluate,HASH}=require('../verification/source-context-20261024/evaluate.cjs');
const result=evaluate(),{find}=require('../static/source-context.js');
for(const row of result.rows)test('frozen source locator: '+row.id,()=>assert.deepEqual(row.failures,[]));
test('frozen lineage, complete rows and no network',()=>{assert.equal(result.contract_sha256,HASH);assert.equal(result.rows.length,12);assert.equal(result.network_calls,0);});
test('strict string and nonblank validation uses private-input-free errors',()=>{
 for(const bad of ['', ' \t\n ',null,undefined,3,true,[],{}])for(const [quote,source]of [[bad,'PRIVATE_SOURCE'],['PRIVATE_QUOTE',bad]])assert.throws(()=>find(quote,source),e=>!e.message.includes('PRIVATE'));
});
test('UTF16 quote/source limits inclusive, with either side separately enforced',()=>{
 const quote='x'.repeat(4000),source='x'.repeat(30000);assert.equal(find(quote,source).total,7);
 assert.throws(()=>find('x'.repeat(4001),'PRIVATE_SOURCE'),e=>!e.message.includes('PRIVATE'));
 assert.throws(()=>find('PRIVATE_QUOTE','x'.repeat(30001)),e=>!e.message.includes('PRIVATE'));
 assert.equal(find('😀'.repeat(2000),'😀'.repeat(15000)).total,7);
 assert.throws(()=>find('😀'.repeat(2001),'valid'));assert.throws(()=>find('valid','😀'.repeat(15001)));
});
test('leading/trailing whitespace is preserved rather than trimmed for matching',()=>{
 assert.equal(find(' a ','a').total,0);const r=find(' a ','x a y');assert.equal(r.total,1);assert.equal(r.matches[0].text,' a ');assert.equal(r.matches[0].start,1);
});
test('all occurrences counted after first five, with exact truncation boundary',()=>{
 assert.equal(find('x','x'.repeat(5)).truncated,false);const start=performance.now(),r=find('x','x'.repeat(30000));assert.equal(r.total,30000);assert.equal(r.matches.length,5);assert.equal(r.truncated,true);assert.ok(performance.now()-start<1000,'Loose guard against unbounded scanning; not a latency benchmark');
});
test('context limits extend only enough to retain boundary surrogate pairs',()=>{
 const before=result.rows.find(r=>r.id==='before-surrogate-boundary').result.matches[0];assert.equal(before.before.length,161);assert.ok(before.before.startsWith('😀'));assert.equal(before.after,'');
 const after=result.rows.find(r=>r.id==='after-surrogate-boundary').result.matches[0];assert.equal(after.after.length,161);assert.ok(after.after.endsWith('😀'));assert.equal(after.before,'');
 const regular=find('Q','a'.repeat(200)+'Q'+'b'.repeat(200)).matches[0];assert.equal(regular.before.length,160);assert.equal(regular.after.length,160);
});
