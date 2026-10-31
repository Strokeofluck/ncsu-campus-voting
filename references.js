'use strict';
(()=>{
 const $=id=>document.getElementById(id),data=JSON.parse($('reference-data').textContent),query=new URLSearchParams(location.search);
 const el=(tag,text,attrs={})=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;for(const [name,value]of Object.entries(attrs))node.setAttribute(name,value);return node;};
 let baseline=query.get('baseline')==='2024'?2024:2022,selected=query.get('figure')||`change-${baseline}-age-group-18-24`;
 const proof=CsvProofView.create($('csv-workspace'),{figure:data.records[selected]?selected:`change-${baseline}-age-group-18-24`,initialTab:'calculation'});
 const summary=(year,scope)=>data.summary.find(r=>r.year===year&&r.scope===scope);
 const number=(n,unit)=>unit==='%'?n.toFixed(1)+'%':n.toLocaleString('en-US');
 const delta=(n,unit)=>(n>0?'+':'')+n.toFixed(1)+(unit==='%'?'%':' pp');
 const date=day=>new Intl.DateTimeFormat('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'}).format(new Date(day+'T00:00:00Z'));
 const id=(kind)=>({all:`growth-${baseline}-campus-site-all-ages`,college:`growth-${baseline}-campus-site-age-18-24`,share:`change-${baseline}-age-group-18-24`,older:`change-${baseline}-age-group-65`,county:`growth-${baseline}-wake-county-age-18-24`}[kind]);
 function choose(figure,scroll){
  const record=data.records[figure];if(!record)return;selected=figure;
  proof.setFigure(figure);
  $('selected-title').textContent=record.label;$('source-details').href='figure-source.html#'+encodeURIComponent(figure);
  for(const row of $('comparison-rows').rows)row.classList.toggle('is-selected',row.dataset.figure===figure);
  history.replaceState(null,'','?baseline='+baseline+'&figure='+encodeURIComponent(figure)+(scroll?'#csv':location.hash));
  if(scroll)$('csv').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
 }
 function render(){
  const previous=summary(baseline,'Campus site'),current=summary(2026,'Campus site'),wakePrevious=summary(baseline,'Wake County'),wakeCurrent=summary(2026,'Wake County');
  const share=(year,group)=>data.records[`demographic-${year}-age-group-${group}`].value;
  const rows=[['all','Campus site · all ages',previous.all_ages,current.all_ages,'ballots'],['college','Campus site · ages 18–24',previous.age_18_24,current.age_18_24,'ballots'],['share','College-age share of site ballots',share(baseline,'18-24'),share(2026,'18-24'),'%'],['older','65+ share of site ballots',share(baseline,'65'),share(2026,'65'),'%'],['county','Wake County · ages 18–24',wakePrevious.age_18_24,wakeCurrent.age_18_24,'ballots']];
  $('previous-header').textContent=String(baseline);$('baseline').value=String(baseline);
  $('period-note').textContent=`Talley: ${date(previous.start_date)}–${date(previous.end_date)}. Western Boulevard: ${date(current.start_date)}–${date(current.end_date)}. `+(baseline===2022?'Both elections are midterms.':'2024 was a presidential election; 2026 is a midterm.');
  $('comparison-rows').replaceChildren();
  for(const [kind,label,before,after,unit]of rows){
   const record=data.records[id(kind)],tr=el('tr',undefined,{'data-kind':kind,'data-figure':record.id});
   const link=el('a','Check math',{class:'figure-link',href:'csv-proof.html?figure='+record.id+'&tab=calculation','data-figure':record.id,'aria-label':'Check math: '+label});
   const td=el('td');td.append(link);tr.append(el('th',label,{scope:'row'}),el('td',number(before,unit)),el('td',number(after,unit)),el('td',delta(record.value,record.unit)),td);$('comparison-rows').append(tr);
  }
  choose(data.records[selected]?selected:id('share'),false);
 }
 $('baseline').addEventListener('change',()=>{const kind=[...$('comparison-rows').rows].find(row=>row.dataset.figure===selected)?.dataset.kind||'share';baseline=Number($('baseline').value);selected=id(kind);render();});
 $('comparison-rows').addEventListener('click',event=>{const link=event.target.closest('a[data-figure]');if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return;event.preventDefault();choose(link.dataset.figure,true);});
 render();
})();
