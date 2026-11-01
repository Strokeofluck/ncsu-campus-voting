/* The download is generated on the reader's computer from official files. */
importScripts('csv-viewer-worker.js','vendor/pako.min.js','vendor/jszip.min.js','csv-zip-stream.js','article-excel-plan.js?v=1','article-excel-export.js?v=1');
onmessage=async({data})=>{
 try{
  const response=await fetch('article-excel-template.json?v=1');if(!response.ok)throw Error('Excel template unavailable');
  const t=await response.json(),bytes=Uint8Array.from(atob(t.base64),c=>c.charCodeAt(0));
  const result=await ArticleExcelExport.build(bytes,data.sources,data.context,data.expected,wakeBytes,say,JSZip,CsvZipStream,pako);
  postMessage({type:'download',bytes:result.bytes.buffer,filename:'talley-western-originals-and-excel.zip'},[result.bytes.buffer]);
 }catch(error){postMessage({type:'export-error',message:error.message||String(error)});}
};
