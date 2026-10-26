'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {inspect}=require('../static/unicode-notice.js');
const points=[0x00ad,0x061c,0x200b,0x200c,0x200d,0x200e,0x200f,0x202a,0x202b,0x202c,0x202d,0x202e,0x2060,0x2066,0x2067,0x2068,0x2069,0xfeff];
test('finite controls are counted/named without returning original text',()=>{
 const input='PRIVATE_MARKER'+points.map(point=>String.fromCodePoint(point)).join('')+'\u200b',r=inspect(input);
 assert.equal(r.total,19);assert.equal(r.counts.length,18);assert.equal(r.counts.find(x=>x.codePoint==='U+200B').count,2);assert.equal(r.directional,true);
 assert.doesNotMatch(JSON.stringify(r),/PRIVATE_MARKER|malicious|safe|fraud/i);assert.equal(input.includes('PRIVATE_MARKER'),true);
});
test('legitimate emoji and shaping joiners get factual counts, never normalization',()=>{
 const emoji='👩\u200d💻',persian='می\u200cروم';assert.equal(inspect(emoji).counts[0].name,'ZERO WIDTH JOINER');assert.equal(inspect(persian).counts[0].name,'ZERO WIDTH NON-JOINER');assert.equal(inspect(emoji).directional,false);
 assert.deepEqual(inspect('Ordinary العربية עברית café 😀'),{total:0,counts:[],directional:false});
});
test('bounded strict UTF16 input with fixed errors',()=>{
 assert.equal(inspect('\u200b'.repeat(30000)).total,30000);assert.throws(()=>inspect('PRIVATE'+ 'x'.repeat(30000)),e=>!e.message.includes('PRIVATE'));
 for(const bad of [null,undefined,true,3,{}])assert.throws(()=>inspect(bad));assert.deepEqual(inspect(''),{total:0,counts:[],directional:false});
});
class Node{constructor(){this.children=[];this.hidden=true;this.value='';this.events={};this._text='';}set textContent(t){this._text=String(t);this.children=[];}get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}append(...nodes){this.children.push(...nodes);}replaceChildren(){this.children=[];this._text='';}addEventListener(n,fn){(this.events[n]??=[]).push(fn);}fire(n){for(const fn of this.events[n]||[])fn({preventDefault(){}});}}
function setup(){
 const ids=Object.fromEntries(['quote-original','quote-revised','source-passage','quote-form','source-form','quote-result','source-result','quote-formatting','source-formatting','quote-clear','source-clear','quote-example'].map(id=>[id,new Node()]));const events={},state={quoteSuccess:true,sourceSuccess:true};
 ids['quote-form'].addEventListener('submit',()=>{ids['quote-result'].hidden=!state.quoteSuccess;});ids['source-form'].addEventListener('submit',()=>{ids['source-result'].hidden=!state.sourceSuccess;});
 const scope={module:{exports:{}},document:{getElementById:id=>ids[id],createElement:()=>new Node()},window:{addEventListener:(n,fn)=>(events[n]??=[]).push(fn)}};
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/unicode-notice.js'),'utf8'),scope);return {ids,events,state};
}
test('only explicit successful submissions show fixed presence details',()=>{
 const {ids,state}=setup();ids['quote-original'].value='PRIVATE\u200b';ids['quote-revised'].value='same';assert.equal(ids['quote-formatting'].hidden,true);ids['quote-form'].fire('submit');
 assert.equal(ids['quote-formatting'].hidden,false);assert.match(ids['quote-formatting'].textContent,/legitimate text/);assert.match(ids['quote-formatting'].textContent,/U\+200B/);assert.doesNotMatch(ids['quote-formatting'].textContent,/PRIVATE/);assert.equal(ids['quote-original'].value,'PRIVATE\u200b');
 state.quoteSuccess=false;ids['quote-form'].fire('submit');assert.equal(ids['quote-formatting'].hidden,true);
});
test('source notice scans all source text, including controls outside returned windows',()=>{
 const {ids}=setup();ids['quote-original'].value='Q';ids['source-passage'].value='Q'+'x'.repeat(1000)+'\u202e';ids['source-form'].fire('submit');assert.equal(ids['source-formatting'].hidden,false);assert.match(ids['source-formatting'].textContent,/display order/);assert.match(ids['source-formatting'].textContent,/U\+202E/);
});
test('absence hides notice and never produces reassurance',()=>{
 const {ids}=setup();ids['quote-original'].value='ordinary';ids['quote-revised'].value='ordinary';ids['quote-form'].fire('submit');assert.equal(ids['quote-formatting'].hidden,true);assert.equal(ids['quote-formatting'].textContent,'');
});
test('input, all clears/examples and exit reset correct notices',()=>{
 for(const trigger of ['quote-original','quote-revised','source-passage','quote-clear','source-clear','quote-example','pagehide','pageshow']){
  const {ids,events}=setup();ids['quote-original'].value='a\u00ad';ids['quote-revised'].value='b';ids['source-passage'].value='c\u200d';ids['quote-form'].fire('submit');ids['source-form'].fire('submit');
  if(events[trigger])for(const fn of events[trigger])fn({persisted:true});else ids[trigger].fire(['quote-clear','source-clear','quote-example'].includes(trigger)?'click':'input');
  const quoteClears=['quote-original','quote-revised','quote-clear','quote-example','pagehide','pageshow'].includes(trigger),sourceClears=trigger!=='quote-revised';
  if(quoteClears){assert.equal(ids['quote-formatting'].hidden,true);assert.equal(ids['quote-formatting'].textContent,'');}if(sourceClears){assert.equal(ids['source-formatting'].hidden,true);assert.equal(ids['source-formatting'].textContent,'');}
 }
});

test('both failed and native-invalid submissions clear a previous notice',()=>{
 for(const kind of ['quote','source'])for(const failure of ['failed','invalid']){
  const {ids,state}=setup();ids['quote-original'].value='a\u200b';ids['quote-revised'].value='b';ids['source-passage'].value='c\u200d';ids[kind+'-form'].fire('submit');assert.equal(ids[kind+'-formatting'].hidden,false);
  if(failure==='failed'){state[kind+'Success']=false;ids[kind+'-form'].fire('submit');}else ids[kind+'-form'].fire('invalid');
  assert.equal(ids[kind+'-formatting'].hidden,true);assert.equal(ids[kind+'-formatting'].textContent,'');
 }
});
test('root markup provides hidden polite status regions and correct controller order',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../static/quote-context.html'),'utf8');
 for(const id of ['quote-formatting','source-formatting']){const tag=html.match(new RegExp('<[^>]+id="'+id+'"[^>]*>'))?.[0];assert.ok(tag);assert.match(tag,/hidden/);assert.match(tag,/role="status"/);assert.match(tag,/aria-live="polite"/);}
 assert.ok(html.indexOf('src="/static/quote-context.js"')<html.indexOf('src="/static/source-context.js"'));assert.ok(html.indexOf('src="/static/source-context.js"')<html.indexOf('src="/static/unicode-notice.js"'));
 const helper=fs.readFileSync(path.join(__dirname,'../static/unicode-notice.js'),'utf8');assert.doesNotMatch(helper,/(?:fetch|localStorage|sessionStorage|XMLHttpRequest)\s*[(.]/);
});
