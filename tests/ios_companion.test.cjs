const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../static/phone/ios.js'),'utf8');
function setup(readText,writeText=async()=>{}){
 const ids={},events={},timers=new Map();let timerId=0;
 class Element{
  constructor(){this.value='';this.textContent='';this.events={};this.disabled=false;}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  fire(type){return Promise.all((this.events[type]||[]).map(fn=>fn({type,persisted:true})));}
  dispatchEvent(event){this.fire(event.type);}
  focus(){document.activeElement=this;}
 }
 for(const id of ['message','paste-message','paste-status','clear','example','guide','ios-recipe','copy-ios-recipe','recipe-status'])ids[id]=new Element();
 ids['ios-recipe'].textContent='MANUAL RECIPE: Text input → Copy to Clipboard (Local Only) → fixed HTTPS /phone/ → Open URLs. Never put Shortcut Input in the URL.';
 const choices=[new Element()];
 const document={getElementById:id=>ids[id],querySelectorAll:()=>choices};
 const navigator={clipboard:{...(readText?{readText}:{}),writeText}};
 vm.runInNewContext(source,{document,navigator,window:{addEventListener:(type,fn)=>{(events[type]??=[]).push(fn);}},Event:class{constructor(type){this.type=type;}},setTimeout:fn=>{timers.set(++timerId,fn);return timerId;},clearTimeout:id=>timers.delete(id)});
 return {ids,events,timers,document,choices};
}

test('iPhone paste reads only on click then dispatches the normal invalidation event',async()=>{
 let reads=0;const x=setup(async()=>{reads++;return '<PRIVATE> Read me your code.';});
 assert.equal(reads,0);let inputs=0;x.ids.message.addEventListener('input',()=>inputs++);
 await x.ids['paste-message'].fire('click');
 assert.equal(reads,1);assert.equal(x.ids.message.value,'<PRIVATE> Read me your code.');assert.equal(inputs,1);
 assert.equal(x.document.activeElement,x.ids.message);assert.match(x.ids['paste-status'].textContent,/Review/);
 assert.equal(x.ids['paste-message'].disabled,false);
});

test('unavailable denied empty and oversized clipboard preserve current input and give manual recovery',async()=>{
 for(const read of [undefined,async()=>{throw new Error('PRIVATE');},async()=>'',async()=>'x'.repeat(30001)]){
  const x=setup(read);x.ids.message.value='Keep my text';await x.ids['paste-message'].fire('click');
  assert.equal(x.ids.message.value,'Keep my text');assert.match(x.ids['paste-status'].textContent,/paste|Paste/);assert.doesNotMatch(x.ids['paste-status'].textContent,/PRIVATE/);
 }
});

test('pending paste cannot overwrite editing clear example submission topic changes or page exit',async()=>{
 for(const action of ['input','clear','example','guide','topic','pagehide','pageshow']){
  let resolve;const x=setup(()=>new Promise(r=>resolve=r));const pending=x.ids['paste-message'].fire('click');
  x.ids.message.value='Newer text';
  if(action==='input')await x.ids.message.fire('input');
  else if(action==='pagehide'||action==='pageshow')for(const fn of x.events[action])fn({persisted:true});
  else if(action==='topic')await x.choices[0].fire('change');
  else await x.ids[action].fire(action==='guide'?'submit':'click');
  resolve('STALE PRIVATE TEXT');await pending;
  assert.equal(x.ids.message.value,'Newer text',action);assert.equal(x.ids['paste-status'].textContent,'',action);assert.equal(x.ids['paste-message'].disabled,false);
 }
});

test('pending permission times out and a later answer does not paste',async()=>{
 let resolve;const x=setup(()=>new Promise(r=>resolve=r));const pending=x.ids['paste-message'].fire('click');
 for(const fn of [...x.timers.values()])fn();await pending;
 assert.match(x.ids['paste-status'].textContent,/manually/);assert.equal(x.ids['paste-message'].disabled,false);
 resolve('TOO LATE');await Promise.resolve();assert.equal(x.ids.message.value,'');
});

test('setup recipe copy is explicit fixed text and unavailable copy keeps selectable recipe',async()=>{
 const copies=[];const x=setup(undefined,async text=>copies.push(text));assert.equal(copies.length,0);
 await x.ids['copy-ios-recipe'].fire('click');assert.equal(copies.length,1);assert.equal(copies[0],x.ids['ios-recipe'].textContent);
 const y=setup(undefined,async()=>{throw new Error('denied');});await y.ids['copy-ios-recipe'].fire('click');
 assert.match(y.ids['recipe-status'].textContent,/select|Select/);
});


