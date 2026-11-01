const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
require('../csv-county-excel.js');
const root=path.resolve(__dirname,'..'),plan=require(path.join(root,'csv-excel-export.js'));
const context=JSON.parse(fs.readFileSync(path.join(root,'data/processed/comparison/comparison.json'),'utf8'));
const year=2026,site=context.site_mapping[year];
const rows=[
 [year,2,'WAKE','EARLY VOTING','ACCEPTED','10/15/2026',site,'18','Y'],
 [year,3,'WAKE','EARLY VOTING','ACCEPTED','10/30/2026',site,'24','YES'],
 [year,4,'WAKE','EARLY VOTING','ACCEPTED','10/30/2026',site,'25',''],
 [year,5,'WAKE','EARLY VOTING','ACCEPTED','10/31/2026',site,'20',''],
 [year,6,'WAKE','EARLY VOTING','REJECTED','10/30/2026',site,'20',''],
 [year,7,'WAKE','EARLY VOTING','ACCEPTED','10/30/2026',site,'','']];
const flags=plan.evaluateRows({source:{year},rows},context),counts=plan.totals(flags);
assert.deepEqual(counts,[4,2,1,0,0,0,1,2]);assert.equal(flags.at(-1)[12],4);assert.equal(flags.at(-1)[13],2);
const changed=structuredClone(rows);changed[1][7]='25';assert.equal(plan.totals(plan.evaluateRows({source:{year},rows:changed},context))[1],1);
assert(plan.flagFormulas(7)[12].includes('M6+K7'));
assert(plan.countFormulas(7,45403).every(f=>f.startsWith('=COUNTIFS(')&&f.includes('$45403')));
assert(plan.mathFormulas(7)[9].includes('(G7-C7)*100'));
const template=JSON.parse(fs.readFileSync(path.join(root,'csv-excel-template.json'),'utf8'));
const county=require('../csv-county-excel.js');
const countyRows=[...rows,[year,8,'WAKE','EARLY VOTING','ACCEPTED','10/30/2026','OTHER SITE','21','']];
const countyFlags=county.evaluate({source:{year},countyRows},context,plan);
assert.deepEqual(countyFlags.reduce((n,r)=>n.map((v,i)=>v+r[9+i]),[0,0,0]),[3,2,1]);
assert.deepEqual(countyFlags.at(-1).slice(12),[3,2,1]);
assert(county.flagFormulas(7)[12].includes('SUM(M6,J7)'));
assert(county.countFormulas(6,6,100)[0].startsWith('=SUM('));
assert(county.countFormulas(6,6,100)[3].startsWith('=COUNTIFS('));
assert.equal(county.growthFormulas(6,'site',2022)[1],"='3 Counts'!D7");
assert.equal(county.growthFormulas(7,'county',2022)[1],"='7 County counts'!B6");
assert.equal(county.growthFormulas(7,'county',2022)[3],'=C7-B7');
assert.equal(template.countyGrowth,true);
assert.deepEqual(template.sheetNames,plan.sheetNames);assert.equal(template.fullCopies,true);assert(Buffer.from(template.base64,'base64').subarray(0,2).equals(Buffer.from('PK')));
(async()=>{
 await assert.rejects(()=>plan.workbook(null,[],context,null),/requires all three/);
 await assert.rejects(()=>plan.workbook(null,[2022,2024,2026].map(y=>({source:{year:y},rows:[]})),context,null),/counts differ/);
 console.log('Passed Excel export tests: age/date/status boundaries, unknown ages, SDR flags, running totals, edits, native formula ranges, percentage-point math, template identity and mismatched-count rejection.');
})().catch(e=>{console.error(e);process.exitCode=1;});
