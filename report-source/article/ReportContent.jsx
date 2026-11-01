import React from 'react';
import {ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusAgeMaps} from './PrecinctAgeComparison.jsx';
import './article.css';

export function ReportContent(){
 const {snapshot}=useDataApp();
 const rows=snapshot.queries.age_growth_benchmarks.rows;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <nav className="voting-page-nav" aria-label="Page links"><a href="index.html?view=1" aria-current="page">Article · Work in progress</a><a href="../index.html?view=1#campus-age-growth">Prototype</a><a href="../references.html">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="NC State’s new voting site trails Wake most among college-age voters"><RichNarrative id="voting-article-intro:body" value={`# NC State’s new voting site trails Wake most among college-age voters

College-age early voting grew **40.5%** at the campus polling site, compared with **103.6%** across Wake County. Voters **65 and older** were the only age group whose site growth outpaced the county.

Matched first 16 early-voting days · 2022 vs. 2026 · Preliminary through October 30, 2026.`}/></ReportSection>
  <CampusAgeMaps article/>
  <ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="College-age voters show the largest growth gap"><RichNarrative id="voting-article-reading:body" value={`## College-age voters show the largest growth gap

The campus site recorded **2,999** early ballots from voters ages 18–24 at Talley Student Union in 2022 and **4,214** at Western Boulevard Business Services in 2026. That increase was **63.1 percentage points behind** Wake’s growth in the same age group—the largest gap among the five groups.

Growth also lagged Wake among voters ages 25–34, 35–44 and 45–64. Ages 65+ moved in the other direction: **76.0%** growth at the campus site, compared with **53.4%** countywide.

All five groups cast more ballots at the campus site. This comparison describes slower growth, not a decline in the number voting. It does not establish why the gap occurred or whether the relocation caused it.

[Follow the counts and calculations, step by step](../references.html).`}/></ReportSection>
 </article>;
}
