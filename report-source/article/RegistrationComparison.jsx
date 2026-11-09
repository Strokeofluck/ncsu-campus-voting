import React from 'react';
import {DataComponent,useDataApp} from '../../data-app-public.jsx';
export function RegistrationComparison(){
 const {snapshot}=useDataApp();
 const source=snapshot.queries.summary.rows.filter(r=>[2022,2026].includes(r.year)&&['Campus site','Wake County'].includes(r.scope));
 const rows=['Campus site','Wake County'].map(scope=>{
  const before=source.find(r=>r.scope===scope&&r.year===2022).same_day_registration;
  const after=source.find(r=>r.scope===scope&&r.year===2026).same_day_registration;
  return {scope,before,after,growth:(after-before)/before*100};
 });
 const gap=rows[1].growth-rows[0].growth,n=v=>v.toLocaleString('en-US');
 return <section id="same-day-registration-comparison"><DataComponent id="voting-article-registration-comparison" queryId="summary" sourceRows={source} displayRows={rows} kind="custom" title="Same-day registration growth also trailed Wake">
  <div data-reviewed-rows>
   <p>Same-day-registration ballots increased at both locations, but the Talley-to-Western Boulevard increase was <strong>{gap.toFixed(1)} percentage points behind Wake County’s</strong>.</p>
   <div className="voting-table-scroll"><table className="voting-table"><thead><tr><th>Location</th><th>2022</th><th>2026</th><th>Growth</th></tr></thead><tbody>{rows.map(r=><tr key={r.scope}><th scope="row">{r.scope==='Campus site'?'Talley → Western Boulevard':'Wake County'}</th><td>{n(r.before)}</td><td>{n(r.after)}</td><td>+{r.growth.toFixed(1)}%</td></tr>)}</tbody></table></div>
   <p><strong>Worked calculations</strong></p>
   {rows.map(r=><p key={r.scope}>{r.scope==='Campus site'?'Site':'Wake County'}: ({n(r.after)} − {n(r.before)}) ÷ {n(r.before)} × 100 = {r.growth.toFixed(4)}% ≈ <strong>{r.growth.toFixed(1)}%</strong>.</p>)}
   <p>Growth gap: {rows[1].growth.toFixed(4)} − {rows[0].growth.toFixed(4)} = {gap.toFixed(4)} percentage points ≈ <strong>{gap.toFixed(1)} pp</strong>. Calculations use unrounded growth rates.</p>
   <p className="age-growth-scope">Source: NCSBE accepted in-person early-voting records, all ages, all 17 days: October 20–November 5, 2022, and October 15–31, 2026. 2026 is preliminary. Wake includes the named site. Same-day-registration ballots are included in total ballots; do not add these counts to the age chart. These counts do not establish the effect of moving the site. <a href="../references.html?v=20261104full17">Sources and step-by-step math →</a></p>
  </div>
 </DataComponent></section>;
}
