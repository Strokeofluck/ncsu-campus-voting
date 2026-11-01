import assert from 'node:assert/strict';
import fs from 'node:fs';
import {precinctGrowth,growthColor} from '../report-source/report/precinct-growth.js';
const s=JSON.parse(fs.readFileSync(new URL('../report-source/snapshot.json',import.meta.url),'utf8'));
const rows=s.queries.geography.rows.filter(r=>r.dimension==='Precinct');
for(const cohort of new Set(rows.map(r=>r.cohort))){
 const selected=rows.filter(r=>r.cohort===cohort),lookup=new Map(selected.map(r=>[`${r.year}|${r.area}`,r]));
 for(const area of new Set(selected.map(r=>r.area)))for(const field of ['wake_ballots','site_ballots']){
  const a=lookup.get(`2022|${area}`),b=lookup.get(`2026|${area}`),g=precinctGrowth(a,b,field);
  if(a?.area_present&&b?.area_present){assert.equal(g.change,b[field]-a[field]);if(a[field]>0)assert.equal(g.growth,(b[field]-a[field])/a[field]*100);else assert.equal(g.growth,null);}else assert.equal(g.growth,null);
  assert.equal(typeof growthColor(g),'string');assert(g.growth===null||Number.isFinite(g.growth));
 }
}
assert.equal(precinctGrowth({area_present:true,wake_ballots:0},{area_present:true,wake_ballots:5}).newFromZero,true);
assert.equal(precinctGrowth(undefined,{area_present:true,wake_ballots:5}).growth,null);
for(const year of [2022,2026])for(const field of ['wake_ballots','site_ballots'])assert.equal(rows.filter(r=>r.year===year&&r.cohort==='18–24'&&r.area_present).reduce((n,r)=>n+r[field],0),s.queries.summary.rows.find(r=>r.year===year&&r.scope===(field==='wake_ballots'?'Wake County':'Campus site')).age_18_24);
console.log('Passed all precinct/cohort growth calculations, missing/zero baselines, colors and county/site headline reconciliation.');
