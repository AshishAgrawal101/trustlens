const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
const evidence=id=>({...fixture.report().evidence[0],id,detail:'PRIVATE SCORE <script>bad()</script>'});
async function show(x,extra={}){x.state.fetch=async()=>({ok:true,json:async()=>({...fixture.report(),kind:'image',evidence:[],...extra})});await x.submit();}
const rows=x=>x.ids['cross-check-rows'].textContent;
test('only actually reported branches appear and combination is not counted as a third model',async()=>{
 const x=fixture.setup();await show(x,{model_ran:true,evidence:['image:clip','image:community','image:model'].map(evidence)});assert.equal(x.ids['cross-checks'].hidden,false);assert.match(rows(x),/CLIP pattern classifier/);assert.match(rows(x),/CommunityForensics/);assert.match(rows(x),/not a third independent model/);assert.doesNotMatch(rows(x),/PRIVATE|<script>|probability|3 models/);assert.match(x.ids['cross-check-status'].textContent,/does not establish agreement/);
 await show(x,{model_ran:true,evidence:[evidence('image:model')]});assert.doesNotMatch(rows(x),/CLIP|CommunityForensics/);assert.match(rows(x),/complete component breakdown was not reported/);
});
test('credential states are distinct and signed generated or edited history does not imply model agreement',async()=>{
 const labels={verified:/file binding.*trust validated/,untrusted:/trust was not established/,invalid:/validation failed/,absent:/No embedded credentials/,unavailable:/No credential verification result/,external:/not fetched or verified/};
 for(const [status,expected] of Object.entries(labels)){const x=fixture.setup();await show(x,{model_ran:false,content_credentials:{status,detail:'PRIVATE',declaration:'generated'}});assert.match(rows(x),expected);assert.doesNotMatch(rows(x),/PRIVATE|CLIP|CommunityForensics/);assert.match(x.ids['cross-check-status'].textContent,/did not return a model result/);}
 const x=fixture.setup();await show(x,{model_ran:true,content_credentials:{status:'verified',detail:'PRIVATE',declaration:'edited'},evidence:[evidence('image:model')]});assert.match(x.ids['cross-check-status'].textContent,/No component-disagreement finding was reported/);assert.doesNotMatch(x.ids['cross-check-status'].textContent,/components disagree|conflict/);
});
test('only explicit disagreement evidence produces the disagreement statement and no score parsing occurs',async()=>{
 const x=fixture.setup();await show(x,{model_ran:true,evidence:[evidence('image:disagreement')]});assert.match(x.ids['cross-check-status'].textContent,/components disagree/);assert.equal(rows(x).includes('CLIP'),false);assert.doesNotMatch(rows(x),/PRIVATE/);
});
test('communication reports hide and empty cross-checks; exports keep original safe-summary semantics',async()=>{
 const x=fixture.setup();await show(x,{evidence:[evidence('image:clip')]});await x.ids.copy.fire('click');assert.equal(x.clipboard[0],'Input-free summary');assert.equal(x.ids['print-summary'].textContent,'Input-free summary');
 await show(x,{kind:'text'});assert.equal(x.ids['cross-checks'].hidden,true);assert.equal(rows(x),'');assert.equal(x.ids['cross-check-status'].textContent,'');
});
test('edit, clear, mode and page lifecycle remove rows and pending responses cannot revive them',async()=>{
 for(const reset of ['input','clear','mode','pagehide','pageshow']){const x=fixture.setup();await show(x,{evidence:[evidence('image:clip')]});if(reset==='input')await x.ids.content.fire('input');else if(reset==='clear')await x.ids.clear.fire('click');else if(reset==='mode')await x.mode('call');else for(const fn of x.windowEvents[reset])fn({persisted:true});assert.equal(rows(x),'');assert.equal(x.ids['cross-checks'].hidden,true);}
 const x=fixture.setup();let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();await x.ids.clear.fire('click');resolve({ok:true,json:async()=>({...fixture.report(),kind:'image',evidence:[evidence('image:clip')]})});await pending;assert.equal(rows(x),'');assert.equal(x.ids['cross-checks'].hidden,true);
});

