const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
test('screenshot-only help explains faithful manual wrap correction without changing shared QR review',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');
 const help=html.match(/<p id="screenshot-sample-help"[^>]*>([\s\S]*?)<\/p>/)[1];
 assert.match(help,/Compare the recognized text with the screenshot/);
 assert.match(help,/only when you confirm it is visual wrapping/);
 assert.match(help,/Keep true sentence boundaries, punctuation and negation/);
 assert.match(help,/Nothing is joined automatically/);
 assert.match(help,/Line breaks can hide wording matches/);
 const shared=html.match(/<div id="ocr-review"[^>]*>([\s\S]*?)<\/div>/)[1];
 assert.match(shared,/I reviewed the text and corrected any errors/);assert.doesNotMatch(shared,/wrapp|sentence boundaries/);
 const controller=fs.readFileSync(path.join(__dirname,'../static/primary-flow.js'),'utf8');assert.match(controller,/get\('screenshot-sample-help'\)\.hidden = mode !== 'screenshot'/);
});
