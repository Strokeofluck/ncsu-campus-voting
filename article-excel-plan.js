/* Shared Excel formulas and source rules for the article's two-year audit. */
(function(root){
 'use strict';
 const years=[2022,2026],fields=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age'];
 const names=['Growth gaps','0 Sources','Copy 2022','Copy 2026','1 Fields 2022','1 Fields 2026','2 Rules 2022','2 Rules 2026','3 Counts','4 Growth math'];
 const bands=[[18,24,'18–24'],[25,34,'25–34'],[35,44,'35–44'],[45,64,'45–64'],[65,120,'65+']];
 const serial=day=>(Date.parse(day+'T00:00:00Z')-Date.UTC(1899,11,30))/86400000;
 function rules(year,row){
  const s=c=>`'1 Fields ${year}'!${c}${row}`,meta=year===2022?6:7;
  return [`=${s('A')}`,`=IF(TRIM(${s('B')})="WAKE",1,0)`,
   `=IF(OR(UPPER(TRIM(${s('C')}))="ONE-STOP",UPPER(TRIM(${s('C')}))="ONE STOP",UPPER(TRIM(${s('C')}))="EARLY VOTING"),1,0)`,
   `=IF(TRIM(${s('D')})="ACCEPTED",1,0)`,
   `=IFERROR(DATE(VALUE(RIGHT(TRIM(${s('E')}),4)),VALUE(LEFT(TRIM(${s('E')}),2)),VALUE(MID(TRIM(${s('E')}),4,2))),"")`,
   `=IF(AND(ISNUMBER(E${row}),E${row}>='0 Sources'!E${meta},E${row}<='0 Sources'!F${meta}),1,0)`,
   `=IF(TRIM(${s('G')})="","",IFERROR(VALUE(TRIM(${s('G')})),""))`,
   `=IF(TRIM(${s('F')})='0 Sources'!D${meta},1,0)`,
   `=IF(AND(B${row}=1,C${row}=1,D${row}=1,F${row}=1),1,0)`,
   `=IF(AND(I${row}=1,H${row}=1),1,0)`,
   row===6?'=SUM(I6)':`=SUM(K${row-1},I${row})`,row===6?'=SUM(J6)':`=SUM(L${row-1},J${row})`];
 }
 function evaluate(values,meta,run){
  const [record,county,type,status,date,site,age]=values,clean=date.trim();
  const day=/^\d{2}\/\d{2}\/\d{4}$/.test(clean)?clean.slice(6)+'-'+clean.slice(0,2)+'-'+clean.slice(3,5):'';
  const numeric=/^\d+$/.test(age.trim())?Number(age.trim()):'';
  const wake=Number(county.trim()==='WAKE'),early=Number(['ONE-STOP','ONE STOP','EARLY VOTING'].includes(type.trim().toUpperCase())),accepted=Number(status.trim()==='ACCEPTED');
  const matched=Number(Boolean(day)&&day>=meta.start_date&&day<=meta.end_date),at=Number(site.trim()===meta.site);
  const included=wake*early*accepted*matched,siteIncluded=included*at;run[0]+=included;run[1]+=siteIncluded;
  return [record,wake,early,accepted,day?serial(day):'',matched,numeric,at,included,siteIncluded,...run];
 }
 function countFormula(year,scope,row,last){
  const range=c=>`'2 Rules ${year}'!$${c}$6:$${c}$${last}`;
  return `=COUNTIFS(${range(scope==='site'?'J':'I')},1,${range('G')},">="&$F${row},${range('G')},"<="&$G${row})`;
 }
 function math(row){return [null,`='3 Counts'!B${row}`,`='3 Counts'!C${row}`,`=C${row}-B${row}`,`=D${row}/B${row}`,`=E${row}*100`,
  `='3 Counts'!D${row}`,`='3 Counts'!E${row}`,`=H${row}-G${row}`,`=I${row}/G${row}`,`=J${row}*100`,`=F${row}-K${row}`];}
 root.ArticleExcelPlan={years,fields,names,bands,serial,rules,evaluate,countFormula,math};
 if(typeof module!=='undefined')module.exports=root.ArticleExcelPlan;
})(globalThis);
