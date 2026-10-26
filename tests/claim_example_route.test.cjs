const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.join(__dirname,'..');
const base=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/claim-review.html').replace('static/app.js','static/claim-review.js');
function setup(hash='',pathname='/static/claim-review.html',search=''){
  const location={hash,pathname,search},replaced=[];const history={replaceState(state,title,url){replaced.push({state,title,url});const next=new URL(url,'http://127.0.0.1');assert.equal(next.origin,'http://127.0.0.1');location.hash=next.hash;location.pathname=next.pathname;location.search=next.search;}};
  let harness=base.replace('setAttribute(k,v){this.attributes[k]=v;}','setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k];}');
  harness=harness.replace('window:{innerWidth:1200,','history,window:{location,innerWidth:1200,');
  harness=harness.replace('return {ids,state,','return {async route(hash){location.hash=hash;for(const fn of windowEvents.hashchange||[])await fn({});},ids,state,');
  const fixture={require,__dirname,AbortController,AbortSignal,Blob,history,location};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);return {...fixture.setup(),location,replaced};
}
test('main has one ordinary constructed-claim link with explicit separate Review and replacement wording',()=>{
  const html=fs.readFileSync(path.join(root,'static/index.template.html'),'utf8');assert.match(html,/<a\b[^>]*href="\/static\/claim-review.html#example=caption"[^>]*>Open a constructed photo-claim example/);
  assert.match(html,/Constructed fields replace.*Review separately/);assert.equal((html.match(/data-demo="/g)||[]).length,3);
  const css=fs.readFileSync(path.join(root,'static/styles.css'),'utf8');assert.match(css,/#claim-example-link\{[^}]*min-height:44px/);assert.match(css,/\.demo-bar :focus-visible[^}]*outline-color:#b5ee96/);
});
test('static initial Message help exactly matches the current configured English scope',()=>{
  const html=fs.readFileSync(path.join(root,'static/index.template.html'),'utf8'),source=fs.readFileSync(path.join(root,'static/app.js'),'utf8');
  const configured=source.match(/text: \{label:'[^']*', help:'([^']*)'/)?.[1];assert.ok(configured);assert.match(configured,/Wording rules cover English/);
  assert.equal(html.match(/<p id="input-help"[^>]*>([^<]*)<\/p>/)?.[1],configured);
});
test('both exact startup choices load existing constructed fields open Sources focus claim and consume the fragment without Review',()=>{
  for(const key of ['caption','headline']){
    const x=setup('#example='+key);assert.match(x.ids['claim-text'].value,key==='caption'?/15 June 2024/:/library/i);assert.equal(x.ids['claim-sources'].open,true);assert.equal(x.document.activeElement,x.ids['claim-text']);assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.requests.length,0);assert.equal(x.clipboard.length,0);assert.equal(x.blobs.length,0);
    assert.equal(x.location.hash,'');assert.deepEqual(x.replaced,[{state:null,title:'',url:'/static/claim-review.html'}]);
  }
});
test('same-document choices reuse replacement and invalidation while preserving current path/query without including fields',async()=>{
  const x=setup('','/phone/workspace/claims.html','?view=local');x.ids['claim-text'].value='PRIVATE draft';x.ids['source-a-quote'].value='PRIVATE source';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-result'].hidden,false);
  await x.route('#example=caption');assert.doesNotMatch(x.ids['claim-text'].value+x.ids['source-a-quote'].value,/PRIVATE/);assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.ids['claim-copy-plan'].disabled,true);assert.equal(x.ids['claim-sources'].open,true);assert.equal(x.replaced[0].url,'/phone/workspace/claims.html?view=local');assert.equal(x.location.hash,'');
  await x.ids['claim-clear'].fire('click');assert.equal(x.ids['claim-text'].value,'');await x.route('#example=caption');assert.match(x.ids['claim-text'].value,/15 June 2024/);assert.equal(x.replaced.length,2);assert.equal(x.requests.length,0);
});
test('unknown encoded partial private and newline-bearing fragments do not touch drafts result focus or history',async()=>{
  const bad=['','#claim-workspace','#example=other','#example=Caption','#example=%63aption','#example=caption&claim=PRIVATE','#example=headline?source=PRIVATE','#example=caption\n'];
  for(const hash of bad){const x=setup(hash);assert.equal(x.ids['claim-text'].value,'');assert.equal(x.replaced.length,0);}
  const x=setup();x.ids['claim-text'].value='PRIVATE draft';await x.ids['claim-form'].fire('submit');const focus=x.document.activeElement;
  for(const hash of bad){await x.route(hash);assert.equal(x.ids['claim-text'].value,'PRIVATE draft');assert.equal(x.ids['claim-result'].hidden,false);assert.equal(x.document.activeElement,focus);assert.equal(x.replaced.length,0);assert.equal(x.requests.length,0);}
});
test('Clear and persisted Back stay blank and closed after a consumed example; pure code and PLAN remain unchanged',async()=>{
  const x=setup('#example=caption');await x.ids['claim-clear'].fire('click');for(const fn of x.windowEvents.pageshow)fn({persisted:true});assert.equal(x.ids['claim-text'].value,'');assert.equal(x.ids['source-a-url'].value,'');assert.equal(x.ids['claim-sources'].open,false);assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.replaced.length,1);assert.equal(x.location.hash,'');
  const before=require('../verification/claim-onboarding-20261024/before.json'),hash=value=>crypto.createHash('sha256').update(value).digest('hex');let pure=fs.readFileSync(path.join(root,'static/claim-review.js'),'utf8').split("if(typeof document!=='undefined')")[0];const factory='  function sourceUrlError(message,field){const error=new Error(message);error.field=field;return error;}';assert.equal(pure.split(factory).length-1,1);pure=pure.replace(factory+(pure.includes(factory+'\r\n')?'\r\n':'\n'),'');const calls=/sourceUrlError\('([^']*)',key\+'Url'\)/g;assert.equal([...pure.matchAll(calls)].length,3);pure=pure.replace(calls,"new Error('$1')");assert.equal(hash(pure),before.pure);assert.equal(hash(require('../static/claim-review.js').PLAN),before.plan);
});
