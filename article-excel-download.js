'use strict';
(()=>{
 const button=document.getElementById('download-article-excel'),status=document.getElementById('article-excel-status');if(!button)return;
 const savedButton=document.getElementById('download-article-excel-saved'),savedPanel=document.getElementById('article-excel-saved');
 const results=document.getElementById('article-excel-results');
 const showResults=data=>{
  if(!results)return;
  results.replaceChildren();if(data.mode!=='updated')return;
  const heading=document.createElement('h4');heading.textContent='Updated-file calculations';results.append(heading);
  const note=document.createElement('p');note.textContent='Calculated '+new Date(data.generatedAt).toLocaleString()+'. Same first 16 early-voting days; these are separate from the article snapshot above. Displays round to four decimal places; calculations use unrounded values.';results.append(note);
  const number=n=>n.toLocaleString(undefined,{maximumFractionDigits:4});
  for(const row of data.results){
   const detail=document.createElement('details'),label=document.createElement('summary'),steps=document.createElement('ol');
   label.textContent='Ages '+row.cohort+' — counts and step-by-step math';detail.append(label,steps);
   const a=row.site_ballots_2022,z=row.site_ballots_2026,c=row.county_ballots_2022,d=row.county_ballots_2026;
   for(const text of [`Talley 2022: ${number(a)}; Western 2026: ${number(z)}. All Wake 2022: ${number(c)}; all Wake 2026: ${number(d)}.`,`Site growth: (${number(z)} − ${number(a)}) ÷ ${number(a)} × 100 ≈ ${number(row.site_growth_pct)}%.`,`Wake growth: (${number(d)} − ${number(c)}) ÷ ${number(c)} × 100 ≈ ${number(row.county_growth_pct)}%.`,`Gap: ${number(row.site_growth_pct)}% − ${number(row.county_growth_pct)}% ≈ ${number(row.site_growth_gap_pp)} percentage points.`]){const item=document.createElement('li');item.textContent=text;steps.append(item);}
   results.append(detail);
  }
 };
 let url;
 const run=async(originals,mode='updated')=>{
  button.disabled=true;savedButton.disabled=true;status.textContent=originals?'Reading your chosen CSVs…':'Fetching the latest official files and preparing fresh calculations…';
  results?.replaceChildren();
  let worker;
  const fail=(message,code)=>{status.textContent=(code==='SOURCE_SNAPSHOT_CHANGED'?'':'Download could not finish: ')+message;button.disabled=false;savedButton.disabled=false;savedPanel.open=true;worker?.terminate();};
  try{
   const get=async path=>{const r=await fetch(path);if(!r.ok)throw Error('Source details unavailable');return r.json();};
   const [figures,context]=await Promise.all([get('data/processed/comparison/figure_sources.json'),get('data/processed/comparison/comparison.json')]);
   const sources=[2022,2026].map(year=>figures.records[`summary-${year}-campus-site-all-ages`].sources[0]);
   const expected=JSON.parse(document.getElementById('reference-data').textContent).rows;
   worker=new Worker('article-excel-worker.js?v=3');
   worker.onmessage=({data})=>{
    if(data.type==='status')status.textContent=data.text;
    if(data.type==='export-error')fail(data.message,data.code);
    if(data.type==='download'){
     if(url)URL.revokeObjectURL(url);url=URL.createObjectURL(new Blob([data.bytes],{type:'application/zip'}));
     const link=document.createElement('a');link.href=url;link.download=data.filename;link.textContent='Save originals + Excel ZIP';
     const message=data.mode==='updated'?'Ready. Recalculated from the updated files using the same first 16 days. These results may differ from the saved article. ':'Ready. Both original file hashes and all 20 ballot counts match the article. ';
     status.replaceChildren(document.createTextNode(message),link,document.createTextNode(' Extract the entire ZIP, then open Excel in 02 Working copy.'));
     showResults(data);
     button.disabled=false;savedButton.disabled=false;worker.terminate();link.click();
    }
   };worker.onerror=()=>fail('The export worker could not run.');worker.postMessage({sources,context,expected,originals,mode});
  }catch(error){fail(error.message);}
 };
 button.addEventListener('click',()=>run());
 savedButton.addEventListener('click',()=>{
  const originals=Object.fromEntries([2022,2026].map(year=>[year,document.getElementById('article-excel-csv-'+year).files[0]]));
  if(!originals[2022]||!originals[2026]){status.textContent='Choose both Wake County CSVs, one for each year. Download links and extraction steps are above the file selectors.';return;}
  return run(originals,document.getElementById('article-excel-mode').value);
 });
})();
