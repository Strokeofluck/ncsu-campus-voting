import {campusWalkingColors} from './campus-map-context.jsx';
// Offset time labels with thin leaders to actual visible route points.
// This is screen-space annotation only; the reviewed paths/times are unchanged.
const NS='http://www.w3.org/2000/svg';
const node=(tag,attrs={},text)=>{const el=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;return el;};
const overlaps=(a,b,pad=0)=>a.x<b.x+b.w+pad&&a.x+a.w+pad>b.x&&a.y<b.y+b.h+pad&&a.y+a.h+pad>b.y;
const inside=(p,r,pad=0)=>p.x>=r.x-pad&&p.x<=r.x+r.w+pad&&p.y>=r.y-pad&&p.y<=r.y+r.h+pad;
function crosses(a,b,r,pad=0){const dx=b.x-a.x,dy=b.y-a.y,ps=[-dx,dx,-dy,dy],qs=[a.x-r.x+pad,r.x+r.w+pad-a.x,a.y-r.y+pad,r.y+r.h+pad-a.y];let lo=0,hi=1;for(let i=0;i<4;i++){if(Math.abs(ps[i])<1e-8){if(qs[i]<0)return false;}else{const t=qs[i]/ps[i];if(ps[i]<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;}}return true;}
function lineDistance(L,p,points){let best=Infinity;for(let i=1;i<points.length;i++)best=Math.min(best,L.LineUtil.pointToSegmentDistance(p,points[i-1],points[i]));return best;}
function atDistance(L,points,fraction){const lengths=points.slice(1).map((p,i)=>p.distanceTo(points[i])),total=lengths.reduce((a,b)=>a+b,0);let left=total*fraction;for(let i=0;i<lengths.length;i++){if(left<=lengths[i]||i===lengths.length-1){const part=lengths[i]?left/lengths[i]:0;return L.point(points[i].x+(points[i+1].x-points[i].x)*part,points[i].y+(points[i+1].y-points[i].y)*part);}left-=lengths[i];}return points[0];}
function place(L,map,routes,obstacles,key){const size=map.getSize(),w=96,h=44,mb=map.getContainer().getBoundingClientRect(),kb=key?.getBoundingClientRect(),blocked=[{x:size.x-54,y:size.y-92,w:50,h:88},{x:3,y:size.y-40,w:115,h:37}];if(kb)blocked.push({x:kb.left-mb.left,y:kb.top-mb.top,w:kb.width,h:kb.height});const chosen=[];
 for(let index=0;index<routes.length;index++){
  const route=routes[index],other=routes[1-index].points,anchors=[.2,.35,.5,.65,.8,.92].map(f=>atDistance(L,route.points,f)).filter(p=>inside(p,{x:7,y:7,w:size.x-14,h:size.y-14}));if(!anchors.length)continue;
  let best=null;
  for(const target of anchors){const candidates=[];for(const [dx,dy] of [[24,30],[-w-24,30],[-w/2,40],[24,-h-30],[-w-24,-h-30],[-w/2,-h-40],[40,-h/2],[-w-40,-h/2]])candidates.push({x:target.x+dx,y:target.y+dy,w,h});for(let y=12;y<=size.y-h-12;y+=28)for(let x=12;x<=size.x-w-12;x+=36)candidates.push({x,y,w,h});
   for(const rect of candidates){if(rect.x<10||rect.y<10||rect.x+w>size.x-10||rect.y+h>size.y-10||blocked.some(b=>overlaps(rect,b,8))||chosen.some(c=>overlaps(rect,c.rect,10)))continue;
    if(routes.some(r=>r.points.slice(1).some((p,i)=>crosses(r.points[i],p,rect,7))))continue;
    const edge=[L.point(rect.x+w/2,rect.y),L.point(rect.x+w/2,rect.y+h),L.point(rect.x,rect.y+h/2),L.point(rect.x+w,rect.y+h/2)].sort((a,b)=>a.distanceTo(target)-b.distanceTo(target))[0],length=edge.distanceTo(target),markers=obstacles.filter(p=>inside(p,rect,7)).length,hidden=blocked.some(b=>inside(target,b,3)),throughLabel=chosen.some(c=>crosses(edge,target,c.rect,5));
    const score=length+markers*65+(hidden?500:0)+(throughLabel?500:0)+35/(lineDistance(L,target,other)+2)+(target.x<size.x/2&&index===0?3:0);
    if(!best||score<best.score)best={rect,target,edge,score,...route};
   }
  }
  if(best)chosen.push(best);
 }
 return chosen;
}
export function addWalkingTimeCallouts(L,map,layer,{row,pace,buildingCenters}){
 const Callouts=L.Layer.extend({
  onAdd(activeMap){this.map=activeMap;if(!activeMap.getPane('walking-callouts')){const pane=activeMap.createPane('walking-callouts');pane.style.zIndex='490';pane.style.pointerEvents='none';}this.svg=node('svg',{'class':'walking-route-callouts','aria-label':'Estimated walking times and miles to the two voting sites'});activeMap.getPane('walking-callouts').append(this.svg);this.redraw=()=>{cancelAnimationFrame(this.frame);this.frame=requestAnimationFrame(()=>this.draw());};activeMap.on('move zoomend resize',this.redraw);const key=activeMap.getContainer().closest('.campus-map-with-key')?.querySelector('.campus-map-key');this.key=key;this.observer=new ResizeObserver(this.redraw);if(key)this.observer.observe(key);this.draw();},
  draw(){const activeMap=this.map,size=activeMap.getSize();this.svg.setAttribute('width',size.x);this.svg.setAttribute('height',size.y);this.svg.setAttribute('viewBox',`0 0 ${size.x} ${size.y}`);L.DomUtil.setPosition(this.svg,activeMap.containerPointToLayerPoint([0,0]));this.svg.replaceChildren();
   const routes=[['talley','Talley (2022)',campusWalkingColors.talley],['western','Western (2026)',campusWalkingColors.western]].map(([key,title,color])=>({key,title,color,time:`≈ ${(row[key+'_m']/pace).toFixed(1)} min`,distance:`${(row[key+'_m']/1609.344).toFixed(2)} mi`,points:row[key+'_route'].geometry.coordinates.map(p=>activeMap.latLngToContainerPoint([p[1],p[0]]))})),obstacles=Object.values(buildingCenters).map(p=>activeMap.latLngToContainerPoint([p[1],p[0]])),placements=place(L,activeMap,routes,obstacles,this.key);
   for(const p of placements){const line=node('line',{x1:p.edge.x,y1:p.edge.y,x2:p.target.x,y2:p.target.y,stroke:p.color,'stroke-width':1.1,'class':'walking-time-leader','data-route-site':p.key});this.svg.append(line);}
   for(const p of placements){const group=node('g',{'class':'walking-time-callout','data-route-site':p.key,role:'img','aria-label':`${p.title}: ${p.time}, ${p.distance} estimated one-way walk`});group.append(node('rect',{x:p.rect.x,y:p.rect.y,width:p.rect.w,height:p.rect.h,rx:3,fill:'#fff','fill-opacity':.97,stroke:'#c3ccd1','stroke-width':.7}),node('text',{x:p.rect.x+p.rect.w/2,y:p.rect.y+12,'text-anchor':'middle',fill:p.color,'class':'walking-time-callout-title'},p.title),node('text',{x:p.rect.x+p.rect.w/2,y:p.rect.y+26,'text-anchor':'middle',fill:'#203040','class':'walking-time-callout-value'},p.time),node('text',{x:p.rect.x+p.rect.w/2,y:p.rect.y+39,'text-anchor':'middle',fill:'#4c5962','class':'walking-time-callout-distance'},p.distance));this.svg.append(group);}
  },
  onRemove(activeMap){cancelAnimationFrame(this.frame);activeMap.off('move zoomend resize',this.redraw);this.observer.disconnect();this.svg.remove();this.map=null;}
 });return new Callouts().addTo(layer);
}
