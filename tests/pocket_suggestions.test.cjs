const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const suggestions=require('../static/phone/suggestions.js');

test('literal topics are bounded, deduplicated and retain matched evidence',()=>{
  const rows=suggestions.suggest('Buy gift cards. Read me your security code. Install AnyDesk. Keep this secret. Buy gift cards.');
  assert.deepEqual(rows.map(row=>row.topic),['money','code','device','secret']);
  assert.equal(rows[1].snippet,'Read me your security code');
  assert.ok(rows.every(row=>row.snippet.length<=120));
  assert.deepEqual(suggestions.suggest(''),[]);
  assert.throws(()=>suggestions.suggest('a'.repeat(30001)),/30,000/);
});

test('negation advice and completed history do not suggest current requests',()=>{
  for(const text of ['Do not buy gift cards.','Never share your password.','If anyone asks you to install AnyDesk, stop.','Yesterday he said to read me your security code.','Training example: buy gift cards.','Caller said “Read me your security code.”','Please share the source code.', 'We will not ask you to share your password.', "Caller said 'Read me your security code.'"])assert.deepEqual(suggestions.suggest(text),[],text);
  assert.deepEqual(suggestions.suggest('Never share your password.\nInstall AnyDesk.').map(row=>row.topic),['device']);
});

function setup(){
  const ids={},events={},topics=['money','code','device','secret'];
  class Element{
    constructor(){this.events={};this.children=[];this.value='';this.text='';this.checked=false;this.disabled=false;}
    addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
    dispatchEvent(event){this.fire(event.type);}
    setAttribute(name,value){(this.attributes??={})[name]=value;}
    fire(type){for(const fn of this.events[type]||[])fn({persisted:true});}
    replaceChildren(){this.children=[];this.text='';}
    append(...children){this.children.push(...children);}
    set textContent(value){this.text=value;this.children=[];}
    get textContent(){return this.text+this.children.map(c=>c.textContent).join('');}
    focus(){document.activeElement=this;}
  }
  for(const id of ['message','suggest-topics','suggestion-status','suggestion-results','guide','clear','example'])ids[id]=new Element();
  const checkboxes=topics.map(value=>Object.assign(new Element(),{value}));
  const document={getElementById:id=>ids[id],createElement:()=>new Element(),querySelectorAll:()=>checkboxes};
  const window={addEventListener:(type,fn)=>{(events[type]??=[]).push(fn);}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/phone/suggestions.js'),'utf8'),{document,window,Event:class{constructor(type){this.type=type;}}});
  return {ids,events,checkboxes,document};
}

test('suggest is opt-in; apply is a separate explicit topic action',()=>{
  const x=setup();x.ids.message.value='Read me your security code. Buy gift cards.';
  assert.equal(x.ids['suggestion-results'].children.length,0);
  x.ids['suggest-topics'].fire('click');
  assert.ok(x.checkboxes.every(input=>!input.checked));
  assert.match(x.ids['suggestion-status'].textContent,/not a fraud verdict/);
  const row=x.ids['suggestion-results'].children[0],button=row.children.at(-1);
  assert.match(row.textContent,/Read|Buy/);
  assert.equal(button.attributes['aria-label'],'Apply topic: Pay or move money');
  let changes=0;x.checkboxes[0].addEventListener('change',()=>changes++);
  button.fire('click');
  assert.equal(x.checkboxes[0].checked,true);assert.equal(changes,1);
  assert.equal(x.checkboxes[1].checked,false);
  assert.equal(x.document.activeElement,x.checkboxes[0]);
  assert.match(x.ids['suggestion-status'].textContent,/Topic selected/);
  assert.equal(button.attributes['aria-label'],'Topic already selected: Pay or move money');
});

test('private snippets clear on edits clear examples guide submission and page lifecycle',()=>{
  const x=setup();
  for(const [id,event] of [['message','input'],['clear','click'],['example','click'],['guide','submit']]){
    x.ids.message.value='Read me your security code.';x.ids['suggest-topics'].fire('click');
    assert.ok(x.ids['suggestion-results'].textContent);x.ids[id].fire(event);
    assert.equal(x.ids['suggestion-results'].textContent,'');assert.equal(x.ids['suggestion-status'].textContent,'');
  }
  for(const type of ['pagehide','pageshow']){
    x.ids.message.value='Buy gift cards.';x.ids['suggest-topics'].fire('click');
    for(const fn of x.events[type])fn({persisted:true});
    assert.equal(x.ids['suggestion-results'].textContent,'');
  }
});

test('manual topic changes update apply controls; empty matches preserve uncertainty',()=>{
  const x=setup();x.ids.message.value='Read me your security code.';x.ids['suggest-topics'].fire('click');
  const button=x.ids['suggestion-results'].children[0].children.at(-1);
  x.checkboxes[1].checked=true;x.checkboxes[1].fire('change');assert.equal(button.disabled,true);
  x.checkboxes[1].checked=false;x.checkboxes[1].fire('change');assert.equal(button.disabled,false);
  x.ids.message.value='Ordinary message';x.ids['suggest-topics'].fire('click');
  assert.match(x.ids['suggestion-status'].textContent,/does not establish safety/);
});


test('dots in amounts domains and abbreviations cannot erase advice context',()=>{
  for(const text of ['Do not send $1.00 or buy gift cards.', 'Do not visit example.com and install AnyDesk.', 'Never ask Mr. Smith to share your password.'])assert.deepEqual(suggestions.suggest(text),[],text);
  for(const [text,topic] of [['Send $1.00 or buy gift cards.','money'],['Visit bank.test and install AnyDesk.','device'],['Ask Mr. Smith to share your password.','code']])assert.deepEqual(suggestions.suggest(text).map(row=>row.topic),[topic],text);
  assert.deepEqual(suggestions.suggest('Never share your password. Install AnyDesk.'),[]);
});
