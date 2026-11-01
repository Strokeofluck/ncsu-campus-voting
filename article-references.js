'use strict';
(()=>{
 const data=JSON.parse(document.getElementById('reference-data').textContent);
 const $=id=>document.getElementById(id);
 const number=n=>n.toLocaleString('en-US');
 const precise=n=>n.toFixed(7)+'…';
 const rate=n=>(n>0?'+':'')+n.toFixed(1)+'%';
 const bounds={'18–24':[18,24],'25–34':[25,34],'35–44':[35,44],'45–64':[45,64],'65+':[65,120]};
 const requested=new URLSearchParams(location.search).get('age');
 let selected=data.rows.some(r=>r.cohort===requested)?requested:'18–24';
 function render(){
  const r=data.rows.find(r=>r.cohort===selected);
  $('age').value=selected;
  $('scope-note').textContent=`Ages ${selected}. These counts include voters from any home precinct in Wake who voted at Talley in 2022 or Western Boulevard in 2026; Wake County includes all sites.`;
  const [lo,hi]=bounds[selected];$('age-filter').textContent=`Age filter: ${lo} through ${hi}, inclusive.`;
  const cells=$('count-rows').querySelectorAll('td');
  [r.site_ballots_2022,r.site_ballots_2026,r.county_ballots_2022,r.county_ballots_2026].forEach((v,i)=>cells[i].textContent=number(v));
  for(const scope of ['site','county']){
   const before=r[scope+'_ballots_2022'],after=r[scope+'_ballots_2026'],difference=after-before;
   const growth=difference/before*100;
   const texts=[`${number(after)} − ${number(before)} = ${number(difference)} additional ballots.`,`${number(difference)} ÷ ${number(before)} = ${precise(difference/before)}.`,`Multiply by 100 ≈ ${precise(growth)}%. Round to one decimal: ${growth.toFixed(1)}%.`];
   $(scope+'-steps').replaceChildren(...texts.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
   $(scope+'-result').textContent=`${scope==='site'?'Talley → Western Boulevard':'Wake County'} growth: ${rate(growth)}`;
  }
  const sg=(r.site_ballots_2026/r.site_ballots_2022-1)*100,cg=(r.county_ballots_2026/r.county_ballots_2022-1)*100,gap=sg-cg;
  $('gap-formula').textContent=`${precise(sg)}% − ${precise(cg)}% ≈ ${precise(gap)} percentage points.`;
  $('gap-result').textContent=`Talley → Western Boulevard growth was ${Math.abs(gap).toFixed(1)} percentage points ${gap<0?'behind':'ahead of'} Wake’s growth.`;
  $('all-age-rows').querySelectorAll('tr').forEach(row=>row.classList.toggle('is-selected',row.dataset.age===selected));
 }
 function choose(value,scroll){selected=value;render();const q=new URLSearchParams(location.search);q.set('age',value);history.replaceState(null,'','?'+q+'#math');if(scroll)$('math').scrollIntoView({block:'start'});}
 $('age').addEventListener('change',e=>choose(e.target.value,false));
 $('all-age-rows').addEventListener('click',e=>{const link=e.target.closest('a[data-age]');if(link){e.preventDefault();choose(link.dataset.age,true);}});
 render();
})();
