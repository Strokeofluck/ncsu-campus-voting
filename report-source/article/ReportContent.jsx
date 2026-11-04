import React from 'react';
import {DataComponent,ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusPassbyMap} from './CampusPassbyMap.jsx';
import {CampusWalkingMap} from './CampusWalkingMap.jsx';
import {AgeGrowthChart} from './AgeGrowthChart.jsx';
import {TechnicianHeader} from './TechnicianHeader.jsx';
import './article.css';

function YoungestBenchmark({row}){
 const expected=row.site_ballots_2022*(row.county_ballots_2026/row.county_ballots_2022),actual=row.site_ballots_2026;
 const maximum=Math.ceil(Math.max(expected,actual)/1000)*1000,n=v=>Math.round(v).toLocaleString('en-US');
 return <div className="voting-article-benchmark-wrap"><DataComponent id="voting-article-youngest-benchmark" queryId="age_growth_benchmarks" sourceRows={[row]} displayRows={[row]} kind="custom" title="College-age early voting: actual versus keeping pace with Wake">
  <figure className="voting-article-benchmark" data-reviewed-rows aria-label={`Ages 18–24: ${n(actual)} actual early ballots at Western Boulevard, compared with about ${n(expected)} if the location retained Talley's 2022 share of Wake's early ballots.`}>
   <p>Ages 18–24 · full 17-day early-voting periods · 2026</p>
   <div className="voting-article-bar-row"><div className="voting-article-bar-label"><span>Western Boulevard: actual</span><strong>{n(actual)}</strong></div><div className="voting-article-bar-plot"><div className="voting-article-bar" style={{width:`${actual/maximum*100}%`}}/></div></div>
   <div className="voting-article-bar-row"><div className="voting-article-bar-label"><span>If the location kept pace with Wake</span><strong>≈ {n(expected)}</strong></div><div className="voting-article-bar-plot"><div className="voting-article-bar voting-article-bar-benchmark" style={{width:`${expected/maximum*100}%`}}/></div></div>
   <p className="voting-article-benchmark-gap">About <strong>{n(expected-actual)} ballots below the benchmark</strong></p>
   <div className="voting-article-bar-axis" aria-hidden="true">{[0,2000,4000,6000].map(v=><span key={v} style={{left:`${v/maximum*100}%`}}>{n(v)}</span>)}</div>
   <div className="voting-article-axis-title">Early ballots</div>
   <figcaption>Source: NCSBE. The benchmark holds Talley’s 2022 share of Wake’s ages 18–24 early ballots constant; it does not count people who failed to vote. <a href="../references.html?v=20261104full17#youngest-benchmark">Worked calculation →</a></figcaption>
  </figure>
 </DataComponent></div>;
}

