const fs=require('node:fs');
const path=require('node:path');
const {suggest}=require('../../static/phone/suggestions.js');
const cases=JSON.parse(fs.readFileSync(path.join(__dirname,'segmentation-cases.json'),'utf8'));
console.log(JSON.stringify(cases.map(item=>({id:item.id,expected:item.topics,actual:suggest(item.text).map(row=>row.topic)})),null,2));
