/* Build the complete download locally in the viewer's browser; no voter data is uploaded. */
importScripts('csv-viewer-worker.js','vendor/pako.min.js','vendor/jszip.min.js','csv-zip-stream.js','csv-original-copy.js?v=age-growth-5','csv-county-excel.js?v=age-growth-5','csv-excel-export.js?v=age-growth-5','csv-excel-package.js?v=age-growth-5');
onmessage=async({data})=>{
 try{
  const response=await fetch('csv-excel-template.json?v=age-growth-5');if(!response.ok)throw Error('Excel template unavailable');
  const template=await response.json(),templateBytes=Uint8Array.from(atob(template.base64),c=>c.charCodeAt(0)),templateZip=await JSZip.loadAsync(templateBytes);
  if(!template.fullCopies||!template.countyGrowth)throw Error('Reload the page to get the complete-copy Excel template');
  const bundle=new CsvZipStream.Archive(),datasets=[];
  for(const source of data.sources){
   say('Downloading untouched '+source.year+' Wake CSV…');
   const bytes=await wakeBytes(source),digest=await crypto.subtle.digest('SHA-256',bytes),hash=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
   if(hash!==source.wake_csv_sha256)throw Error('The original '+source.year+' CSV has changed since this report. Refresh the report snapshot before exporting a verified workbook.');
   say('Preserving the untouched '+source.year+' original in its own folder…');
   const original=CsvZipStream.packed(CsvExcelPackage.originalPath(source),pako);original.push(bytes);bundle.add(original.finish());
   const sheet={2022:2,2024:3,2026:4}[source.year],xml=await templateZip.file(`xl/worksheets/sheet${sheet}.xml`).async('string');
   datasets.push(CsvOriginalCopy.copy(bytes,source,data.context,xml,CsvZipStream,pako,CsvExcel.fields,say));
  }
  say('Linking full copies, site and county extracts, 1-or-0 flags, sums and growth formulas…');
  const result=await CsvExcel.workbook(templateBytes,datasets,data.context,JSZip,{Stream:CsvZipStream,Pako:pako});
  say('Packing the untouched originals and complete Excel working copy…');
  const bytes=CsvExcelPackage.finish(bundle,result,datasets,data.context,CsvZipStream,pako);
  postMessage({type:'download',bytes:bytes.buffer,filename:'ncsu-voting-originals-and-excel.zip',counts:result.counts},[bytes.buffer]);
 }catch(error){postMessage({type:'export-error',message:error.message||String(error)});}
};
