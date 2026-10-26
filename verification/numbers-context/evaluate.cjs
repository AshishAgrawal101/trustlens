'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),vm=require('node:vm');
const folder=__dirname,HASH='28bb0edad81dcd514759998d08860d0b22f91dcb3970ad57fbd584260fa7c4bb',sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function evaluate(){
 const bytes=fs.readFileSync(path.join(folder,'acceptance.json'));if(sha(bytes)!==HASH)throw Error('Frozen arithmetic contract changed');const contract=JSON.parse(bytes),source=fs.readFileSync(path.join(folder,'../../static/numbers-context.js'));let networkCalls=0;
 const denied=()=>{networkCalls++;throw Error('Network forbidden');},sandbox={module:{exports:{}},fetch:denied,XMLHttpRequest:denied};vm.runInNewContext(source.toString(),sandbox);const api=sandbox.module.exports;
 const rows=contract.cases.map(c=>{const before=JSON.stringify(c.input),failures=[];let result=null,error=null;try{result=JSON.parse(JSON.stringify(api.compare(c.input)));}catch(e){error=e.message;}
  if(error)failures.push('unexpected_error');else{if(JSON.stringify(Object.keys(result).sort())!==JSON.stringify(Object.keys(c.expected).sort()))failures.push('unexpected_result_keys');for(const [key,expected]of Object.entries(c.expected)){if(expected===null){if(result[key]!==null)failures.push(key+':expected_null');}else if(typeof result[key]!=='number'||!Number.isFinite(result[key])||Math.abs(result[key]-expected)>contract.tolerance)failures.push(key+':value_mismatch');}}
  if(before!==JSON.stringify(c.input))failures.push('input_mutated');return {id:c.id,input:c.input,expected:c.expected,result,error,failures};
 });return {label:'Frozen exact-arithmetic acceptance, not significance or truth evaluation',contract_sha256:HASH,source_sha256:sha(source),network_calls:networkCalls,rows,failures:rows.filter(r=>r.failures.length).length};
}
module.exports={evaluate,HASH};if(require.main===module){const dest=path.join(folder,'results.json');if(fs.existsSync(dest))throw Error('Refusing to overwrite retained arithmetic results');const r=evaluate();fs.writeFileSync(dest,JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify({cases:r.rows.length,failures:r.failures,network_calls:r.network_calls}));}
