/* Deflate entries incrementally so full government worksheets do not become one giant XML string. */
(function(root){
 'use strict';
 const encoder=new TextEncoder(),table=new Uint32Array(256);
 for(let i=0;i<256;i++){let n=i;for(let k=0;k<8;k++)n=(n&1)?0xedb88320^(n>>>1):n>>>1;table[i]=n>>>0;}
 function crc(previous,bytes){let n=previous;for(let i=0;i<bytes.length;i++)n=table[(n^bytes[i])&255]^(n>>>8);return n>>>0;}
 function packed(name,Pako){
  const chunks=[],deflater=new Pako.Deflate({raw:true,level:1,chunkSize:65536});let checksum=0xffffffff,size=0;
  deflater.onData=chunk=>chunks.push(chunk);deflater.onEnd=status=>{if(status!==0)throw Error('Could not compress '+name);};
  return {push(value){const bytes=typeof value==='string'?encoder.encode(value):value;size+=bytes.length;if(size>=0xffffffff)throw Error('Worksheet exceeds the supported ZIP entry size');checksum=crc(checksum,bytes);if(!deflater.push(bytes,false))throw Error(deflater.msg||'Compression failed');},finish(){deflater.push(new Uint8Array(0),true);if(deflater.err)throw Error(deflater.msg);return {name,method:8,crc:(checksum^0xffffffff)>>>0,size,chunks,compressed:chunks.reduce((n,b)=>n+b.length,0)};}};
 }
 class Archive{
  constructor(){this.entries=[];}
  add(entry){if(this.entries.some(e=>e.name===entry.name))throw Error('Duplicate ZIP entry');this.entries.push(entry);}
  store(name,bytes){this.add({name,method:0,crc:(crc(0xffffffff,bytes)^0xffffffff)>>>0,size:bytes.length,compressed:bytes.length,chunks:[bytes]});}
  text(name,value,Pako){const entry=packed(name,Pako);entry.push(value);this.add(entry.finish());}
  finish(){
   const pieces=[],directory=[];let offset=0;
   for(const entry of this.entries){
    const name=encoder.encode(entry.name),local=new Uint8Array(30+name.length),l=new DataView(local.buffer),central=new Uint8Array(46+name.length),c=new DataView(central.buffer);
    l.setUint32(0,0x04034b50,true);l.setUint16(4,20,true);l.setUint16(6,0x800,true);l.setUint16(8,entry.method,true);l.setUint16(12,0x21,true);l.setUint32(14,entry.crc,true);l.setUint32(18,entry.compressed,true);l.setUint32(22,entry.size,true);l.setUint16(26,name.length,true);local.set(name,30);
    c.setUint32(0,0x02014b50,true);c.setUint16(4,20,true);c.setUint16(6,20,true);c.setUint16(8,0x800,true);c.setUint16(10,entry.method,true);c.setUint16(14,0x21,true);c.setUint32(16,entry.crc,true);c.setUint32(20,entry.compressed,true);c.setUint32(24,entry.size,true);c.setUint16(28,name.length,true);c.setUint32(42,offset,true);central.set(name,46);
    pieces.push(local,...entry.chunks);directory.push(central);offset+=local.length+entry.compressed;
   }
   const directorySize=directory.reduce((n,b)=>n+b.length,0),end=new Uint8Array(22),e=new DataView(end.buffer),length=offset+directorySize+22;
   if(length>=0xffffffff||this.entries.length>65535)throw Error('Download exceeds the supported ZIP size');
   e.setUint32(0,0x06054b50,true);e.setUint16(8,this.entries.length,true);e.setUint16(10,this.entries.length,true);e.setUint32(12,directorySize,true);e.setUint32(16,offset,true);
   const bytes=new Uint8Array(length);let position=0;for(const piece of [...pieces,...directory,end]){bytes.set(piece,position);position+=piece.length;}return bytes;
  }
 }
 const col=index=>{let value='';for(let n=index+1;n;n=Math.floor((n-1)/26))value=String.fromCharCode(65+(n-1)%26)+value;return value;};
 const cellText=value=>String(value).replace(/_x[0-9a-f]{4}_/gi,s=>'_x005F_'+s.slice(1)).replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]/g,c=>'_x'+c.charCodeAt(0).toString(16).padStart(4,'0').toUpperCase()+'_').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\r','&#13;');
 function worksheet(name,template,total,columns,Pako){
  const p=(template.match(/<([\w]+:)?worksheet\b/)||[])[1]||'',opening=new RegExp(`<${p}sheetData[^>]*>`),match=opening.exec(template);
  const before=template.slice(0,match.index+match[0].length).replace(new RegExp(`<${p}dimension\\b[^>]*/>`),`<${p}dimension ref="A1:${col(columns-1)}${total+1}"/>`);
  const after=template.slice(template.indexOf(`</${p}sheetData>`)),entry=packed(name,Pako);entry.push(before);let buffer='',rowCount=0;
  return {row(values){rowCount++;buffer+=`<${p}row r="${rowCount}">`;for(let i=0;i<values.length;i++)buffer+=`<${p}c r="${col(i)}${rowCount}" t="inlineStr"><${p}is><${p}t xml:space="preserve">${cellText(values[i])}</${p}t></${p}is></${p}c>`;buffer+=`</${p}row>`;if(buffer.length>262144){entry.push(buffer);buffer='';}},finish(){if(rowCount!==total+1)throw Error('Incomplete original worksheet copy');entry.push(buffer+after);return entry.finish();}};
 }
 root.CsvZipStream={Archive,packed,worksheet,col,cellText};if(typeof module!=='undefined')module.exports=root.CsvZipStream;
})(globalThis);
