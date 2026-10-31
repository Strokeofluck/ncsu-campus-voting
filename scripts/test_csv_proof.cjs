const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),model=require(path.join(root,'csv-proof-model.js'));
const records=JSON.parse(fs.readFileSync(path.join(root,'data/processed/comparison/figure_sources.json'),'utf8')).records;
for(const id of Object.keys(records)){
 const plan=model.buildPlan(records,id),steps=model.calculate(plan);
 assert(steps.every(s=>s.matches),id);
 const actual=Object.fromEntries(plan.counts.map(c=>[c.key,c.expected]));
 assert(model.calculate(plan,actual).every(s=>s.matches),id);
 actual[plan.counts[0].key]++;
 assert(model.calculate(plan,actual).some(s=>!s.matches),id+' detects changed count');
}
const context=JSON.parse(fs.readFileSync(path.join(root,'data/processed/comparison/comparison.json'),'utf8'));
const messages=[],sandbox={postMessage:m=>messages.push(m),TextDecoder,Uint32Array,Uint8Array,DataView,crypto:crypto.webcrypto,console};
const ctx=vm.createContext(sandbox);sandbox.importScripts=(...files)=>{for(const file of files)if(!file.startsWith('vendor/'))vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),ctx,{filename:file});};
vm.runInContext(fs.readFileSync(path.join(root,'csv-proof-worker.js'),'utf8'),ctx);
const headers=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr','test_quoted'];
const lines=[headers.join(',')];
for(let i=0;i<60;i++)lines.push(['WAKE','ONE-STOP','ACCEPTED','10/20/2022',context.site_mapping['2022'],i<51?'24':'25','Y',i===0?'"comma, and ""quote""\nline"':'plain'].join(','));
lines.push(['WAKE','ONE-STOP','ACCEPTED','10/19/2022',context.site_mapping['2022'],'24','Y','outside window'].join(','));
const bytes=new TextEncoder().encode(lines.join('\r\n')+'\r\n');sandbox.fixture=bytes;
vm.runInContext('wakeBytes=async()=>fixture;',ctx);
(async()=>{
 const plan=model.buildPlan(records,'summary-2022-campus-site-age-18-24-share');
 await sandbox.onmessage({data:{type:'load',sources:records[plan.id].sources,counts:plan.counts,context}});
 const ready=messages.find(m=>m.type==='ready');assert(ready,JSON.stringify(messages));
 assert.equal(ready.counts[plan.counts.find(c=>c.selection.field==='age_18_24').key],51);
 assert.equal(ready.counts[plan.counts.find(c=>c.selection.field==='all_ages').key],60);
 assert.equal(ready.hashes[2022].matches,false,'changed source hash is explicit');
 await sandbox.onmessage({data:{type:'page',year:2022,key:plan.counts[0].key,page:99,id:1}});
 let page=messages.at(-1);assert.equal(page.page,1);assert.equal(page.rows.length,1);assert.equal(page.rows[0].ordinal,51);assert.equal(page.rows[0].line,52);
 await sandbox.onmessage({data:{type:'page',year:2022,key:null,page:0,id:2}});
 page=messages.at(-1);assert.equal(page.count,61);assert.equal(page.rows[0].values[7],'comma, and "quote"\nline');
 await sandbox.onmessage({data:{type:'page',year:2024,key:null,page:0,id:3}});assert.equal(messages.at(-1).type,'error');
 console.log('Passed: all 211 calculation graphs, changed-count detection, CSV quoted fields/newlines, filters, separate numerator/denominator, pagination, running totals and changed-hash reporting.');
})().catch(e=>{console.error(e);process.exitCode=1;});
