'use strict';
(()=>{
 const button=document.getElementById('download-article-excel'),status=document.getElementById('article-excel-status');if(!button)return;
 const savedButton=document.getElementById('download-article-excel-saved'),savedPanel=document.getElementById('article-excel-saved');
 let url;
 const run=async originals=>{
  button.disabled=true;savedButton.disabled=true;status.textContent=originals?'Checking your saved original CSVs…':'Loading source details and preparing the original CSV downloads…';
  let worker;
  const fail=(message,code)=>{status.textContent=(code==='SOURCE_SNAPSHOT_CHANGED'?'':'Download could not finish: ')+message;button.disabled=false;savedButton.disabled=false;savedPanel.open=true;worker?.terminate();};
  try{
   const get=async path=>{const r=await fetch(path);if(!r.ok)throw Error('Source details unavailable');return r.json();};
   const [figures,context]=await Promise.all([get('data/processed/comparison/figure_sources.json'),get('data/processed/comparison/comparison.json')]);
   const sources=[2022,2026].map(year=>figures.records[`summary-${year}-campus-site-all-ages`].sources[0]);
   const expected=JSON.parse(document.getElementById('reference-data').textContent).rows;
   worker=new Worker('article-excel-worker.js?v=2');
   worker.onmessage=({data})=>{
    if(data.type==='status')status.textContent=data.text;
    if(data.type==='export-error')fail(data.message,data.code);
    if(data.type==='download'){
     if(url)URL.revokeObjectURL(url);url=URL.createObjectURL(new Blob([data.bytes],{type:'application/zip'}));
     const link=document.createElement('a');link.href=url;link.download=data.filename;link.textContent='Save originals + Excel ZIP';
     status.replaceChildren(document.createTextNode('Ready. Both original file hashes and all 20 ballot counts match the article. '),link,document.createTextNode(' Extract the entire ZIP, then open Excel in 02 Working copy.'));
     button.disabled=false;savedButton.disabled=false;worker.terminate();link.click();
    }
   };worker.onerror=()=>fail('The export worker could not run.');worker.postMessage({sources,context,expected,originals});
  }catch(error){fail(error.message);}
 };
 button.addEventListener('click',()=>run());
 savedButton.addEventListener('click',()=>{
  const originals=Object.fromEntries([2022,2026].map(year=>[year,document.getElementById('article-excel-csv-'+year).files[0]]));
  if(!originals[2022]||!originals[2026]){status.textContent='Choose both saved original CSVs, one for each year.';return;}
  return run(originals);
 });
})();
