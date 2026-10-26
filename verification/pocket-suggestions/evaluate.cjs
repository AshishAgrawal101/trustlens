// Constructed diagnostic only; run from the development root.
const fs=require('node:fs');
const path=require('node:path');
const {suggest}=require('../../static/phone/suggestions.js');
const cases=JSON.parse(fs.readFileSync(path.join(__dirname,'frozen-cases.json'),'utf8'));
const rows=cases.map(item=>{
 const actual=suggest(item.text).map(row=>row.topic);
 return {id:item.id,expected:item.topics,actual,missing:item.topics.filter(topic=>!actual.includes(topic)),extra:actual.filter(topic=>!item.topics.includes(topic))};
});
console.log(JSON.stringify({cases:rows.length,exact:rows.filter(row=>!row.missing.length&&!row.extra.length).length,rows},null,2));
