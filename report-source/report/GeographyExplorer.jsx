import React,{useState} from 'react';
import {DataComponent,EvidenceChart,ReportSection,RichNarrative,useDataApp} from '../../data-app-public.jsx';
const years=[2022,2024,2026],bands=['All ages','18–24','25–34','35–44','45–64','65+'];
const n=value=>value===null||value===undefined?'N/A':Number(value).toLocaleString('en-US');
const p=value=>value===null||value===undefined?'N/A':`${value.toFixed(1)}%`;
const signed=value=>{const rounded=Number(value.toFixed(1));return `${rounded>0?'+':''}${rounded.toFixed(1)}`;};
const site=year=>year===2026?'Western Boulevard Business Services':'Talley Student Union';
function YearCell({row}){return <><span className="voting-final-count">{n(row?.site_ballots)} at site</span><span className="voting-final-detail">{n(row?.other_wake_ballots)} at other Wake sites</span><span className="voting-final-detail">{p(row?.site_share_pct)} using named site</span></>;}
function ChangeCell({current,previous}){
 if(!current?.area_present||!previous?.area_present)return <>N/A</>;
 const change=current.site_ballots-previous.site_ballots,growth=previous.site_ballots>0?change/previous.site_ballots*100:null,shareChange=current.site_share_pct!==null&&previous.site_share_pct!==null?current.site_share_pct-previous.site_share_pct:null;
 return <><span className="voting-final-count">{change>0?'+':''}{n(change)} at site</span><span className="voting-final-detail">{growth===null?'Growth N/A':`${signed(growth)}% growth`}</span><span className="voting-final-detail">{shareChange===null?'Share change N/A':`${signed(shareChange)} pp site share`}</span></>;
}
export function GeographyExplorer(){
 const {snapshot,visible}=useDataApp();
 const [dimension,setDimension]=useState('Precinct'),[cohort,setCohort]=useState('18–24'),[measure,setMeasure]=useState('count'),[search,setSearch]=useState(''),[page,setPage]=useState(0);
 const rows=snapshot.queries.geography.rows.filter(r=>r.dimension===dimension&&r.cohort===cohort);
 const allAreas=[...new Set(rows.map(r=>r.area))];
 const byArea=Object.fromEntries(allAreas.map(area=>[area,Object.fromEntries(rows.filter(r=>r.area===area).map(r=>[r.year,r]))]));
 const rank=area=>years.reduce((sum,year)=>sum+(byArea[area][year]?.site_ballots??0),0);
 const areas=allAreas.filter(area=>area.toLowerCase().includes(search.trim().toLowerCase())).sort((a,b)=>rank(b)-rank(a)||a.localeCompare(b));
 const selected=new Set(areas),topAreas=new Set(areas.slice(0,10)),source=rows.filter(r=>selected.has(r.area));
 const plotted=source.filter(r=>topAreas.has(r.area)).map(r=>({...r,area_label:dimension==='Precinct'?r.area.replace(/^PRECINCT\s+/i,''):r.area,year_label:`${r.year} · ${r.year===2026?'Western Boulevard':'Talley'}`,'Named-site share (%)':r.site_share_pct}));
 // Retain the same area order for all three years and both measures.
 plotted.sort((a,b)=>areas.indexOf(a.area)-areas.indexOf(b.area)||a.year-b.year);
 const pageSize=20,maxPage=Math.max(0,Math.ceil(areas.length/pageSize)-1),currentPage=Math.min(page,maxPage),shown=areas.slice(currentPage*pageSize,(currentPage+1)*pageSize);
 const totals=Object.fromEntries(years.map(year=>{const values=source.filter(r=>r.year===year&&r.area_present),at=values.reduce((sum,r)=>sum+r.site_ballots,0),other=values.reduce((sum,r)=>sum+r.other_wake_ballots,0),wake=at+other;return [year,{area_present:values.length>0,site_ballots:values.length?at:null,other_wake_ballots:values.length?other:null,wake_ballots:values.length?wake:null,site_share_pct:wake>0?at/wake*100:null}];}));
 const reset=setter=>e=>{setter(e.target.value);setPage(0);};
 return <div id="voter-origins" className="voting-party-section">
  <ReportSection id="voting-geography-intro" title="Where voters came from" queryId="geography" sourceRows={source} showHeading={false}>
   <RichNarrative id="voting-geography-intro:body" value={`## Where voters came from

Did early voters from the same residential areas use Talley or Western Boulevard, or other Wake locations? Explore their recorded precincts and ZIP codes across the first 16 early-voting days in each year.`}/>
  </ReportSection>
  <div className="voting-controls voting-geography-controls">
   <label>Group residence by <select value={dimension} onChange={reset(setDimension)}><option>Precinct</option><option>ZIP code</option></select></label>
   <label>Residence age group <select value={cohort} onChange={reset(setCohort)}>{bands.map(v=><option key={v} value={v}>{v==='All ages'?'All ages':`Ages ${v}`}</option>)}{snapshot.queries.geography.rows.some(r=>r.cohort==='Unknown / outside range'&&r.wake_ballots>0)&&<option value="Unknown / outside range">Unknown / outside age bands</option>}</select></label>
   <label>Show <select value={measure} onChange={reset(setMeasure)}><option value="count">Ballots at Talley / Western Boulevard</option><option value="share">Share using Talley / Western Boulevard</option></select></label>
   <label>Find an area <input type="search" value={search} onChange={reset(setSearch)} placeholder={dimension==='Precinct'?'Search precinct code':'Search ZIP code'}/></label>
  </div>
  <RichNarrative id="voting-geography:scope" value={`${cohort==='All ages'?'All ages':cohort==='Unknown / outside range'?'Unknown / outside age bands':`Ages ${cohort}`} · ${dimension}. Talley Student Union in 2022 and 2024; Western Boulevard Business Services in 2026. Share means the fraction of an area’s selected early ballots cast at that year’s named site.`}/>
  {visible('voting-geography-chart')&&<EvidenceChart id="voting-geography-chart" queryId="geography" title={`Where ${cohort==='All ages'?'site voters':`site voters ages ${cohort}`} lived · ${dimension.toLowerCase()}`} description="Up to ten matching areas, ranked by their combined Talley/Western Boulevard ballots across all three years." rows={plotted} sourceRows={source.filter(r=>topAreas.has(r.area))} spec={{type:'horizontalBar',x:'area_label',y:measure==='count'?'site_ballots':'Named-site share (%)',series:'year_label',stackable:false,startAtZero:true,valueDecimals:measure==='count'?0:1}} height={Math.max(320,topAreas.size*55)}>
   <RichNarrative id="voting-geography-chart:note" value="The chart shows up to ten areas. Use the search to find another area; the table includes every matching area. A missing area/year stays N/A, rather than being treated as zero."/>
  </EvidenceChart>}
  <DataComponent id="voting-geography-table" queryId="geography" kind="table" className="voting-final-summary" title="Location choices by residential area" sourceRows={source} displayRows={source}>
   <div className="voting-table-scroll"><table className="voting-table voting-final-table"><thead><tr><th>{dimension}</th>{years.map(year=><th key={year}>{site(year)}<br/>{year}<span className="voting-final-detail">Named site · other Wake sites · site share</span></th>)}<th>2026 versus 2022</th><th>2026 versus 2024</th></tr></thead><tbody data-reviewed-rows>{shown.map(area=><tr key={area}><th scope="row">{area}</th>{years.map(year=><td key={year}><YearCell row={byArea[area][year]}/></td>)}{[2022,2024].map(year=><td key={year}><ChangeCell current={byArea[area][2026]} previous={byArea[area][year]}/></td>)}</tr>)}{!shown.length&&<tr><td colSpan={6}>No areas match this search.</td></tr>}</tbody><tfoot data-reviewed-rows><tr><th scope="row">All matching areas</th>{years.map(year=><td key={year}><YearCell row={totals[year]}/></td>)}{[2022,2024].map(year=><td key={year}><ChangeCell current={totals[2026]} previous={totals[year]}/></td>)}</tr></tfoot></table></div>
   <div className="voting-geography-pagination"><button disabled={currentPage===0} onClick={()=>setPage(currentPage-1)}>Previous areas</button><span role="status">{areas.length?`${currentPage*pageSize+1}–${Math.min((currentPage+1)*pageSize,areas.length)} of ${areas.length} areas`:'0 areas'}</span><button disabled={currentPage>=maxPage} onClick={()=>setPage(currentPage+1)}>Next areas</button></div>
   <RichNarrative id="voting-geography-table:math" value="Named-site share = ballots at Talley or Western Boulevard ÷ all selected early ballots from that residential area at any Wake site × 100. Other Wake ballots = that area’s Wake total minus its named-site ballots. Percentage-point changes use unrounded shares. The total combines all matching areas, including later table pages."/>
   <a href="data/processed/comparison/matched_geography.csv" download>Download all precinct and ZIP aggregates (.csv)</a>
  </DataComponent>
  <RichNarrative id="voting-geography:limits" value="Precinct boundaries, area labels and populations can change between elections. ZIP codes are broad residence groups. This does not track the same people across years or identify students. It describes location use among accepted early ballots, not turnout among residents. 2024 was presidential; 2022 and 2026 are midterms. Mail and Election Day voting are outside this comparison."/>
 </div>;
}
