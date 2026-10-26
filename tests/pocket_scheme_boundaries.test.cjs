'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const guide=require('../static/phone/guide.js');
for(const known of ['ftp:/example.com','file:/example.com','foo:/example.com','ftp:','foo:PRIVATE','mailto:PRIVATE@example.com'])test('unsupported malformed scheme rejected: '+known,()=>{
 assert.throws(()=>guide.compareHosts('https://example.com/',known),e=>!e.message.includes('PRIVATE')&&/HTTP\(S\)/.test(e.message));
});
test('decimal hostname ports, paths and queries remain bare-site references',()=>{
 for(const known of ['example.com:8080','intranet:8080','intranet:8080/path','example.com:8080?x=1','example.com:8080#part','example.com/path:8080']){
  const expected=known.startsWith('intranet')?'intranet':'example.com';assert.equal(guide.compareHosts('https://'+expected+'/',known).known,expected);
 }
});
test('ambiguous scheme-shaped decimal port is explicitly interpreted as hostname port',()=>{
 const result=guide.compareHosts('https://ftp/','ftp:80');assert.equal(result.known,'ftp');assert.equal(result.rows[0].match,true);
});
test('proper unsupported protocols reject and bracketed IPv6 stays supported',()=>{
 for(const known of ['ftp://example.com','file://example.com','foo://example.com'])assert.throws(()=>guide.compareHosts('https://example.com/',known));
 for(const known of ['[::1]','[::1]:8080','http://[::1]:8080/path'])assert.equal(guide.compareHosts('https://[::1]/',known).rows[0].match,true);
});
test('existing malformed HTTP guard and fixed guidance behavior stay intact',()=>{
 for(const known of ['https:/example.com','https:80','http:80'])assert.throws(()=>guide.compareHosts('https://example.com/',known));
 const before=guide.summary(['code']);try{guide.compareHosts('https://PRIVATE/','foo:/PRIVATE');}catch{}assert.equal(guide.summary(['code']),before);assert.doesNotMatch(before,/PRIVATE/);
});
