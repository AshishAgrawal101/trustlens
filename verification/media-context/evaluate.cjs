'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const folder=__dirname,HASH='fbb7e5aa404186c5fa39a5bb50a7c99bc2a72591f413af67b71634ebe84a9877',sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function evaluate(){
 const bytes=fs.readFileSync(path.join(folder,'acceptance.json'));if(sha(bytes)!==HASH)throw Error('Frozen contract changed');const contract=JSON.parse(bytes),source=fs.readFileSync(path.join(folder,'../../static/media-context.js'));let networkCalls=0;
 const denied=()=>{networkCalls++;throw Error('Network forbidden');},scope={module:{exports:{}},URL,fetch:denied,XMLHttpRequest:denied};vm.runInNewContext(source.toString(),scope);const api=scope.module.exports;
 const rows=contract.cases.map(c=>{const m=c.illustrative_metadata;
  // Explicit illustrative-to-API adapter: no file decoding or caption submission is represented.
  const data={format:m.format,width:m.width,height:m.height,display_width:m.orientation===6?m.height:m.width,display_height:m.orientation===6?m.width:m.height,bytes:1024,capture_time:m.date??null,software:m.software??null,camera_make:null,camera_model:m.camera??null,gps_present:m.gps_present??false,notice:'Local fixture metadata; not authenticated.'};
  const original=JSON.stringify(data);let result=null,error=null;try{result=JSON.parse(JSON.stringify(api.review(data,contract.now)));}catch(e){error=e.message;}
  const failures=[],ids=result?result.questions.map(q=>q.id):[];
  const required=['metadata:mutable','story:context','dates:separate','origin:separate'];if(data.gps_present)required.push('gps:privacy');if(data.software)required.push('software:unverified');if(data.camera_model)required.push('camera:unverified');if(c.id==='date-future')required.push('date:future');
  if(c.id==='date-invalid'){if(error!=='Invalid embedded clock value.')failures.push('invalid_clock_not_rejected');}
  else {if(error)failures.push('unexpected_error');for(const id of required)if(!ids.includes(id))failures.push('missing_question:'+id);}
  if(result&&data.gps_present){const gps=result.facts.find(row=>row[0]==='GPS-related tag');if(!gps||!gps[1].includes('coordinates are not displayed or returned'))failures.push('gps_output_scope_unclear');if(/coordinates (?:were|are) not inspected/i.test(JSON.stringify(result)))failures.push('gps_internal_parse_overclaim');}
  if(JSON.stringify(data)!==original)failures.push('input_mutated');if(result&&JSON.stringify(result).includes('PRIVATE_CAPTION'))failures.push('caption_echo');
  return {id:c.id,adapter_input:data,caption_omitted:!Object.hasOwn(data,'caption'),expected_outcome:c.id==='date-invalid'?'fixed_invalid_clock_error':'review',required_question_ids:c.id==='date-invalid'?[]:required,result,error,failures};
 });return {label:'Frozen illustrative metadata semantic acceptance; no image file execution or factual accuracy',contract_sha256:HASH,source_sha256:sha(source),adapter_defaults:{bytes:1024,capture_time:null,software:null,camera_make:null,camera_model:null,gps_present:false,notice:'Local fixture metadata; not authenticated.',orientation:'6 swaps display dimensions; otherwise encoded dimensions'},network_calls:networkCalls,rows,failures:rows.filter(r=>r.failures.length).length};
}
module.exports={evaluate,HASH};if(require.main===module){const dest=path.join(folder,'results.json');if(fs.existsSync(dest))throw Error('Refusing to overwrite retained results');const result=evaluate();fs.writeFileSync(dest,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({cases:result.rows.length,failures:result.failures,network_calls:result.network_calls}));}
