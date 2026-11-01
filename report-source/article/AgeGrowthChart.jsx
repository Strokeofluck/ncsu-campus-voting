import React from 'react';
import {DataComponent,useDataApp} from '../../data-app-public.jsx';

const AGES=['18–24','25–34','35–44','45–64','65+'];
const pct=v=>`${v>0?'+':''}${v.toFixed(1)}%`;
const n=v=>v.toLocaleString('en-US');
export function AgeGrowthChart(){
 const {snapshot}=useDataApp(),rows=AGES.map(age=>snapshot.queries.age_growth_benchmarks.rows.find(r=>r.cohort===age));
 const ceiling=125;
 return <section id="age-growth-chart" className="voting-article-growth-chart-wrap"><DataComponent id="voting-article-age-growth-chart" queryId="age_growth_benchmarks" sourceRows={rows} displayRows={rows} kind="custom" title="Early-ballot growth by age, 2022–2026">
  <figure className="voting-article-growth-chart" data-reviewed-rows aria-label="Talley to Western Boulevard growth compared with Wake County, youngest age group first. All five age groups gained ballots; ages under 65 grew more slowly than Wake.">
   <p className="growth-chart-scope">NC State early-voting site compared with Wake County · first 16 early-voting days</p>
   <div className="growth-chart-legend"><span><i className="growth-site"/>Talley (2022) → Western Boulevard (2026)</span><span><i className="growth-county"/>Wake County</span></div>
   <div className="growth-chart-axis" aria-hidden="true">{[0,25,50,75,100,125].map(v=><span key={v} style={{left:`${v/ceiling*100}%`}}>{v}%</span>)}</div>
   <div className="growth-chart-groups">{rows.map(row=><section className="growth-chart-group" key={row.cohort} aria-label={`Ages ${row.cohort}`}>
    <div className="growth-chart-group-heading"><h3>Ages {row.cohort}</h3><span><strong>{Math.abs(row.site_growth_gap_pp).toFixed(1)} pp</strong> {row.site_growth_gap_pp<0?'behind':'ahead of'} Wake</span></div>
    {[['site','Talley (2022) → Western Blvd (2026)'],['county','Wake County']].map(([key,label])=><div className="growth-chart-bar-row" key={key} tabIndex={0} aria-label={`${label}, ages ${row.cohort}: ${pct(row[key+'_growth_pct'])} growth; ${n(row[key+'_ballots_2022'])} to ${n(row[key+'_ballots_2026'])} ballots`}>
     <span className="growth-chart-series-label">{label}</span><div className="growth-chart-track"><div className={`growth-chart-bar growth-${key}`} style={{width:`${row[key+'_growth_pct']/ceiling*100}%`}} data-growth={row[key+'_growth_pct']}/></div><strong className="growth-chart-value">{pct(row[key+'_growth_pct'])}</strong>
     <span className="growth-chart-tooltip" role="tooltip">{label} · Ages {row.cohort}<br/>{n(row[key+'_ballots_2022'])} → {n(row[key+'_ballots_2026'])} ballots<br/>({n(row[key+'_ballots_2026'])} − {n(row[key+'_ballots_2022'])}) ÷ {n(row[key+'_ballots_2022'])} × 100 = {pct(row[key+'_growth_pct'])}</span>
    </div>)}
    <p className="growth-chart-counts">Talley 2022: {n(row.site_ballots_2022)} → Western Boulevard 2026: {n(row.site_ballots_2026)} ballots · <a href={`../references.html?age=${encodeURIComponent(row.cohort)}#math`}>Math →</a></p>
   </section>)}</div>
   <figcaption>pp = percentage points. Each age group is compared with Wake’s growth in that same age group; Wake includes the two sites. All counts increased. These are ballot counts, not turnout rates or verified student enrollment. Matched periods: October 20–November 4, 2022, and October 15–30, 2026 (preliminary). Source: NCSBE. <a href="../references.html#math">Counts and worked calculations →</a></figcaption>
  </figure>
 </DataComponent></section>;
}
