/* Builds the requested download in the viewer's browser; no voter data is uploaded. */
importScripts('csv-viewer-worker.js','vendor/jszip.min.js','csv-excel-export.js');
onmessage=async({data})=>{
 try{
  const response=await fetch('csv-excel-template.json');if(!response.ok)throw Error('Excel template unavailable');
  const template=await response.json(),templateBytes=Uint8Array.from(atob(template.base64),c=>c.charCodeAt(0));
  const bundle=new JSZip(),datasets=[],manifest=[];
  for(const source of data.sources){
   say('Downloading original '+source.year+' Wake CSV…');
   const bytes=await wakeBytes(source),digest=await crypto.subtle.digest('SHA-256',bytes);
   const hash=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
   if(hash!==source.wake_csv_sha256)throw Error('The original '+source.year+' CSV has changed since this report. Refresh the report snapshot before exporting a verified workbook.');
   csv=new TextDecoder('windows-1252').decode(bytes);bounds=indexRecords(csv);headers=cells(rowAt(0));total=bounds.length/2-1;
   const siteColumn=headers.indexOf('site_name'),columns=CsvExcel.fields.map(f=>headers.indexOf(f));
   if(siteColumn<0||columns.some(i=>i<0))throw Error('The official CSV columns changed');
   say('Copying '+source.year+' campus source rows with original record numbers…');
   const rows=[];
   for(let i=1;i<=total;i++){
    const values=cells(rowAt(i));if(values.length!==headers.length)throw Error('CSV column count changed');
    if(values[siteColumn].trim()===data.context.site_mapping[source.year])rows.push([source.year,i+1,...columns.map(c=>values[c])]);
   }
   datasets.push({source,total,rows});manifest.push({...source,original_records:total,campus_source_records:rows.length});
   bundle.file('originals/'+source.member,bytes,{compression:'DEFLATE',compressionOptions:{level:3}});
   csv='';bounds=null;
  }
  say('Building Excel tabs with actual filter, count and percentage formulas…');
  const result=await CsvExcel.workbook(templateBytes,datasets,data.context,JSZip);
  bundle.file('campus-voting-step-by-step.xlsx',result.bytes,{compression:'STORE'});
  bundle.file('source-manifest.json',JSON.stringify({sources:manifest,matched_days:data.context.matched_days,as_of:data.context.as_of},null,2));
  bundle.file('READ FIRST.txt','Extract the entire ZIP before opening the Excel workbook.\r\n\r\noriginals/ contains the complete, unchanged Wake County CSV members from the official NCSBE archives. Their SHA-256 hashes match this report snapshot.\r\n\r\nWorkbook tabs, in order:\r\n0 Original files: original file links, source URLs, hashes and dates.\r\n1 Source rows: individual campus-site records before date/status filtering. Seven source columns retain their original values; added year and CSV record numbers identify each original record. Full county records and all original columns remain in the original CSVs.\r\n2 Filter flags: actual Excel formulas mark accepted early-voting records in the matched window. Green includes a ballot; amber identifies ages 18-24. Running counts reset by year.\r\n3 Counts: COUNTIFS counts included records by year and age group.\r\n4 Math: linked counts, shares, growth and percentage-point changes. These are real Excel formulas, not formula text.\r\n\r\nOriginal CSV fields are not edited. Numeric age, dates and filter flags are added in tab 2. Editing a copied value in tab 1 recalculates the later tabs without changing the original CSVs. 2026 is preliminary.\r\n');
  let progress=-1;
  const bytes=await bundle.generateAsync({type:'uint8array',compression:'DEFLATE',compressionOptions:{level:3}},meta=>{const current=Math.floor(meta.percent/10)*10;if(current!==progress){progress=current;say('Packing original CSVs and Excel workbook… '+current+'%');}});
  postMessage({type:'download',bytes:bytes.buffer,filename:'ncsu-voting-originals-and-excel.zip',counts:result.counts},[bytes.buffer]);
 }catch(error){postMessage({type:'export-error',message:error.message||String(error)});}
};
