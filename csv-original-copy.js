/* Preserve all CSV fields in original order; prepare only a separate campus extract. */
(function(root){
 'use strict';
 function cells(line){const result=[];let value='',quoted=false;for(let i=0;i<line.length;i++){const c=line[i];if(quoted){if(c==='"'){if(line[i+1]==='"'){value+='"';i++;}else quoted=false;}else value+=c;}else if(c===','){result.push(value);value='';}else if(c==='"'&&value==='')quoted=true;else value+=c;}result.push(value);return result;}
 function indexRecords(text){const out=[];let quoted=false,start=0,fieldStart=true;for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'){if(text[i+1]==='"')i++;else quoted=false;}}else if(c==='"'&&fieldStart){quoted=true;fieldStart=false;}else if(c===',')fieldStart=true;else if(c==='\n'){let end=i;if(text[end-1]==='\r')end--;if(end>start)out.push(start,end);start=i+1;fieldStart=true;}else fieldStart=false;}if(start<text.length)out.push(start,text.length);if(quoted)throw Error('Unclosed quoted CSV field');return new Uint32Array(out);}
 function copy(bytes,source,context,template,Stream,Pako,fields,progress){
  const text=new TextDecoder('windows-1252').decode(bytes),bounds=indexRecords(text),at=i=>text.slice(bounds[i*2],bounds[i*2+1]),headers=cells(at(0)),total=bounds.length/2-1;
  const siteColumn=headers.indexOf('site_name'),columns=fields.map(f=>headers.indexOf(f));
  if(siteColumn<0||columns.some(i=>i<0))throw Error('The official CSV columns changed');
  const writer=Stream.worksheet(`xl/worksheets/sheet${{2022:2,2024:3,2026:4}[source.year]}.xml`,template,total,headers.length,Pako),rows=[];
  writer.row(headers);
  for(let i=1;i<=total;i++){
   const values=cells(at(i));if(values.length!==headers.length)throw Error('CSV column count changed at record '+(i+1));
   writer.row(values);
   if(values[siteColumn].trim()===context.site_mapping[source.year])rows.push([source.year,i+1,...columns.map(c=>values[c])]);
   if(i%20000===0)progress(`Copying every ${source.year} CSV row and column into Excel… ${i.toLocaleString()} / ${total.toLocaleString()} records`);
  }
  return {source,total,rows,headers,rawEntry:writer.finish()};
 }
 root.CsvOriginalCopy={cells,indexRecords,copy};if(typeof module!=='undefined')module.exports=root.CsvOriginalCopy;
})(globalThis);
