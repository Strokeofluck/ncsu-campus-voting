import React,{useEffect,useRef} from 'react';
import * as L from './vendor/leaflet/leaflet-src.esm.js';
import './vendor/leaflet/leaflet.css';
import {DataComponent,RichNarrative,useDataApp} from '../../data-app-public.jsx';

const AGES=['18–24','25–34','35–44','45–64','65+'];
const COLORS={talley:'#b65b32',western:'#2176a5'};
const n=v=>v.toLocaleString('en-US');
const pct=v=>`${v>0?'+':''}${v.toFixed(1)}%`;
// A shared area scale across all five maps: area, not radius, encodes ballots.
const radius=(count,maximum)=>40*Math.sqrt(count/maximum);
function SiteMap({index,row,sites,shapes,basemap,maximum,onReady,prototype=false}){
 const {visible}=useDataApp(),host=useRef(null),id=`${prototype?'voting-site-circle':'voting-campus-age'}-${index}`;
 useEffect(()=>{
  if(!host.current)return;
  const map=L.map(host.current,{attributionControl:false,scrollWheelZoom:false,minZoom:8,maxZoom:18,zoomSnap:0.25,center:[35.784,-78.678],zoom:14});
  L.tileLayer(basemap.basemap_url,{maxZoom:18,crossOrigin:true,attribution:basemap.basemap_attribution}).addTo(map);
  const outlines=L.geoJSON({type:'FeatureCollection',features:shapes.map(r=>({type:'Feature',geometry:r.geometry,properties:{area:r.area}}))},{interactive:false,style:f=>({color:'#68757f',weight:['PRECINCT 01-23','PRECINCT 01-31'].includes(f.properties.area)?1.6:.6,opacity:.65,fill:false})}).addTo(map);
  const bounds=L.latLngBounds(sites.map(s=>[s.latitude,s.longitude]));
  for(const site of sites){
   const year=site.id==='talley'?2022:2026,count=row[`site_ballots_${year}`],r=radius(count,maximum),name=site.id==='talley'?'Talley':'Western Blvd';
   const marker=L.circleMarker([site.latitude,site.longitude],{radius:r,color:COLORS[site.id],weight:2,fillColor:COLORS[site.id],fillOpacity:.75}).addTo(map);
   const content=document.createElement('div');content.className='voting-map-tooltip-content';
   for(const text of [site.name,`${year} · Ages ${row.cohort}`,`${n(count)} accepted early ballots cast here`,year===2022?'October 20–November 5, 2022':'October 15–31, 2026 · preliminary','Full 17-day early-voting periods; voters from any home precinct in Wake.']){const line=document.createElement('div');line.textContent=text;content.append(line);}
   marker.bindTooltip(content,{className:'voting-map-tooltip',opacity:1,direction:'center'});
   marker.on('tooltipopen',()=>{const tooltip=marker.getTooltip(),node=tooltip.getElement();node.style.maxWidth=`${Math.min(280,map.getSize().x-24)}px`;node.style.minWidth='0';tooltip.options.offset=L.point(map.getSize().x/2-map.latLngToContainerPoint(marker.getLatLng()).x,0);tooltip.update();});
   const el=marker.getElement();el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',`${site.name}, ${year}, ages ${row.cohort}: ${n(count)} ballots`);el.setAttribute('data-ballots',count);el.setAttribute('data-year',year);el.setAttribute('data-radius',r);
   el.addEventListener('focus',()=>marker.openTooltip());el.addEventListener('blur',()=>marker.closeTooltip());el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();marker.toggleTooltip();}});
   L.marker([site.latitude,site.longitude],{interactive:false,keyboard:false,icon:L.divIcon({className:`voting-site-map-label voting-site-map-label-${site.id}`,html:`<span>${name} · ${year}</span><strong>${n(count)} ballots</strong>`,iconSize:[130,46],iconAnchor:[site.id==='western'?55:75,site.id==='western'?r+50:-r-5]})}).addTo(map);
  }
  const reset=()=>map.fitBounds(bounds,{paddingTopLeft:[65,100],paddingBottomRight:[65,100],maxZoom:14.5,animate:false});
  reset();onReady(index,{reset,county:()=>map.fitBounds(outlines.getBounds(),{padding:[10,10],animate:false})});
  const observer=new ResizeObserver(()=>{map.invalidateSize({pan:false});reset();});observer.observe(host.current);
  return()=>{observer.disconnect();map.remove();onReady(index,null);};
 },[row,sites,shapes,basemap,maximum]);
 if(!visible(id))return null;
 return <DataComponent id={id} queryId="age_growth_benchmarks" queryIds={['age_growth_benchmarks','voting_site_points','precinct_shapes']} sourceRowsByQuery={{age_growth_benchmarks:[row],voting_site_points:sites,precinct_shapes:shapes}} displayRows={[row]} kind="custom" title={`Ages ${row.cohort} · 2022 to 2026`}>
  <div className="voting-article-map-body">
   <p className="voting-region-map-unit">Ballots cast at Talley → Western Boulevard</p>
   <div className="voting-site-map-frame"><div ref={host} className="voting-region-age-map" aria-label={`Ages ${row.cohort}: ballots cast at Talley in 2022 and Western Boulevard in 2026`}/><div className="voting-site-map-attribution"><a href="https://leafletjs.com/">Leaflet</a> | <span dangerouslySetInnerHTML={{__html:basemap.basemap_attribution}}/> · <a href="https://data.wake.gov/datasets/Wake::precincts">Wake County GIS</a></div></div>
   <div className="voting-campus-site-benchmark voting-article-number-panel" data-reviewed-rows>
    <strong className="voting-article-number-heading">Early-ballot growth · 2022–2026</strong>
    <dl className="voting-article-growth-pair"><div><dt>Talley → Western Boulevard</dt><dd>{pct(row.site_growth_pct)}</dd></div><div><dt>Wake County</dt><dd>{pct(row.county_growth_pct)}</dd></div></dl>
    <p className="voting-article-growth-gap"><strong>{Math.abs(row.site_growth_gap_pp).toFixed(1)}</strong><span>percentage points {row.site_growth_gap_pp<0?'behind':'ahead of'} Wake</span></p>
    <p className="voting-article-count-line"><span>Talley 2022 → Western 2026</span><span>{n(row.site_ballots_2022)} → {n(row.site_ballots_2026)} ballots</span></p>
    <a href={`${prototype?'':'../'}references.html?age=${encodeURIComponent(row.cohort)}#math`}>Counts and math →</a>
   </div>
  </div>
 </DataComponent>;
}
export function SiteAgeMaps({afterYoungest=null,beforeOtherAges=null,prototype=false}){
 const {snapshot}=useDataApp(),rows=snapshot.queries.age_growth_benchmarks.rows,sites=snapshot.queries.voting_site_points.rows,shapes=snapshot.queries.precinct_shapes.rows,maps=useRef([]);
 const maximum=Math.max(...rows.flatMap(r=>[r.site_ballots_2022,r.site_ballots_2026]));
 const panels=AGES.map((age,i)=><SiteMap key={age} prototype={prototype} index={i} row={rows.find(r=>r.cohort===age)} sites={sites} shapes={shapes} basemap={snapshot.precinctMap} maximum={maximum} onReady={(index,map)=>{maps.current[index]=map;}}/>);
 return <section id={prototype?"site-circle-age-growth":"campus-age-growth"} className="voting-region-comparison">
  <RichNarrative id={prototype?"voting-site-circle:scope":"voting-campus-age:article-scope"} value="**Circles show how many early ballots were cast at Talley in 2022 and Western Boulevard in 2026.** Bigger circles mean more ballots, using the same size scale across all five age groups. Counts include voters from any home precinct in Wake. Precinct outlines provide geographic context only."/>
  <div className="voting-map-toolbar"><button onClick={()=>maps.current.forEach(m=>m?.reset())}>Reset maps to voting sites</button><button onClick={()=>maps.current.forEach(m=>m?.county())}>Show all Wake County in every age map</button></div>
  <div className="voting-site-map-legend"><div><span><i style={{background:COLORS.talley}}/>Talley · 2022</span><span><i style={{background:COLORS.western}}/>Western Boulevard · 2026</span></div><span>Circle area = ballots cast · same scale in every map</span><svg viewBox="0 0 270 100" role="img" aria-label="Circle size key: 1,000, 2,000 and 4,000 ballots">{[1000,2000,4000].map((count,i)=><g key={count}><circle cx={45+i*90} cy={41} r={radius(count,maximum)} fill="none" stroke="currentColor"/><text x={45+i*90} y="97" textAnchor="middle" fill="currentColor">{n(count)}</text></g>)}</svg></div>
  <div className="voting-campus-age-grid voting-article-map-layout"><div className="voting-article-featured-map">{panels[0]}</div>{afterYoungest}{beforeOtherAges}<div className="voting-article-comparison-layout"><div className="voting-article-middle-maps">{panels.slice(1,4)}</div><div className="voting-article-senior-map">{panels[4]}</div></div></div>
  <RichNarrative id={prototype?"voting-site-circle:limits":"voting-campus-age:limits"} value={`Matched full 17-day early-voting periods in both years; 2026 is preliminary through October 31. These are early-ballot counts, not turnout rates. Age does not verify student enrollment. The comparison does not establish the effect of moving the site. [Home-precinct maps remain in the prototype](${prototype?'':'../index.html?view=1'}#campus-age-growth). [Download the age-specific site and county counts](${prototype?'':'../'}data/processed/comparison/age_growth_benchmarks.csv).`}/>
 </section>;
}
