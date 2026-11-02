import React from 'react';
import {DataComponent,useDataApp} from '../../data-app-public.jsx';
const AGES=['18–24','25–34','35–44','45–64','65+'];
const pct=v=>`${v>0?'+':''}${v.toFixed(1)}%`;
const n=v=>v.toLocaleString('en-US');
export function AgeGrowthChart(){
 const {snapshot}=useDataApp(),rows=AGES.map(age=>snapshot.queries.age_growth_benchmarks.rows.find(r=>r.cohort===age)),ceiling=125;
 return <section id="age-growth-chart" className="voting-article-growth-chart-wrap"><DataComponent id="voting-article-age-growth-chart" queryId="age_growth_benchmarks" sourceRows={rows} displayRows={rows} kind="custom" title="Early-ballot growth by age, 2022–2026">
  <figure className="voting-article-growth-chart age-growth-compact" data-reviewed-rows aria-label="Talley to Western Boulevard growth compared with Wake County, youngest age group first. All five age groups gained ballots; ages under 65 grew more slowly than Wake.">
   <p className="age-growth-scope">First 16 early-voting days · percentage growth on a shared 0–125% scale</p>
   <div className="age-growth-legend"><span><i className="growth-site"/>Talley (2022) → Western Boulevard (2026)</span><span><i className="growth-county"/>Wake County</span></div>
   <div className="age-growth-head" aria-hidden="true"><span>Age</span><div className="age-growth-axis">{[0,25,50,75,100,125].map(v=><span key={v} style={{left:`${v/ceiling*100}%`}}>{v}%</span>)}</div><span>Gap vs Wake</span><span>Talley → Western<br/>Ballots · 2022 → 2026</span></div>
   <div className="age-growth-rows">{rows.map(row=><section className="age-growth-row" key={row.cohort} aria-label={`Ages ${row.cohort}`}>
    <h3>{row.cohort}</h3>
    <div className="age-growth-bars">{[['site','Talley (2022) → Western Blvd (2026)'],['county','Wake County']].map(([key,label])=><div className="age-growth-series" key={key} tabIndex={0} aria-label={`${label}, ages ${row.cohort}: ${pct(row[key+'_growth_pct'])} growth; ${n(row[key+'_ballots_2022'])} to ${n(row[key+'_ballots_2026'])} ballots`}>
     <div className="age-growth-track"><div className={`age-growth-bar growth-${key}`} style={{width:`${row[key+'_growth_pct']/ceiling*100}%`}} data-growth={row[key+'_growth_pct']}/></div><strong>{pct(row[key+'_growth_pct'])}</strong>
     <span className="age-growth-tooltip" role="tooltip">{label} · Ages {row.cohort}<br/>{n(row[key+'_ballots_2022'])} → {n(row[key+'_ballots_2026'])} ballots<br/>({n(row[key+'_ballots_2026'])} − {n(row[key+'_ballots_2022'])}) ÷ {n(row[key+'_ballots_2022'])} × 100 = {pct(row[key+'_growth_pct'])}</span>
    </div>)}</div>
    <div className="age-growth-gap"><strong>{Math.abs(row.site_growth_gap_pp).toFixed(1)} pp</strong><span><span className={row.site_growth_gap_pp<0?'growth-behind':'growth-ahead'}>{row.site_growth_gap_pp<0?'behind':'ahead'}</span> {row.site_growth_gap_pp<0?'Wake':'of Wake'}</span></div>
    <p className="age-growth-counts"><span>{n(row.site_ballots_2022)} → {n(row.site_ballots_2026)}</span></p>
   </section>)}</div>
   <figcaption>pp = percentage points. Each age group is compared with Wake’s growth in that same age group; Wake includes the named site. All counts increased. These are ballot counts, not turnout rates or verified student enrollment. Matched periods: October 20–November 4, 2022, and October 15–30, 2026 (preliminary). Source: NCSBE. Hover or focus a bar for counts and its calculation. <a href="../references.html?v=20261102refs3#math">Counts and worked calculations →</a></figcaption>
  </figure>
 </DataComponent></section>;
}
