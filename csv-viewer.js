/* Original NCSBE CSV viewer. Voter records are fetched directly into this browser. */
(()=>{
 'use strict';
 const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),year=Number(params.get('year')),figure=params.get('figure');
 let worker,source,context,selection=[],page=0,pageCount=0,current,requestId=0;
 const status=text=>{$('status').textContent=text;};
 function renderPage(data){
  current=data;pageCount=Math.ceil(data.count/50);page=data.page;
  $('summary').textContent=`${data.count.toLocaleString()} ${$('scope').value==='all'?'original records':'matching original records'} · ${data.total.toLocaleString()} records in the full CSV · ${data.headers.length} original columns. Showing ${data.rows.length?data.page*50+1:0}–${Math.min((data.page+1)*50,data.count)}.`;
  const wanted=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr'];
  const cols=data.headers.map((name,index)=>({name,index})).filter(c=>$('all-columns').checked||wanted.includes(c.name));
  const table=$('csv-table');table.replaceChildren();const head=document.createElement('thead'),hr=document.createElement('tr');
  for(const name of ['CSV row',...cols.map(c=>c.name)]){const th=document.createElement('th');th.scope='col';th.textContent=name;hr.append(th);}head.append(hr);table.append(head);const body=document.createElement('tbody');
  for(const row of data.rows){const tr=document.createElement('tr'),th=document.createElement('th');th.scope='row';th.textContent=row.line.toLocaleString();tr.append(th);for(const c of cols){const td=document.createElement('td');td.textContent=row.values[c.index];tr.append(td);}body.append(tr);}table.append(body);
  $('previous').disabled=page===0;$('next').disabled=page+1>=pageCount;$('page').value=page+1;$('page').max=Math.max(1,pageCount);$('pages').textContent=`of ${Math.max(1,pageCount).toLocaleString()}`;
  // Raw text is kept off the DOM until explicitly expanded.
  $('raw').textContent=$('raw-details').open?data.raw:'';status('Original CSV loaded. No records are uploaded or saved by this viewer.');
 }
 function getPage(nextPage=0){if(worker)worker.postMessage({type:'page',page:Math.max(0,nextPage),scope:$('scope').value,id:++requestId});}
 $('load').addEventListener('click',()=>{
  $('load').disabled=true;status('Connecting to the original NCSBE ZIP…');
  if(worker)worker.terminate();worker=new Worker('csv-viewer-worker.js');
  worker.onmessage=({data})=>{
   if(data.type==='status')status(data.text);
   else if(data.type==='ready'){
    $('loaded').hidden=false;$('load').hidden=true;
    const match=data.hash===source.wake_csv_sha256;
    $('verification').className=match?'verified':'changed';
    $('verification').textContent=match?'Verified: the original CSV bytes exactly match the snapshot used in this report.':'The live CSV has changed since this report’s snapshot. These are the current original rows; they may not reproduce the report’s figures.';
    $('hash').textContent=`Current Wake CSV SHA-256: ${data.hash}. Report snapshot SHA-256: ${source.wake_csv_sha256}. This verifies the CSV member; the entire ZIP was not downloaded or hashed.`;
    getPage();
   }else if(data.type==='page'&&data.id===requestId)renderPage(data);
   else if(data.type==='error'){status('CSV preview could not load: '+data.message+' You can still open the official source page or original ZIP above.');$('load').disabled=false;$('load').textContent='Retry loading the original CSV';}
  };
  worker.onerror=()=>{status('The CSV reader stopped. Try again or use the original source links above.');$('load').disabled=false;};
  worker.postMessage({type:'load',source,context,selections:selection});
 });
 $('scope').addEventListener('change',()=>getPage());$('all-columns').addEventListener('change',()=>{if(current)renderPage(current);});
 $('previous').addEventListener('click',()=>getPage(page-1));$('next').addEventListener('click',()=>getPage(page+1));
 $('page').addEventListener('change',()=>getPage(Math.min(Math.max(0,Number($('page').value)-1),Math.max(0,pageCount-1))));
 $('raw-details').addEventListener('toggle',()=>{$('raw').textContent=$('raw-details').open&&current?current.raw:'';});
 (async()=>{
  try{
   if(![2022,2024,2026].includes(year))throw Error('Choose a supported election year');
   const results=await Promise.all(['figure_sources.json','comparison.json'].map(name=>fetch('data/processed/comparison/'+name).then(r=>{if(!r.ok)throw Error('Source metadata unavailable');return r.json();})));
   const record=results[0].records[figure]||Object.values(results[0].records).find(r=>r.sources.some(s=>s.year===year));
   source=record.sources.find(s=>s.year===year);if(!source)throw Error('Source year does not match this figure');
   const url=new URL(source.url);if(url.origin!=='https://s3.amazonaws.com'||!url.pathname.startsWith('/dl.ncsbe.gov/ENRS/'))throw Error('Unexpected original source');
   selection=record.selections.filter(s=>s.year===year);context=results[1];
   $('title').textContent=`${year} · ${source.member}`;
   $('source-page').href=source.listing_url;$('source-page').textContent='Official source page: '+source.listing_url;
   $('source-file').href=source.url;$('source-file').textContent='Original ZIP file: '+source.url;
   if(!selection.length){$('scope').value='all';$('scope').querySelector('[value="figure"]').disabled=true;}
   $('load').disabled=false;status('Ready. Loading reads only the Wake County portion of the ZIP, then checks its SHA-256. Large CSVs may take a moment.');
  }catch(error){status(error.message);}
 })();
})();
