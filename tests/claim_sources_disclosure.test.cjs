const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.join(__dirname,'..'),before=require('../verification/claim-usability-20261024/source-before.json');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/claim-review.html').replace('static/app.js','static/claim-review.js');
harness=harness.replace("URL:{createObjectURL(blob){blobs.push(blob);return 'blob:fixture';},revokeObjectURL(url){revoked.push(url);}}","URL:class extends URL{static createObjectURL(blob){blobs.push(blob);return 'blob:fixture';}static revokeObjectURL(url){revoked.push(url);}}");
const fixture={require,__dirname,AbortController,AbortSignal,Blob,URL};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
const sourceIds=['source-a-url','source-a-quote','source-a-date','source-a-role','source-b-url','source-b-quote','source-b-date','source-b-role'];
async function review(x){x.ids['claim-text'].value='Constructed claim';await x.ids['claim-form'].fire('submit');}
test('one initially closed native disclosure keeps enabled optional fields and unchanged pure code PLAN and print privacy',()=>{
  const x=fixture.setup(),html=fs.readFileSync(path.join(root,'static/claim-review.html'),'utf8');assert.ok(x.ids['claim-sources']);assert.equal(x.ids['claim-sources'].open,false);assert.equal(x.ids['claim-sources-state'].hidden,true);
  const wrapper=html.match(/<details\b[^>]*id="claim-sources"[^>]*>([\s\S]*?)<\/details>/)?.[1];assert.ok(wrapper);assert.match(wrapper,/<summary/);for(const id of sourceIds){assert.ok(wrapper.includes('id="'+id+'"'));assert.notEqual(x.ids[id].disabled,true);}
  const code=fs.readFileSync(path.join(root,'static/claim-review.js'),'utf8'),hash=s=>crypto.createHash('sha256').update(s).digest('hex');let pure=code.split("if(typeof document!=='undefined')")[0];const factory='  function sourceUrlError(message,field){const error=new Error(message);error.field=field;return error;}';assert.equal(pure.split(factory).length-1,1);pure=pure.replace(factory+(pure.includes(factory+'\r\n')?'\r\n':'\n'),'');const calls=/sourceUrlError\('([^']*)',key\+'Url'\)/g;assert.equal([...pure.matchAll(calls)].length,3);pure=pure.replace(calls,"new Error('$1')");assert.equal(hash(pure),before.pureSha256);assert.equal(hash(require('../static/claim-review.js').PLAN),before.planSha256);
  assert.doesNotMatch(html,/<(?:input|textarea|select)\b[^>]*\sname=/);assert.match(html,/<noscript>/);assert.match(fs.readFileSync(path.join(root,'static/claim-review.css'),'utf8'),/body>\*\{display:none!important\}/);
});
test('closing sources retains every draft role and date and includes them in explicit review',async()=>{
  const x=fixture.setup();x.ids['claim-sources'].open=true;x.ids['source-a-url'].value='https://example.org/PRIVATE';x.ids['source-a-quote'].value='PRIVATE quote';x.ids['source-a-date'].value='2020-01-01';x.ids['source-a-role'].value='supports';
  await x.ids['source-a-quote'].fire('input');const snapshot=sourceIds.map(id=>x.ids[id].value);assert.equal(x.ids['claim-sources-state'].hidden,false);assert.equal(x.ids['claim-sources-state'].textContent,'Entries present · included in Review');
  await review(x);assert.equal(x.ids['claim-result'].hidden,false);x.ids['claim-sources'].open=false;await x.ids['claim-sources'].fire('toggle');assert.deepEqual(sourceIds.map(id=>x.ids[id].value),snapshot);assert.equal(x.ids['claim-result'].hidden,false);
  await x.ids['claim-form'].fire('submit');assert.match(x.ids['claim-labels'].textContent,/supporting/);assert.equal(x.ids['claim-sources'].open,false);assert.equal(x.requests.length,0);
});
test('date-only and role-only presence is descriptive and edits invalidate without counting a source',async()=>{
  for(const [id,value,event]of [['source-a-date','2020-01-01','input'],['source-b-role','challenges','change']]){
    const x=fixture.setup();await review(x);x.ids[id].value=value;await x.ids[id].fire(event);assert.equal(x.ids['claim-result'].hidden,true);assert.equal(x.ids['claim-sources-state'].hidden,false);assert.doesNotMatch(x.ids['claim-sources-state'].textContent,/2020|challenges/);
    await review(x);assert.match(x.ids['claim-observations'].textContent,/No source addresses/);assert.match(x.ids['claim-labels'].textContent,/no address or quotation/);
  }
});
test('native invalid source opens before default focus and custom source rejection also reveals correction fields',async()=>{
  const x=fixture.setup();await review(x);assert.equal(x.ids['claim-sources'].open,false);await x.ids['claim-form'].fire('invalid',{target:x.ids['source-a-url']});assert.equal(x.ids['claim-sources'].open,true);assert.equal(x.ids['claim-result'].hidden,true);
  x.ids['claim-sources'].open=false;await x.ids['claim-form'].fire('invalid',{target:x.ids['claim-text']});assert.equal(x.ids['claim-sources'].open,false);
  x.ids['source-a-url'].value='javascript:PRIVATE';await x.ids['claim-form'].fire('submit');assert.equal(x.ids['claim-sources'].open,true);assert.equal(x.document.activeElement,x.ids['claim-error']);assert.doesNotMatch(x.ids['claim-error'].textContent,/PRIVATE/);
});
test('examples reveal populated sources while Clear exit and persisted Back collapse and erase',async()=>{
  for(const action of ['clear','pagehide','pageshow']){
    const x=fixture.setup(),example=x.document.querySelectorAll('[data-claim-example]')[0];example.getAttribute=k=>example.attributes[k];await example.fire('click');assert.equal(x.ids['claim-sources'].open,true);assert.equal(x.ids['claim-sources-state'].hidden,false);assert.equal(x.ids['claim-result'].hidden,true);
    if(action==='clear')await x.ids['claim-clear'].fire('click');else for(const fn of x.windowEvents[action])fn({persisted:true});
    assert.equal(x.ids['claim-sources'].open,false);assert.equal(x.ids['claim-sources-state'].hidden,true);assert.equal(x.ids['claim-sources-state'].textContent,'');for(const id of sourceIds)assert.equal(x.ids[id].value,id.endsWith('-role')?'unsure':'');assert.equal(x.requests.length,0);
  }
});
