const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
test('every context workspace has a direct route to the local directory without transferring input',()=>{
 for(const page of ['claim-review','media-context','numbers-context','quote-context']){const html=fs.readFileSync(path.join(__dirname,'../static/'+page+'.html'),'utf8');const footer=html.slice(html.indexOf('<footer'),html.indexOf('</footer>'));assert.match(footer,/<a href="\/static\/tools.html">Explore all local tools →<\/a>/,page);assert.doesNotMatch(footer,/\?(?:text|claim|source|content|quote)=/);}
});
