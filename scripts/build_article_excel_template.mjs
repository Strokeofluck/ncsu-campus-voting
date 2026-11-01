import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const dependencies=process.env.CODEX_NODE_DEPENDENCIES||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node');
const require=createRequire(pathToFileURL(path.join(dependencies,'runtime.cjs')));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
import Plan from '../article-excel-plan.js';
const root=path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const out=process.argv[2];if(!out)throw Error('Pass an absolute scratch output directory');await fs.mkdir(out,{recursive:true});
const headers=JSON.parse(await fs.readFile(root+'/report-source/article-excel-headers.json','utf8'));
const sources=JSON.parse(await fs.readFile(root+'/data/processed/comparison/figure_sources.json','utf8')).records;
const context=JSON.parse(await fs.readFile(root+'/data/processed/comparison/comparison.json','utf8'));
const wb=Workbook.create();for(const name of Plan.names)wb.worksheets.add(name);
const sheet=name=>wb.worksheets.getItem(name),set=(s,r,v)=>s.getRange(r).values=v;
function setup(s,title,cols){
 s.showGridLines=false;s.getRange(`A1:${cols}24`).format.font={name:'Arial',size:10,color:'#202B35'};
 s.getRange(`A1:${cols}24`).format.verticalAlignment='center';s.getRange(`A1:${cols}24`).format.rowHeight=23;
 s.getRange(`A:${cols}`).format.columnWidth=20;set(s,'A2',[[title]]);s.getRange('A2').format.font={name:'Arial',size:15,bold:true};
}
function head(s,labels){set(s,`A5:${String.fromCharCode(64+labels.length)}5`,[labels]);s.getRange(`A5:${String.fromCharCode(64+labels.length)}5`).format={fill:'#273D52',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42,horizontalAlignment:'center',verticalAlignment:'center'};s.freezePanes.freezeRows(5);}
const result=sheet('Growth gaps');setup(result,'Talley to Western Boulevard: growth gaps','H');head(result,['Age group','Talley to Western growth (%)','Wake growth (%)','Gap (percentage points)']);
result.getRange('A:D').format.columnWidth=25;result.tabColor='#273D52';
set(result,'A3',[['Matched first 16 early-voting days. 2022 at Talley; 2026 at Western Boulevard.']]);
for(let i=0;i<5;i++){let r=i+6;set(result,`A${r}`,[[Plan.bands[i][2]]]);result.getRange(`B${r}:D${r}`).formulas=[[`='4 Growth math'!F${r}`,`='4 Growth math'!K${r}`,`='4 Growth math'!L${r}`]];}
result.getRange('B6:D10').setNumberFormat('0.0');result.getRange('D6:D10').conditionalFormats.addCustom('D6<0',{fill:'#FFE3C7'});result.getRange('D6:D10').conditionalFormats.addCustom('D6>0',{fill:'#D8EAF4'});
set(result,'A13',[['Read tabs left to right: original files, full copies, selected fields, rule flags, counts, then growth math.']]);
set(result,'A15',[['2026 is preliminary through October 30. Age is not verified student status.']]);
set(result,'A16',[['Wake includes Talley / Western Boulevard. These are ballot counts, not turnout rates.']]);
set(result,'A18',[['Editing any copied record updates its field links, flags, counts and growth formulas in Excel.']]);
const meta=sheet('0 Sources');setup(meta,'Original CSVs and matched windows','I');head(meta,['Year','CSV member','Open untouched CSV','Exact location','First date','Last date','Records','Original CSV SHA-256','Official archive']);
meta.getRange('B:D').format.columnWidth=36;meta.getRange('H:H').format.columnWidth=70;meta.getRange('I:I').format.columnWidth=25;
const datasets=[];
for(const [j,year] of Plan.years.entries()){
 const window=context.summary.find(r=>r.year===year&&r.scope==='Campus site'),source=sources[`summary-${year}-campus-site-all-ages`].sources[0];
 const raw=[];
 for(const [lo]of Plan.bands)for(let k=0;k<(year===2022?2:4);k++){const v=headers.map(()=> '');for(const [key,val]of Object.entries({county_desc:'WAKE',ballot_req_type:'ONE-STOP',ballot_rtn_status:'ACCEPTED',ballot_rtn_dt:year===2022?'10/20/2022':'10/15/2026',site_name:k%2===0?context.site_mapping[year]:'ANOTHER WAKE SITE',age:String(lo)}))v[headers.indexOf(key)]=val;raw.push(v);}
 const excluded=[...raw[0]];excluded[headers.indexOf('ballot_rtn_status')]='REJECTED';raw.push(excluded);
 const late=[...raw[0]];late[headers.indexOf('ballot_rtn_dt')]=year===2022?'11/05/2022':'10/31/2026';raw.push(late);
 const m={...window,site:context.site_mapping[year]};datasets.push({year,raw,meta:m});
 const r=j+6;set(meta,`A${r}:I${r}`,[[year,source.member,'Open untouched CSV',m.site,Plan.serial(m.start_date),Plan.serial(m.end_date),raw.length,source.wake_csv_sha256,'Official NCSBE archive']]);
 meta.getRange(`C${r}`).formulas=[[`=HYPERLINK("../01 Original files/${year}/${source.member}","Open untouched CSV")`]];
 meta.getRange(`I${r}`).formulas=[[`=HYPERLINK("${source.url}","Official NCSBE archive")`]];
 const copy=sheet('Copy '+year);copy.showGridLines=false;copy.getRange('A:AP').format.columnWidth=21;set(copy,'A1',[headers,...raw]);copy.getRange('A1:AP1').format={fill:'#273D52',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:46};copy.getRange(`A2:AP${raw.length+1}`).setNumberFormat('@');copy.freezePanes.freezeRows(1);
 for(const f of Plan.fields){const c=String.fromCharCode(65+headers.indexOf(f)%26);const index=headers.indexOf(f),col=index<26?c:'A'+c;copy.getRange(`${col}1`).format={fill:'#FFE9A8',font:{name:'Arial',size:10,bold:true,color:'#202B35'}};}
 const field=sheet('1 Fields '+year);setup(field,'Step 1: link the six source fields','G');head(field,['Original CSV record',...Plan.fields]);field.getRange('F:F').format.columnWidth=47;field.getRange('B:G').format.columnWidth=24;field.getRange('F:F').format.columnWidth=47;set(field,'A3',[['All original records remain in order. Yellow headers identify the six fields used.']]);field.getRange('B5:G5').format={fill:'#FFE9A8',font:{name:'Arial',size:10,bold:true,color:'#202B35'}};
 const rules=sheet('2 Rules '+year);setup(rules,'Step 2: test each record','L');head(rules,['Original CSV record','WAKE? 1=yes','Early type?','Accepted?','Parsed date','Matched dates?','Parsed age','Named location?','County adds 1','Named site adds 1','County running SUM','Site running SUM']);set(rules,'A3',[['Each test is an Excel formula. Green contributions count county ballots; amber marks Talley / Western ballots.']]);
 for(let i=0;i<raw.length;i++){const r=i+6,record=i+2;set(field,`A${r}`,[[record]]);field.getRange(`B${r}:G${r}`).formulas=[Plan.fields.map(f=>{let n=headers.indexOf(f)+1,c='';while(n){c=String.fromCharCode(65+(n-1)%26)+c;n=Math.floor((n-1)/26);}const ref=`'Copy ${year}'!${c}${record}`;return `=IF(${ref}="","",${ref})`;} )];rules.getRange(`A${r}:L${r}`).formulas=[Plan.rules(year,r)];}
 rules.getRange(`E6:E${raw.length+5}`).setNumberFormat('mm/dd/yyyy');rules.getRange(`I6:I${raw.length+5}`).conditionalFormats.addCustom('I6=1',{fill:'#DDEDDD'});rules.getRange(`J6:J${raw.length+5}`).conditionalFormats.addCustom('J6=1',{fill:'#FFE9A8'});
}
meta.getRange('E6:F7').setNumberFormat('mm/dd/yyyy');meta.getRange('A6:A7').setNumberFormat('0');
const counts=sheet('3 Counts');setup(counts,'Step 3: count each age group','G');head(counts,['Age group','Talley 2022','Western 2026','Wake 2022','Wake 2026','Age minimum','Age maximum']);set(counts,'A3',[['COUNTIFS reads each rule flag and numeric age. Bounds are inclusive.']]);
const math=sheet('4 Growth math');setup(math,'Step 4: calculate growth and the gap','L');head(math,['Age group','Talley 2022','Western 2026','Site increase','Site divide by 2022','Site multiply by 100','Wake 2022','Wake 2026','Wake increase','Wake divide by 2022','Wake multiply by 100','Growth gap (pp)']);set(math,'A3',[['Increase = 2026 minus 2022. Growth = increase / 2022 × 100. Gap = site growth minus Wake growth.']]);math.getRange('A:L').format.columnWidth=20;
for(let i=0;i<5;i++){
 const r=i+6,[lo,hi,label]=Plan.bands[i];set(counts,`A${r}:G${r}`,[[label,null,null,null,null,lo,hi]]);
 counts.getRange(`B${r}:E${r}`).formulas=[[Plan.countFormula(2022,'site',r,datasets[0].raw.length+5),Plan.countFormula(2026,'site',r,datasets[1].raw.length+5),Plan.countFormula(2022,'county',r,datasets[0].raw.length+5),Plan.countFormula(2026,'county',r,datasets[1].raw.length+5)]];
 set(math,`A${r}`,[[label]]);math.getRange(`B${r}:L${r}`).formulas=[Plan.math(r).slice(1)];
}
counts.getRange('B6:G10').setNumberFormat('#,##0');math.getRange('B6:D10').setNumberFormat('#,##0');math.getRange('G6:I10').setNumberFormat('#,##0');math.getRange('E6:E10').setNumberFormat('0.000000000');math.getRange('J6:J10').setNumberFormat('0.000000000');for(const col of ['F','K','L'])math.getRange(`${col}6:${col}10`).setNumberFormat('0.0');
set(math,'A13',[['Countywide share of early ballots from ages 18–24']]);set(math,'A14:D14',[['Year and location','Location ballots','All Wake ages 18–24','Location / Wake']]);
set(math,'A15',[['2022 Talley']]);set(math,'A16',[['2026 Western Boulevard']]);set(math,'A17',[['Change (percentage points)']]);
math.getRange('B15:D15').formulas=[["=B6","=G6","=B15/C15"]];math.getRange('B16:D16').formulas=[["=C6","=H6","=B16/C16"]];math.getRange('D17').formulas=[['=(D16-D15)*100']];
math.getRange('A14:D14').format={fill:'#273D52',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42};math.getRange('B15:C16').setNumberFormat('#,##0');math.getRange('D15:D16').setNumberFormat('0.0%');math.getRange('D17').setNumberFormat('0.0');math.getRange('A:A').format.columnWidth=31;
wb.recalculate();
let baseline=result.getRange('B6:D10').values;for(const row of baseline)if(Math.abs(row[0]-100)>1e-8||Math.abs(row[1]-100)>1e-8||Math.abs(row[2])>1e-8)throw Error('Fixture math failed '+JSON.stringify(baseline));
const copy=sheet('Copy 2022'),ageIndex=headers.indexOf('age');let ageCol='';for(let n=ageIndex+1;n;n=Math.floor((n-1)/26))ageCol=String.fromCharCode(65+(n-1)%26)+ageCol;
copy.getRange(ageCol+'2').values=[['25']];wb.recalculate();if(result.getRange('B6').values[0][0]===baseline[0][0])throw Error('Copied age edit did not update growth');copy.getRange(ageCol+'2').values=[['18']];wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Growth gaps!A5:D10',include:'values,formulas',tableMaxRows:6,tableMaxCols:4,maxChars:1500})).ndjson);
for(const name of Plan.names){const blob=await wb.render({sheetName:name,range:name.startsWith('Copy')?'A1:G5':name==='0 Sources'?'A2:G7':name.includes('Rules')?'A2:L10':name.includes('math')?'A2:L18':'A2:G11',scale:1,format:'png'});await fs.writeFile(out+'/excel-'+name.replaceAll(' ','-')+'.png',new Uint8Array(await blob.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(wb)).save(out+'/article-excel-template.xlsx');
const bytes=await fs.readFile(out+'/article-excel-template.xlsx');await fs.writeFile(root+'/article-excel-template.json',JSON.stringify({version:1,names:Plan.names,base64:bytes.toString('base64')}));
console.log('Created and recalculated ten-tab Excel template; copied-age edit propagates through counts and growth.');
