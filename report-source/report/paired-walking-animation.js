// Both paths share one preview clock; the displayed walking estimates are unchanged.
export function tracePairedWalkingRoutes({L,layer,routes,container,onComplete,seconds=1}){
 const maxMinutes=Math.max(...routes.map(r=>r.minutes)),duration=Math.min(seconds*1000,maxMinutes*35);
 const tracks=routes.map(({coordinates,color,decorateLine,minutes})=>{
  const points=coordinates.map(p=>L.latLng(p[1],p[0])),lengths=[0];
  for(let i=1;i<points.length;i++)lengths.push(lengths[i-1]+points[i-1].distanceTo(points[i]));
  const line=L.polyline([points[0]],{pane:'walking-routes',color,weight:5,opacity:.95,lineCap:'round',lineJoin:'round',className:'walking-paired-trace',interactive:true}).addTo(layer);
  if(decorateLine)decorateLine(line);
  const dot=L.circleMarker(points[0],{pane:'walking-routes',radius:5,color:'#fff',weight:2,fillColor:color,fillOpacity:1,interactive:false,className:'walking-paired-dot'}).addTo(layer);
  return {points,lengths,total:lengths.at(-1),line,dot,duration:duration*minutes/maxMinutes};
 });
 const reduced=false;
 let frame,last=null,elapsed=0,cancelled=false;
 const draw=progress=>{for(const t of tracks){const fraction=Math.min(1,elapsed/t.duration),target=t.total*fraction;let i=1;while(i<t.lengths.length-1&&t.lengths[i]<target)i++;const a=t.points[i-1],b=t.points[i]||a,part=(target-t.lengths[i-1])/(t.lengths[i]-t.lengths[i-1]||1),tip=L.latLng(a.lat+(b.lat-a.lat)*part,a.lng+(b.lng-a.lng)*part);t.line.setLatLngs(fraction===1?t.points:[...t.points.slice(0,i),tip]);t.dot.setLatLng(tip);}container.dataset.walkingProgress=String(progress);container.dataset.walkingPhase=progress===1?'complete':'drawing';};
 const tick=time=>{if(cancelled)return;const rect=container.getBoundingClientRect(),inView=rect.bottom>0&&rect.top<innerHeight;
  if(last!==null&&!document.hidden&&inView)elapsed+=Math.min(time-last,150);last=time;
  const fraction=reduced?1:Math.min(1,elapsed/duration);draw(fraction);
  if(elapsed>=(reduced?0:duration)+250){onComplete();return;}frame=requestAnimationFrame(tick);
 };
 draw(reduced?1:0);frame=requestAnimationFrame(tick);
 return()=>{cancelled=true;cancelAnimationFrame(frame);tracks.forEach(t=>{t.line.remove();t.dot.remove();});delete container.dataset.walkingProgress;delete container.dataset.walkingPhase;};
}
