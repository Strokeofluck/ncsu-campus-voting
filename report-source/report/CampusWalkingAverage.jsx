import React,{useState} from 'react';
import {DataComponent,useDataApp} from '../../data-app-public.jsx';

export default function WalkingAverageSummary({rows,buildings,comparisons,supplemental,group,pace,onGroup,onPace,onBuilding}){
 const {snapshot}=useDataApp(),[expanded,setExpanded]=useState(null),[source,setSource]=useState('google');
 const google=source==='google',googleRows=snapshot.queries.campus_google_walks.rows,googleAverages=snapshot.queries.campus_google_averages.rows,averages=google?googleAverages:rows,avg=averages.find(r=>r.group===group);
 const distance=(r,key)=>google?r['mean_'+key+'_miles']:r['mean_'+key+'_m']/1609.344,time=(r,key)=>google?r['mean_'+key+'_minutes']:r['mean_'+key+'_m']/pace;
 const changeDistance=r=>google?r.mean_change_miles:r.mean_change_m/1609.344,changeTime=r=>google?r.mean_change_minutes:r.mean_change_m/pace;
 return <DataComponent id="voting-campus-walking-average" queryId={google?'campus_google_averages':'campus_walk_averages'} queryIds={['campus_google_averages','campus_google_walks','campus_walk_averages','campus_walking_routes','campus_estimated_access']} sourceRowsByQuery={{campus_google_averages:googleAverages,campus_google_walks:googleRows,campus_walk_averages:rows,campus_walking_routes:buildings,campus_estimated_access:supplemental}} displayRows={averages} kind="custom" title="Is the new site farther on average?">
  <div className="walking-controls walking-average-controls">
   <label>Walking source<select aria-label="Walking source" value={source} onChange={e=>setSource(e.target.value)}><option value="google">Google walking directions</option><option value="gis">NC State GIS model</option></select></label>
   <label>Housing area<select aria-label="Housing area" value={group} onChange={e=>onGroup(e.target.value)}>{averages.map(r=><option key={r.group}>{r.group}</option>)}</select></label>
   {!google&&<label>Assumed walking pace<select aria-label="Assumed walking pace" value={pace} onChange={e=>onPace(Number(e.target.value))}><option value="60">26.8 min per mile</option><option value="80">20.1 min per mile</option><option value="100">16.1 min per mile</option></select></label>}
  </div>
  <div className="walking-average-results" data-reviewed-rows aria-live="polite">
   <h3>Building average · {group}</h3><p className="walking-average-coverage">{avg.included_buildings} / {avg.total_buildings} buildings · {google?'Google suggested walks, checked November 1, 2026':'GIS model · includes recovered and estimated access'}</p>
   <div className="walking-result-pair">{[['talley','Talley (2022)'],['western','Western Boulevard (2026)']].map(([key,title])=><div key={key}><span>{title}</span><strong>≈ {time(avg,key).toFixed(1)} min</strong><span>{distance(avg,key).toFixed(2)} mi average one way</span></div>)}</div>
   <p className="walking-average-change"><strong>{Math.abs(changeDistance(avg)).toFixed(2)} mi {changeDistance(avg)>=0?'farther':'closer'} on average</strong><span>≈ {Math.abs(changeTime(avg)).toFixed(1)} min {changeTime(avg)>=0?'longer':'shorter'} one way{!google&&` at ${(1609.344/pace).toFixed(1)} min per mile`}</span></p>
   <p className="walking-average-direction">{avg.farther_buildings} buildings farther · {avg.closer_buildings} closer{avg.unchanged_buildings?` · ${avg.unchanged_buildings} same rounded mileage`:''}</p>
  </div>
  <p className="walking-average-limit">Each building counts equally, regardless of occupancy. {google?'Google supplies the suggested route, rounded mileage and estimated time. Its paths can differ from the GIS preview below; exact voting-room doors are unverified.':'All 40 route pairs are included: one recovered mapped entrance and three estimated building-edge starts. The earlier 36-building baseline is preserved in References.'}</p>
  <div className="voting-table-scroll"><table className="voting-table walking-average-table"><caption>How the average changes by housing area</caption><thead><tr><th>Housing area</th><th>Buildings compared</th><th>Average distance change</th><th>Average time change</th></tr></thead><tbody data-reviewed-rows>
   {averages.map(r=><React.Fragment key={r.group}>
    <tr className={r.group===group?'walking-average-selected':undefined}><th><button aria-expanded={expanded===r.group} onClick={()=>{onGroup(r.group);setExpanded(v=>v===r.group?null:r.group);}}>{expanded===r.group?'▾ ':'▸ '}{r.group}</button></th><td>{r.included_buildings} / {r.total_buildings}</td><td>{Math.abs(changeDistance(r)).toFixed(2)} mi {changeDistance(r)>=0?'farther':'closer'}</td><td>{Math.abs(changeTime(r)).toFixed(1)} min {changeTime(r)>=0?'longer':'shorter'}</td></tr>
    {expanded===r.group&&<tr><td colSpan="4"><div className="walking-group-locations" aria-label={`${r.group} building locations`}><p>{google?'Google’s suggested walks, one way. Links open the checked directions.':'GIS model distances for the prototype paths below. Google can suggest a different route.'}</p><ul>
     {comparisons.filter(b=>r.group==='All housing'||b.group===r.group).map(b=>{const g=googleRows.find(r=>r.id===b.id);return <li key={b.id}><button onClick={()=>onBuilding(b.id)}>{b.name}</button><div className="walking-building-mileage"><span>Talley: ≈ {google?g.talley_miles.toFixed(1):(b.talley_m/1609.344).toFixed(2)} mi · Western: ≈ {google?g.western_miles.toFixed(1):(b.western_m/1609.344).toFixed(2)} mi</span><small><a href={g.talley_url} target="_blank" rel="noopener">Google walk: Talley{google?` · ${g.talley_minutes} min`:''}</a><span> · </span><a href={g.western_url} target="_blank" rel="noopener">Western{google?` · ${g.western_minutes} min`:''}</a>{b.estimated_access&&<> · <a href="references.html#housing-access-recovery">Estimated start pin</a></>}</small></div></li>;})}
    </ul></div></td></tr>}
   </React.Fragment>)}
  </tbody></table></div>
  <p className="walking-average-links"><a href={google?'references.html#google-walking-checks':'references.html#walking-average'}>Average calculation and sources →</a> · <a href={google?'data/processed/campus-walk/google-averages.csv':'data/processed/campus-walk/averages.csv'}>Download averages (.csv)</a></p>
 </DataComponent>;
}
