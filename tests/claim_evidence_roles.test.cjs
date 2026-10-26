const {test}=require('node:test'),assert=require('node:assert/strict');
const {review:analyze,PLAN}=require('../static/claim-review.js');
const ids=rows=>rows.map(row=>row.id);
const base={claim:'PRIVATE CLAIM',aUrl:'https://a.example/report',aQuote:'PRIVATE A',bUrl:'https://b.example/report',bQuote:'PRIVATE B'};

test('user labels remain separate from observed source structure and never become a verdict',()=>{
 const result=analyze({...base,aRole:'supports',bRole:'challenges'},'2026-10-23');
 assert.ok(ids(result.labels).includes('labels:a:supports'));assert.ok(ids(result.labels).includes('labels:b:challenges'));
 assert.ok(ids(result.questions).includes('labels:human_judgment'));assert.doesNotMatch(JSON.stringify(result),/PRIVATE|verified support|truth score/);
 assert.doesNotMatch(PLAN,/PRIVATE/);assert.match(result.nextStep,/compare/i);
});

test('support-only and challenge-only labels expose a review gap without demanding false balance',()=>{
 for(const [role,code]of [['supports','coverage:no_challenge'],['challenges','coverage:no_support']]){
  const result=analyze({...base,aRole:role,bRole:role},'2026-10-23');assert.ok(ids(result.questions).includes(code));assert.ok(result.questions.some(row=>/not equal weight|not require equal weight/.test(row.text)));
 }
});

test('a selected role without an address or quotation cannot close a coverage gap',()=>{
 const result=analyze({claim:'Claim',aQuote:'Account',aRole:'supports',bRole:'challenges',bDate:'2026-01-01'},'2026-10-23');
 assert.ok(ids(result.questions).includes('coverage:no_challenge'));assert.ok(!ids(result.labels).includes('labels:b:challenges'));
});

test('unknown and invalid roles are handled explicitly with no private echo',()=>{
 const result=analyze(base,'2026-10-23');assert.ok(ids(result.labels).includes('labels:a:unsure'));assert.ok(ids(result.questions).includes('labels:unresolved'));
 for(const aRole of ['PRIVATE INVALID',true,{},'verified'])assert.throws(()=>analyze({...base,aRole},'2026-10-23'),error=>!error.message.includes('PRIVATE'));
});

test('literal HTTP authority is required rather than silently repairing source spelling',()=>{
 for(const aUrl of ['https:example.org/a','https:/example.org/a','https:///example.org/a','https:////example.org/a'])assert.throws(()=>analyze({...base,aUrl},'2026-10-23'),/HTTP|address/);
 assert.doesNotThrow(()=>analyze({...base,aUrl:'HTTPS://EXAMPLE.ORG/a'},'2026-10-23'));
});

test('quote equality explains its surrounding-whitespace normalization',()=>{
 const result=analyze({...base,aQuote:'  Same quote  ',bQuote:'Same quote'},'2026-10-23');assert.match(result.observations.find(row=>row.id==='quotes:identical').text,/trimming surrounding whitespace/);
});

test('opposite labels on the same quotation prompt context review without alleging factual contradiction',()=>{
 const result=analyze({...base,aRole:'supports',bRole:'challenges',aQuote:' Same quotation ',bQuote:'Same quotation'},'2026-10-23');
 assert.ok(ids(result.questions).includes('labels:opposed_same_quote'));assert.match(result.nextStep,/identical quotations/);assert.doesNotMatch(result.nextStep,/false|true|contradiction detected/);
 const paired=analyze({...base,aRole:'supports',bRole:'supports',aQuote:'Same quotation',bQuote:'Same quotation'},'2026-10-23');assert.ok(!ids(paired.questions).includes('labels:opposed_same_quote'));
});
