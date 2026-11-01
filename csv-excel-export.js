/* Fill the authored Excel template locally. Original CSV bytes stay separate and unchanged. */
(function(root){
 'use strict';
 const names=['0 Original files','1 Source rows','2 Filter flags','3 Counts','4 Math'];
 const sheetNames=[names[0],'Copy 2022','Copy 2024','Copy 2026',...names.slice(1),...root.CsvCountyExcel.names];
 const column=index=>{let s='';for(let n=index+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
 const sourceFormula=(year,column,record)=>{const ref=`'Copy ${year}'!${column}${record}`;return `=IF(${ref}="","",${ref})`;};
 const fields=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr'];
 const bands=[[18,24,'18–24'],[25,34,'25–34'],[35,44,'35–44'],[45,64,'45–64'],[65,120,'65+']];
 const xml=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 const dateSerial=day=>(Date.parse(day+'T00:00:00Z')-Date.UTC(1899,11,30))/86400000;
 const range=(sheet,col,last)=>`'${sheet}'!$${col}$6:$${col}$${last}`;
 function flagFormulas(row){
  const s=col=>`'1 Source rows'!${col}${row}`,lookup=index=>`VLOOKUP(A${row},'0 Original files'!$A$6:$I$8,${index},FALSE)`;
  return [`=${s('A')}`,`=${s('B')}`,`=IF(TRIM(${s('C')})="WAKE",1,0)`,
   `=IF(OR(UPPER(TRIM(${s('D')}))="ONE-STOP",UPPER(TRIM(${s('D')}))="ONE STOP",UPPER(TRIM(${s('D')}))="EARLY VOTING"),1,0)`,
   `=IF(TRIM(${s('G')})=${lookup(4)},1,0)`,`=IF(TRIM(${s('E')})="ACCEPTED",1,0)`,
   `=IF(TRIM(${s('F')})="","",DATE(VALUE(RIGHT(TRIM(${s('F')}),4)),VALUE(LEFT(TRIM(${s('F')}),2)),VALUE(MID(TRIM(${s('F')}),4,2))))`,
   `=IF(AND(ISNUMBER(G${row}),G${row}>=${lookup(5)},G${row}<=${lookup(6)}),1,0)`,
   `=IF(TRIM(${s('H')})="","",IFERROR(VALUE(TRIM(${s('H')})),""))`,
   `=IF(OR(UPPER(TRIM(${s('I')}))="Y",UPPER(TRIM(${s('I')}))="YES"),1,0)`,
   `=IF(AND(C${row}=1,D${row}=1,E${row}=1,F${row}=1,H${row}=1),1,0)`,
   `=IF(AND(K${row}=1,ISNUMBER(I${row}),I${row}>=18,I${row}<=24),1,0)`,
   row===6?'=K6':`=IF(A${row}=A${row-1},M${row-1}+K${row},K${row})`,
   row===6?'=L6':`=IF(A${row}=A${row-1},N${row-1}+L${row},L${row})`];
 }
 function countFormulas(row,last){
  return ['D','E','F'].map(col=>{
   let args=`${range(names[2],'A',last)},${col}$5,${range(names[2],'K',last)},1`;
   if(row>=7&&row<=12)args+=`,${range(names[2],'I',last)},">="&$B${row},${range(names[2],'I',last)},"<="&$C${row}`;
   if(row===13)args+=`,${range(names[2],'J',last)},1`;
   return `=COUNTIFS(${args})`;
  });
 }
 function mathFormulas(row){return [`='3 Counts'!A${row}`,`='3 Counts'!D${row}`,`=IF(B$6=0,"",B${row}/B$6)`,
  `='3 Counts'!E${row}`,`=IF(D$6=0,"",D${row}/D$6)`,`='3 Counts'!F${row}`,`=IF(F$6=0,"",F${row}/F$6)`,
  `=F${row}-B${row}`,`=IF(B${row}=0,"",H${row}/B${row})`,`=IF(OR(C${row}="",G${row}=""),"",(G${row}-C${row})*100)`];}
 function evaluateRows(dataset,context){
  const year=dataset.source.year,w=context.summary.find(r=>r.year===year&&r.scope==='Campus site');
  let running=0,young=0;
  return dataset.rows.map(values=>{
   const [y,record,county,type,status,date,site,age,sdr]=values;
   const clean=String(date).trim(),day=/^\d{2}\/\d{2}\/\d{4}$/.test(clean)?clean.slice(6)+'-'+clean.slice(0,2)+'-'+clean.slice(3,5):'';
   const parsedAge=/^\d+$/.test(String(age).trim())?Number(String(age).trim()):'';
   const flags=[y,record,Number(county.trim()==='WAKE'),Number(['ONE-STOP','ONE STOP','EARLY VOTING'].includes(type.trim().toUpperCase())),Number(site.trim()===context.site_mapping[y]),Number(status.trim()==='ACCEPTED'),day?dateSerial(day):'',Number(Boolean(day)&&day>=w.start_date&&day<=w.end_date),parsedAge,Number(['Y','YES'].includes(sdr.trim().toUpperCase()))];
   const included=Number([2,3,4,5,7].every(i=>flags[i]===1));
   const college=Number(included===1&&typeof parsedAge==='number'&&parsedAge>=18&&parsedAge<=24);
   running+=included;young+=college;return [...flags,included,college,running,young];
  });
 }
 function totals(flags){return [flags.reduce((n,r)=>n+r[10],0),...bands.map(([lo,hi])=>flags.filter(r=>r[10]===1&&typeof r[8]==='number'&&r[8]>=lo&&r[8]<=hi).length),flags.filter(r=>r[10]===1&&typeof r[8]==='number'&&r[8]>=18&&r[8]<=22).length,flags.filter(r=>r[10]===1&&r[9]===1).length];}
 async function workbook(template,datasets,context,JSZip,streaming){
  if(datasets.length!==3||datasets.map(d=>d.source.year).join(',')!=='2022,2024,2026')throw Error('The workbook requires all three source years');
  const flags=datasets.map(d=>evaluateRows(d,context)),counts=flags.map(totals);
  for(let j=0;j<datasets.length;j++){
   const year=datasets[j].source.year,w=context.summary.find(r=>r.year===year&&r.scope==='Campus site');
   const expected=[w.all_ages,...bands.map(([, ,label])=>context.demographics.filter(r=>r.year===year&&r.scope==='Campus site'&&r.dimension==='age_group'&&r.value===label).reduce((n,r)=>n+r.votes,0)),w.age_18_22,w.same_day_registration];
   if(counts[j].some((value,i)=>value!==expected[i]))throw Error('Original '+year+' record counts differ from the report; workbook export stopped');
  }
  const zip=await JSZip.loadAsync(template),last=datasets.reduce((n,d)=>n+d.rows.length,5),stats={};
  const parts=zip.file('xl/worksheets/sheet8.xml')?[1,5,6,7,8]:[1,2,3,4,5];
  for(let sheet=1;sheet<=5;sheet++){
   const filename=`xl/worksheets/sheet${parts[sheet-1]}.xml`;let text=await zip.file(filename).async('string');
   const p=(text.match(/<([\w]+:)?worksheet\b/)||[])[1]||'';
   const allRows=[...text.matchAll(new RegExp(`<${p}row\\b[^>]*\\br="(\\d+)"[\\s\\S]*?<\\/${p}row>`,'g'))];
   const head=allRows.filter(r=>Number(r[1])<6).map(r=>r[0]).join('');
   const tail=allRows.filter(r=>Number(r[1])>13&&sheet>=4).map(r=>r[0]).join('');
   const styles={};for(const match of text.matchAll(new RegExp(`<${p}c\\b([^>]*\\br="([A-Z]+)6"[^>]*)>`,'g')))styles[match[2]]=(match[1].match(/\bs="(\d+)"/)||[])[1]||'0';
   const cell=(ref,value,formula)=>{
    const col=ref.match(/^[A-Z]+/)[0],style=styles[col]||'0',f=formula?`<${p}f>${xml(formula.replace(/^=/,''))}</${p}f>`:'';
    if(formula)return `<${p}c r="${ref}" s="${style}"${typeof value==='number'?'':' t="str"'}>${f}<${p}v>${xml(value)}</${p}v></${p}c>`;
    if(typeof value==='number')return `<${p}c r="${ref}" s="${style}"><${p}v>${value}</${p}v></${p}c>`;
    return `<${p}c r="${ref}" s="${style}" t="inlineStr"><${p}is><${p}t xml:space="preserve">${xml(value)}</${p}t></${p}is></${p}c>`;
   };
   const row=(r,values,formulas=[])=>`<${p}row r="${r}" ht="22" customHeight="1">${values.map((v,i)=>cell(String.fromCharCode(65+i)+r,v,formulas[i])).join('')}</${p}row>`;
   let body='';
   if(sheet===1){
    body=datasets.map((d,i)=>{const w=context.summary.find(r=>r.year===d.source.year&&r.scope==='Campus site');return row(i+6,[d.source.year,d.source.member,'Open untouched CSV',context.site_mapping[d.source.year],dateSerial(w.start_date),dateSerial(w.end_date),d.total,d.rows.length,'Official NCSBE archive',d.source.wake_csv_sha256,'Open full Excel copy'],[null,null,`=HYPERLINK("../01 Original files/${d.source.year}/${d.source.member}","Open untouched CSV")`,null,null,null,null,null,`=HYPERLINK("${d.source.url}","Official NCSBE archive")`,null,`=HYPERLINK("#'Copy ${d.source.year}'!A1","Open full Excel copy")`]);}).join('');
   }else if(sheet===2||sheet===3){
    let r=6;const bodyParts=[head];for(let j=0;j<datasets.length;j++)for(let i=0;i<datasets[j].rows.length;i++,r++){
     const d=datasets[j],values=d.rows[i],sourceFormulas=d.headers?[null,null,...fields.map(field=>sourceFormula(d.source.year,column(d.headers.indexOf(field)),values[1]))]:[];
     bodyParts.push(sheet===2?row(r,values,sourceFormulas):row(r,flags[j][i],flagFormulas(r)));
    }body=bodyParts.join('');
   }else if(sheet===4){
    const labels=['All site ballots',...bands.map(b=>b[2]),'18–22 (overlaps 18–24)','Same-day registration (all ages)'];
    body=labels.map((label,i)=>row(i+6,[label,i>=1&&i<=5?bands[i-1][0]:i===6?18:'',i>=1&&i<=5?bands[i-1][1]:i===6?22:'',...counts.map(c=>c[i])],[null,null,null,...countFormulas(i+6,last)])).join('');
   }else{
    const labels=['All site ballots',...bands.map(b=>b[2]),'18–22 (overlaps 18–24)','Same-day registration (all ages)'];
    body=labels.map((label,i)=>{const [a,b,c]=counts.map(v=>v[i]);return row(i+6,[label,a,a/counts[0][0],b,b/counts[1][0],c,c/counts[2][0],c-a,a?(c-a)/a:'',(c/counts[2][0]-a/counts[0][0])*100],mathFormulas(i+6));}).join('');
   }
   const first=sheet===2||sheet===3?'':head;
   text=text.replace(new RegExp(`<${p}sheetData[^>]*>[\\s\\S]*?<\\/${p}sheetData>`),()=>`<${p}sheetData>${first}${body}${tail}</${p}sheetData>`);
   const end=sheet===1?8:sheet<=3?last:19,col=sheet===1?'K':sheet===2?'I':sheet===3?'N':sheet===4?'F':'J';
   text=text.replace(new RegExp(`<${p}dimension\\b[^>]*/>`),`<${p}dimension ref="A1:${col}${end}"/>`);
   if(sheet===2||sheet===3){
    text=text.replace(/sqref="([A-Z]+)6:([A-Z]+)13"/g,(_,a,b)=>`sqref="${a}6:${b}${last}"`);
    if(!text.includes(`<${p}autoFilter`))text=text.replace(`</${p}sheetData>`,`</${p}sheetData><${p}autoFilter ref="A5:${col}${last}"/>`);
   }
   zip.file(filename,text);stats[names[sheet-1]]={dataRows:sheet<=3?sheet===1?3:last-5:8};
  }
  const county=await root.CsvCountyExcel.append(zip,datasets,context,root.CsvExcel);
  let workbookXml=await zip.file('xl/workbook.xml').async('string');
  const p=(workbookXml.match(/<([\w]+:)?workbook\b/)||[])[1]||'';
  const calc=`<${p}calcPr calcId="0" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>`;
  if(new RegExp(`<${p}calcPr\\b`).test(workbookXml))workbookXml=workbookXml.replace(new RegExp(`<${p}calcPr\\b[^>]*(?:/>|>[\\s\\S]*?<\\/${p}calcPr>)`),calc);
  else workbookXml=workbookXml.replace(`</${p}workbook>`,calc+`</${p}workbook>`);
  zip.file('xl/workbook.xml',workbookXml);
  if(streaming){
   const archive=new streaming.Stream.Archive(),raw=new Map(datasets.map(d=>[d.rawEntry.name,d.rawEntry]));
   for(const filename of Object.keys(zip.files)){
    if(zip.files[filename].dir)continue;
    if(raw.has(filename)){archive.add(raw.get(filename));continue;}
    const entry=streaming.Stream.packed(filename,streaming.Pako);entry.push(await zip.file(filename).async('uint8array'));archive.add(entry.finish());
   }
   return {bytes:archive.finish(),counts,stats,county};
  }
  return {bytes:await zip.generateAsync({type:'uint8array',compression:'DEFLATE',compressionOptions:{level:3}}),counts,stats,county};
 }
 root.CsvExcel={names,sheetNames,column,sourceFormula,fields,bands,flagFormulas,countFormulas,mathFormulas,evaluateRows,totals,workbook,dateSerial};
 if(typeof module!=='undefined')module.exports=root.CsvExcel;
})(globalThis);
