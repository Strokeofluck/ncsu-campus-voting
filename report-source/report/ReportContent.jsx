import React, { useState } from 'react';
import { EvidenceChart, DataComponent, MetricCard, ReportSection, RichNarrative, useDataApp } from '../../data-app-public.jsx';
const num=n=>Number(n).toLocaleString('en-US');
const short=n=>n>=1000?`${(n/1000).toFixed(1)}k`:num(n);
const one=n=>Number(n).toFixed(1);
const signed=n=>`${n>0?'+':''}${one(n)}`;
export function ReportContent(){
 const {snapshot,visible,appTitle,canEdit,mode,setAppTitle}=useDataApp();
 const [baseline,setBaseline]=useState(2024),[scope,setScope]=useState('Campus site'),[cohort,setCohort]=useState('18–24'),[ageMeasure,setAgeMeasure]=useState('votes');
 const summaries=snapshot.queries.summary.rows,daily=snapshot.queries.daily.rows,demos=snapshot.queries.demographics.rows;
 const campusRows=summaries.filter(r=>r.scope==='Campus site');
 const get=(y,s)=>summaries.find(r=>r.year===y&&r.scope===s);
 const a=get(baseline,'Campus site'),b=get(2026,'Campus site'),w=get(baseline,'Wake County'),z=get(2026,'Wake County');
 const paired=summaries.filter(r=>r.year===baseline||r.year===2026),isPair=y=>y===baseline||y===2026;
 const period=baseline===2024?'October 17–27, 2024':'October 20–30, 2022';
 const growth=(n,o)=>(n/o-1)*100,share22=a.age_18_24/w.age_18_24*100,share26=b.age_18_24/z.age_18_24*100,days=b.matched_days;
 const trendRows=daily.filter(r=>r.scope===scope&&r.cohort===cohort&&isPair(r.year));
 const plotRows=trendRows.map(r=>({...r,yearLabel:String(r.year)}));
 const indexSource=daily.filter(r=>r.cohort==='18–24'&&isPair(r.year));
 const indexRows=indexSource.filter(r=>r.year===2026).map(r=>{const base=indexSource.find(v=>v.year===baseline&&v.scope===r.scope&&v.day===r.day);return{day:r.day,scope:r.scope,index:base?.cumulative?r.cumulative/base.cumulative*100:null};});
 const ages=demos.filter(r=>r.scope==='Campus site'&&r.dimension==='age_group'&&isPair(r.year));
 const ageRows=['18–24','25–34','35–44','45–64','65+','Unknown / outside range'].flatMap(value=>ages.filter(r=>r.value===value).map(r=>({age:value,year:String(r.year),'Ballots (%)':r.share})));
 const shareRows=[{year:String(baseline),'Campus share (%)':share22},{year:'2026','Campus share (%)':share26}];
 const moveRows=[{site:`Talley (${baseline})`,votes:a.age_18_24},{site:'Western (2026)',votes:b.age_18_24}];
 const exactAges=demos.filter(r=>r.scope==='Campus site'&&r.dimension==='age'&&isPair(r.year)&&Number(r.value)>=18&&Number(r.value)<=24);
 const detailRows=Array.from({length:7},(_,i)=>String(i+18)).flatMap(age=>exactAges.filter(r=>r.value===age).map(r=>({age,year:String(r.year),votes:r.votes,'Share of site (%)':r.share})));
 const previews={'https://www.ncsbe.gov/results-data/absentee-and-provisional-data':{title:'NCSBE absentee and early-voting data',summary:'Official download catalog explaining absentee records and early-voting ballots. This analysis uses Wake County records from the 2022, 2024 and 2026 general-election archives.',source:'North Carolina State Board of Elections',approvedForReport:true}};
 return <article className="report-content voting-report" aria-label="NC State early-voting comparison">
  <header className="report-hero">
   <RichNarrative id="voting:eyebrow" value="NC STATE · TALLEY → WESTERN BOULEVARD" className="voting-eyebrow"/>
   <h1 data-data-app-title contentEditable={canEdit&&mode==='edit'} suppressContentEditableWarning onBlur={canEdit&&mode==='edit'?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}>{appTitle}</h1>
   <RichNarrative id="voting:deck" className="report-deck" value={`What changed when early voting moved from Talley Student Union to Western Boulevard Business Services, 1220 Varsity Drive? The default view compares the first ${days} days in 2024 and 2026; current records through ${b.end_date}.`}/>
  </header>
  <div className="voting-controls"><label>Compare 2026 with <select value={baseline} onChange={e=>setBaseline(Number(e.target.value))}><option value={2024}>2024 · Talley · presidential election</option><option value={2022}>2022 · Talley · midterm election</option></select></label></div>
  <RichNarrative id="voting:cycle-context" value={baseline===2024?'**Reading this comparison:** 2024 was a presidential election; 2026 is a midterm. Matching voting days does not remove that difference. A decline cannot be attributed to the location move alone. Ages 18–24 identify college-age voters, not confirmed NC State students.':'**Reading this comparison:** both elections are midterms. The age measure is a proxy, not confirmed NC State students. Changes in site use still do not identify the causal effect of moving the location.'}/>
  <ReportSection id="voting-summary" title="Executive Summary" queryId="summary" sourceRows={paired} showHeading={false}>
   <RichNarrative id="voting-summary:body" value={`## Executive Summary

- **College-age ballots at the campus site:** ${short(a.age_18_24)} at Talley in ${baseline} → ${short(b.age_18_24)} at Western Boulevard in 2026, a **${one(Math.abs(growth(b.age_18_24,a.age_18_24)))}% ${b.age_18_24<a.age_18_24?'decrease':'increase'}** over the first ${days} days.
- **The age mix changed:** ages 18–24 accounted for **${one(a.age_18_24_share)}% → ${one(b.age_18_24_share)}%** of all site ballots (${signed(b.age_18_24_share-a.age_18_24_share)} percentage points).
- **Countywide context:** Wake’s college-age early ballots changed by **${signed(growth(z.age_18_24,w.age_18_24))}%**. The campus site’s share of those ballots fell from **${one(share22)}% to ${one(share26)}%**. ${baseline===2024?'This comparison spans a presidential election and a midterm, so the location move cannot be isolated.':'Both elections are midterms; site use and age composition still cannot establish student turnout or causal impact.'}`}/>
  </ReportSection>
  <div className="report-facts voting-facts">
   <MetricCard id="campus-youth-count" queryId="summary" sourceRows={paired.filter(r=>r.scope==='Campus site')} title="College-age ballots at campus site" value={short(b.age_18_24)} comparison={`${signed(growth(b.age_18_24,a.age_18_24))}% vs ${baseline}`} deltaTone="neutral" description={`Ages 18–24; matched first ${days} days`}/>
   <MetricCard id="campus-youth-share" queryId="summary" sourceRows={paired.filter(r=>r.scope!=='Other Wake sites')} title="Share of Wake college-age votes" value={`${one(share26)}%`} comparison={`${one(share26-share22)} percentage points`} deltaTone="neutral" description="Campus site ÷ all Wake ballots, ages 18–24"/>
   <MetricCard id="campus-all-count" queryId="summary" sourceRows={paired.filter(r=>r.scope==='Campus site')} title="All ballots at campus site" value={short(b.all_ages)} comparison={`${signed(growth(b.all_ages,a.all_ages))}% vs ${baseline}`} deltaTone="neutral" description={`All ages; matched first ${days} days`}/>
  </div>
  <DataComponent id="voting-campus-exact-table" queryId="summary" kind="table" title="Talley and its replacement: exact campus-site counts" sourceRows={campusRows} displayRows={campusRows}>
   <div className="voting-table-scroll"><table className="voting-table voting-campus-table"><thead><tr><th>Site / year</th><th>All ages</th><th>Ages 18–24</th><th>Ages 18–22</th><th>18–24 share</th><th>Same-day registration</th></tr></thead><tbody data-reviewed-rows>{campusRows.map(r=><tr key={r.year}><th>{r.year===2026?'Western Boulevard':'Talley Student Union'} · {r.year}</th><td>{num(r.all_ages)}</td><td>{num(r.age_18_24)}</td><td>{num(r.age_18_22)}</td><td>{one(r.age_18_24_share)}%</td><td>{num(r.same_day_registration)}</td></tr>)}</tbody></table></div>
   <RichNarrative id="voting-campus-exact-table:note" value="First 11 early-voting days in each year. Talley: Oct 20–30, 2022 and Oct 17–27, 2024. Western Boulevard Business Services: Oct 15–25, 2026 (preliminary). Same-day registration includes all ages. The 18–24 share is a share of site ballots. 2024 was presidential; 2022 and 2026 are midterms. [Verify each figure against the source and arithmetic](https://strokeofluck.github.io/ncsu-campus-voting/verify-figures.html)."/>
  </DataComponent>
  {visible('voting-move-counts')&&<EvidenceChart id="voting-move-counts" queryId="summary" title="Talley versus the replacement site: college-age ballots" description={`Ages 18–24. Talley: ${period}. Western Boulevard: October 15–25, 2026. Both windows contain ${days} days. ${baseline===2024?'Presidential vs midterm election.':'Both are midterm elections.'}`} rows={moveRows} sourceRows={paired.filter(r=>r.scope==='Campus site')} spec={{type:'horizontalBar',x:'site',y:'votes',stackable:false,startAtZero:true,valueDecimals:0}} height={300}/>}
  <ReportSection id="voting-age-intro" title="How the campus site’s age mix changed" queryId="summary" sourceRows={paired.filter(r=>r.scope==='Campus site')} showHeading={false}>
   <RichNarrative id="voting-age-intro:body" value={`## How the campus site's age mix changed

College-age voters represented **${one(a.age_18_24_share)}% at Talley (${baseline})** and **${one(b.age_18_24_share)}% at Western Boulevard (2026)**, a change of ${signed(b.age_18_24_share-a.age_18_24_share)} percentage points. This compares composition within each site, alongside the absolute ballot counts above. Site users also include staff, neighbors and other Wake voters.`}/>
  </ReportSection>
  {visible('voting-ages')&&<EvidenceChart id="voting-ages" queryId="demographics" title="Age composition at each campus site" description={`Share of all accepted early-voting ballots at Talley (${baseline}) and Western Boulevard (2026), matched first ${days} days. ${baseline===2024?'Presidential vs midterm election; this does not isolate the location move.':'Both are midterm elections; this does not isolate the location move.'}`} rows={ageRows} sourceRows={ages} spec={{type:'bar',x:'age',y:'Ballots (%)',series:'year',stackable:false,startAtZero:true,valueDecimals:1}} height={330}/>}
  <ReportSection id="voting-college-detail-intro" queryId="demographics" sourceRows={exactAges} title="A closer look at college-age voters" showHeading={false}><RichNarrative id="voting-college-detail-intro:body" value="## A closer look at college-age voters

See each age from 18 through 24 at the old and new sites. Switch between ballot counts and each age's share of all site ballots to distinguish volume from demographic composition."/></ReportSection>
  <div className="voting-controls"><label>Individual-age chart <select value={ageMeasure} onChange={e=>setAgeMeasure(e.target.value)}><option value="votes">Ballot counts</option><option value="share">Share of all site ballots</option></select></label></div>
  {visible('voting-college-age-detail')&&<EvidenceChart id="voting-college-age-detail" queryId="demographics" title={`Ages 18–24 at Talley (${baseline}) and Western Boulevard (2026)`} description={`Each individual age, matched first ${days} days. ${ageMeasure==='votes'?'Accepted early-voting ballots.':'Percentage of all accepted site ballots, including older voters in the denominator.'} ${baseline===2024?'Presidential vs midterm election; this does not isolate the location move.':'Both are midterm elections; this does not isolate the location move.'}`} rows={detailRows} sourceRows={exactAges} spec={{type:'bar',x:'age',y:ageMeasure==='votes'?'votes':'Share of site (%)',series:'year',stackable:false,startAtZero:true,valueDecimals:ageMeasure==='votes'?0:1}} height={340}/>}
  <ReportSection id="voting-pace-intro" title="How the pattern developed" queryId="daily" sourceRows={daily} showHeading={false}>
   <RichNarrative id="voting-pace-intro:body" value="## How the pattern developed\n\nCompare the same day of the early-voting period. Day 1 is Thursday in both years. Switch the age proxy or location to see whether the pattern is specific to the campus site."/>
  </ReportSection>
  <div className="voting-controls">
   <label>Location <select value={scope} onChange={e=>setScope(e.target.value)}>{['Campus site','Wake County','Other Wake sites'].map(v=><option key={v}>{v}</option>)}</select></label>
   <label>Voters <select value={cohort} onChange={e=>setCohort(e.target.value)}>{['18–24','18–22','All ages'].map(v=><option key={v}>{v}</option>)}</select></label>
  </div>
  {visible('voting-cumulative')&&<EvidenceChart id="voting-cumulative" queryId="daily" title="Cumulative accepted early-voting ballots" description={`${scope} · ${cohort==='All ages'?'all ages':`ages ${cohort}`} · first ${days} days. Talley: ${period}; Western Boulevard: Oct 15–25, 2026.`} rows={plotRows} sourceRows={trendRows} spec={{type:'line',x:'day',y:'cumulative',series:'yearLabel',stackable:false,startAtZero:true,xLabel:'Day of early voting',valueDecimals:0}} height={340}/>}
  <ReportSection id="voting-relative-intro" title="How the campus pattern compares with Wake County" queryId="summary" sourceRows={paired} showHeading={false}>
   <RichNarrative id="voting-relative-intro:body" value={`## How the campus pattern compares with Wake County

At other Wake sites, college-age ballots changed from **${short(get(baseline,'Other Wake sites').age_18_24)} to ${short(get(2026,'Other Wake sites').age_18_24)}** (${signed(growth(get(2026,'Other Wake sites').age_18_24,get(baseline,'Other Wake sites').age_18_24))}%). The campus site changed by ${signed(growth(b.age_18_24,a.age_18_24))}%. The county comparison gives context; it is not a control group that removes election-cycle or population differences, and it does not track the same people switching sites.`}/>
  </ReportSection>
  {visible('voting-growth-index')&&<EvidenceChart id="voting-growth-index" queryId="daily" title={`2026 college-age ballots relative to the same day in ${baseline}`} description={`Index: 100 means equal cumulative ballots to ${baseline}; 200 means twice as many. Ages 18–24; matched voting days. This does not adjust for election-cycle differences.`} rows={indexRows} sourceRows={indexSource} spec={{type:'line',x:'day',y:'index',series:'scope',stackable:false,startAtZero:true,xLabel:'Day of early voting',valueDecimals:1}} height={340}/>}
  {visible('voting-site-share')&&<EvidenceChart id="voting-site-share" queryId="summary" title="The campus site's share of Wake college-age early voting" description="Denominator: all accepted Wake County early-voting ballots from ages 18–24 in each matched period." rows={shareRows} sourceRows={paired.filter(r=>r.scope!=='Other Wake sites')} spec={{type:'bar',x:'year',y:'Campus share (%)',stackable:false,startAtZero:true,valueDecimals:1}} height={300}/>}
  <DataComponent id="voting-exact-table" queryId="summary" kind="table" title="Exact matched-period counts" sourceRows={summaries} displayRows={summaries}>
   <div className="voting-table-scroll"><table className="voting-table"><thead><tr><th>Scope / year</th><th>All ages</th><th>Ages 18–24</th><th>Ages 18–22</th><th>18–24 share</th><th>Same-day registration</th></tr></thead><tbody data-reviewed-rows>{summaries.map(r=><tr key={`${r.year}-${r.scope}`}><th>{r.scope} · {r.year}</th><td>{num(r.all_ages)}</td><td>{num(r.age_18_24)}</td><td>{num(r.age_18_22)}</td><td>{one(r.age_18_24_share)}%</td><td>{num(r.same_day_registration)}</td></tr>)}</tbody></table></div>
  </DataComponent>
  <ReportSection id="voting-interpretation" queryId="summary" sourceRows={summaries} title="What this can tell us" showHeading={false}>
   <RichNarrative id="voting-interpretation:body" value={`## What this can tell us

**The observed pattern depends on the baseline:** the new site's college-age count is ${one(Math.abs(growth(b.age_18_24,get(2024,'Campus site').age_18_24)))}% below Talley in the matched 2024 presidential period, and ${one(growth(b.age_18_24,get(2022,'Campus site').age_18_24))}% above the matched 2022 midterm period. Both comparisons are retained here.

**The unresolved question:** whether moving the site affected NC State students' probability of voting. Enrollment and eligible-student denominators are unavailable. Presidential-versus-midterm participation, mobilization, population changes, voting schedules and site availability all matter. Wake had 15 recorded sites in 2022, 22 in 2024 and 18 in 2026.

For a stronger impact analysis, complete early voting and include finalized mail and Election Day history, a documented student or campus-resident cohort, and comparison areas. These charts describe early-voting counts and demographics at the two locations; they do not estimate the move's causal effect.`}/>
  </ReportSection>
  <ReportSection id="voting-methods" queryId="summary" sourceRows={summaries} title="Sources and comparison rules" showHeading={false}>
   <RichNarrative id="voting-methods:body" sourcePreviews={previews} value={`## Sources and comparison rules

[Official NCSBE downloads](https://www.ncsbe.gov/results-data/absentee-and-provisional-data) supply all three years. [NC State’s event listing](https://packthepolls.dasa.ncsu.edu/event/2026-general-early-voting/) identifies the new site.

- **Matched dates:** October 20–30, 2022; October 17–27, 2024; October 15–25, 2026. Each window is the first ${days} calendar days, Thursday through Sunday. All historical charts use matched windows, not complete historical elections against partial 2026.
- **Cycle:** 2024 is a presidential general election. 2022 and 2026 are midterm general elections. Matching calendar days cannot remove cycle effects or differences in site hours and availability.
- **Population:** Wake records with an early-voting request type and return status exactly ACCEPTED. Talley is the exact source site TA - NCSU TALLEY STUDENT CENTER in 2022/2024; the new site is NCSU WESTERN BLVD BUSINESS SERVICES in 2026. Mail, cancelled and other-status ballots are excluded.
- **Demographics:** use the source age field, 18–24 inclusive as the principal proxy and 18–22 as a sensitivity check. Individual ages 18–24 are shown separately. Percentage charts divide each age count by all accepted ballots at that year's campus site. Student enrollment and registered-voter turnout rates are unavailable.
- **Freshness and checks:** 2026 records are through October 25 from the October 26 morning file; 2022 and 2024 records are finalized. Historical daily reporting lag is not reconstructed. The 2022 locked totals reproduce 10,390 Talley and 219,169 Wake ballots. All three years have no duplicate accepted voter identifiers, and days, scopes, ages and demographic totals reconcile. No independent 2024/2026 site-total reconciliation against a separate Wake publication has been completed. Only aggregates are published.

[Data, archive hashes and reporting methods](https://github.com/Strokeofluck/ncsu-campus-voting/blob/main/docs/2026-early-voting-update.md) · [Downloadable aggregate tables](https://github.com/Strokeofluck/ncsu-campus-voting/tree/main/data/processed/comparison)`}/>
  </ReportSection>
 </article>;
}
