/* Reuses the original ZIP reader and CSV parser. No original records are uploaded or stored. */
importScripts('csv-viewer-worker.js');
const datasets=new Map();
onmessage=async({data})=>{
 try{
  if(data.type==='load'){
   datasets.clear();const counts={},hashes={};
   for(const source of data.sources){
    say('Loading '+source.year+' original CSV…');
    const bytes=await wakeBytes(source);
    const digest=await crypto.subtle.digest('SHA-256',bytes);
    const hash=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
    csv=new TextDecoder('windows-1252').decode(bytes);bounds=indexRecords(csv);headers=cells(rowAt(0));total=bounds.length/2-1;
    const choices=data.counts.filter(c=>c.selection.year===source.year),indices=Object.fromEntries(choices.map(c=>[c.key,[]]));
    say('Counting all '+total.toLocaleString()+' original '+source.year+' records…');
    for(let i=1;i<=total;i++){
     const values=cells(rowAt(i));if(values.length!==headers.length)throw Error('CSV column count changed');
     for(const choice of choices)if(matches(values,choice.selection,data.context))indices[choice.key].push(i);
    }
    for(const choice of choices)counts[choice.key]=indices[choice.key].length;
    hashes[source.year]={actual:hash,expected:source.wake_csv_sha256,matches:hash===source.wake_csv_sha256,total};
    datasets.set(source.year,{csv,bounds,headers,total,indices});
   }
   postMessage({type:'ready',counts,hashes});
  }else if(data.type==='page'){
   const d=datasets.get(Number(data.year));if(!d)throw Error('Load the originals first');
   const indices=data.key?d.indices[data.key]:null,count=indices?indices.length:d.total;
   const page=Math.min(Math.max(0,data.page),Math.max(0,Math.ceil(count/50)-1)),rows=[];
   for(let n=page*50;n<Math.min((page+1)*50,count);n++){
    const i=indices?indices[n]:n+1;
    rows.push({line:i+1,ordinal:n+1,values:cells(d.csv.slice(d.bounds[i*2],d.bounds[i*2+1]))});
   }
   postMessage({type:'page',id:data.id,headers:d.headers,page,count,total:d.total,rows});
  }
 }catch(error){postMessage({type:'error',message:error.message||String(error)});}
};
