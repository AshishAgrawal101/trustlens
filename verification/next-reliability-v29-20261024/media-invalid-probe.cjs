const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');const testDir=path.join(process.cwd(),'tests');
const prefix=fs.readFileSync(path.join(testDir,'media_context.test.cjs'),'utf8').split("test('metadata yields")[0];
const fixture={require:require("node:module").createRequire(path.join(testDir,"media_context.test.cjs")),__dirname:testDir,AbortController,AbortSignal,Blob};vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;this.file=file;this.report=report;',fixture);
(async()=>{const x=fixture.setup();await fixture.file(x);x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.ids['media-form'].fire('submit');const before=x.requests.length;x.ids['media-form'].valid=false;await x.ids['media-form'].fire('invalid');console.log(JSON.stringify({oldResultVisible:!x.ids['media-result'].hidden,oldFactsRetained:!!x.ids['media-facts'].textContent,extraRequests:x.requests.length-before}));})();

