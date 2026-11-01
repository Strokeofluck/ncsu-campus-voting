import fs from 'node:fs';
import assert from 'node:assert/strict';
import {METRICS,regionColor,scaleColors,rankedRegions} from '../report-source/report/age-region-metrics.js';
const s=JSON.parse(fs.readFileSync(new URL('../report-source/snapshot.json',import.meta.url),'utf8')),rows=s.queries.precinct_age_changes.rows;
for(const [metric,definition]of Object.entries(METRICS)){
 assert.equal(scaleColors(metric).length,definition.cuts.length+1);
 for(const cohort of ['18–24','25–34','35–44','45–64','65+']){
  const r=rows.filter(v=>v.cohort===cohort),rank=rankedRegions(r,metric,'absolute',20);
  assert(rank.every(v=>v.mapped&&Number.isFinite(v[metric])&&(metric!=='growth_pct'||v.ballots_2022>=20)));
  for(let i=1;i<rank.length;i++)assert(Math.abs(rank[i-1][metric])>=Math.abs(rank[i][metric]));
  assert(rankedRegions(r,metric,'increase').every(v=>v[metric]>0));assert(rankedRegions(r,metric,'decrease').every(v=>v[metric]<0));
  for(const v of r)assert.equal(typeof regionColor(v,metric),'string');
 }
}
const young=rankedRegions(rows.filter(r=>r.cohort==='18–24'),'ballot_change');
assert.equal(young[0].area,'PRECINCT 01-23');assert.equal(young[0].ballot_change,467);
assert.equal(regionColor({ballot_change:null},'ballot_change'),'#bdbdbd');
console.log('Passed shared map scales, all ranking directions, missing values, relative-growth baseline filter and the focal precinct’s count ranking.');
