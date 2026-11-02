import React from 'react';
import {DataComponent,ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusPassbyMap} from './CampusPassbyMap.jsx';
import {CampusWalkingMap} from './CampusWalkingMap.jsx';
import {AgeGrowthChart} from './AgeGrowthChart.jsx';
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
   <figcaption>Source: NCSBE. The benchmark holds Talley’s 2022 share of Wake’s ages 18–24 early ballots constant; it does not count people who failed to vote. <a href="../references.html?v=20261102parking5#youngest-benchmark">Worked calculation →</a></figcaption>
  </figure>
 </DataComponent></div>;
}

export function ReportContent(){
 const {snapshot}=useDataApp(),rows=snapshot.queries.age_growth_benchmarks.rows,youngest=rows.find(r=>r.cohort==='18–24');
 const otherAges=<ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Every age group under 65 lagged Wake’s growth"><RichNarrative id="voting-article-reading:body" value={`## Every age group under 65 lagged Wake’s growth

The gap extended beyond college-age voters. Growth from **Talley in 2022 to Western Boulevard in 2026** fell behind Wake’s same-age growth among voters **25–34, 35–44 and 45–64**. Voters **65 and older** were the exception: **76.0%** growth at the two locations, versus **53.4%** countywide. All five groups cast more early ballots; the difference is how quickly their counts grew.`}/></ReportSection>;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <nav className="voting-page-nav" aria-label="Page links"><a href="index.html?view=1&v=20261102parking5" aria-current="page">Article · Work in progress</a><a href="../references.html?v=20261102parking5">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="article_opening_context" queryIds={['article_opening_context','campus_parking','age_growth_benchmarks']} sourceRowsByQuery={{article_opening_context:snapshot.queries.article_opening_context.rows,campus_parking:snapshot.queries.campus_parking.rows,age_growth_benchmarks:rows}} showHeading={false} title="Talley to Western Boulevard: college-age voting growth trails Wake"><RichNarrative id="voting-article-intro:body" value={`# Talley to Western Boulevard: college-age voting growth trails Wake

**[Update this opening after the Nov. 3 election.]** Early voting has ended in North Carolina with a record number of ballots for a midterm, [WRAL reported October 31](https://www.wral.com/news/nccapitol/end-early-voting-nc-last-day-register-how-to-guide-midterms-mail-id-2026/). With Election Day still ahead, the preliminary numbers offer a first look at voting after NC State’s early-voting site moved from **Talley Student Union to Western Boulevard Business Services**.

Parking was one argument for the move: board members said the Western Boulevard location would be easier for off-campus voters to reach by car, [according to NC Newsline’s meeting coverage](https://ncnewsline.com/2026/06/12/republicans-axe-nc-state-student-center-as-an-early-voting-site/). Yet Talley sits beside Coliseum Deck, whose university GIS records list **2,192 spaces**, compared with **660 across the McKimmon lots**—about **3.3 times as many**. Those are total inventories, not spaces available to voters. NC State [reserved part of McKimmon’s parking for early voting](https://transportation.ncsu.edu/2026/10/early-voting-at-nc-state-october-15-31/), with general and accessible voter-parking areas identified in its [official map](https://transportation.ncsu.edu/2026/10/early-voting-at-nc-state-october-15-31/).

The map below compares modeled walks from student housing. The ballot analysis that follows compares **Talley in 2022 with Western Boulevard in 2026**, using the same first 16 early-voting days. It shows what changed, without isolating the move’s effect.`}/></ReportSection>
  <CampusWalkingMap article/>
  <ReportSection id="voting-article-routine-intro" queryId="campus_passby" sourceRows={snapshot.queries.campus_passby.rows.filter(r=>!r.ends_at_talley)} showHeading={false} title="Would routine walks bring students near the site?"><RichNarrative id="voting-article-routine-intro:body" value={`## Would routine walks bring students near the site?

A simulation modeled **756 routes from housing to classroom and dining buildings identified in NC State’s GIS, plus Hill and Hunt libraries**, to test whether routine walks would pass near either voting site. [GIS labels and exclusions](../references.html?v=20261102parking5#destination-gis-sources).

**334 routes—44.2%—passed within 50 meters of Talley’s building outline**, the former early-voting location. **None passed within 50 meters of Western Boulevard’s building outline**. The simulation describes opportunities to pass nearby; it does not measure how many students actually walked those routes, noticed the site or voted.`}/></ReportSection>
  <CampusPassbyMap article/>
  <ReportSection id="voting-article-turnout" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="College-age voting grew, but fell behind Wake"><RichNarrative id="voting-article-turnout:body" value={`Among voters ages **18–24**, early ballots grew **40.5%** from Talley in 2022 to Western Boulevard in 2026, compared with **103.6%** across Wake County—a **63.1 percentage-point growth gap**, the largest of the five age groups.

*Work in progress · Accepted in-person early ballots during the first 16 days of each election, through October 30, 2026. These preliminary counts are not full-election turnout. Ages 18–24 do not verify student enrollment.*`}/></ReportSection>
  <AgeGrowthChart/>
  {otherAges}
  <YoungestBenchmark row={youngest}/>
  <ReportSection id="voting-article-closing" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Reading the comparison"><RichNarrative id="voting-article-closing:body" value={`These figures describe early-ballot counts and location use. They do not establish whether the relocation caused the growth gap. Ages 18–24 are an age proxy, not verified student enrollment.

[Follow the original counts and calculations, step by step](../references.html?v=20261102parking5).`}/></ReportSection>
 </article>;
}
