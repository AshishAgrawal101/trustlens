const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'../static/phone'),staticRoot=path.join(root,'..');
const VERSION='trustlens-pocket-v35';
const STATIC_ASSETS=['/static/claim-review.css','/static/claim-review.js','/static/numbers-context.css','/static/numbers-context.js','/static/quote-context.css','/static/quote-context.js','/static/source-context.js','/static/unicode-notice.js'];
const WORKSPACES=['/phone/workspace/claims.html','/phone/workspace/numbers.html','/phone/workspace/quotes.html'];
// These route responses are transport fixtures, not copied renderer/app logic.
const ALIAS_FIXTURE='<!doctype html><html lang="en"><meta charset="utf-8"><title>Constructed workspace response</title><p>Safe cache transport fixture.</p></html>';
async function worker(){
 const handlers={},stored=new Map(),deleted=[];let work,reply,network=0;
 const cache={async addAll(urls){for(const url of urls){
  if(WORKSPACES.includes(url))stored.set(url,ALIAS_FIXTURE);
  else if(STATIC_ASSETS.includes(url))stored.set(url,fs.readFileSync(path.join(staticRoot,url.slice('/static/'.length)),'utf8'));
  else if(url.startsWith('/phone/'))stored.set(url,fs.readFileSync(path.join(root,url.slice('/phone/'.length)||'index.html'),'utf8'));
  else throw Error('Unexpected cached path in fixture: '+url);
 }},async match(url){return stored.has(url)?new Response(stored.get(url)):undefined;}};
 const self={location:{origin:'https://local.test'},clients:{claim:async()=>{}},skipWaiting:async()=>{},addEventListener:(key,fn)=>handlers[key]=fn};
 vm.runInNewContext(fs.readFileSync(path.join(root,'sw.js'),'utf8'),{self,caches:{open:async()=>cache,keys:async()=>['other-app','trustlens-pocket-v11','trustlens-pocket-v12','trustlens-pocket-v13','trustlens-pocket-v14','trustlens-pocket-v15','trustlens-pocket-v16','trustlens-pocket-v17','trustlens-pocket-v18',VERSION],delete:async key=>deleted.push(key)},URL,Response,importScripts(){},fetch:async()=>{network++;throw Error('Network forbidden');}});
 handlers.install({waitUntil:p=>work=p});await work;
 return {handlers,stored,deleted,get network(){return network;},async status(){handlers.message({data:{type:'POCKET_STATUS'},ports:[{postMessage:data=>reply=data}],waitUntil:p=>work=p});await work;return reply;},async activate(){handlers.activate({waitUntil:p=>work=p});await work;}};
}
function cachedFetch(w,url,method='GET'){let result;w.handlers.fetch({request:new Request(url,{method,...(method==='POST'?{body:'PRIVATE_FIXTURE'}:{})}),respondWith:p=>result=p});return result;}

test('context guide participates in exact-version readiness and old caches are scoped',async()=>{
 const w=await worker();assert.ok(w.stored.has('/phone/context.html'));const body=w.stored.get('/phone/context.html');assert.match(body,/Sources|source/i);assert.equal((await w.status()).ready,true);
 w.stored.delete('/phone/context.html');assert.equal((await w.status()).ready,false);w.stored.set('/phone/context.html',body);
 const status=await w.status();assert.equal(status.ready,true);assert.equal(status.cache,VERSION);
 for(const file of ['index.html','share-demo.html'])assert.ok(fs.readFileSync(path.join(root,file),'utf8').includes('content="'+VERSION+'"'));
 await w.activate();assert.deepEqual(w.deleted,['trustlens-pocket-v11','trustlens-pocket-v12','trustlens-pocket-v13','trustlens-pocket-v14','trustlens-pocket-v15','trustlens-pocket-v16','trustlens-pocket-v17','trustlens-pocket-v18']);assert.ok(!w.deleted.includes(VERSION));assert.ok(!w.deleted.includes('other-app'));
});

test('exact three aliases and eight static assets are admitted; every omission fails readiness',async()=>{
 const w=await worker();assert.deepEqual([...w.stored.keys()].filter(url=>url.startsWith('/static/')).sort(),[...STATIC_ASSETS].sort());
 assert.deepEqual([...w.stored.keys()].filter(url=>url.startsWith('/phone/workspace/')).sort(),[...WORKSPACES].sort());
 for(const url of [...WORKSPACES,...STATIC_ASSETS]){
  const body=w.stored.get(url);assert.ok(body,url);if(WORKSPACES.includes(url))assert.equal(body,ALIAS_FIXTURE);
  w.stored.delete(url);assert.equal((await w.status()).ready,false,'missing '+url);w.stored.set(url,body);assert.equal((await w.status()).ready,true,'restored '+url);
 }
 assert.equal(w.network,0);
});

test('context, workspace aliases and explicit static assets serve cached GETs without network',async()=>{
 const w=await worker();for(const pathname of ['/phone/context.html',...WORKSPACES,...STATIC_ASSETS]){
  const result=cachedFetch(w,'https://local.test'+pathname);assert.ok(result,pathname);const response=await result;assert.equal(response.status,200);assert.equal(await response.text(),w.stored.get(pathname));
 }
 assert.equal(w.network,0);
});

test('cache boundary excludes other static paths, queries, POSTs and cross-origin requests',async()=>{
 const w=await worker();
 for(const pathname of ['/phone/context.html',...WORKSPACES,...STATIC_ASSETS]){
  assert.equal(cachedFetch(w,'https://local.test'+pathname+'?private=PRIVATE_FIXTURE'),undefined,pathname+' query');
  assert.equal(cachedFetch(w,'https://other.test'+pathname),undefined,pathname+' cross-origin');
  assert.equal(cachedFetch(w,'https://local.test'+pathname,'POST'),undefined,pathname+' POST');
 }
 for(const pathname of ['/api/analyze/text','/static/tools.html','/static/claim-review.html','/static/media-context.js','/static/other.js','/phone/workspace/unknown.html'])assert.equal(cachedFetch(w,'https://local.test'+pathname),undefined,pathname);
 assert.ok([...w.stored.keys()].every(url=>(url.startsWith('/phone/')||STATIC_ASSETS.includes(url))&&!url.includes('?')));assert.equal(w.network,0);
});
