'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const dir=__dirname,bytes=fs.readFileSync(path.join(dir,'acceptance.json')),contract=JSON.parse(bytes);let networkCalls=0;
const context={module:{exports:{}},fetch(){networkCalls++;throw Error('No network');},XMLHttpRequest:function(){networkCalls++;throw Error('No network');}};
const source=fs.readFileSync(path.join(dir,'../../static/source-context.js'),'utf8');vm.runInNewContext(source,context);
const find=context.module.exports.find,rows=[];let pageMessage=null;
for(const c of contract.valid){let actual,error=null;try{actual=find(c.quote,c.source,c.page);}catch(e){error=e.message;}rows.push({id:c.id,pass:!error&&JSON.stringify(actual)===JSON.stringify(c.expected),actual,error});}
for(const c of contract.errors){let error=null;try{find(c.quote,c.source,c.page);}catch(e){error=e.message;}if(pageMessage===null&&error)pageMessage=error;rows.push({id:c.id,pass:Boolean(error)&&!error.includes('PRIVATE')&&error===pageMessage,error});}
const output={contract_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),source_sha256:crypto.createHash('sha256').update(source).digest('hex'),network_calls:networkCalls,rows};
if(require.main===module){fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify(output,null,2)+'\n');console.log(rows.filter(r=>r.pass).length+'/'+rows.length+' oracle rows; network calls '+networkCalls);if(networkCalls||rows.some(r=>!r.pass))process.exitCode=1;}
module.exports=output;
