/* Populate the Artifact Tool template from exact source bytes, locally. */
(function(root){
 'use strict';
 const P=root.ArticleExcelPlan;
 const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 function layout(text){
  const p=(text.match(/<([\w]+:)?worksheet\b/)||[])[1]||'';
  const rows=[...text.matchAll(new RegExp(`<${p}row\\b[^>]*\\br="(\\d+)"[\\s\\S]*?<\\/${p}row>`,'g'))];
  const cache=new Map(),styles=r=>{if(!cache.has(r))cache.set(r,Object.fromEntries([...((rows.find(v=>Number(v[1])===r)||[])[0]||'').matchAll(new RegExp(`<${p}c\\b([^>]*\\br="([A-Z]+)\\d+"[^>]*)>`,'g'))].map(m=>[m[2],(m[1].match(/\bs="(\d+)"/)||[])[1]||'0'])));return cache.get(r);};
  return {p,rows,styles};
 }
 function rowXml(info,r,values,formulas=[],styleRow=6){
  const {p}=info,styles=info.styles(styleRow);
  return `<${p}row r="${r}" ht="23" customHeight="1">`+values.map((v,i)=>{
   const c=root.CsvZipStream.col(i),ref=c+r,s=styles[c]||'0',f=formulas[i];
   if(f)return `<${p}c r="${ref}" s="${s}"${typeof v==='number'?'':' t="str"'}><${p}f>${esc(f.slice(1))}</${p}f><${p}v>${esc(v)}</${p}v></${p}c>`;
   return typeof v==='number'?`<${p}c r="${ref}" s="${s}"><${p}v>${v}</${p}v></${p}c>`:`<${p}c r="${ref}" s="${s}" t="inlineStr"><${p}is><${p}t xml:space="preserve">${root.CsvZipStream.cellText(v)}</${p}t></${p}is></${p}c>`;
  }).join('')+`</${p}row>`;
 }
 function streamSheet(name,text,total,columns,raw,Stream,Pako){
  const info=layout(text),{p}=info,start=new RegExp(`<${p}sheetData[^>]*>`).exec(text);
  let before=text.slice(0,start.index+start[0].length).replace(new RegExp(`<${p}dimension\\b[^>]*/>`),`<${p}dimension ref="A1:${Stream.col(columns-1)}${total+(raw?1:5)}"/>`);
  const end=total+(raw?1:5),first=raw?2:6,hasTotals=!raw&&columns===12;
  if(hasTotals)before=before.replace(`ref="A1:L${end}"`,`ref="A1:L${end+1}"`);
  let after=text.slice(text.indexOf(`</${p}sheetData>`)).replace(/sqref="([A-Z]+)6:([A-Z]+)\d+"/g,(_,a,b)=>`sqref="${a}6:${b}${end}"`);
  after=after.replace(new RegExp(`<${p}autoFilter\\b[^>]*/>`,'g'),'');
  after=after.replace(`</${p}sheetData>`,`</${p}sheetData><${p}autoFilter ref="A${raw?1:5}:${Stream.col(columns-1)}${end}"/>`);
  const entry=Stream.packed(name,Pako);entry.push(before+info.rows.filter(v=>Number(v[1])<first).map(v=>v[0]).join(''));
  let buffer='',r=first;
  return {row(values,formulas){buffer+=rowXml(info,r++,values,formulas,raw?2:6);if(buffer.length>262144){entry.push(buffer);buffer='';}},finish(totals){if(r!==end+1)throw Error('Incomplete worksheet '+name);if(hasTotals){if(!totals)throw Error('Missing rule totals');const style=Number(info.rows.find(v=>v[0].includes('Total of 1s'))?.[1]||6);buffer+=rowXml(info,r,['TOTAL','','','','','','','Total of 1s',...totals,'',''],[null,null,null,null,null,null,null,null,`=SUM(I6:I${end})`,`=SUM(J6:J${end})`],style);}entry.push(buffer+after);return entry.finish();}};
 }
 async function build(templateBytes,sources,context,expected,readSource,progress,JSZip,Stream,Pako,options={}){
  if(sources.map(s=>s.year).join(',')!=='2022,2026')throw Error('The article audit requires 2022 and 2026 sources');
  const updated=options.mode==='updated',generatedAt=new Date().toISOString();
  const originals=[];
  for(const source of sources){
   progress(updated?`Reading and hashing the ${source.year} CSV for a fresh calculation…`:`Checking the ${source.year} original CSV against the article snapshot…`);
   const bytes=await readSource(source);
   const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
   if(!updated&&hash!==source.wake_csv_sha256){
    const error=Error(`NCSBE has updated the ${source.year} file. Choose the saved original CSVs below to reproduce this article's snapshot.`);
    error.code='SOURCE_SNAPSHOT_CHANGED';throw error;
   }
   originals.push({bytes,source:updated?{...source,article_snapshot:{...source},sha256:null,wake_csv_sha256:hash,last_modified:null,downloaded_at:null,retrieved_at_utc:generatedAt,input_kind:options.inputKind||'selected_csv',input_filename:options.filenames?.[source.year]||source.member,matches_article_snapshot:hash===source.wake_csv_sha256}:source});
  }
  const template=await JSZip.loadAsync(templateBytes),book=new Stream.Archive(),bundle=new Stream.Archive(),replaced=new Map(),datasets=[];
  for(let j=0;j<sources.length;j++){
   const {source,bytes}=originals[j],year=source.year;
   const original=Stream.packed(`01 Original files/${year}/${source.member}`,Pako);original.push(bytes);bundle.add(original.finish());
   const text=new TextDecoder('windows-1252').decode(bytes),bounds=root.CsvOriginalCopy.indexRecords(text),at=i=>text.slice(bounds[2*i],bounds[2*i+1]);
   const headers=root.CsvOriginalCopy.cells(at(0)),total=bounds.length/2-1,columns=P.fields.map(f=>headers.indexOf(f));if(columns.some(i=>i<0))throw Error('Official CSV fields changed');
   const window=context.summary.find(r=>r.year===year&&r.scope==='Campus site'),meta={...window,site:context.site_mapping[year]},counts=P.bands.map(()=>({site:0,county:0}));
   const paths=[3+j,5+j,7+j].map(n=>`xl/worksheets/sheet${n}.xml`),templates=await Promise.all(paths.map(p=>template.file(p).async('string')));
   const writers=[streamSheet(paths[0],templates[0],total,headers.length,true,Stream,Pako),streamSheet(paths[1],templates[1],total,7,false,Stream,Pako),streamSheet(paths[2],templates[2],total,12,false,Stream,Pako)];
   const run=[0,0];
   for(let i=1;i<=total;i++){
    const values=root.CsvOriginalCopy.cells(at(i));if(values.length!==headers.length)throw Error('CSV field count changed at record '+(i+1));
    writers[0].row(values);
    const fields=[i+1,...columns.map(c=>values[c])],r=i+5;
    writers[1].row(fields,[null,...columns.map(c=>{const ref=`'Copy ${year}'!${Stream.col(c)}${i+1}`;return `=IF(${ref}="","",${ref})`})]);
    const rules=P.evaluate(fields,meta,run);writers[2].row(rules,P.rules(year,r));
    for(let b=0;b<P.bands.length;b++){const [lo,hi]=P.bands[b];if(typeof rules[6]==='number'&&rules[6]>=lo&&rules[6]<=hi){counts[b].county+=rules[8];counts[b].site+=rules[9];}}
    if(i%20000===0)progress(`Copying ${year} originals and writing linked fields, rule formulas and highlights: ${i.toLocaleString()} / ${total.toLocaleString()}`);
   }
   for(const writer of writers){const entry=writer.finish(run);replaced.set(entry.name,entry);}
   if(!updated)for(let b=0;b<5;b++)for(const scope of ['site','county'])if(counts[b][scope]!==expected[b][`${scope}_ballots_${year}`])throw Error(`Original ${year} ${P.bands[b][2]} ${scope} count differs from the article`);
   datasets.push({source,total,headers,meta,counts});
   originals[j]=null;
  }
  const results=P.bands.map(([lo,hi,cohort],b)=>{
   const a=datasets[0].counts[b],z=datasets[1].counts[b];
   if(a.site<=0||a.county<=0||z.county<=0)throw Error(`The ${cohort} baseline or county count is zero. Check that both files are the Wake County CSVs for the correct elections.`);
   const siteGrowth=(z.site-a.site)/a.site*100,countyGrowth=(z.county-a.county)/a.county*100;
   return {cohort,site_ballots_2022:a.site,site_ballots_2026:z.site,county_ballots_2022:a.county,county_ballots_2026:z.county,site_growth_pct:siteGrowth,county_growth_pct:countyGrowth,site_growth_gap_pp:siteGrowth-countyGrowth};
  });
  function fill(text,body,end,col,keepTail=false){const {p,rows}=layout(text);return text.replace(new RegExp(`<${p}sheetData[^>]*>[\\s\\S]*?<\\/${p}sheetData>`),`<${p}sheetData>${rows.filter(v=>Number(v[1])<6).map(v=>v[0]).join('')}${body}${keepTail?rows.filter(v=>Number(v[1])>10).map(v=>v[0]).join(''):''}</${p}sheetData>`).replace(new RegExp(`<${p}dimension\\b[^>]*/>`),`<${p}dimension ref="A1:${col}${end}"/>`);}
  for(const index of [1,2,9,10]){
   const path=`xl/worksheets/sheet${index}.xml`,text=await template.file(path).async('string'),info=layout(text);let body='';
   if(index===2){body=datasets.map((d,i)=>rowXml(info,i+6,[d.source.year,d.source.member,'Open untouched CSV',d.meta.site,P.serial(d.meta.start_date),P.serial(d.meta.end_date),d.total,d.source.wake_csv_sha256,'Official NCSBE archive'],[null,null,`=HYPERLINK("../01 Original files/${d.source.year}/${d.source.member}","Open untouched CSV")`,null,null,null,null,null,`=HYPERLINK("${d.source.url}","Official NCSBE archive")`])).join('');}
   else for(let b=0;b<5;b++){
    const r=b+6,[lo,hi,label]=P.bands[b],a=datasets[0].counts[b],z=datasets[1].counts[b],site=(z.site-a.site)/a.site*100,county=(z.county-a.county)/a.county*100;
    if(index===1)body+=rowXml(info,r,[label,site,county,site-county],[null,`='4 Growth math'!F${r}`,`='4 Growth math'!K${r}`,`='4 Growth math'!L${r}`]);
    if(index===9)body+=rowXml(info,r,[label,a.site,z.site,a.county,z.county,lo,hi],[null,P.countFormula(2022,'site',r,datasets[0].total+5),P.countFormula(2026,'site',r,datasets[1].total+5),P.countFormula(2022,'county',r,datasets[0].total+5),P.countFormula(2026,'county',r,datasets[1].total+5)]);
    if(index===10)body+=rowXml(info,r,[label,a.site,z.site,z.site-a.site,site/100,site,a.county,z.county,z.county-a.county,county/100,county,site-county],P.math(r));
   }
   if(index===10){
    const a=datasets[0].counts[0],z=datasets[1].counts[0];
    body+=info.rows.filter(v=>[13,14].includes(Number(v[1]))).map(v=>v[0]).join('');
    body+=rowXml(info,15,['2022 Talley',a.site,a.county,a.site/a.county],[null,'=B6','=G6','=B15/C15'],15);
    body+=rowXml(info,16,['2026 Western Boulevard',z.site,z.county,z.site/z.county],[null,'=C6','=H6','=B16/C16'],16);
    body+=rowXml(info,17,['Change (percentage points)','','',(z.site/z.county-a.site/a.county)*100],[null,null,null,'=(D16-D15)*100'],17);
   }
   let sheet=fill(text,body,index===1?18:index===2?7:index===10?17:10,index===1?'H':index===2?'I':index===9?'G':'L',index===1);
   if(updated&&[1,2].includes(index))sheet=sheet.replace((info.rows.find(v=>Number(v[1])===3)||[])[0]||'<unused>',rowXml(info,3,[`UPDATED FILES · calculated ${generatedAt} · same full 17-day periods; may differ from the saved article.`],[],3));
   const entry=Stream.packed(path,Pako);entry.push(sheet);replaced.set(path,entry.finish());
  }
  for(const path of Object.keys(template.files)){
   if(template.files[path].dir)continue;if(replaced.has(path)){book.add(replaced.get(path));continue;}
   let bytes=await template.file(path).async('uint8array');
   if(path==='xl/workbook.xml'){
    let text=new TextDecoder().decode(bytes);const prefix=(text.match(/<([\w]+:)?workbook\b/)||[])[1]||'';
    const calc=`<${prefix}calcPr calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>`;
    text=/<([\w]+:)?calcPr\b/.test(text)?text.replace(/<([\w]+:)?calcPr\b[^>]*\/>/,calc):text.replace(`</${prefix}workbook>`,calc+`</${prefix}workbook>`);
    bytes=new TextEncoder().encode(text);
   }
   const entry=Stream.packed(path,Pako);entry.push(bytes);book.add(entry.finish());
  }
  progress(updated?'Fresh counts and calculations complete. Packing source CSVs and the formula-linked workbook…':'All 20 site/county counts match. Packing originals and the formula-linked Excel workbook…');
  bundle.store('02 Working copy/talley-western-growth-step-by-step.xlsx',book.finish());
  const manifest={mode:updated?'updated':'snapshot',generated_at_utc:generatedAt,as_of:context.as_of,matched_days:context.matched_days,years:P.years,age_groups:results.map(r=>r.cohort),sources:datasets.map(d=>({...d.source,original_records:d.total,original_columns:d.headers.length,excel_copy:'Copy '+d.source.year})),counts:datasets.map(d=>({year:d.source.year,counts:d.counts})),results,article_snapshot_results:expected,verified:updated?'Fresh counts computed from the included CSV bytes; SHA-256 recorded for each input. Results may differ from the saved article.':'Every original CSV hash and all 20 cohort/scope/year counts match the article snapshot'};
  bundle.text('03 Source checks/source-manifest.json',JSON.stringify(manifest,null,2),Pako);
  bundle.text('READ FIRST.txt',(updated?'UPDATED FILES: these calculations use the included CSV bytes and may differ from the saved article. See UPDATED RESULTS.txt.\r\n\r\n':'')+'Extract the entire ZIP, keeping its folders, before opening Excel.\r\n\r\n01 Original files: exact untouched government CSV bytes for 2022 and 2026.\r\n02 Working copy: Excel with Growth gaps, 0 Sources, Copy 2022, Copy 2026, 1 Fields 2022/2026, 2 Rules 2022/2026, 3 Counts and 4 Growth math.\r\n03 Source checks: hashes, source URLs, original record counts and calculated counts.\r\n\r\nEach Copy tab preserves every original row and column as text. Blue source headers identify the six fields used. Fields tabs use actual formulas pointing to those copied cells, retaining every record. Rules tabs parse dates/ages and test county, early-voting type, acceptance, matched dates and exact location. Light-blue county contributions and darker-blue named-site contributions add 1 or 0. Running SUMs show accumulation. The TOTAL row below every original record uses simple SUM formulas over the county and site contribution columns. Counts uses COUNTIFS for all five nonoverlapping age bands. Growth math links the counts and shows subtraction, division, multiplication by 100, and the site-minus-Wake percentage-point gap in separate actual Excel formula cells. Growth gaps links those finished results.\r\n\r\nEditing a copied source value recalculates every affected step in Excel, without changing the separate original CSV. All source records are included, including rejected and outside-window records; no candidate extract membership is frozen. Adding new CSV records requires rebuilding the package or extending the formula ranges.\r\n\r\nThe comparison uses the full 17-day early-voting periods: October 20–November 5, 2022 at Talley, and October 15–31, 2026 at Western Boulevard. 2026 is preliminary. Wake includes the named sites. Ages are not verified student enrollment; counts are not turnout rates or proof that relocation caused a change.\r\n\r\nThis is a large workbook. Opening and recalculating all source-linked formulas may take several minutes in desktop Excel. The original files and workbook are assembled locally; no voter records are uploaded to the website.\r\n',Pako);
  if(updated){
   const columns=Object.keys(results[0]);bundle.text('03 Source checks/updated-calculations.csv',[columns.join(','),...results.map(r=>columns.map(c=>r[c]).join(','))].join('\r\n')+'\r\n',Pako);
   bundle.text('UPDATED RESULTS.txt',`These results were recalculated from the included files at ${generatedAt}. They may differ from the article's saved snapshot. The article itself has not been refreshed.\r\n\r\nThe voting windows are still October 20–November 5, 2022 and October 15–31, 2026 (full 17-day early-voting periods in each year). Later voting dates are excluded even if present in updated files. See 0 Sources for dates and CSV hashes, and source-manifest.json for input provenance and the old/new calculations.\r\n`,Pako);
  }
  return {bytes:bundle.finish(),manifest};
 }
 root.ArticleExcelExport={build};if(typeof module!=='undefined')module.exports=root.ArticleExcelExport;
})(globalThis);
