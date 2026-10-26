const {test}=require('node:test');
const assert=require('node:assert/strict');
const {analyze,PLAN}=require('../static/claim-review.js');
const ids=rows=>rows.map(row=>row.id);

test('missing source evidence produces questions rather than a truth or credibility score',()=>{
 const result=analyze({claim:'PRIVATE CLAIM'},'2026-10-23');
 assert.ok(ids(result.observations).includes('sources:zero'));
 assert.ok(ids(result.questions).includes('context:missing'));
 assert.ok(ids(result.questions).includes('source:a:missing_url'));
 assert.doesNotMatch(JSON.stringify(result),/PRIVATE CLAIM|confidence|risk_index|true claim|false claim/);
 assert.equal(result.steps.length,4);
});

test('same and different source hosts both leave independence unverified',()=>{
 for(const [aUrl,bUrl,code] of [['https://NEWS.example/a','https://news.example/b','hosts:same'],['https://a.example/a','https://b.example/b','hosts:different']]){
  const result=analyze({claim:'Claim',aUrl,bUrl,aQuote:'Quote A',bQuote:'Quote B'},'2026-10-23');
  assert.ok(ids(result.observations).includes(code));
  assert.ok(ids(result.questions).includes('sources:independence'));
  assert.ok(ids(result.questions).includes('quotes:compare'));
 }
});

test('dates describe supplied chronology only, including future dates and missing dates',()=>{
 const result=analyze({claim:'This event happened yesterday',aDate:'2026-10-24',bDate:'2020-01-01'},'2026-10-23');
 assert.ok(ids(result.questions).includes('source:a:future_date'));
 assert.ok(ids(result.questions).includes('dates:context'));
 assert.doesNotMatch(JSON.stringify(result),/claim is false|outdated source|yesterday/);
 assert.doesNotThrow(()=>analyze({claim:'Leap',aDate:'2024-02-29'},'2026-10-23'));
 for(const date of ['2026-02-29','2026-02-30','23/10/2026','2026-13-01'])assert.throws(()=>analyze({claim:'Claim',aDate:date},'2026-10-23'),/valid calendar date/);
});

test('unsafe addresses and oversized fields fail with fixed private validation',()=>{
 for(const aUrl of ['javascript:alert(1)','data:text/html,PRIVATE','https://PRIVATE:password@news.example','not a URL']){
  assert.throws(()=>analyze({claim:'Claim',aUrl},'2026-10-23'),error=>!error.message.includes('PRIVATE')&&/HTTP|address/.test(error.message));
 }
 for(const input of [{claim:''},{claim:'x'.repeat(4001)},{claim:'Claim',aQuote:'x'.repeat(4001)},{claim:'Claim',aUrl:'https://a.example/'+ 'x'.repeat(4096)}])assert.throws(()=>analyze(input,'2026-10-23'));
});

test('generic plan does not incorporate supplied claims, quotes, contacts, paths or dates',()=>{
 const result=analyze({claim:'PRIVATE CLAIM',context:'PRIVATE CONTEXT',aUrl:'https://a.example/PRIVATE?token=PRIVATE',aQuote:'PRIVATE QUOTE',aDate:'2026-10-22'},'2026-10-23');
 assert.doesNotMatch(JSON.stringify(result)+PLAN,/PRIVATE|token=|2026-10-22/);
 assert.match(PLAN,/not a truth verdict/);
});
