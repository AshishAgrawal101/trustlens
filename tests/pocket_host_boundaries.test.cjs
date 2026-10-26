'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const guide=require('../static/phone/guide.js');
const message='https://example.com/page';
for(const known of ['https:/example.com','http:/example.com','https:///example.com','https:////example.com','https:example.com','http://?query','https://#fragment'])test('reject malformed explicit reference '+known,()=>{
 assert.throws(()=>guide.compareHosts(message,known));
});
test('raw reference Cc/Cf/Cs are rejected before trimming or normalization',()=>{
 for(const known of ['\texample.com','exa\u00admple.com','exa\u200bmple.com','exa\ufeffmple.com','https://example.com/\u202epath','https://example.com/\u0001path','https://example.com/\ud800'])assert.throws(()=>guide.compareHosts(message,known),e=>!e.message.includes('example.com'));
});
test('known references reject empty and nonempty raw userinfo syntax',()=>{
 for(const known of ['https://@example.com','https://:@example.com','https://reader@example.com','https://reader:PRIVATE@example.com'])assert.throws(()=>guide.compareHosts(message,known),e=>!e.message.includes('PRIVATE'));
});
test('formatted/control/surrogate literal tokens stay unreadable and later normal URLs remain inspected',()=>{
 for(const first of ['https://exa\u00admple.com/','https://exa\u200bmple.com/','https://exa\ufeffmple.com/','https://example.com/\u202epath','https://example.com/\u0001path','https://example.com/\ud800']){
  const text=first+' https://example.com/good',coverage=guide.hostCoverage(text),compared=guide.compareHosts(text,'example.com');
  assert.equal(coverage.items[0].host,'Unreadable web address');assert.equal(coverage.items[1].host,'example.com');assert.equal(coverage.remaining,0);
  assert.equal(compared.rows[0].match,null);assert.equal(compared.rows[1].match,true);
 }
});
test('ordinary IDNA, complete schemes, bare references and astral pairs remain supported',()=>{
 for(const known of ['example.com','HTTPS://example.com/😀',' https://example.com/path '])assert.equal(guide.compareHosts(message,known).rows[0].match,true);
 assert.equal(guide.compareHosts('https://faß.de/😀','xn--fa-hia.de').rows[0].match,true);
 assert.equal(guide.hostCoverage('https://example.com/😀').items[0].host,'example.com');
});
test('browser numeric canonicalization remains deliberate and unchanged',()=>{
 for(const known of ['127.1','0x7f000001','0177.0.0.1'])assert.equal(guide.compareHosts('https://127.0.0.1/',known).rows[0].match,true);
});
test('coverage and input bounds remain unchanged including malformed first token',()=>{
 const text=['https://exa\u200bmple.com/','https://exa\ufeffmple.com/',...Array.from({length:12},(_,i)=>'https://example.com/'+i)].join(' '),r=guide.compareHosts(text,'example.com');
 assert.equal(r.rows.length,12);assert.equal(r.remaining,2);assert.equal(r.rows[0].match,null);assert.equal(r.rows[1].match,null);
 assert.throws(()=>guide.hostCoverage('x'.repeat(30001)));assert.throws(()=>guide.compareHosts(message,'x'.repeat(4097)));
 assert.equal(guide.hostCoverage('x'.repeat(30000)).items.length,0);
});
test('message userinfo shows actual destination without becoming reference syntax',()=>{
 const r=guide.compareHosts('https://example.com@other.test/','example.com');assert.equal(r.rows[0].host,'other.test');assert.equal(r.rows[0].match,false);
 assert.match(guide.hostCoverage('https://example.com@other.test/').items[0].notes.join(' '),/before @/);
});
test('desktop manual fallback and exports keep fixed topic-only contract',()=>{
 assert.deepEqual(guide.nextSteps(['unknown']),guide.nextSteps([]));
 const selected=['money','code'],before=guide.summary(selected);try{guide.compareHosts('https://example.com/PRIVATE','https:/PRIVATE');}catch{}
 assert.equal(guide.summary(selected),before);assert.doesNotMatch(before,/PRIVATE|example\.com/);assert.match(before,/User-selected request topics; no automatic scam verdict/);
});
