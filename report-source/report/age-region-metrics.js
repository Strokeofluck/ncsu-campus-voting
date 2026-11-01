export const FOCAL_AREAS=['PRECINCT 01-23','PRECINCT 01-31'];
export const METRICS={
 growth_gap_pp:{label:'Growth versus Wake County',unit:'percentage points',cuts:[-50,-20,-5,5,20,50],labels:['50+ points behind','20–50 behind','5–20 behind','Within 5 points','5–20 ahead','20–50 ahead','50+ ahead']},
 ballot_change:{label:'Extra / fewer ballots',unit:'ballots',cuts:[-500,-200,-50,50,200,500],labels:['<−500','−500 to <−200','−200 to <−50','−50 to <50','50 to <200','200 to <500','500+']},
 growth_pct:{label:'Percentage growth',unit:'%',cuts:[0,50,100,200],labels:['Decrease','0 to <50%','50 to <100%','100 to <200%','200%+']},
 share_change_pp:{label:'Change in age-group share',unit:'pp',cuts:[-10,-5,-1,1,5,10],labels:['<−10 pp','−10 to <−5','−5 to <−1','−1 to <1','1 to <5','5 to <10','10+ pp']}
};
const diverging=['#9c3f16','#d67a45','#f2b994','#f1eee9','#b6d5e7','#609fc7','#17618d'];
const growth=['#bf653e','#edf4f7','#b6d5e7','#609fc7','#17618d'];
export const scaleColors=metric=>metric==='growth_pct'?growth:diverging;
export function regionColor(row,metric){
 const value=row?.[metric];if(typeof value!=='number')return '#bdbdbd';
 const index=METRICS[metric].cuts.findIndex(c=>value<c);
 return scaleColors(metric)[index<0?METRICS[metric].cuts.length:index];
}
export function rankedRegions(rows,metric,direction='absolute',minimum=20){
 return rows.filter(r=>r.mapped&&typeof r[metric]==='number'&&(!['growth_pct','growth_gap_pp'].includes(metric)||r.ballots_2022>=minimum)&&(direction==='absolute'||(direction==='increase'?r[metric]>0:r[metric]<0)))
 .sort((a,b)=>(direction==='absolute'?Math.abs(b[metric])-Math.abs(a[metric]):direction==='increase'?b[metric]-a[metric]:a[metric]-b[metric])||a.area.localeCompare(b.area));
}
