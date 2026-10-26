'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {evaluate,HASH}=require('../verification/quote-context/evaluate.cjs');
const result=evaluate(),{compare}=require('../static/quote-context.js');
for(const row of result.rows)test('frozen literal comparison: '+row.id,()=>assert.deepEqual(row.failures,[]));
test('frozen contract, complete cases and no network',()=>{assert.equal(result.contract_sha256,HASH);assert.equal(result.rows.length,12);assert.equal(result.network_calls,0);});
test('strict strings and trimmed nonempty inputs on both sides',()=>{
 for(const bad of ['', ' \t\n ', null,undefined,0,true,[],{}]){assert.throws(()=>compare(bad,'valid'));assert.throws(()=>compare('valid',bad));}
});
test('UTF16 code-unit limit is inclusive and does not count Unicode code points instead',()=>{
 for(const good of ['x'.repeat(4000),'😀'.repeat(2000)])assert.equal(compare(good,good).identical,true);
 for(const bad of ['x'.repeat(4001),'😀'.repeat(2001)]){assert.throws(()=>compare(bad,'valid'));assert.throws(()=>compare('valid',bad));}
});
test('800 exact whitespace/nonwhitespace segments allowed, 801 rejected independently',()=>{
 const good='x '.repeat(400),bad='x '.repeat(400)+'x';assert.equal(good.match(/\s+|[^\s]+/gu).length,800);assert.equal(bad.match(/\s+|[^\s]+/gu).length,801);
 assert.equal(compare(good,good).identical,true);assert.throws(()=>compare(bad,'valid'));assert.throws(()=>compare('valid',bad));
});
test('long whitespace run is one segment and is preserved exactly',()=>{
 const original='a'+' '.repeat(3998)+'b',revised='a b',r=compare(original,revised);
 assert.equal(r.parts.filter(p=>p.type!=='added').map(p=>p.text).join(''),original);assert.equal(r.parts.filter(p=>p.type!=='removed').map(p=>p.text).join(''),revised);assert.equal(r.identical,false);
});

test('small independent brute-force subsequence oracle checks LCS length without fixing ambiguous alignments',()=>{
 const tokens=s=>s.match(/\s+|[^\s]+/gu)||[];
 const values=['a','b','a b','b a','a a','a b a','a\tb','a  b'];
 const isSubsequence=(small,big)=>{let i=0;for(const t of big)if(small[i]===t)i++;return i===small.length;};
 for(const a of values)for(const b of values){
  const ta=tokens(a),tb=tokens(b);let best=0;
  for(let bits=0;bits<2**ta.length;bits++){const seq=ta.filter((_,i)=>bits&(2**i));if(isSubsequence(seq,tb))best=Math.max(best,seq.length);}
  const result=compare(a,b),same=result.parts.filter(p=>p.type==='same').flatMap(p=>tokens(p.text));
  assert.equal(same.length,best,a+' vs '+b);assert.ok(isSubsequence(same,ta)&&isSubsequence(same,tb));
 }
});
