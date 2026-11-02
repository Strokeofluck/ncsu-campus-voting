import React,{useEffect,useState} from 'react';
export default function CompactRoutePager({items,selectedId,idFor,renderItem,onBrowse,label}){
 const [size,setSize]=useState(()=>window.matchMedia('(max-width:600px)').matches?2:4),[page,setPage]=useState(0),key=items.map(idFor).join('|');
 useEffect(()=>{const media=window.matchMedia('(max-width:600px)'),change=()=>setSize(media.matches?2:4);media.addEventListener('change',change);return()=>media.removeEventListener('change',change);},[]);
 useEffect(()=>{const at=items.findIndex(r=>idFor(r)===selectedId);setPage(at<0?0:Math.floor(at/size));},[selectedId,key,size]);
 const last=Math.max(0,Math.ceil(items.length/size)-1),safe=Math.min(page,last),start=safe*size;
 const go=next=>{onBrowse?.();setPage(next);};
 return <div className="compact-route-pager" aria-label={label}><div className="compact-route-pager-nav"><button type="button" aria-label={`Previous ${label}`} disabled={safe===0} onClick={()=>go(safe-1)}>← Previous</button><span aria-live="polite">{start+1}–{Math.min(start+size,items.length)} of {items.length}</span><button type="button" aria-label={`Next ${label}`} disabled={safe===last} onClick={()=>go(safe+1)}>Next →</button></div><div className="compact-route-strip">{items.slice(start,start+size).map(renderItem)}</div></div>;
}
