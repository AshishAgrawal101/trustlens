'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {evaluate,HASH}=require('../verification/numbers-context/evaluate.cjs');
const result=evaluate(),{compare}=require('../static/numbers-context.js');
for(const row of result.rows)test('frozen arithmetic: '+row.id,()=>assert.deepEqual(row.failures,[]));
test('frozen lineage and no pure-function network calls',()=>{assert.equal(result.contract_sha256,HASH);assert.equal(result.rows.length,12);assert.equal(new Set(result.rows.map(r=>r.id)).size,12);assert.equal(result.network_calls,0);});
const base={countA:1,totalA:2,countB:3,totalB:4};
for(const key of Object.keys(base))test('reject invalid safe-integer number for '+key,()=>{
 for(const value of [undefined,null,'1',true,false,NaN,Infinity,-Infinity,1.5,-1,Number.MAX_SAFE_INTEGER+1])assert.throws(()=>compare({...base,[key]:value}),String(key)+' accepted '+String(value));
});
test('denominator and numerator limits are enforced independently',()=>{
 for(const input of [{...base,totalA:0},{...base,totalB:0},{...base,countA:3},{...base,countB:5}])assert.throws(()=>compare(input));
 assert.doesNotThrow(()=>compare({countA:0,totalA:1,countB:1,totalB:1}));
});
test('zero rates do not become infinite or an invented relative zero',()=>{
 for(const countB of [0,1])assert.equal(compare({countA:0,totalA:1,countB,totalB:1}).relativePercent,null);
 assert.equal(compare({countA:1,totalA:1,countB:0,totalB:1}).relativePercent,-100);
});
test('swapping groups reverses points but relative percent has its own denominator',()=>{
 const a=compare(base),b=compare({countA:3,totalA:4,countB:1,totalB:2});
 assert.equal(a.percentagePoints,-b.percentagePoints);assert.equal(a.relativePercent,50);assert.ok(Math.abs(b.relativePercent+100/3)<1e-10);
});

test('separate numerical regression: nearly equal safe-max rates retain the true tiny difference',()=>{
 const n=Number.MAX_SAFE_INTEGER;
 const r=compare({countA:n-1,totalA:n,countB:n-2,totalB:n-1});
 // Exact cross-product difference is -1, although independently rounded rates coincide.
 assert.equal(r.rateA,r.rateB);assert.ok(r.percentagePoints<0);assert.ok(r.relativePercent<0);
 const expectedPoints=-100/(n*(n-1)),expectedRelative=-100/((n-1)*(n-1));
 assert.ok(Math.abs((r.percentagePoints-expectedPoints)/expectedPoints)<1e-14);
 assert.ok(Math.abs((r.relativePercent-expectedRelative)/expectedRelative)<1e-14);
});
