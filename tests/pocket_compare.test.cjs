const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const guide=require('../static/phone/guide.js');

test('known-site comparison uses exact normalized hosts, not brand text or suffixes',()=>{
  const text='https://bank.example/pay?secret=PRIVATE https://login.bank.example https://bank.example.evil.test https://bank.example@evil.test';
  const result=guide.compareHosts(text,'https://BANK.example./known-path');
  assert.deepEqual(result.rows.map(r=>r.match),[true,false,false,false]);
  assert.equal(result.known,'bank.example');assert.doesNotMatch(JSON.stringify(result),/PRIVATE|known-path/);
  assert.equal(guide.compareHosts('https://bücher.example','xn--bcher-kva.example').rows[0].match,true);
  assert.equal(guide.compareHosts('https://[bad','bank.example').rows[0].match,null);
});
test('invalid known routes never become trusted comparisons',()=>{
  for(const known of ['','bank.example other.test','https://bank.example@evil.test','file:///tmp/file','https://bank.example\\@evil.test','https://bank.example:bad'])assert.throws(()=>guide.compareHosts('https://bank.example',known));
});
test('comparison invalidates on edits and erases its known route on Clear and page exit',()=>{
  const ids={},events={};
  class Element{
    constructor(){this.events={};this.children=[];this.value='';this.text='';}
    addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
    fire(type){for(const fn of this.events[type]||[])fn({persisted:true});}
    replaceChildren(){this.children=[];this.text='';}
    append(child){this.children.push(child);}
    set textContent(value){this.text=value;this.children=[];}
    get textContent(){return this.text+this.children.map(c=>c.textContent).join('');}
    focus(){document.activeElement=this;}
  }
  for(const id of ['message','known-host','compare-hosts','compare-status','compare-results','guide','clear','example'])ids[id]=new Element();
  const document={getElementById:id=>ids[id],createElement:()=>new Element(),querySelectorAll:()=>[]};
  const window={addEventListener:(type,fn)=>{(events[type]??=[]).push(fn);}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/phone/compare.js'),'utf8'),{document,window,PocketGuide:guide});
  ids.message.value='https://bank.example@other.test';ids['known-host'].value='bank.example';ids['compare-hosts'].fire('click');
  assert.match(ids['compare-results'].textContent,/Different parsed hostname/);assert.match(ids['compare-status'].textContent,/safety remain unverified/);
  ids.message.fire('input');assert.equal(ids['compare-results'].textContent,'');
  ids['compare-hosts'].fire('click');ids.clear.fire('click');assert.equal(ids['known-host'].value,'');assert.equal(ids['compare-results'].textContent,'');
  ids['known-host'].value='private-internal.example';for(const fn of events.pagehide)fn();assert.equal(ids['known-host'].value,'');
});