test('exact clipboard size bound accepts30000 and does not silently truncate larger text',async()=>{
 const x=setup(async()=>'a'.repeat(30000));await x.ids['paste-message'].fire('click');assert.equal(x.ids.message.value.length,30000);
 const y=setup(async()=>'a'.repeat(30001));y.ids.message.value='original';await y.ids['paste-message'].fire('click');assert.equal(y.ids.message.value,'original');
});

test('onboarding works without Pocket controls and copies only its fixed manual recipe',async()=>{
 const listeners={},copies=[];const recipe={textContent:'FIXED MANUAL RECIPE'};const button={addEventListener:(type,fn)=>listeners[type]=fn};const status={textContent:''};
 const document={getElementById:id=>({'ios-recipe':recipe,'copy-ios-recipe':button,'recipe-status':status}[id]||null)};
 vm.runInNewContext(source,{document,navigator:{clipboard:{readText(){assert.fail('No clipboard read on setup page');},async writeText(text){copies.push(text);}}},window:{addEventListener(){}},setTimeout,clearTimeout});
 assert.equal(copies.length,0);await listeners.click();assert.deepEqual(copies,['FIXED MANUAL RECIPE']);
});

test('iPhone setup keeps message text out of URLs and labels the manual installation boundary',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../static/phone/ios.html'),'utf8');
 assert.match(html,/not an installable shortcut/);assert.match(html,/Paste copied text/);assert.doesNotMatch(html,/Paste message/);assert.match(html,/replaces any text already/);assert.match(html,/Local Only/);assert.match(html,/Expire At/);assert.match(html,/https:\/\/YOUR-TRUSTED-HOST\/phone\//);
 assert.doesNotMatch(html,/shortcuts:\/\/|data:text|text=|input=text|javascript:/);
 assert.match(html,/not promise iPhone Web Share Target/);assert.match(html,/Physical iPhone installation has not been verified/);
 for(const resource of html.matchAll(/(?:src|href)="(\/phone\/[^"#]+\.(?:js|css))"/g))assert.ok(fs.existsSync(path.join(__dirname,'../static',resource[1])));
});


test('Shortcut navigation opens and focuses its disclosure including a repeated same hash',()=>{
 const events={},linkEvents={};let focuses=0;
 const panel={open:false,querySelector:selector=>{assert.equal(selector,'summary');return {focus(){focuses++;}};}};
 const link={addEventListener:(type,fn)=>linkEvents[type]=fn};
 const location={hash:'#shortcut'};
 const document={getElementById:id=>id==='shortcut'?panel:null,querySelectorAll:selector=>{assert.equal(selector,'a[href="#shortcut"]');return [link];}};
 vm.runInNewContext(source,{document,navigator:{clipboard:{readText(){assert.fail('Navigation must not read clipboard');}}},window:{location,addEventListener:(type,fn)=>events[type]=fn}});
 assert.equal(panel.open,true);assert.equal(focuses,1);
 panel.open=false;linkEvents.click({preventDefault(){}});assert.equal(panel.open,true);assert.equal(focuses,2);
 panel.open=false;events.hashchange();assert.equal(panel.open,true);assert.equal(focuses,3);
 panel.open=false;location.hash='#photo';events.hashchange();assert.equal(panel.open,false);assert.equal(focuses,3);
});

test('setup page uses the Pocket manifest start URL and existing Apple touch icon',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../static/phone/ios.html'),'utf8');
 assert.match(html,/rel="manifest" href="\/phone\/manifest.webmanifest"/);
 assert.match(html,/rel="apple-touch-icon" href="\/phone\/icon-192.png"/);
 assert.match(html,/name="apple-mobile-web-app-capable" content="yes"/);
 const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../static/phone/manifest.webmanifest'),'utf8'));assert.equal(manifest.start_url,'/phone/');
 assert.ok(fs.existsSync(path.join(__dirname,'../static/phone/icon-192.png')));
});


test('Shortcut anchor prevents only repeated same-hash default focus stealing',()=>{
 let click,prevented=0,focused=0;const location={hash:'#shortcut'};
 const panel={open:false,querySelector:()=>({focus(){focused++;}})};
 const document={getElementById:id=>id==='shortcut'?panel:null,querySelectorAll:()=>[{addEventListener:(type,fn)=>click=fn}]};
 vm.runInNewContext(source,{document,window:{location,addEventListener(){}},navigator:{}});
 panel.open=false;click({preventDefault(){prevented++;}});assert.equal(prevented,1);assert.equal(panel.open,true);assert.equal(focused,2);
 location.hash='#photo';panel.open=false;click({preventDefault(){prevented++;}});assert.equal(prevented,1);assert.equal(panel.open,true);assert.equal(focused,3);
});
