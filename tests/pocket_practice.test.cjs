const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {cases}=require('../static/phone/practice.js');

test('practice uses twelve fixed scenarios with one supported choice and explicit reasoning',()=>{
  assert.equal(cases.length,12);
  for(const item of cases){assert.equal(item.choices.length,3);assert.ok(item.choices[item.best]);assert.ok(item.why.length>70);}
  assert.ok(cases.some(item=>item.title==='A routine appointment'));
});

test('practice feedback, progression and reset do not touch private message text',()=>{
  class Element{
    constructor(){this.attributes={};this.events={};this.children=[];this.hidden=false;this.open=true;this.textContent='';}
    setAttribute(name,value){this.attributes[name]=value;}
    addEventListener(type,fn){this.events[type]=fn;}
    fire(type){this.events[type]?.();}
    append(child){this.children.push(child);}
    replaceChildren(){this.children=[];}
    focus(){this.focused=true;}
  }
  const ids={},events={};
  for(const id of ['practice','practice-start','practice-ads-start','practice-session','practice-progress','practice-title','practice-text','practice-options','practice-feedback','practice-next'])ids[id]=new Element();
  const document={getElementById:id=>{assert.ok(ids[id], 'Only practice elements may be accessed');return ids[id];},createElement:()=>new Element()};
  const window={addEventListener:(type,fn)=>events[type]=fn};
  vm.runInNewContext(fs.readFileSync(require.resolve('../static/phone/practice.js'),'utf8'),{document,window});
  ids['practice-start'].fire('click');
  assert.equal(ids['practice-session'].hidden,false);assert.match(ids['practice-progress'].textContent,/1 of 12/);
  ids['practice-options'].children[0].fire('click');
  assert.match(ids['practice-feedback'].textContent,/A useful next check/);
  assert.ok(ids['practice-options'].children.every(button=>button.disabled));
  assert.equal(ids['practice-next'].hidden,false);
  ids['practice-next'].fire('click');assert.match(ids['practice-progress'].textContent,/2 of 12/);
  ids['practice-options'].children[0].fire('click');assert.match(ids['practice-feedback'].textContent,/That is a useful next check/);
  events.pagehide();assert.equal(ids['practice-session'].hidden,true);assert.equal(ids['practice-options'].children.length,0);assert.equal(ids['practice-feedback'].textContent,'');
  ids['practice-start'].fire('click');ids.practice.open=false;ids.practice.fire('toggle');assert.equal(ids['practice-session'].hidden,true);
});
