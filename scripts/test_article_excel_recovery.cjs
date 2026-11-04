const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8'));
const figures=read('data/processed/comparison/figure_sources.json'),context=read('data/processed/comparison/comparison.json');
const expected=read('report-source/snapshot.json').queries.age_growth_benchmarks.rows;
const script=fs.readFileSync(path.join(root,'article-excel-download.js'),'utf8');
async function checkPage(){
 const handlers={},inputs={2022:{name:'original-2022.csv'},2026:{name:'original-2026.csv'}};
 const button=id=>({disabled:false,addEventListener:(event,fn)=>{handlers[id]=fn;}});
 const elements={'download-article-excel':button('live'),'download-article-excel-saved':button('saved'),'article-excel-status':{textContent:''},'article-excel-saved':{open:false},'article-excel-mode':{value:'updated'},'reference-data':{textContent:JSON.stringify({rows:expected})},'article-excel-csv-2022':{files:[inputs[2022]]},'article-excel-csv-2026':{files:[inputs[2026]]}};
 let worker,message;
 const files={'data/processed/comparison/figure_sources.json':figures,'data/processed/comparison/comparison.json':context};
 vm.runInNewContext(script,{document:{getElementById:id=>elements[id]},URL,fetch:async url=>({ok:true,json:async()=>files[url]}),Worker:class{constructor(){worker=this;}postMessage(data){message=data;}terminate(){}}});
 await handlers.live();assert.equal(message.originals,undefined);assert.equal(message.mode,'updated');
 worker.onmessage({data:{type:'export-error',code:'SOURCE_SNAPSHOT_CHANGED',message:'Choose the saved originals.'}});
 assert.equal(elements['article-excel-saved'].open,true);assert.equal(elements['download-article-excel'].disabled,false);assert.equal(elements['download-article-excel-saved'].disabled,false);
 await handlers.saved();assert.equal(message.originals[2022],inputs[2022]);assert.equal(message.originals[2026],inputs[2026]);assert.equal(message.mode,'updated');
 elements['article-excel-mode'].value='snapshot';await handlers.saved();assert.equal(message.mode,'snapshot');
 worker.onmessage({data:{type:'export-error',message:'Wrong source hash'}});
 assert.match(elements['article-excel-status'].textContent,/Wrong source hash/);
 elements['article-excel-csv-2026'].files=[];await handlers.saved();assert.match(elements['article-excel-status'].textContent,/Choose both/);
}
async function checkPreflight(){
 globalThis.ArticleExcelPlan=require('../article-excel-plan.js');
 const exporter=require('../article-excel-export.js'),bytes=new TextEncoder().encode('original');
 const hash=Buffer.from(await crypto.subtle.digest('SHA-256',bytes)).toString('hex');
 const sources=[2022,2026].map(year=>({year,wake_csv_sha256:hash}));let read=0,templateLoaded=false;
 await assert.rejects(()=>exporter.build(null,sources,{},[],async source=>{read++;return source.year===2022?bytes:new Uint8Array([0]);},()=>{},{loadAsync:async()=>{templateLoaded=true;}},null,null),error=>error.code==='SOURCE_SNAPSHOT_CHANGED');
 assert.equal(read,2);assert.equal(templateLoaded,false);
}
(async()=>{await checkPage();await checkPreflight();console.log('PASS: changed source opens recovery; both saved files reach the worker; missing/incorrect files remain rejected; all source hashes checked before workbook generation.');})().catch(error=>{console.error(error);process.exitCode=1;});
