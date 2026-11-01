import React,{useState} from 'react';
import {DataComponent,EvidenceChart,ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
const years=[2022,2024,2026];
const n=value=>Number(value).toLocaleString('en-US');
const date=value=>new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',timeZone:'UTC'}).format(new Date(value+'T12:00:00Z'));

export function AgeDistribution(){
 const {snapshot,visible}=useDataApp();
 const [measure,setMeasure]=useState('share');
 const rows=snapshot.queries.age_distribution.rows;
 const shares=measure==='share',field=shares?'Age share (%)':'votes',guide=shares?'Share ceiling (%)':'count_ceiling';
 const ages=[...new Set(rows.map(r=>r.age))];
 const table=ages.map(age=>({age,...Object.fromEntries(years.flatMap(year=>{const r=rows.find(v=>v.year===year&&v.age===age);return [[`${year} ballots`,r.votes],[`${year} share (%)`,r['Age share (%)']]];}))}));
 const days=snapshot.comparison.matched_days;
 return <div id="age-distribution" className="voting-party-section voting-age-distribution">
  <ReportSection id="voting-age-distribution-intro" title="The full age distribution, year by year" queryId="age_distribution" sourceRows={rows} showHeading={false}>
   <RichNarrative id="voting-age-distribution-intro:body" value={`## The full age distribution, year by year

Each point is one age, covering everyone who cast an accepted early ballot at Talley Student Union (2022 and 2024) or Western Boulevard Business Services (2026) in the first ${days} early-voting days. Percentages compare the age mix; counts compare ballot volume. All three charts use the same axes. These are the actual distributions, without fitting a bell curve.`}/>
  </ReportSection>
  <div className="voting-controls"><label>Age distribution measure <select value={measure} onChange={e=>setMeasure(e.target.value)}><option value="share">Percentage of each year’s site ballots</option><option value="votes">Number of ballots at each age</option></select></label></div>
  <div className="voting-party-grid">{years.map(year=>{
   const id=`voting-age-distribution-${year}`,values=rows.filter(r=>r.year===year);
   const summary=snapshot.queries.summary.rows.find(r=>r.year===year&&r.scope==='Campus site');
   const peak=values.reduce((a,b)=>b.votes>a.votes?b:a);
   return visible(id)&&<EvidenceChart key={year} id={id} queryId="age_distribution" title={`${year} · ${year===2026?'Western Boulevard':'Talley Student Union'}`} description={`Every age · ${shares?'percentage of all site ballots':'accepted early-ballot counts'}`} rows={values} sourceRows={values} spec={{type:'line',x:'age',y:field,stackable:false,startAtZero:true,valueDecimals:shares?2:0,xLabel:'Recorded age',yLabel:shares?'Site ballots (%)':'Ballots',annotations:[{id:`age-shared-scale-${year}`,kind:'benchmark',measure:field,field:guide,label:`Shared scale: ${n(values[0][guide])}${shares?'%':' ballots'}`}]}} height={300}>
    <RichNarrative id={`${id}:note`} value={`${values[0].site} · ${date(summary.start_date)}–${date(summary.end_date)}, ${year} · ${n(summary.all_ages)} ballots. Most common age: **${peak.age}**, with **${n(peak.votes)} ballots (${peak['Age share (%)'].toFixed(1)}%)**.`}/>
   </EvidenceChart>;
  })}</div>
  <RichNarrative id="voting-age-distribution:context" value={`All ages shown: ${ages[0]}–${ages[ages.length-1]}. 2024 was a presidential election; 2022 and 2026 are midterms. Ages are recorded in the source files and do not establish student status. 2026 records are preliminary through ${snapshot.comparison.as_of}.`}/>
  <DataComponent id="voting-age-distribution-table" queryId="age_distribution" kind="table" title="Check the exact age counts" sourceRows={rows} displayRows={table}>
   <a href="data/processed/comparison/age_distribution.csv" download>Download all ages, counts and percentage calculations (.csv)</a>
   <details className="voting-age-exact"><summary>Show every age across the three years</summary>
    <div className="voting-table-scroll"><table className="voting-table"><caption>Accepted early ballots by recorded age · first {days} days. Each cell shows count and percentage of that year’s site total.</caption><thead><tr><th scope="col">Age</th>{years.map(year=><th key={year} scope="col">{year}<br/>{year===2026?'Western Boulevard Business Services':'Talley Student Union'}</th>)}</tr></thead>
     <tbody data-reviewed-rows>{table.map(r=><tr key={r.age}><th scope="row">{r.age}</th>{years.map(year=><td key={year}>{n(r[`${year} ballots`])}<span className="voting-final-detail">{r[`${year} share (%)`].toFixed(2)}%</span></td>)}</tr>)}</tbody>
     <tfoot data-reviewed-rows><tr><th scope="row">All ages</th>{years.map(year=><td key={year}>{n(rows.find(r=>r.year===year).site_ballots)}<span className="voting-final-detail">100.00%</span></td>)}</tr></tfoot>
    </table></div>
   </details>
  </DataComponent>
 </div>;
}
