import React from 'react';
import {ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusAgeMaps} from './PrecinctAgeComparison.jsx';
import './article.css';

export function ReportContent(){
 const {snapshot}=useDataApp();
 const rows=snapshot.queries.age_growth_benchmarks.rows;
 return <article className="report-content voting-report voting-article" aria-label="Article work in progress: NC State early voting">
  <nav className="voting-page-nav" aria-label="Page links"><a href="index.html?view=1" aria-current="page">Article · Work in progress</a><a href="../index.html?view=1#campus-age-growth">Prototype</a><a href="../references.html">References and step-by-step math</a></nav>
  <ReportSection id="voting-article-intro" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="Talley to Western Boulevard: college-age voting growth trails Wake most"><RichNarrative id="voting-article-intro:body" value={`# Talley to Western Boulevard: college-age voting growth trails Wake most

Talley Student Union’s early-voting site moved to **Western Boulevard Business Services**. Comparing **2022 at Talley** with **2026 at Western Boulevard**, early ballots from voters ages **18–24** grew **40.5%**, versus **103.6%** across Wake County. Only voters **65 and older** showed faster growth between these locations than countywide.

Matched first 16 early-voting days · 2022 vs. 2026 · Preliminary through October 30, 2026.`}/></ReportSection>
  <CampusAgeMaps article/>
  <ReportSection id="voting-article-reading" queryId="age_growth_benchmarks" sourceRows={rows} showHeading={false} title="College-age voters show the largest growth gap"><RichNarrative id="voting-article-reading:body" value={`## College-age voters show the largest growth gap

Talley Student Union recorded **2,999** early ballots from voters ages 18–24 in 2022; its replacement at Western Boulevard Business Services recorded **4,214** in 2026. That increase was **63.1 percentage points behind** Wake’s growth in the same age group—the largest gap among the five groups.

Growth from Talley in 2022 to Western Boulevard in 2026 also lagged Wake among voters ages 25–34, 35–44 and 45–64. Ages 65+ moved in the other direction: **76.0%** growth between the two locations, compared with **53.4%** countywide.

All five age groups cast more ballots at Western Boulevard in 2026 than at Talley in 2022. This comparison describes slower growth, not a decline in the number voting. It does not establish why the gap occurred or whether the relocation caused it.

[Follow the counts and calculations, step by step](../references.html).`}/></ReportSection>
 </article>;
}
