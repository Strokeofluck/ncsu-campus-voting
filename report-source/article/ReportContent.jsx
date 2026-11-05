import React from 'react';
import {ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusPassbyMap} from './CampusPassbyMap.jsx';
import {CampusWalkingMap} from './CampusWalkingMap.jsx';
import {AgeGrowthChart} from './AgeGrowthChart.jsx';
import {YoungestBenchmark} from './YoungestBenchmark.jsx';
import {TechnicianHeader} from './TechnicianHeader.jsx';
import './article.css';

export function ReportContent(){
 const {snapshot}=useDataApp(),rows=snapshot.queries.age_growth_benchmarks.rows,youngest=rows.find(r=>r.cohort==='18–24');
 const otherAges=<ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Every age group under 65 lagged Wake’s growth at the new Western Boulevard site"><RichNarrative id="voting-article-reading:body" value={`## Every age group under 65 lagged Wake’s growth at the new Western Boulevard site

The gap extended beyond college-age voters. Growth from **Talley in 2022 to Western Boulevard in 2026** fell behind Wake’s same-age growth among voters **25–34, 35–44 and 45–64**. Voters **65 and older** were the exception: **73.7%** growth at the two locations, versus **52.8%** countywide. All five groups cast more early ballots; the difference is how quickly their counts grew.`}/></ReportSection>;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <TechnicianHeader/>
  <nav className="voting-page-nav technician-preview-links" aria-label="Preview and evidence"><a href="index.html?view=1" aria-current="page">Full article · Draft</a><a href="../editor-preview.html">Map editor preview</a><a href="../references.html?v=20261104full17">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="age_growth_benchmarks" queryIds={['age_growth_benchmarks','article_opening_context']} sourceRowsByQuery={{age_growth_benchmarks:rows,article_opening_context:snapshot.queries.article_opening_context.rows}} showHeading={false} title="Talley to Western Boulevard: college-age voting growth trails Wake"><RichNarrative id="voting-article-intro:body" value={`# Talley to Western Boulevard: college-age voting growth trails Wake

Growth at the replacement site lagged Wake County’s in every age group under 65, with the largest gap among voters ages 18–24.`}/>
   <div className="technician-preview-byline"><a href="https://technicianonline.com/staff_name/sean-ryan/">Sean Ryan</a>, Correspondent · Draft</div>
   <RichNarrative id="voting-article-intro:opening" value={`

Early ballots cast by voters ages **18–24** grew **36.4%** from **Talley Student Union in 2022 to Western Boulevard Business Services in 2026**, compared with **90.8%** across Wake County. The **54.5 percentage-point growth gap** was the largest of the five age groups in the comparison.

The findings offer a first look at use of NC State’s replacement early-voting location after a [record midterm early-voting period statewide](https://ncnewsline.com/2026/11/02/democrats-and-unaffiliated-voters-cast-about-73-of-ballots-in-ncs-record-setting-early-turnout/). The comparison describes changes in ballot counts and site use; it does not isolate the relocation’s effect.`}/></ReportSection>
  <ReportSection id="voting-article-turnout" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="College-age voting grew, but fell behind Wake"><RichNarrative id="voting-article-turnout:body" value={`The campus-site count for ages 18–24 increased from **3,402 to 4,639**, while Wake’s increased from **13,398 to 25,570**. The location’s share of Wake’s early ballots in that age group fell from **25.4% to 18.1%**.

*Accepted in-person early ballots across all 17 days: October 20–November 5, 2022, and October 15–31, 2026. Downloaded November 4; 2026 remains preliminary. Election Day and mail ballots are excluded from this comparison. We’re awaiting finalized full-election data, including Election Day counts by age, before expanding the analysis. Ages 18–24 do not verify student enrollment.*`}/></ReportSection>
  <AgeGrowthChart/>
  {otherAges}
  <YoungestBenchmark row={youngest}/>
  <ReportSection id="voting-article-location-context" queryId="article_opening_context" queryIds={['article_opening_context','campus_parking']} sourceRowsByQuery={{article_opening_context:snapshot.queries.article_opening_context.rows,campus_parking:snapshot.queries.campus_parking.rows}} showHeading={false} title="Why the voting site moved"><RichNarrative id="voting-article-location-context:body" value={`## Why the voting site moved

The Wake County Board of Elections moved the early-voting site from Talley to Western Boulevard Business Services for the 2026 general election. Parking was one argument for the move: board members said the Western Boulevard location would be easier for off-campus voters to reach by car, [according to NC Newsline’s meeting coverage](https://ncnewsline.com/2026/06/12/republicans-axe-nc-state-student-center-as-an-early-voting-site/).

University GIS records list **2,192 spaces in Coliseum Deck beside Talley**, compared with **660 across the McKimmon lots**—about **3.3 times as many**. These are total parking inventories; they do not measure how many spaces were available to voters or how easy either location was to reach. At McKimmon, only part of the lot was reserved for early voters, as shown in [NC State’s map of general and accessible voter parking](https://transportation.ncsu.edu/2026/10/early-voting-at-nc-state-october-15-31/).

Access on foot varied by residence. The map below compares the two locations from student housing, with estimated walking times and distances for each building.`}/></ReportSection>
  <CampusWalkingMap article/>
  <ReportSection id="voting-article-routine-intro" queryId="campus_passby" sourceRows={snapshot.queries.campus_passby.rows.filter(r=>!r.ends_at_talley)} showHeading={false} title="Would routine walks bring students near the site?"><RichNarrative id="voting-article-routine-intro:body" value={`## Would routine walks bring students near the site?

A simulation modeled **756 routes from housing to classroom and dining buildings identified in NC State’s GIS, plus Hill and Hunt libraries**, to test whether routine walks would pass near either voting site. [GIS labels and exclusions](../references.html?v=20261104full17#destination-gis-sources).

**334 routes—44.2%—passed within 50 meters of Talley’s building outline**, the former early-voting location. **None passed within 50 meters of Western Boulevard’s building outline**. The simulation describes opportunities to pass nearby; it does not measure how many students actually walked those routes, noticed the site or voted.`}/></ReportSection>
  <CampusPassbyMap article/>
  <ReportSection id="voting-article-closing" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Reading the comparison"><RichNarrative id="voting-article-closing:body" value={`These figures describe early-ballot counts and location use. They do not establish whether the relocation caused the growth gap. Ages 18–24 are an age proxy, not verified student enrollment.

[Follow the original counts and calculations, step by step](../references.html?v=20261104full17).`}/></ReportSection>
  <footer className="technician-preview-footer">Editor preview · Work in progress · <a href="../references.html#statewide-early-voting">Sources and original chart reference</a></footer>
 </article>;
}
