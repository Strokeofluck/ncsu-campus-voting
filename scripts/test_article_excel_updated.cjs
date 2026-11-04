const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8'));
globalThis.ArticleExcelPlan=require('../article-excel-plan.js');globalThis.CsvZipStream=require('../csv-zip-stream.js');globalThis.CsvOriginalCopy=require('../csv-original-copy.js');
const exporter=require('../article-excel-export.js'),JSZip=require('../vendor/jszip.min.js'),pako=require('../vendor/pako.min.js');
const headers=read('report-source/article-excel-headers.json'),context=read('data/processed/comparison/comparison.json'),expected=read('report-source/snapshot.json').queries.age_growth_benchmarks.rows,figures=read('data/processed/comparison/figure_sources.json');
const template=Buffer.from(read('article-excel-template.json').base64,'base64'),inputs={};
for(const year of [2022,2026]){
 const rows=[];
 const row=(age,site=true,overrides={})=>headers.map(h=>({...{county_desc:'WAKE',ballot_req_type:'ONE-STOP',ballot_rtn_status:'ACCEPTED',ballot_rtn_dt:year===2022?'10/20/2022':'10/15/2026',site_name:site?context.site_mapping[year]:'OTHER WAKE SITE',age:String(age)},...overrides})[h]||'');
 for(const age of [18,25,35,45,65]){for(let i=0;i<(year===2022?1:3);i++)rows.push(row(age));rows.push(row(age,false));}
 if(year===2026)rows.push(row(24));
 rows.push(row(18,true,{ballot_rtn_status:'REJECTED'}),row(18,true,{ballot_rtn_dt:year===2022?'11/06/2022':'11/01/2026'}));
 const meta={...context.summary.find(r=>r.year===year&&r.scope==='Campus site'),site:context.site_mapping[year]};
 const finalDay=year===2022?'11/05/2022':'10/31/2026';
 const evaluated=ArticleExcelPlan.evaluate([1,'WAKE','ONE-STOP','ACCEPTED',finalDay,meta.site,'18'],meta,[0,0]);
 assert.equal(evaluated[8],1,'The final Saturday must be included');
 assert.equal(evaluated[9],1,'The final Saturday campus ballot must be included');
 inputs[year]=Buffer.from([headers.join(','),...rows.map(r=>r.join(','))].join('\r\n')+'\r\n');
}
(async()=>{
 const sources=[2022,2026].map(y=>figures.records[`summary-${y}-campus-site-all-ages`].sources[0]);
 const result=await exporter.build(template,sources,context,expected,async s=>inputs[s.year],()=>{},JSZip,CsvZipStream,pako,{mode:'updated',inputKind:'selected_csv'});
 assert.equal(result.manifest.mode,'updated');assert.equal(result.manifest.results.length,5);
 for(const [i,r]of result.manifest.results.entries()){
  assert.equal(r.site_ballots_2022,1);assert.equal(r.county_ballots_2022,2);assert.equal(r.site_ballots_2026,i===0?4:3);assert.equal(r.county_ballots_2026,i===0?5:4);
  assert.equal(r.site_growth_pct,i===0?300:200);assert.equal(r.county_growth_pct,i===0?150:100);assert.equal(r.site_growth_gap_pp,i===0?150:100);
 }
 const zip=await JSZip.loadAsync(result.bytes),book=await JSZip.loadAsync(await zip.file('02 Working copy/talley-western-growth-step-by-step.xlsx').async('uint8array'));
 for(const s of result.manifest.sources){assert.equal(s.sha256,null);assert.equal(s.matches_article_snapshot,false);assert.equal(s.wake_csv_sha256,Buffer.from(await crypto.subtle.digest('SHA-256',inputs[s.year])).toString('hex'));assert.equal(s.article_snapshot.wake_csv_sha256,sources.find(v=>v.year===s.year).wake_csv_sha256);assert.deepEqual(Buffer.from(await zip.file(`01 Original files/${s.year}/${s.member}`).async('uint8array')),inputs[s.year]);}
 const math=await book.file('xl/worksheets/sheet10.xml').async('string');assert.match(math,/<(?:\w+:)?c r="L6"[^>]*>[\s\S]*?<(?:(?:\w+):)?f>F6-K6<\//);assert.match(math,/>150<\//);
 assert.match(await zip.file('READ FIRST.txt').async('string'),/^UPDATED FILES:/);assert.match(await zip.file('UPDATED RESULTS.txt').async('string'),/Later voting dates are excluded/);assert(zip.file('03 Source checks/updated-calculations.csv'));
 assert.match(await book.file('xl/worksheets/sheet1.xml').async('string'),/UPDATED FILES/);
  assert.equal(expected[0].site_ballots_2026,4639);
 console.log('PASS: changed CSVs produce fresh five-age-group counts and formulas; rejected/later rows excluded; included bytes and hashes recorded; updated results labeled; article data untouched.');
})().catch(error=>{console.error(error);process.exitCode=1;});
