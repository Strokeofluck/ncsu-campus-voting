/* Extend the browser-local workbook with a trace of the county college-age count. */
(function(root){
 'use strict';
 const names=['5 County source','6 County flags','7 County counts','8 Growth proof'];
 const range=(col,first,last)=>`'6 County flags'!$${col}$${first}:$${col}$${last}`;
 function flagFormulas(r){
  const s=c=>`'5 County source'!${c}${r}`,lookup=i=>`VLOOKUP(A${r},'0 Original files'!$A$6:$I$8,${i},FALSE)`;
  return [`=${s('A')}`,`=${s('B')}`,`=IF(TRIM(${s('C')})="WAKE",1,0)`,
   `=IF(OR(UPPER(TRIM(${s('D')}))="ONE-STOP",UPPER(TRIM(${s('D')}))="ONE STOP",UPPER(TRIM(${s('D')}))="EARLY VOTING"),1,0)`,
   `=IF(TRIM(${s('E')})="ACCEPTED",1,0)`,
   `=IF(TRIM(${s('F')})="","",DATE(VALUE(RIGHT(TRIM(${s('F')}),4)),VALUE(LEFT(TRIM(${s('F')}),2)),VALUE(MID(TRIM(${s('F')}),4,2))))`,
   `=IF(AND(ISNUMBER(F${r}),F${r}>=${lookup(5)},F${r}<=${lookup(6)}),1,0)`,
   `=IF(TRIM(${s('H')})="","",IFERROR(VALUE(TRIM(${s('H')})),""))`,
   `=IF(AND(ISNUMBER(H${r}),H${r}>=18,H${r}<=24),1,0)`,
   `=IF(AND(C${r}=1,D${r}=1,E${r}=1,G${r}=1,I${r}=1),1,0)`,
   `=IF(AND(J${r}=1,TRIM(${s('G')})=${lookup(4)}),1,0)`,
   `=J${r}-K${r}`,
   ...['J','K','L'].map((c,i)=>r===6?`=SUM(${c}6)`:`=IF(A${r}=A${r-1},SUM(${String.fromCharCode(77+i)}${r-1},${c}${r}),SUM(${c}${r}))`)];
 }
 function evaluate(dataset,context,Plan){
  let county=0,site=0,other=0;
  return dataset.countyRows.map(v=>{
   const raw=Plan.evaluateRows({source:dataset.source,rows:[v]},context)[0];
   const included=Number(raw[2]===1&&raw[3]===1&&raw[5]===1&&raw[7]===1&&typeof raw[8]==='number'&&raw[8]>=18&&raw[8]<=24);
   const at=included*raw[4],elsewhere=included-at;county+=included;site+=at;other+=elsewhere;
   return [v[0],v[1],raw[2],raw[3],raw[5],raw[6],raw[7],raw[8],Number(typeof raw[8]==='number'&&raw[8]>=18&&raw[8]<=24),included,at,elsewhere,county,site,other];
  });
 }
 function countFormulas(row,first,last){return [
  `=SUM(${range('J',first,last)})`,`=SUM(${range('K',first,last)})`,`=SUM(${range('L',first,last)})`,
  `=COUNTIFS(${range('J',first,last)},1)`,`=SUM(C${row}:D${row})`,`=B${row}-E${row}`,`=B${row}-F${row}`];}
 function growthFormulas(r,scope,baseline){
  const old=baseline===2022?'D':'E',oldCounty=baseline===2022?6:7;
  return [null,scope==='site'?`='3 Counts'!${old}7`:`='7 County counts'!B${oldCounty}`,
   scope==='site'?"='3 Counts'!F7":"='7 County counts'!B8",`=C${r}-B${r}`,`=IF(B${r}=0,"",D${r}/B${r})`,
   `=IF(B${r}=0,"",E${r}*100)`];
 }
 function comparisonFormulas(r){return r===22?["='4 Math'!C7","='4 Math'!G7",'=(C22-B22)*100']:[ '=IF(B7=0,"",B6/B7)','=IF(C7=0,"",C6/C7)','=(C23-B23)*100'];}
 const xml=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 async function append(zip,datasets,context,Plan){
  const flags=datasets.map(d=>evaluate(d,context,Plan)),totals=flags.map(rows=>rows.reduce((out,r)=>out.map((n,i)=>n+r[9+i]),[0,0,0]));
  for(let j=0;j<3;j++)for(const [i,scope]of ['Wake County','Campus site','Other Wake sites'].entries()){
   const expected=context.summary.find(r=>r.year===datasets[j].source.year&&r.scope===scope).age_18_24;
   if(totals[j][i]!==expected)throw Error('County original '+datasets[j].source.year+' '+scope+' count differs; export stopped');
  }
  let first=6;const spans=datasets.map(d=>{const out={first,last:first+d.countyRows.length-1};first=out.last+1;return out;}),last=first-1;
  for(let index=0;index<4;index++){
   const filename=`xl/worksheets/sheet${9+index}.xml`;let text=await zip.file(filename).async('string');
   const p=(text.match(/<([\w]+:)?worksheet\b/)||[])[1]||'';
   const rows=[...text.matchAll(new RegExp(`<${p}row\\b[^>]*\\br="(\\d+)"[\\s\\S]*?<\\/${p}row>`,'g'))];
   const head=rows.filter(r=>Number(r[1])<6).map(r=>r[0]).join('');
   const styles={};for(const m of text.matchAll(new RegExp(`<${p}c\\b([^>]*\\br="([A-Z]+)6"[^>]*)>`,'g')))styles[m[2]]=(m[1].match(/\bs="(\d+)"/)||[])[1]||'0';
   const row=(r,values,formulas=[])=>`<${p}row r="${r}" ht="24" customHeight="1">`+values.map((v,i)=>{
    const ref=Plan.column(i)+r,style=styles[Plan.column(i)]||'0',f=formulas[i];
    return f?`<${p}c r="${ref}" s="${style}"${typeof v==='number'?'':' t="str"'}><${p}f>${xml(f.slice(1))}</${p}f><${p}v>${xml(v)}</${p}v></${p}c>`:
     typeof v==='number'?`<${p}c r="${ref}" s="${style}"><${p}v>${v}</${p}v></${p}c>`:`<${p}c r="${ref}" s="${style}" t="inlineStr"><${p}is><${p}t xml:space="preserve">${xml(v)}</${p}t></${p}is></${p}c>`;
   }).join('')+`</${p}row>`;
   let body='';
   if(index<2){let r=6;const parts=[];for(let j=0;j<3;j++)for(let k=0;k<datasets[j].countyRows.length;k++,r++){
    const d=datasets[j],values=d.countyRows[k];parts.push(index===0?row(r,values,[null,null,...Plan.fields.map(f=>Plan.sourceFormula(d.source.year,Plan.column(d.headers.indexOf(f)),values[1]))]):row(r,flags[j][k],flagFormulas(r)));
   }body=parts.join('');
   }else if(index===2){body=datasets.map((d,j)=>{const r=j+6,[a,b,c]=totals[j];return row(r,[d.source.year,a,b,c,a,b+c,0,0],[null,...countFormulas(r,spans[j].first,spans[j].last)]);}).join('');
   }else{body=[[6,'site',2022],[7,'county',2022],[11,'site',2024],[12,'county',2024]].map(([r,scope,base])=>{
    const j=base===2022?0:1,k=scope==='site'?1:0,a=totals[j][k],b=totals[2][k],f=growthFormulas(r,scope,base);
    return row(r,[`${scope==='site'?'Talley to Western':'Wake County'} ages 18–24 (${base} to 2026)`,a,b,b-a,a?(b-a)/a:'',a?(b-a)/a*100:'',...f.slice(3,6)],f);
   }).join('')+rows.filter(r=>Number(r[1])>=15).map(v=>{const r=Number(v[1]);if(r!==22&&r!==23)return v[0];const a=r===22?totals[0][1]/context.summary.find(s=>s.year===2022&&s.scope==='Campus site').all_ages:totals[0][1]/totals[0][0],b=r===22?totals[2][1]/context.summary.find(s=>s.year===2026&&s.scope==='Campus site').all_ages:totals[2][1]/totals[2][0];return row(r,[r===22?'Ages 18–24 share of site ballots':'Site share of Wake ages 18–24 ballots',a,b,(b-a)*100],[null,...comparisonFormulas(r)]);}).join('');}
   const end=index<2?Math.max(6,last):index===2?8:28,col=index===0?'I':index===1?'O':index===2?'H':'I';
   text=text.replace(new RegExp(`<${p}sheetData[^>]*>[\\s\\S]*?<\\/${p}sheetData>`),`<${p}sheetData>${head}${body}</${p}sheetData>`).replace(new RegExp(`<${p}dimension\\b[^>]*/>`),`<${p}dimension ref="A1:${col}${end}"/>`);
   if(index<2){text=text.replace(/sqref="([A-Z]+)6:([A-Z]+)13"/g,(_,a,b)=>`sqref="${a}6:${b}${end}"`);text=text.replace(`</${p}sheetData>`,`</${p}sheetData><${p}autoFilter ref="A5:${col}${end}"/>`);}
   zip.file(filename,text);
  }
  return {totals,sourceRows:datasets.map(d=>d.countyRows.length)};
 }
 root.CsvCountyExcel={names,flagFormulas,countFormulas,growthFormulas,comparisonFormulas,evaluate,append};if(typeof module!=='undefined')module.exports=root.CsvCountyExcel;
})(globalThis);
