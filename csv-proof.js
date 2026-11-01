'use strict';
(()=>{
 const displayLabel=text=>{const years=[...new Set((String(text).match(/\b(?:2022|2024|2026)\b/g)||[]))];const site=years.length===1?(years[0]==='2026'?'Western Boulevard Business Services':'Talley Student Union'):'Talley Student Union → Western Boulevard Business Services';return String(text).replaceAll('Campus site',site);};
 function create(root,options={}){
 const prefix=root.dataset.proofPrefix||'', $=id=>root.querySelector('#'+prefix+id)||options.downloadRoot?.querySelector('#'+prefix+id),el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);return n;};
 const fmt=(n,unit)=>!Number.isFinite(n)?'Unavailable':unit==='ballots'?n.toLocaleString('en-US'):n.toFixed(1)+(unit==='%'?'%':' percentage points');
 let plan,record,context,worker,exportSources,exportUrl,exporting=false,counts=null,verified=false,active='original',request=0,loaded=false,pages={original:0,selected:0};
 let payload,wantedFigure=options.figure||new URLSearchParams(location.search).get('figure')||'change-2022-age-group-18-24';
 const normalColumns=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr'];
 function showMath(){
  const results=CsvProof.calculate(plan,counts),last=results.find(r=>r.id===plan.id),host=$('math');host.replaceChildren();
  $('calculation-status').textContent=!loaded?'Saved report snapshot. The live original CSVs have not been recounted yet.':verified?'Recounted from the original CSVs. All source hashes and all results match the saved report.':'Live recount. At least one source hash or result differs from the saved report. These are not verified as the report’s snapshot.';
  host.append(el('p',fmt(last.value,last.unit),{class:'result'}));
  const scroll=el('div',undefined,{class:'scroll'}),table=el('table',undefined,{class:'calcs'}),head=el('tr');
  for(const name of ['Input or step','Calculation','Saved report','Recount'])head.append(el('th',name,{scope:'col'}));const thead=el('thead');thead.append(head);table.append(thead);const body=el('tbody');
  for(const step of results.filter(s=>s.operation!=='identity')){
   const r=step.refsValues,n=n=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:6}):'unavailable';
   const formula=step.operation==='count'?'Count matching original records':step.operation==='difference'?`${n(r[1])} − ${n(r[0])}`:step.operation==='growth'?`(${n(r[1])} − ${n(r[0])}) ÷ ${n(r[0])} × 100`:`${n(r[0])} ÷ ${n(r[1])} × 100`;
   const tr=el('tr');tr.append(el('td',displayLabel(step.label)),el('td',formula,{class:'math'}),el('td',fmt(step.expected,step.unit)),el('td',loaded?fmt(step.value,step.unit)+(step.matches?' · matches':' · differs'):'Not loaded'));body.append(tr);
  }table.append(body);scroll.append(table);host.append(scroll);
 }
 function sourceInfo(){
  const source=record.sources.find(s=>s.year===Number($('year').value)),host=$('source-info');host.replaceChildren();
  host.append(el('p',source.member),el('a','Download the original NCSBE ZIP',{href:source.url,target:'_blank',rel:'noopener'}));
 }
 function chosen(){return plan.counts[Number($('selection').value)||0];}
 function filterInfo(){
  const s=chosen().selection,w=context.summary.find(r=>r.year===s.year&&r.scope===s.scope);
  $('filter').textContent=`${s.year} · ${displayLabel(`${s.scope} ${s.year}`).replace(` ${s.year}`,'')} · ${w.start_date} through ${w.end_date}, inclusive. WAKE, accepted early-voting records. `+(s.scope==='Campus site'?`Site: ${context.site_mapping[s.year]}. `:s.scope==='Other Wake sites'?`Excludes ${context.site_mapping[s.year]}. `:'All Wake sites. ')+(s.dimension?`${s.dimension}: ${s.value}.`:s.field==='all_ages'?'All ages.':s.field==='same_day_registration'?'sdr is Y or YES, all ages.':s.field==='age_18_22'?'Age 18 through 22.':'Age 18 through 24.');
 }
 function page(){
  if(!loaded||active==='calculation')return;
  const c=chosen();worker.postMessage({type:'page',year:active==='original'?Number($('year').value):c.selection.year,key:active==='original'?null:c.key,page:pages[active],id:++request});
 }
 function renderPage(data){
  if(data.id!==request)return;pages[active]=data.page;
  const host=$(active+'-grid'),selected=active==='selected';host.replaceChildren();
  const summary=el('p',`${data.count.toLocaleString()} ${selected?'matching':'original'} records. Showing ${data.rows.length?data.page*50+1:0}–${Math.min((data.page+1)*50,data.count).toLocaleString()}.`,{class:'result'});host.append(summary);
  const toolbar=el('div',undefined,{class:'toolbar'});
  for(const [label,next] of [['First',0],['Previous',data.page-1],['Next',data.page+1],['Last',Math.max(0,Math.ceil(data.count/50)-1)]]){
   const button=el('button',label,{type:'button'});button.disabled=next<0||next===data.page||next*50>=data.count;button.onclick=()=>{pages[active]=next;page();};toolbar.append(button);
  }host.append(toolbar);
  const columns=$('all-columns').checked&&!selected?data.headers:normalColumns;
  const scroll=el('div',undefined,{class:'scroll',tabindex:'0','aria-label':selected?'Records used and running count':'Original CSV records'}),table=el('table'),head=el('tr');
  for(const name of ['Original record',...columns,...(selected?['Adds to count','Running count']:[])])head.append(el('th',name,{scope:'col'}));const thead=el('thead');thead.append(head);table.append(thead);const body=el('tbody');
  for(const row of data.rows){const tr=el('tr');tr.append(el('td',row.line.toLocaleString()));for(const name of columns)tr.append(el('td',row.values[data.headers.indexOf(name)]||''));if(selected)tr.append(el('td','1',{class:'count'}),el('td',row.ordinal.toLocaleString(),{class:'count'}));body.append(tr);}table.append(body);scroll.append(table);host.append(scroll);
 }
 function switchTab(name,focus=false){
  active=name;for(const tab of ['original','selected','calculation']){$(tab).hidden=tab!==name;$('tab-'+tab).setAttribute('aria-selected',String(tab===name));$('tab-'+tab).tabIndex=tab===name?0:-1;}if(focus)$('tab-'+name).focus();page();
 }
 for(const [i,name] of ['original','selected','calculation'].entries()){
  const tab=$('tab-'+name);tab.onclick=()=>switchTab(name);tab.onkeydown=e=>{const names=['original','selected','calculation'];if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();switchTab(names[e.key==='Home'?0:e.key==='End'?2:(i+(e.key==='ArrowRight'?1:2))%3],true);}};
 }
 $('year').onchange=()=>{pages.original=0;sourceInfo();page();};$('all-columns').onchange=page;$('selection').onchange=()=>{pages.selected=0;filterInfo();page();};
 $('download-workbook').onclick=()=>{
  if(exporting)return;exporting=true;
  $('download-workbook').disabled=true;$('download-status').textContent='Downloading and checking all three original government CSVs…';
  const exporter=new Worker('csv-excel-worker.js?v=age-growth-5');
  const failed=message=>{exporting=false;$('download-status').textContent='Excel download could not finish: '+message;$('download-workbook').disabled=false;exporter.terminate();};
  exporter.onmessage=({data})=>{
   if(data.type==='status')$('download-status').textContent=data.text;
   if(data.type==='export-error')failed(data.message);
   if(data.type==='download'){exporting=false;
    if(exportUrl)URL.revokeObjectURL(exportUrl);exportUrl=URL.createObjectURL(new Blob([data.bytes],{type:'application/zip'}));
    const link=el('a','Save originals + Excel ZIP',{href:exportUrl,download:data.filename});
    $('download-status').replaceChildren(document.createTextNode('Ready. All original file hashes and all workbook counts match the report. '),link,document.createTextNode(' Extract the entire ZIP. Open Excel in 02 Working copy, then follow Original files → full Copy tabs → site steps 1–4 → county steps 5–7 → Growth proof → Individual ages.'));
    $('download-workbook').disabled=false;exporter.terminate();link.click();
   }
  };exporter.onerror=()=>failed('The export worker could not run.');exporter.postMessage({sources:exportSources,context});
 };
 $('load').onclick=()=>{
  $('load').disabled=true;$('status').textContent='Loading original source files. This can take a minute.';
  worker=new Worker('csv-proof-worker.js');worker.onmessage=({data})=>{
   if(data.type==='status')$('status').textContent=data.text;
   if(data.type==='error'){$('status').textContent='Recount could not finish: '+data.message+'. Saved results remain available in Calculation.';$('load').disabled=false;worker.terminate();}
   if(data.type==='ready'){
    counts=data.counts;loaded=true;const results=CsvProof.calculate(plan,counts);verified=Object.values(data.hashes).every(h=>h.matches)&&results.every(r=>r.matches);
    $('status').textContent=verified?'Complete: all original CSV hashes and recounted figures match the saved report.':'Recount complete with a difference. Review Calculation and Source verification.';
    $('status').className=verified?'':'warning';$('load').textContent='Original CSVs loaded';
    $('hashes').replaceChildren();for(const [year,h]of Object.entries(data.hashes)){$('hashes').append(el('h3',year+(h.matches?' · exact snapshot match':' · source differs')),el('p','Saved SHA-256: '+h.expected),el('p','Loaded SHA-256: '+h.actual));}
    showMath();page();
   }if(data.type==='page')renderPage(data);
  };worker.onerror=()=>{$('status').textContent='The original-file worker could not run. Saved calculations and downloads remain available.';$('load').disabled=false;worker.terminate();};
  worker.postMessage({type:'load',sources:record.sources,counts:plan.counts,context});
 };
 function renderFigure(id){
  record=payload.records[id];if(!record)throw Error('Choose a figure from the report');
  if(worker){worker.terminate();worker=null;}counts=null;loaded=false;verified=false;pages={original:0,selected:0};request++;
  plan=CsvProof.buildPlan(payload.records,id);$('year').replaceChildren();$('selection').replaceChildren();
  exportSources=[2022,2024,2026].map(year=>payload.records[`summary-${year}-campus-site-all-ages`].sources[0]);
  $('download-workbook').disabled=exporting;$('title').textContent=displayLabel(record.label);if($('evidence'))$('evidence').href='figure-source.html#'+encodeURIComponent(id);
  for(const source of record.sources)$('year').append(el('option',String(source.year),{value:source.year}));
  plan.counts.forEach((c,i)=>$('selection').append(el('option',`${displayLabel(c.label)} · saved count ${c.expected.toLocaleString()}`,{value:i})));
  sourceInfo();filterInfo();showMath();$('status').textContent='Saved calculation ready. Load the originals to verify every count.';$('status').className='';$('load').disabled=false;$('load').textContent='Load official CSVs and recount';
  $('hashes').textContent='Load the original CSVs to compare their SHA-256 hashes with the saved report snapshot.';
  for(const id of ['original-grid','selected-grid'])$(id).replaceChildren(el('p','Load the official CSVs to see the original rows and running counts.',{class:'muted'}));
  const initialTab=options.initialTab||new URLSearchParams(location.search).get('tab');switchTab(['original','selected','calculation'].includes(initialTab)?initialTab:'original');
 }
 const ready=Promise.all([fetch('data/processed/comparison/figure_sources.json').then(r=>{if(!r.ok)throw Error('Figure data unavailable');return r.json();}),fetch('data/processed/comparison/comparison.json').then(r=>{if(!r.ok)throw Error('Comparison unavailable');return r.json();})]).then(([figures,data])=>{payload=figures;context=data;renderFigure(wantedFigure);}).catch(error=>{$('status').textContent=error.message;});
 return {ready,setFigure(id){wantedFigure=id;if(payload)renderFigure(id);}};
 }
 window.CsvProofView={create};
 const standalone=document.querySelector('main[data-csv-proof]');if(standalone)create(standalone);
})();
