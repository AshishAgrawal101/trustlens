const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const guide=require('../static/phone/guide.js');
const {receiveSharedText,sharedPage}=require('../static/phone/share.js');
const root=path.join(__dirname,'../static/phone');

test('literal IPv6 hosts survive sentence and bracket punctuation',()=>{
  assert.equal(guide.hosts('See https://[2001:db8::1].')[0].host,'[2001:db8::1]');
  assert.equal(guide.hosts('[https://example.test]')[0].host,'example.test');
  assert.equal(guide.hosts('https://[broken')[0].host,'Unreadable web address');
});
test('worker readiness requires every asset in the current cache',async()=>{
  const handlers={},stored=new Set();let message;
  const self={location:{origin:'https://local.test'},clients:{claim:async()=>{}},skipWaiting:async()=>{},addEventListener:(type,fn)=>handlers[type]=fn};
  const cache={addAll:async urls=>urls.forEach(u=>stored.add(u)),match:async url=>stored.has(url)?new Response('shell'):undefined};
  vm.runInNewContext(fs.readFileSync(path.join(root,'sw.js'),'utf8'),{self,caches:{open:async()=>cache,keys:async()=>[]},URL,Response,importScripts(){},receiveSharedText,sharedPage});
  let work;handlers.install({waitUntil:p=>work=p});await work;
  const status=async()=>{handlers.message({data:{type:'POCKET_STATUS'},ports:[{postMessage:data=>message=data}],waitUntil:p=>work=p});await work;return message;};
  assert.equal((await status()).ready,true);
  stored.delete('/phone/share-demo.js');assert.equal((await status()).ready,false);
  const version=message.cache;
  for(const file of ['index.html','share-demo.html'])assert.ok(fs.readFileSync(path.join(root,file),'utf8').includes('content="'+version+'"'));
});
test('constructed handoff declares bounded body sharing and cannot auto-submit',()=>{
  const html=fs.readFileSync(path.join(root,'share-demo.html'),'utf8');
  assert.match(html,/<form action="\/phone\/share" method="post"/);
  assert.match(html,/<textarea[^>]*name="text"[^>]*readonly>/);
  assert.match(html,/<button[^>]*type="submit" disabled>/);
  assert.match(html,/not an Android share sheet/);
  const script=fs.readFileSync(path.join(root,'share-demo.js'),'utf8');
  assert.doesNotMatch(script,/\.submit\(|requestSubmit\(|fetch\(/);
});
