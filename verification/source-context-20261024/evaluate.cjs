'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const folder=__dirname,HASH='7554de40b53410337188c9deb769303dbce0ea99e1d8299fef721ccee72c274a',sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function evaluate(){const bytes=fs.readFileSync(path.join(folder,'acceptance.json'));if(sha(bytes)!==HASH)throw Error('Frozen contract changed');const contract=JSON.parse(bytes),source=fs.readFileSync(path.join(folder,'../../static/source-context.js'));let networkCalls=0;const denied=()=>{networkCalls++;throw Error('I/O forbidden');},scope={module:{exports:{}},fetch:denied,XMLHttpRequest:denied};vm.runInNewContext(source.toString(),scope);const api=scope.module.exports;
 const rows=contract.cases.map(c=>{const failures=[];let result=null,error=null;try{result=JSON.parse(JSON.stringify(api.find(c.quote,c.source)));}catch(e){error=e.message;}
 if(error)failures.push('unexpected_error');else{
  if(result.total!==c.expected_total)failures.push('total');if(result.truncated!==c.expected_truncated)failures.push('truncated');
  if(!Array.isArray(result.matches)||JSON.stringify(result.matches.map(m=>m.start))!==JSON.stringify(c.expected_starts))failures.push('starts');else for(const m of result.matches){
   if(m.end!==m.start+c.quote.length||m.text!==c.quote||c.source.slice(m.start,m.end)!==m.text)failures.push('match_reconstruction');
   if(typeof m.before!=='string'||typeof m.after!=='string'||m.before.length>161||m.after.length>161)failures.push('context_bounds');
   else if(c.source.slice(m.start-m.before.length,m.end+m.after.length)!==m.before+m.text+m.after)failures.push('context_reconstruction');
  }
  if(JSON.stringify(result)!==JSON.stringify(api.find(c.quote,c.source)))failures.push('nondeterministic');
 }return {id:c.id,result,error,failures};});return {label:'Frozen exact supplied-source location acceptance, not authenticity or meaning',contract_sha256:HASH,source_sha256:sha(source),network_calls:networkCalls,rows,failures:rows.filter(r=>r.failures.length).length};}
module.exports={evaluate,HASH};if(require.main===module){const dest=path.join(folder,'results.json');if(fs.existsSync(dest))throw Error('Refusing to overwrite retained results');const result=evaluate();fs.writeFileSync(dest,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({cases:result.rows.length,failures:result.failures,network_calls:result.network_calls}));}