export function ReportContent(){
 const {snapshot}=useDataApp(),rows=snapshot.queries.age_growth_benchmarks.rows,youngest=rows.find(r=>r.cohort==='18–24');
 const otherAges=<ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Every age group under 65 lagged Wake’s growth at the new Western Boulevard site"><RichNarrative id="voting-article-reading:body" value={`## Every age group under 65 lagged Wake’s growth at the new Western Boulevard site

The gap extended beyond college-age voters. Growth from **Talley in 2022 to Western Boulevard in 2026** fell behind Wake’s same-age growth among voters **25–34, 35–44 and 45–64**. Voters **65 and older** were the exception: **73.7%** growth at the two locations, versus **52.8%** countywide. All five groups cast more early ballots; the difference is how quickly their counts grew.`}/></ReportSection>;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <TechnicianHeader/>
  <nav className="voting-page-nav technician-preview-links" aria-label="Preview and evidence"><a href="index.html?view=1" aria-current="page">Full article · Draft</a><a href="../editor-preview.html">Map editor preview</a><a href="../references.html?v=20261104full17">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="article_opening_context" queryIds={['article_opening_context','campus_parking','age_growth_benchmarks']} sourceRowsByQuery={{article_opening_context:snapshot.queries.article_opening_context.rows,campus_parking:snapshot.queries.campus_parking.rows,age_growth_benchmarks:rows}} showHeading={false} title="Talley to Western Boulevard: college-age voting growth trails Wake"><RichNarrative id="voting-article-intro:body" value={`# Talley to Western Boulevard: college-age voting growth trails Wake

Growth at the replacement site lagged Wake County’s in every age group under 65, with the largest gap among voters ages 18–24.`}/>
   <div className="technician-preview-byline"><a href="https://technicianonline.com/staff_name/sean-ryan/">Sean Ryan</a>, Correspondent · Draft</div>
   <RichNarrative id="voting-article-intro:opening" value={`

North Carolina’s midterm election is over, following a record early-voting period, [NC Newsline reported](https://ncnewsline.com/2026/11/02/democrats-and-unaffiliated-voters-cast-about-73-of-ballots-in-ncs-record-setting-early-turnout/). The complete early-voting period offers a first look at voting after NC State’s location moved from **Talley Student Union to Western Boulevard Business Services**. The NCSBE records downloaded November 4 remain preliminary while canvass continues.

Parking was one argument for the move: board members said the Western Boulevard location would be easier for off-campus voters to reach by car, [according to NC Newsline’s meeting coverage](https://ncnewsline.com/2026/06/12/republicans-axe-nc-state-student-center-as-an-early-voting-site/). Yet Talley sits beside Coliseum Deck, whose university GIS records list **2,192 spaces**, compared with **660 across the McKimmon lots**—about **3.3 times as many**. Those are total parking inventories. At McKimmon, only part of the lot was reserved for early voters, as shown in [NC State’s map of general and accessible voter parking](https://transportation.ncsu.edu/2026/10/early-voting-at-nc-state-october-15-31/).

The map below compares modeled walks from student housing. The ballot analysis that follows compares **Talley in 2022 with Western Boulevard in 2026**, using the same full 17-day early-voting periods. It shows what changed, without isolating the move’s effect.`}/></ReportSection>
  <CampusWalkingMap article/>
  <ReportSection id="voting-article-routine-intro" queryId="campus_passby" sourceRows={snapshot.queries.campus_passby.rows.filter(r=>!r.ends_at_talley)} showHeading={false} title="Would routine walks bring students near the site?"><RichNarrative id="voting-article-routine-intro:body" value={`## Would routine walks bring students near the site?

A simulation modeled **756 routes from housing to classroom and dining buildings identified in NC State’s GIS, plus Hill and Hunt libraries**, to test whether routine walks would pass near either voting site. [GIS labels and exclusions](../references.html?v=20261104full17#destination-gis-sources).

**334 routes—44.2%—passed within 50 meters of Talley’s building outline**, the former early-voting location. **None passed within 50 meters of Western Boulevard’s building outline**. The simulation describes opportunities to pass nearby; it does not measure how many students actually walked those routes, noticed the site or voted.`}/></ReportSection>
  <CampusPassbyMap article/>
  <ReportSection id="voting-article-turnout" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="College-age voting grew, but fell behind Wake"><RichNarrative id="voting-article-turnout:body" value={`Among voters ages **18–24**, early ballots grew **36.4%** from Talley in 2022 to Western Boulevard in 2026, compared with **90.8%** across Wake County—a **54.5 percentage-point growth gap**, the largest of the five age groups.

The campus-site count for ages 18–24 increased from **3,402 to 4,639**, while Wake’s increased from **13,398 to 25,570**. The location’s share of Wake’s early ballots in that age group fell from **25.4% to 18.1%**.

*Accepted in-person early ballots across all 17 days: October 20–November 5, 2022, and October 15–31, 2026. Downloaded November 4; 2026 remains preliminary. Election Day and mail ballots are excluded. Ages 18–24 do not verify student enrollment.*`}/></ReportSection>
  <AgeGrowthChart/>
  {otherAges}
  <YoungestBenchmark row={youngest}/>
  <ReportSection id="voting-article-closing" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Reading the comparison"><RichNarrative id="voting-article-closing:body" value={`These figures describe early-ballot counts and location use. They do not establish whether the relocation caused the growth gap. Ages 18–24 are an age proxy, not verified student enrollment.

[Follow the original counts and calculations, step by step](../references.html?v=20261104full17).`}/></ReportSection>
  <footer className="technician-preview-footer">Editor preview · Work in progress · <a href="../references.html#statewide-early-voting">Sources and original chart reference</a></footer>
 </article>;
}
