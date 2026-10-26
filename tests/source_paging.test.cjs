const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{find}=require('../static/source-context.js');
test('two-argument results and default page remain exactly compatible with frozen outputs',()=>{
  for(const row of require('../verification/passage-paging-20261024/two-argument-before.json')){assert.deepEqual(find(row.quote,row.source),row.result);assert.deepEqual(find(row.quote,row.source,0),row.result);}
});
test('all pages retain exact offsets and literal windows with at most five matches',()=>{
  for(const count of [1,5,6,10,11]){const source=Array.from({length:count},(_,i)=>'before'+i+' Q after'+i+'|').join(''),offsets=[...source.matchAll(/Q/g)].map(m=>m.index);for(let page=0;page<Math.ceil(count/5);page++){
    const result=find('Q',source,page);assert.equal(result.total,count);assert.deepEqual(result.matches.map(m=>m.start),offsets.slice(page*5,page*5+5));assert.ok(result.matches.length<=5);
    for(const row of result.matches){assert.equal(row.text,'Q');assert.ok(source.slice(0,row.start).endsWith(row.before));assert.ok(source.slice(row.end).startsWith(row.after));}
  }}
  assert.equal(find('aa','aaa',0).total,1);assert.equal(find('Q','q q',0).total,0);assert.equal(find(' Q ','Q',0).total,0);assert.equal(find('<b>','<b>'.repeat(6),1).matches[0].start,15);
});
test('later-page surrogate boundaries and the maximum final page preserve existing window limits',()=>{
  const source=('Q'+'x'.repeat(400)).repeat(5)+'😀'+'a'.repeat(159)+'Q'+'b'.repeat(159)+'😀';const row=find('Q',source,1).matches[0];assert.ok(row.before.startsWith('😀'));assert.ok(row.after.endsWith('😀'));assert.equal(row.before.length,161);assert.equal(row.after.length,161);
  const last=find('x','x'.repeat(30000),5999);assert.equal(last.total,30000);assert.deepEqual(last.matches.map(row=>row.start),[29995,29996,29997,29998,29999]);assert.equal(last.truncated,true);
});
test('page validation is bounded integer-only and missing pages reject with input-free errors',()=>{
  for(const page of [-1,6000,.5,NaN,Infinity,null,'1',{},true])assert.throws(()=>find('PRIVATE','PRIVATE',page),error=>!error.message.includes('PRIVATE'));
  for(const [source,page]of [['not present',1],['PRIVATE'.repeat(5),1],['PRIVATE'.repeat(10),2]])assert.throws(()=>find('PRIVATE',source,page),error=>!error.message.includes('PRIVATE'));
});
let harness=fs.readFileSync(path.join(__dirname,'source_controller.test.cjs'),'utf8').split("test('source finding")[0];
harness=harness.replace("vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);","vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);vm.runInContext(fs.readFileSync(path.join(root,'static/unicode-notice.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=fixture.setup;',fixture);
async function search(x,count=11){x.ids['quote-original'].value='Q';x.ids['source-passage'].value=Array.from({length:count},(_,i)=>'row'+i+' Q\u200b end|').join('');await x.ids['source-form'].fire('submit');}
test('zero one and five matches do not offer unavailable page navigation',async()=>{
  for(const count of [0,1,5]){
    const x=fixture.setup();if(count)await search(x,count);else{x.ids['quote-original'].value='needle';x.ids['source-passage'].value='An unrelated passage.';await x.ids['source-form'].fire('submit');}
    assert.equal(x.ids['source-result'].hidden,false);assert.equal(x.ids['source-paging'].hidden,true);assert.equal(x.ids['source-prev'].disabled,true);assert.equal(x.ids['source-next'].disabled,true);assert.equal(x.ids['source-matches'].children.length,count);
    assert.equal(x.ids['source-page-status'].textContent,count?'Matches 1–'+count+' of '+count:'');await x.ids['source-next'].fire('click');assert.equal(x.ids['source-matches'].children.length,count);
  }
});
test('explicit navigation shows true ranges and ordinals with focus and disabled ends, retaining authenticity caveats',async()=>{
  const x=fixture.setup();await search(x);assert.equal(x.ids['source-page-status'].textContent,'Matches 1–5 of 11');assert.equal(x.ids['source-prev'].disabled,true);assert.equal(x.ids['source-next'].disabled,false);
  x.ids['source-next'].focus();await x.ids['source-next'].fire('click');assert.equal(x.ids['source-page-status'].textContent,'Matches 6–10 of 11');assert.match(x.ids['source-matches'].children[0].textContent,/Match 6 of 11/);assert.equal(x.document.activeElement,x.ids['source-next']);assert.equal(x.ids['source-page-status'].scrollOptions.block,'start');
  await x.ids['source-next'].fire('click');assert.equal(x.ids['source-page-status'].textContent,'Matches 11–11 of 11');assert.equal(x.ids['source-matches'].children.length,1);assert.equal(x.ids['source-next'].disabled,true);assert.equal(x.document.activeElement,x.ids['source-page-status']);await x.ids['source-next'].fire('click');assert.equal(x.ids['source-page-status'].textContent,'Matches 11–11 of 11');
  await x.ids['source-prev'].fire('click');assert.equal(x.ids['source-page-status'].textContent,'Matches 6–10 of 11');assert.match(x.ids['source-status'].textContent,/does not authenticate/);assert.equal(x.ids['source-formatting'].hidden,false);assert.equal(x.requests.length+x.clipboard.length+x.blobs.length,0);
});
test('every invalidation erases paging and formatting while next Find starts at first match',async()=>{
  for(const action of ['original','passage','source-clear','quote-clear','quote-example','pagehide','pageshow','invalid']){
    const x=fixture.setup();await search(x);await x.ids['source-next'].fire('click');
    if(action==='original'||action==='passage')await x.ids[action==='original'?'quote-original':'source-passage'].fire('input');else if(action==='pagehide'||action==='pageshow')for(const fn of x.windowEvents[action])fn({persisted:true});else if(action==='invalid')await x.ids['source-form'].fire('invalid',{target:x.ids['source-passage']});else await x.ids[action].fire('click');
    assert.equal(x.ids['source-result'].hidden,true,action);assert.equal(x.ids['source-paging'].hidden,true);assert.equal(x.ids['source-prev'].disabled,true);assert.equal(x.ids['source-next'].disabled,true);assert.equal(x.ids['source-page-status'].textContent,'');assert.equal(x.ids['source-matches'].textContent,'');assert.equal(x.ids['source-formatting'].hidden,true);await x.ids['source-next'].fire('click');assert.equal(x.ids['source-result'].hidden,true);await search(x);assert.equal(x.ids['source-page-status'].textContent,'Matches 1–5 of 11');
  }
});
