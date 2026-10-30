/* Reads one member of the official ZIP using HTTP ranges; nothing is uploaded. */
'use strict';
importScripts('vendor/pako_inflate.min.js');
let csv='',headers=[],bounds,selected=[],total=0;
const say=text=>postMessage({type:'status',text});
const view=bytes=>new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
async function range(url,start,end){
 const value=end===undefined?`bytes=-${start}`:`bytes=${start}-${end}`;
 const response=await fetch(url,{headers:{Range:value},credentials:'omit',cache:'no-store'});
 if(response.status!==206)throw Error('The original server did not return a partial file');
 const bytes=new Uint8Array(await response.arrayBuffer());
 if(end!==undefined&&bytes.length!==end-start+1)throw Error('Incomplete source range');return bytes;
}
async function wakeBytes(source){
 const tail=await range(source.url,65557),d=view(tail);let e=-1;
 for(let i=tail.length-22;i>=0;i--)if(d.getUint32(i,true)===0x06054b50&&i+22+d.getUint16(i+20,true)===tail.length){e=i;break;}
 if(e<0)throw Error('ZIP directory not found');
 const cdSize=d.getUint32(e+12,true),cdOffset=d.getUint32(e+16,true),size=cdOffset+cdSize+22+d.getUint16(e+20,true),tailStart=size-tail.length;
 const directory=cdOffset>=tailStart?tail.subarray(cdOffset-tailStart,cdOffset-tailStart+cdSize):await range(source.url,cdOffset,cdOffset+cdSize-1);
 const cd=view(directory);let member;
 for(let pos=0;pos+46<=directory.length;){
  if(cd.getUint32(pos,true)!==0x02014b50)throw Error('Invalid ZIP directory');
  const nameLen=cd.getUint16(pos+28,true),extraLen=cd.getUint16(pos+30,true),commentLen=cd.getUint16(pos+32,true);
  const name=new TextDecoder().decode(directory.subarray(pos+46,pos+46+nameLen));
  if(name===source.member)member={method:cd.getUint16(pos+10,true),compressed:cd.getUint32(pos+20,true),bytes:cd.getUint32(pos+24,true),offset:cd.getUint32(pos+42,true)};
  pos+=46+nameLen+extraLen+commentLen;
 }
 if(!member)throw Error('Wake CSV not found in the original ZIP');
 const local=await range(source.url,member.offset,member.offset+29),h=view(local);
 if(h.getUint32(0,true)!==0x04034b50)throw Error('Invalid ZIP member header');
 const start=member.offset+30+h.getUint16(26,true)+h.getUint16(28,true);
 say(`Reading the actual Wake CSV from NCSBE (${(member.compressed/1048576).toFixed(1)} MiB compressed)…`);
 const compressed=await range(source.url,start,start+member.compressed-1);
 say('Opening the original CSV and checking its bytes…');
 const bytes=member.method===0?compressed:member.method===8?pako.inflateRaw(compressed):null;
 if(!bytes||bytes.length!==member.bytes)throw Error('Could not unpack the original CSV');return bytes;
}
// CSV parser preserves quoted commas, escaped quotes and embedded line breaks.
function cells(line){
 const result=[];let value='',quoted=false;
 for(let i=0;i<line.length;i++){
  const c=line[i];if(c==='"'){if(quoted&&line[i+1]==='"'){value+='"';i++;}else quoted=!quoted;}
  else if(c===','&&!quoted){result.push(value);value='';}else value+=c;
 }result.push(value);return result;
}
function indexRecords(text){
 const out=[];let quoted=false,start=0;
 for(let i=0;i<text.length;i++){
  if(text[i]==='"')quoted=!quoted;
  if(text[i]==='\n'&&!quoted){let end=i;if(text[end-1]==='\r')end--;if(end>start)out.push(start,end);start=i+1;}
 }
 if(start<text.length)out.push(start,text.length);if(quoted)throw Error('Unclosed quoted CSV field');return new Uint32Array(out);
}
function rowAt(index){return csv.slice(bounds[index*2],bounds[index*2+1]);}
function matches(values,s,context){
 const r=Object.fromEntries(headers.map((h,i)=>[h,(values[i]||'').trim()]));
 const window=context.summary.find(w=>w.year===s.year&&w.scope===s.scope),campus=r.site_name===context.site_mapping[String(s.year)];
 const parts=r.ballot_rtn_dt.split('/'),day=parts.length===3?`${parts[2]}-${parts[0].padStart(2,'0')}-${parts[1].padStart(2,'0')}`:'';
 if(!window||r.county_desc!=='WAKE'||!['ONE-STOP','ONE STOP','EARLY VOTING'].includes(r.ballot_req_type.toUpperCase())||r.ballot_rtn_status!=='ACCEPTED'||day<window.start_date||day>window.end_date)return false;
 if(s.scope==='Campus site'&&!campus||s.scope==='Other Wake sites'&&campus)return false;
 const age=/^\d+$/.test(r.age)?Number(r.age):NaN;
 if(s.field==='age_18_24')return age>=18&&age<=24;
 if(s.field==='age_18_22')return age>=18&&age<=22;
 if(s.field==='same_day_registration')return ['Y','YES'].includes(r.sdr.toUpperCase());
 if(s.dimension==='age_group')return ([[18,24,'18–24'],[25,34,'25–34'],[35,44,'35–44'],[45,64,'45–64'],[65,120,'65+']].find(([lo,hi])=>age>=lo&&age<=hi)||[0,0,'Unknown / outside range'])[2]===s.value;
 if(s.dimension==='party')return (['DEM','REP','UNA'].includes(r.voter_party_code)?r.voter_party_code:'OTHER_PARTIES')===s.value;
 if(['race','gender','ethnicity'].includes(s.dimension))return (r[s.dimension]||'Unknown')===s.value;
 return true;
}
onmessage=async({data})=>{
 try{
  if(data.type==='load'){
   const bytes=await wakeBytes(data.source);
   const digest=await crypto.subtle.digest('SHA-256',bytes),hash=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
   csv=new TextDecoder('windows-1252').decode(bytes);say('Indexing the original rows for the preview…');
   bounds=indexRecords(csv);headers=cells(rowAt(0));total=bounds.length/2-1;selected=[];
   for(let i=1;i<=total;i++){const row=cells(rowAt(i));if(row.length!==headers.length)throw Error('CSV column count changed');if(data.selections.some(s=>matches(row,s,data.context)))selected.push(i);}
   postMessage({type:'ready',hash});
  }else if(data.type==='page'){
   const all=data.scope==='all',count=all?total:selected.length,page=Math.min(Math.max(0,data.page),Math.max(0,Math.ceil(count/50)-1)),rows=[],raw=[rowAt(0)];
   for(let n=page*50;n<Math.min((page+1)*50,count);n++){const index=all?n+1:selected[n],text=rowAt(index);rows.push({line:index+1,values:cells(text)});raw.push(text);}
   postMessage({type:'page',id:data.id,page,count,total,headers,rows,raw:raw.join('\r\n')});
  }
 }catch(error){postMessage({type:'error',message:error.message||String(error)});}
};
