const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');const root=process.cwd(),testDir=path.join(root,'tests');const old=fs.readFileSync('verification/pocket-upgrade-integrity-v38-20261025/v37-claim.html.txt','utf8');
const shim={...fs,readFileSync(p,...args){return String(p).replaceAll('\\','/').endsWith('/static/claim-review.html')?old:fs.readFileSync(p,...args);}};
const customRequire=id=>id==='node:fs'?shim:require(id);
let harness=fs.readFileSync(path.join(testDir,'claim_controller.test.cjs'),'utf8').split('const fixture=')[0];
const fixture={require:customRequire,__dirname:testDir,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.harness=harness;',fixture);const actual={require:customRequire,__dirname:testDir,AbortController,AbortSignal,Blob};vm.runInNewContext(fixture.harness.replace('assert.ok(ids[id],`Missing element ${id}`);return ids[id];','return ids[id]??null;')+'\nthis.setup=setup;',actual);
try{actual.setup();console.log('setup completed');}catch(error){console.log(JSON.stringify({name:error.name,message:error.message,stack:error.stack.split('\n').slice(0,4)}));}



