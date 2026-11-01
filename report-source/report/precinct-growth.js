export function precinctGrowth(previous,current,field='wake_ballots'){
 const before=previous?.area_present?previous[field]:null,after=current?.area_present?current[field]:null;
 const available=typeof before==='number'&&typeof after==='number';
 return {previous:before,current:after,change:available?after-before:null,growth:available&&before>0?(after-before)/before*100:null,newFromZero:available&&before===0&&after>0};
}
export function growthColor(result){
 if(result.newFromZero)return '#756bb1';
 const g=result.growth;if(g===null)return '#bcbcbc';
 return g<0?'#c65c48':g<50?'#eff3ff':g<100?'#bdd7e7':g<200?'#6baed6':'#08519c';
}
