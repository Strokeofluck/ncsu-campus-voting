import React,{useEffect,useMemo,useRef,useState} from 'react';
import * as L from './vendor/leaflet/leaflet-src.esm.js';
import './vendor/leaflet/leaflet.css';
import {DataComponent,EvidenceChart,RichNarrative,useDataApp} from '../../data-app-public.jsx';

const YEARS=[2022,2024,2026],COLORS=['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'];
const AGE_BANDS=['18–24','25–34','35–44','45–64','65+'];
const num=value=>value===null||value===undefined?'N/A':Number(value).toLocaleString('en-US');
const pct=value=>typeof value==='number'?`${value.toFixed(1)}%`:'N/A';
const siteName=year=>year===2026?'Western Boulevard Business Services':'Talley Student Union';
const color=value=>typeof value==='number'?COLORS[Math.min(4,Math.floor(value/20))]:'#bcbcbc';
const escapeHTML=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function tooltipNode(title,lines){
 const box=document.createElement('div');box.className='voting-map-tooltip-content';
 const heading=document.createElement('strong');heading.textContent=title;box.append(heading);
 for(const text of lines){const line=document.createElement('div');line.textContent=text;box.append(line);}
 return box;
}

export function PrecinctMap({cohort,onSelectArea,onCohortChange}){
 const {snapshot,visible}=useDataApp();
 const shapes=snapshot.queries.precinct_shapes.rows,points=snapshot.queries.voting_site_points.rows;
 const [year,setYear]=useState(2026),[selected,setSelected]=useState('PRECINCT 01-23'),[streetError,setStreetError]=useState(false);
 const [ageView,setAgeView]=useState('counts');
 const host=useRef(null),mapRef=useRef(null),layersRef=useRef(new Map()),groupRef=useRef(null),handler=useRef(onSelectArea);
 handler.current=onSelectArea;
 const rows=useMemo(()=>snapshot.queries.geography.rows.filter(r=>r.dimension==='Precinct'&&r.cohort===cohort),[snapshot.queries.geography.rows,cohort]);
 const byKey=useMemo(()=>new Map(rows.map(r=>[`${r.year}|${r.area}`,r])),[rows]);
 const availableAreas=useMemo(()=>[...new Set(rows.map(r=>r.area))].sort(),[rows]);
 const shapeAreas=useMemo(()=>new Set(shapes.map(r=>r.area)),[shapes]);
 const state=useRef({year,selected,byKey,cohort});state.current={year,selected,byKey,cohort};
 const currentRows=rows.filter(r=>r.year===year),mapped=currentRows.filter(r=>shapeAreas.has(r.area));
 const unmapped=currentRows.filter(r=>r.area_present&&!shapeAreas.has(r.area)&&r.wake_ballots>0),unmappedBallots=unmapped.reduce((sum,r)=>sum+r.wake_ballots,0);
 const selectedAgeRows=useMemo(()=>snapshot.queries.geography.rows.filter(r=>r.dimension==='Precinct'&&r.area===selected),[snapshot.queries.geography.rows,selected]);
 const ageLookup=useMemo(()=>new Map(selectedAgeRows.map(r=>[`${r.year}|${r.cohort}`,r])),[selectedAgeRows]);
 const ageBands=[...AGE_BANDS,...(selectedAgeRows.some(r=>r.cohort==='Unknown / outside range'&&r.wake_ballots>0)?['Unknown / outside range']:[])];
 const agePlot=ageBands.flatMap(band=>{const r=ageLookup.get(`${year}|${band}`);return [{age_band:band,location:siteName(year),ballots:r?.site_ballots??null,'Within-age group (%)':r?.site_share_pct??null},{age_band:band,location:'Other Wake locations',ballots:r?.other_wake_ballots??null,'Within-age group (%)':r?.wake_ballots>0?r.other_wake_ballots/r.wake_ballots*100:null}];});
 const ageTableCell=(y,band)=>{const r=ageLookup.get(`${y}|${band}`);return <><span className="voting-final-count">{num(r?.site_ballots)} at {y===2026?'Western Boulevard':'Talley'}</span><span className="voting-final-detail">{num(r?.other_wake_ballots)} at other Wake locations</span><span className="voting-final-detail">{pct(r?.site_share_pct)} of {num(r?.wake_ballots)} used the named site</span></>;};
 const companionArea=selected==='PRECINCT 01-31'?'PRECINCT 01-23':'PRECINCT 01-31';
 const companionRows=snapshot.queries.geography.rows.filter(r=>r.dimension==='Precinct'&&r.area===companionArea);
 const mapEvidenceRows=[...rows.filter(r=>r.area!==selected),...selectedAgeRows];
 const selectArea=area=>{setSelected(area);handler.current?.(area);};
 const selectRef=useRef(selectArea);selectRef.current=selectArea;
 const styleFor=area=>{
  const s=state.current,r=s.byKey.get(`${s.year}|${area}`),chosen=s.selected===area;
  return {color:chosen?'#e36d31':'#536477',weight:chosen?3.5:1.15,opacity:1,fillColor:color(r?.site_share_pct),fillOpacity:typeof r?.site_share_pct==='number'?0.44:0.3,dashArray:typeof r?.site_share_pct==='number'?undefined:'3 4'};
 };
 useEffect(()=>{
  if(!host.current)return undefined;
  const map=L.map(host.current,{center:[points.reduce((s,p)=>s+p.latitude,0)/points.length,points.reduce((s,p)=>s+p.longitude,0)/points.length],zoom:14,scrollWheelZoom:false,minZoom:9,maxZoom:18,zoomControl:true,attributionControl:true});mapRef.current=map;
  let tilesLoaded=0;
  L.tileLayer(snapshot.precinctMap.basemap_url,{maxZoom:18,crossOrigin:true,attribution:escapeHTML(snapshot.precinctMap.basemap_attribution)}).on('tileload',()=>{tilesLoaded++;setStreetError(false);}).on('tileerror',()=>{if(!tilesLoaded)setStreetError(true);}).addTo(map);
  map.attributionControl.addAttribution('<a href="https://data.wake.gov/datasets/Wake::precincts">Wake County GIS</a> · <a href="https://maps.ncsu.edu/">NC State</a>');
  L.control.scale({imperial:true,metric:false,maxWidth:100}).addTo(map);
  const geo={type:'FeatureCollection',features:shapes.map(r=>({type:'Feature',properties:{area:r.area,code:r.code},geometry:r.geometry}))};
  const group=L.geoJSON(geo,{style:feature=>styleFor(feature.properties.area),onEachFeature:(feature,layer)=>{
   const area=feature.properties.area;
   layer.bindTooltip(()=>{const s=state.current,r=s.byKey.get(`${s.year}|${area}`);return tooltipNode(area,[`${s.year} · ${s.cohort==='All ages'?'All ages':`Ages ${s.cohort}`}`,`${num(r?.site_ballots)} at ${siteName(s.year)}`,`${num(r?.other_wake_ballots)} at other Wake sites`,`${pct(r?.site_share_pct)} using the named site`]);},{sticky:true,className:'voting-map-tooltip',direction:'auto',opacity:1});
   layer.on('click',()=>{selectRef.current(area);layer.closeTooltip();});
   layersRef.current.set(area,layer);
  }}).addTo(map);groupRef.current=group;
  for(const [area,layer] of layersRef.current){
   const element=layer.getElement();if(!element)continue;
   element.setAttribute('tabindex','0');element.setAttribute('role','button');element.setAttribute('aria-label',`Select ${area}`);
   element.addEventListener('focus',()=>layer.openTooltip(layer.getBounds().getCenter()));
   element.addEventListener('blur',()=>layer.closeTooltip());
   element.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();selectRef.current(area);layer.closeTooltip();}});
  }
  const labelledMarkers=[];
  for(const point of points){
   const index=point.id==='talley'?1:2;
   const label=`<div class="voting-map-pin-label" aria-hidden="true"><strong>${escapeHTML(point.name)}</strong><small>${point.id==='talley'?'Old site · 2022/2024':'New site · 2026'}</small><small>${escapeHTML(point.current_precinct_area)}</small></div>`;
   const marker=L.marker([point.latitude,point.longitude],{keyboard:true,title:point.name,icon:L.divIcon({className:`voting-map-pin voting-map-pin-${point.id}`,html:`<span>${index}</span>${label}`,iconSize:[32,32],iconAnchor:[16,16]})}).addTo(map);
   marker.bindTooltip(()=>tooltipNode(point.name,[point.address,point.current_precinct_area,point.id==='talley'?'Compared early-voting site: 2022 and 2024':'Compared early-voting site: 2026']),{className:'voting-map-tooltip',direction:'top',offset:[0,-15],opacity:1});
   marker.on('click',()=>{selectRef.current(point.current_precinct_area);marker.openTooltip();});
   const element=marker.getElement();element?.setAttribute('aria-label',`${point.name}, ${point.years.join(' and ')}, ${point.current_precinct_area}`);
   element?.addEventListener('focus',()=>marker.openTooltip());element?.addEventListener('blur',()=>marker.closeTooltip());
   labelledMarkers.push({point,marker,label:element?.querySelector('.voting-map-pin-label')});
  }
  const placeLabels=()=>{
   const size=map.getSize(),width=size.x<500?150:190;
   for(const entry of labelledMarkers){
    const label=entry.label;if(!label)continue;const p=map.latLngToContainerPoint(entry.marker.getLatLng());
    label.hidden=p.x<0||p.y<0||p.x>size.x||p.y>size.y;if(label.hidden)continue;
    label.style.width=`${width}px`;const height=label.offsetHeight;
    const desiredLeft=entry.point.id==='talley'?p.x+24:p.x-width-24;
    const left=Math.max(8,Math.min(desiredLeft,size.x-width-8));
    let top=entry.point.id==='talley'?p.y-height-16:p.y+24;
    top=Math.max(8,Math.min(top,size.y-height-8));
    label.style.left=`${left-p.x+16}px`;label.style.top=`${top-p.y+16}px`;
   }
  };
  map.on('moveend zoomend resize',placeLabels);
  map.fitBounds(points.map(p=>[p.latitude,p.longitude]),{padding:[80,80],maxZoom:15,animate:false});
  placeLabels();
  const observer=new ResizeObserver(()=>map.invalidateSize({pan:false}));observer.observe(host.current);
  return ()=>{observer.disconnect();map.remove();mapRef.current=null;groupRef.current=null;layersRef.current.clear();};
 },[shapes,points,snapshot.precinctMap]);
 useEffect(()=>{
  for(const [area,layer] of layersRef.current){layer.setStyle(styleFor(area));if(area===selected)layer.bringToFront();}
 },[year,selected,byKey]);
 const focusBoth=()=>mapRef.current?.fitBounds(points.map(p=>[p.latitude,p.longitude]),{padding:[80,80],maxZoom:15});
 const focusSelected=()=>{const layer=layersRef.current.get(selected);if(layer)mapRef.current?.fitBounds(layer.getBounds(),{padding:[35,35],maxZoom:16});};
 if(!visible('voting-precinct-map'))return null;
 return <div id="precinct-map" className="voting-map-block">
  <DataComponent id="voting-precinct-map" queryId="geography" queryIds={['geography','precinct_shapes','voting_site_points']} sourceRowsByQuery={{geography:mapEvidenceRows,precinct_shapes:shapes,voting_site_points:points}} displayRows={[...mapped.filter(r=>r.area!==selected),...selectedAgeRows]} kind="custom" title="Talley and Western Boulevard · precinct map">
   <RichNarrative id="voting-map-intro" value="Select a precinct to see where its early voters voted. Both pins stay visible as location references: Talley was the compared site in 2022/2024; Western Boulevard is the compared site in 2026."/>
   <div className="voting-controls voting-map-controls">
    <label>Map year <select value={year} onChange={e=>setYear(Number(e.target.value))}><option value={2026}>2026 · Western Boulevard · midterm</option><option value={2024}>2024 · Talley · presidential</option><option value={2022}>2022 · Talley · midterm</option></select></label>
    <label>Select precinct <select value={selected} onChange={e=>selectArea(e.target.value)}>{availableAreas.map(area=><option key={area} value={area}>{area.replace(/^PRECINCT\s+/,'')}{!shapeAreas.has(area)?' · no outline':''}</option>)}</select></label>
   </div>
   <RichNarrative id="voting-map:site-precincts" value={`The current GIS places Talley Student Union in ${points.find(p=>p.id==='talley').current_precinct_area} and Western Boulevard Business Services in ${points.find(p=>p.id==='western').current_precinct_area}. Compare both areas; people who use either site also live in other precincts.`}/>
   <p className="voting-map-boundary-note">Current Wake County GIS outlines are a reference. Historical counts follow recorded precinct codes; their earlier boundaries may differ.</p>
   <div className="voting-map-layout">
    <div className="voting-map-canvas-column">
     <div className="voting-map-toolbar"><button type="button" onClick={focusBoth}>Both voting sites</button><button type="button" onClick={focusSelected} disabled={!shapeAreas.has(selected)}>Selected precinct</button><button type="button" onClick={()=>groupRef.current&&mapRef.current?.fitBounds(groupRef.current.getBounds(),{padding:[15,15]})}>Whole Wake County</button></div>
     <div ref={host} className="voting-precinct-leaflet" aria-label="Interactive Wake precinct map around Talley and Western Boulevard"/>
     {streetError&&<p role="status" className="voting-map-boundary-note">Street tiles are unavailable. The precinct outlines, site pins and counts still work.</p>}
     <div className="voting-map-legend" aria-label="Map color legend"><span>{year} · {cohort==='All ages'?'All ages':`Ages ${cohort}`} · share using {year===2026?'Western Boulevard':'Talley'}</span><div className="voting-map-color-scale">{COLORS.map((c,i)=><span key={c}><i style={{background:c}}/>{i*20}–{(i+1)*20}%</span>)}<span><i style={{background:'#bcbcbc'}}/>N/A</span></div></div>
     <div className="voting-map-site-key">{points.map(point=><button key={point.id} type="button" onClick={()=>{selectArea(point.current_precinct_area);mapRef.current?.setView([point.latitude,point.longitude],16);}}><span className={`voting-map-key-dot voting-map-key-${point.id}`}>{point.id==='talley'?1:2}</span>{point.name} · {point.current_precinct_area.replace('PRECINCT ','')}</button>)}</div>
    </div>
    <aside className="voting-map-age-panel" aria-label="Selected precinct all age comparisons" data-reviewed-rows>
     <header><h3>{selected}</h3><p>All age groups · first 16 early-voting days. Click an age heading to shade the map for that group.</p><p className="voting-map-age-key"><i/> Named site <span/> Other Wake locations</p></header>
     {!shapeAreas.has(selected)&&<p className="voting-map-boundary-note">This recorded precinct has no matching outline in the current GIS snapshot. Its counts are retained here.</p>}
     <div className="voting-map-age-cards">
      {[...ageBands,'All ages'].map(band=><section key={band} className={`voting-map-age-card${cohort===band?' voting-map-age-card-selected':''}`} aria-label={`${band==='All ages'?'All ages combined':`Ages ${band}`} comparison`}>
       <h4><button type="button" aria-pressed={cohort===band} onClick={()=>onCohortChange?.(band)}>{band==='All ages'?'All ages combined':band==='Unknown / outside range'?'Unknown age':`Ages ${band}`}{cohort===band&&<span>Map shading</span>}</button></h4>
       {YEARS.map(y=>{const r=ageLookup.get(`${y}|${band}`);return <div className="voting-map-age-year" key={y}>
        <h5>{y} · {y===2026?'Western Boulevard':'Talley'}</h5>
        <div><strong>{num(r?.site_ballots)}</strong> at {y===2026?'Western Boulevard':'Talley'}</div><div><strong>{num(r?.other_wake_ballots)}</strong> at other Wake locations</div>
        <div className="voting-map-share-track" aria-hidden="true"><span style={{width:`${r?.site_share_pct??0}%`}}/></div>
        <div className="voting-map-age-rate">{pct(r?.site_share_pct)} used the named site</div><small>{num(r?.wake_ballots)} total early ballots</small>
       </div>;})}
      </section>)}
     </div>
     <p className="voting-map-boundary-note">Age bands do not overlap; All ages combines them. These are different yearly groups, not proof that the same people changed sites. 2024 was presidential; 2022 and 2026 are midterms.</p>
    </aside>
   </div>
   <p className="voting-map-coverage">{unmappedBallots>0?`${num(unmappedBallots)} ${year} ballots in this age group have no matching current outline (${unmapped.map(r=>r.area).join(', ')}). They remain in the tables and CSV.`:`All ${year} precinct-coded ballots in this age group have a matching outline.`}</p>
   <RichNarrative id="voting-precinct-map:math" value="Color = ballots at that year’s named site ÷ all accepted early ballots from the same precinct and age group × 100. This describes voting-location use, not turnout among residents. Drag to pan, use +/− to zoom, or select a precinct from the menu. Selecting a region also filters the charts and table below."/>
   <a href="data/processed/comparison/precinct_map_sources.json" download>Download the public map-source snapshot (.json)</a>
  </DataComponent>
  <section className="voting-map-age-section" aria-label="All age bands in the selected precinct">
   <RichNarrative id="voting-map-ages:intro" value={`## Age breakdown · ${selected}

Every age band is shown here. The chart follows the map year (${year}); the table keeps all three years visible. Counts include accepted early ballots at any Wake location during the first 16 early-voting days.`}/>
   <div className="voting-controls"><label>Age-breakdown view <select value={ageView} onChange={e=>setAgeView(e.target.value)}><option value="counts">Ballot counts</option><option value="share">Share within each age group</option></select></label></div>
   {visible('voting-precinct-age-chart')&&<EvidenceChart id="voting-precinct-age-chart" queryId="geography" title={`${year} · ${selected} · where each age group voted`} description={`All age bands · ${siteName(year)} versus other Wake locations`} rows={agePlot} sourceRows={selectedAgeRows.filter(r=>r.year===year&&r.cohort!=='All ages')} spec={{type:'horizontalStackedBar',x:'age_band',y:ageView==='counts'?'ballots':'Within-age group (%)',series:'location',colors:{[siteName(year)]:'#3182bd','Other Wake locations':'#aeb7c1'},startAtZero:true,valueDecimals:ageView==='counts'?0:1}} height={350}/>}
   <DataComponent id="voting-precinct-age-table" queryId="geography" kind="table" title={`All age groups · ${selected} · 2022, 2024 and 2026`} sourceRows={selectedAgeRows} displayRows={selectedAgeRows}>
    <div className="voting-table-scroll"><table className="voting-table voting-final-table voting-precinct-age-table"><thead><tr><th>Age group</th>{YEARS.map(y=><th key={y}>{siteName(y)}<br/>{y}<span className="voting-final-detail">Named site · other Wake locations · share</span></th>)}</tr></thead><tbody data-reviewed-rows>{ageBands.map(band=><tr key={band} className={cohort===band?'voting-selected-age-band':undefined}><th scope="row">{band}</th>{YEARS.map(y=><td key={y}>{ageTableCell(y,band)}</td>)}</tr>)}</tbody><tfoot data-reviewed-rows><tr><th scope="row">All ages</th>{YEARS.map(y=><td key={y}>{ageTableCell(y,'All ages')}</td>)}</tr></tfoot></table></div>
    <RichNarrative id="voting-map-ages:math" value="The age bands do not overlap. Unknown or outside-range ages are included when observed. In the share view, each age group’s named-site ballots and other-Wake ballots divide by that same age group’s total. N/A means the precinct/year or denominator is unavailable. Ages 18–24 are an age proxy, not confirmed NC State students."/>
   </DataComponent>
   <DataComponent id="voting-site-precinct-companion" queryId="geography" kind="table" title={`${companionArea} · ${companionArea==='PRECINCT 01-31'?'Western Boulevard area':'Talley area'} · age breakdown`} sourceRows={companionRows} displayRows={companionRows}>
    <RichNarrative id="voting-map-companion:intro" value={`${companionArea==='PRECINCT 01-31'?'Western Boulevard Business Services is in current precinct 01-31.':'Talley Student Union is in current precinct 01-23.'} This separate breakdown stays visible below ${selected}. Each row describes residents recorded in this precinct, wherever in Wake County they voted. The named site is Talley in 2022/2024 and Western Boulevard in 2026.`}/>
    <div className="voting-table-scroll"><table className="voting-table voting-final-table voting-precinct-age-table"><thead><tr><th>Age group</th>{YEARS.map(y=><th key={y}>{siteName(y)}<br/>{y}<span className="voting-final-detail">Named site · other Wake locations · share</span></th>)}</tr></thead><tbody data-reviewed-rows>{[...AGE_BANDS,...(companionRows.some(r=>r.cohort==='Unknown / outside range'&&r.wake_ballots>0)?['Unknown / outside range']:[]),'All ages'].map(band=><tr key={band}><th scope="row">{band}</th>{YEARS.map(y=>{const r=companionRows.find(v=>v.year===y&&v.cohort===band);return <td key={y}><span className="voting-final-count">{num(r?.site_ballots)} at {y===2026?'Western Boulevard':'Talley'}</span><span className="voting-final-detail">{num(r?.other_wake_ballots)} at other Wake locations</span><span className="voting-final-detail">{pct(r?.site_share_pct)} of {num(r?.wake_ballots)} used the named site</span></td>;})}</tr>)}</tbody></table></div>
    <RichNarrative id="voting-map-companion:math" value="Share = named-site ballots ÷ all accepted early ballots from the same precinct, age group and year × 100. All ages is a combined total, not another age band. Current precinct outlines may differ from earlier boundaries; these counts describe site use, not turnout among all residents."/>
   </DataComponent>
  </section>
 </div>;
}
