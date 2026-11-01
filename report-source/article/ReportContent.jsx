import React from 'react';
import {DataComponent,ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusAgeMaps} from './PrecinctAgeComparison.jsx';
import './article.css';

function YoungestBenchmark({row}){
 const expected=row.site_ballots_2022*(row.county_ballots_2026/row.county_ballots_2022),actual=row.site_ballots_2026;
 const maximum=Math.ceil(Math.max(expected,actual)/1000)*1000,n=v=>Math.round(v).toLocaleString('en-US');
 return <div className="voting-article-benchmark-wrap"><DataComponent id="voting-article-youngest-benchmark" queryId="age_growth_benchmarks" sourceRows={[row]} displayRows={[row]} kind="custom" title="College-age early voting: actual versus keeping pace with Wake">
  <figure className="voting-article-benchmark" data-reviewed-rows aria-label={`Ages 18–24: ${n(actual)} actual early ballots at Western Boulevard, compared with about ${n(expected)} if the location retained Talley's 2022 share of Wake's early ballots.`}>
   <p>Ages 18–24 · first 16 early-voting days · 2026</p>
   <div className="voting-article-bar-row"><div className="voting-article-bar-label"><span>Western Boulevard: actual</span><strong>{n(actual)}</strong></div><div className="voting-article-bar-plot"><div className="voting-article-bar" style={{width:`${actual/maximum*100}%`}}/></div></div>
   <div className="voting-article-bar-row"><div className="voting-article-bar-label"><span>If the location kept pace with Wake</span><strong>≈ {n(expected)}</strong></div><div className="voting-article-bar-plot"><div className="voting-article-bar voting-article-bar-benchmark" style={{width:`${expected/maximum*100}%`}}/></div></div>
   <p className="voting-article-benchmark-gap">About <strong>{n(expected-actual)} ballots below the benchmark</strong></p>
   <div className="voting-article-bar-axis" aria-hidden="true">{[0,2000,4000,6000].map(v=><span key={v} style={{left:`${v/maximum*100}%`}}>{n(v)}</span>)}</div>
   <div className="voting-article-axis-title">Early ballots</div>
   <figcaption>Source: NCSBE. The benchmark holds Talley’s 2022 share of Wake’s ages 18–24 early ballots constant; it does not count people who failed to vote. <a href="../references.html#youngest-benchmark">Worked calculation →</a></figcaption>
  </figure>
 </DataComponent></div>;
}

export function ReportContent(){
 const {snapshot}=useDataApp(),rows=snapshot.queries.age_growth_benchmarks.rows,youngest=rows.find(r=>r.cohort==='18–24');
 const otherAges=<ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Every age group under 65 lagged Wake’s growth"><RichNarrative id="voting-article-reading:body" value={`## Every age group under 65 lagged Wake’s growth

The gap extended beyond college-age voters. Growth from **Talley in 2022 to Western Boulevard in 2026** fell behind Wake’s same-age growth among voters **25–34, 35–44 and 45–64**. Voters **65 and older** were the exception: **76.0%** growth at the two locations, versus **53.4%** countywide. All five groups cast more early ballots; the difference is how quickly their counts grew.`}/></ReportSection>;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <nav className="voting-page-nav" aria-label="Page links"><a href="index.html?view=1" aria-current="page">Article · Work in progress</a><a href="../index.html?view=1#campus-age-growth">Prototype</a><a href="../references.html">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="statewide_early_voting_context" queryIds={['statewide_early_voting_context','age_growth_benchmarks']} sourceRowsByQuery={{statewide_early_voting_context:snapshot.queries.statewide_early_voting_context.rows,age_growth_benchmarks:rows}} showHeading={false} title="Talley to Western Boulevard: college-age voting growth trails Wake most"><RichNarrative id="voting-article-intro:body" value={`# Talley to Western Boulevard: college-age voting growth trails Wake most

The first early-voting numbers are in, and North Carolina is ahead of its last midterm pace. Through **October 30**, the state had accepted **2,612,240 early ballots—32% more than at the same point in 2022**, according to [NC Election Live’s early vote tracker](https://ncelectionslive.com/early-voting/).

That surge offers a first look at voting after **NC State’s early-voting site moved from Talley Student Union to Western Boulevard Business Services**. Among voters ages **18–24**, early ballots grew **40.5%** between the two locations, compared with **103.6%** across Wake County.

*Work in progress · The statewide tracker includes in-person and mail ballots. The NC State comparisons below cover accepted in-person early ballots during the matched first 16 days of 2022 and 2026, through October 30, 2026. Election Day is November 3; these are preliminary counts.*`}/></ReportSection>
  <ReportSection id="voting-article-placeholder" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Draft placeholder"><RichNarrative id="voting-article-placeholder:body" value={`*Draft placeholder*

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae augue sed lorem tincidunt interdum. Donec malesuada, velit at ullamcorper consequat, sapien lectus cursus massa, at posuere neque neque vitae purus. Sed quis ligula non urna tristique tincidunt. Nulla facilisi. Curabitur feugiat, arcu vitae aliquam dignissim, erat nibh volutpat lectus, eget consequat justo magna sed est.`}/></ReportSection>
  <CampusAgeMaps article afterYoungest={<YoungestBenchmark row={youngest}/>} beforeOtherAges={otherAges}/>
  <ReportSection id="voting-article-closing" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Reading the comparison"><RichNarrative id="voting-article-closing:body" value={`These figures describe early-ballot counts and location use. They do not establish whether the relocation caused the growth gap. Ages 18–24 are an age proxy, not verified student enrollment.

[Follow the original counts and calculations, step by step](../references.html).`}/></ReportSection>
 </article>;
}
