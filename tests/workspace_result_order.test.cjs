'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const cases=[
 ['numbers-context.html','numbers','Supplied counts only; no significance or causal conclusion.','statistical significance'],
 ['quote-context.html','quote','Both versions remain unverified; literal changes only.','source authenticity'],
 ['claim-review.html','claim','Your supplied material and labels remain unverified.','Sources are not visited'],
];
for(const [file,key,caveat,fullLimit]of cases)test(key+' result leads full expanded limits and keeps a local caveat',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../static',file),'utf8');
 const panel=html.match(/<aside\b[^>]*class="result-panel"[^>]*>([\s\S]*?)<\/aside>/)?.[1];assert.ok(panel,'result panel exists');
 const result=panel.match(new RegExp('<section\\b[^>]*id="'+key+'-result"[^>]*>[\\s\\S]*?<\\/section>'));
 const limits=panel.match(/<section\b[^>]*class="limits"[^>]*>([\s\S]*?)<\/section>/);assert.ok(result,'result section exists');assert.ok(limits,'full limits section retained');
 assert.ok(result.index+result[0].length<=limits.index,'complete result section precedes full static limits');
 assert.match(result[0].slice(0,result[0].indexOf('>')+1),/\shidden(?:\s|>)/,'initial result remains hidden');
 const headingThenCaveat=new RegExp('<h3\\b[^>]*id="'+key+'-result-title"[^>]*>[^<]*<\\/h3>\\s*<p\\b[^>]*>'+caveat.replace(/[.*+?^$()|[\]\\]/g,'\\$&')+'<\\/p>');
 assert.match(result[0],headingThenCaveat,'short caveat is directly under the result heading');
 const heading=result[0].match(new RegExp('<h3\\b[^>]*id="'+key+'-result-title"[^>]*>'))?.[0];assert.ok(heading);assert.match(heading,/\stabindex="-1"/,'result heading supports programmatic focus');
 assert.ok(limits[1].includes(fullLimit),'full material caveat remains present');
 const tag=limits[0].slice(0,limits[0].indexOf('>')+1);assert.doesNotMatch(tag,/\shidden(?:\s|>)|aria-hidden="true"|display:\s*none/);
 const before=panel.slice(0,limits.index);let detailsDepth=0;for(const match of before.matchAll(/<(\/?)details\b/g))detailsDepth+=match[1]?-1:1;assert.equal(detailsDepth,0,'full limits are not collapsed in details');
});
