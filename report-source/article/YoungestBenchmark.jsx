import React from 'react';
import {DataComponent} from '../../data-app-public.jsx';

export function YoungestBenchmark({row}){
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
