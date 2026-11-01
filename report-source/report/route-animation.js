// Accelerated route preview. Distances and travel-time estimates stay in the reviewed data.
export function routeCoordinates(route){return [route.origin_connector,route.geometry,route.destination_connector].filter(Boolean).flatMap(g=>g.coordinates).filter((p,i,a)=>!i||p[0]!==a[i-1][0]||p[1]!==a[i-1][1]);}
export function traceRoute({L,layer,coordinates,seconds,color,pane,onProgress,onComplete}){
 const points=coordinates.map(p=>L.latLng(p[1],p[0])),lengths=[0];
 for(let i=1;i<points.length;i++)lengths.push(lengths[i-1]+points[i-1].distanceTo(points[i]));
 const total=lengths.at(-1),line=L.polyline([points[0]],{pane,color,weight:5,opacity:1,interactive:false,className:'route-autoplay-trace'}).addTo(layer),dot=L.circleMarker(points[0],{pane,radius:6,color:'#fff',weight:2,fillColor:color,fillOpacity:1,interactive:false,className:'route-autoplay-dot'}).addTo(layer);
 let frame,timer,elapsed=0,last=null,lastUpdate=-200,cancelled=false;
 const tick=time=>{if(cancelled)return;if(last!==null&&!document.hidden)elapsed+=Math.min(time-last,150);last=time;const fraction=Math.min(1,elapsed/(seconds*1000)),target=total*fraction;let index=1;while(index<lengths.length-1&&lengths[index]<target)index++;const a=points[index-1],b=points[index],part=(target-lengths[index-1])/(lengths[index]-lengths[index-1]||1),tip=L.latLng(a.lat+(b.lat-a.lat)*part,a.lng+(b.lng-a.lng)*part);line.setLatLngs([...points.slice(0,index),tip]);dot.setLatLng(tip);if(elapsed-lastUpdate>=100||fraction===1){onProgress(fraction);lastUpdate=elapsed;}if(fraction<1)frame=requestAnimationFrame(tick);else timer=setTimeout(()=>{if(!cancelled)onComplete();},250);};
 onProgress(0);frame=requestAnimationFrame(tick);
 return()=>{cancelled=true;cancelAnimationFrame(frame);clearTimeout(timer);line.remove();dot.remove();};
}
