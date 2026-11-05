import React from 'react';
import {DataComponent,useDataApp} from '../../data-app-public.jsx';
const n=v=>v.toLocaleString('en-US');
export function FullElectionContext(){
 const {snapshot}=useDataApp(),rows=snapshot.queries.full_election_context.rows,wake=rows.find(r=>r.scope==='Wake County');
 return <section className="full-election-context"><DataComponent id="voting-full-election-context" queryId="full_election_context" sourceRows={rows} displayRows={rows} kind="custom" title="After Election Day: the wider voting picture">
  <div className="full-election-body" data-reviewed-rows>
   <p className="age-growth-scope">All voting methods · all ages · November 4, 2026 pull · 2026 unofficial</p>
   <div className="full-election-table"><table><caption>Ballots cast, including Election Day, early voting and mail</caption><thead><tr><th scope="col">Area</th><th scope="col">2022 official</th><th scope="col">2026 unofficial</th><th scope="col">Change</th></tr></thead><tbody>{rows.map(r=><tr key={r.scope}><th scope="row">{r.scope}</th><td>{n(r.ballots_2022)}</td><td>{n(r.ballots_2026)}</td><td>+{r.growth_pct.toFixed(1)}%</td></tr>)}</tbody></table></div>
   <p>Wake’s reported turnout was <strong>{wake.reported_turnout_pct_2026.toFixed(2)}%</strong>, versus {wake.reported_turnout_pct_2022.toFixed(2)}% in 2022. All {wake.precincts_total_2026} precincts had reported; the 2026 total is still unofficial.</p>
   <div className="full-election-table"><table><caption>Wake County accepted early and mail ballots, from separate absentee-file snapshots</caption><thead><tr><th scope="col">Voting method</th><th scope="col">2022</th><th scope="col">2026 preliminary</th></tr></thead><tbody><tr><th scope="row">In-person early voting</th><td>{n(wake.early_2022)}</td><td>{n(wake.early_2026)}</td></tr><tr><th scope="row">Mail</th><td>{n(wake.mail_2022)}</td><td>{n(wake.mail_2026)}</td></tr></tbody></table></div>
   <p>Wake’s early-ballot count grew 52.4%, compared with {wake.growth_pct.toFixed(1)}% across all voting methods. The voting-method mix changed, so early-voting growth is not the same as overall participation growth.</p>
   <p className="full-election-note">Election Day age breakdowns are not yet available in NCSBE’s 2026 voter-history release. The age charts above still cover in-person early voting only. The provisional file lists {n(wake.pending_provisionals)} pending Wake records; those are not additional counted ballots. Mail includes accepted cured and exception ballots. These files have different cutoffs, so subtracting them from the dashboard total would not establish an Election Day voter count.</p>
   <p><a href="../references.html?v=20261104allmethods#full-election-data">Official sources, Election Day contest votes and aggregate downloads →</a></p>
  </div>
 </DataComponent></section>;
}
