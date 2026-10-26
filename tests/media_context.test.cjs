const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {review}=require('../static/media-context.js');
const report=()=>({format:'JPEG',width:40,height:20,display_width:40,display_height:20,bytes:400,capture_time:null,software:null,camera_make:null,camera_model:null,gps_present:false,notice:'Metadata is editable.'});
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0]
 .replace('static/index.template.html','static/media-context.html').replace('static/app.js','static/media-context.js')
 .replace('FormData:class{append(){}}','FormData:class{constructor(){this.items=[];}append(...args){this.items.push(args);}}');
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function file(x,type='image/png',size=200){x.ids['media-file'].files=[{type,size,name:'PRIVATE_FILENAME.png'}];await x.ids['media-file'].fire('change');}
async function inspect(x,data=report()){x.state.fetch=async()=>({ok:true,json:async()=>data});await x.ids['media-form'].fire('submit');}

test('metadata yields file facts and explicit limits, not origin or scene conclusions',()=>{
 const result=review({...report(),capture_time:'2027:01:01 12:00:00',software:'Editor label',camera_make:'Camera label',gps_present:true},'2026-10-23');
 assert.ok(result.questions.some(row=>row.id==='date:future'));assert.ok(result.questions.some(row=>row.id==='gps:privacy'));assert.match(JSON.stringify(result),/timezone|coordinates/);assert.ok(result.questions.some(row=>row.id==='origin:separate'));
 const absent=review(report(),'2026-10-23');assert.match(JSON.stringify(absent),/missing or unreadable/);assert.match(JSON.stringify(absent),/does not establish location privacy/);
});

test('consumed fields and display orientation are validated before rendering',()=>{
 for(const mutate of [r=>({...r,width:0}),r=>({...r,display_width:21}),r=>({...r,bytes:Infinity}),r=>({...r,gps_present:'yes'}),r=>({...r,capture_time:'2026:02:30 12:00:00'}),r=>({...r,software:'\nPRIVATE'}),r=>({...r,gps_coordinates:'PRIVATE'})])assert.throws(()=>review(mutate(report()),'2026-10-23'));
 assert.doesNotThrow(()=>review({...report(),display_width:20,display_height:40},'2026-10-23'));
});

test('file selection only previews; explicit inspection posts file only and never uploads caption',async()=>{
 const x=fixture.setup();x.ids['media-caption'].value='PRIVATE CAPTION';await file(x);assert.equal(x.requests.length,0);assert.equal(x.blobs.length,1);assert.equal(x.ids['media-preview'].src,'blob:fixture');
 await inspect(x);assert.equal(x.requests.length,1);assert.equal(x.requests[0].url,'/api/inspect/media');assert.equal(x.requests[0].options.body.items.length,1);assert.equal(x.requests[0].options.body.items[0][0],'file');assert.equal(x.ids['media-result'].hidden,false);assert.equal(x.document.activeElement,x.ids['media-result']);assert.doesNotMatch(x.ids['media-facts'].textContent+x.ids['media-questions'].textContent,/PRIVATE/);
});

test('invalid selection clears prior image pixels and rejects unsupported files before fetch',async()=>{
 const x=fixture.setup();await file(x);await inspect(x);await file(x,'image/gif');assert.equal(x.ids['media-preview'].src,undefined);assert.equal(x.revoked.length,1);assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-error'].hidden,false);assert.equal(x.requests.length,1);
});

test('Clear, replacement, exit and Back cannot restore old previews or late results',async()=>{
 for(const reset of ['clear','replace','pagehide','pageshow']){const x=fixture.setup();await file(x);x.ids['media-caption'].value='PRIVATE';let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.ids['media-form'].fire('submit');if(reset==='clear')await x.ids['media-clear'].fire('click');else if(reset==='replace')await file(x);else for(const fn of x.windowEvents[reset])fn({persisted:true});resolve({ok:true,json:async()=>report()});await pending;assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-facts'].textContent,'');if(reset!=='replace'){assert.equal(x.ids['media-preview'].src,undefined);assert.equal(x.ids['media-caption'].value,'');}assert.equal(x.revoked.length,1);}
});

test('Cancel preserves draft while rejecting late results',async()=>{
 {const x=fixture.setup();await file(x);x.ids['media-caption'].value='PRIVATE';let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.ids['media-form'].fire('submit');await x.ids['media-cancel'].fire('click');resolve({ok:true,json:async()=>report()});await pending;assert.equal(x.ids['media-preview'].src,'blob:fixture');assert.equal(x.ids['media-caption'].value,'PRIVATE');assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-submit'].disabled,false);}
});

test('malformed success and unreadable JSON preserve the draft without showing a partial result',async()=>{
 for(const mode of ['shape','json']){const x=fixture.setup();await file(x);x.ids['media-caption'].value='PRIVATE';x.state.fetch=async()=>({ok:true,json:async()=>{if(mode==='json')throw new Error('PRIVATE');return {...report(),width:'PRIVATE'};}});await x.ids['media-form'].fire('submit');assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-facts'].textContent,'');assert.equal(x.ids['media-preview'].src,'blob:fixture');assert.doesNotMatch(x.ids['media-error'].textContent,/PRIVATE/);}
});

test('server failures preserve drafts and give retry guidance instead of blaming the image',async()=>{
 for(const status of [500,503]){const x=fixture.setup();await file(x);x.ids['media-caption'].value='PRIVATE';x.state.fetch=async()=>({ok:false,status});await x.ids['media-form'].fire('submit');assert.match(x.ids['media-error'].textContent,/launcher|retry/);assert.equal(x.ids['media-caption'].value,'PRIVATE');assert.equal(x.ids['media-preview'].src,'blob:fixture');}
});
