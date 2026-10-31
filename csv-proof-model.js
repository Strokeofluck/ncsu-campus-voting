/* Shared calculation plan for the preview, worker tests and saved evidence. */
(function(root){
 'use strict';
 const selectionKey=s=>JSON.stringify(Object.fromEntries(Object.entries(s).sort(([a],[b])=>a.localeCompare(b))));
 function buildPlan(records,id){
  const steps=[],seen=new Set(),counts=new Map();
  function count(selection,label,expected){
   const key=selectionKey(selection);
   if(counts.has(key)){const old=counts.get(key);if(old.expected!==expected)throw Error('Conflicting source counts');return old.id;}
   const step={id:'count-'+counts.size,label:label.includes(String(selection.year))?label:`${selection.year} · ${selection.scope} · ${label}`,operation:'count',selection,key,expected,unit:'ballots'};
   counts.set(key,step);steps.push(step);return step.id;
  }
  function visit(key){
   if(seen.has(key))return key;
   const r=records[key];if(!r)throw Error('Missing figure input: '+key);seen.add(key);
   let refs,operation;
   if(r.unit==='ballots'){
    refs=[count(r.selections[0],r.label,r.value)];operation='identity';
   }else{
    refs=r.inputs.map(input=>input.target?visit(input.target):count(r.selections[0],input.label,input.value));
    operation=r.unit==='percentage points'?'difference':key.startsWith('growth-')?'growth':'share';
    if(refs.length!==2)throw Error('Unsupported calculation inputs');
   }
   steps.push({id:key,label:r.label,operation,refs,expected:r.value,unit:r.unit});return key;
  }
  visit(id);return {id,steps,counts:[...counts.values()]};
 }
 function calculate(plan,actual){
  const values={},out=[];
  for(const step of plan.steps){
   const refs=(step.refs||[]).map(id=>values[id]);let value;
   if(step.operation==='count')value=actual?actual[step.key]:step.expected;
   else if(step.operation==='identity')value=refs[0];
   else if(step.operation==='difference')value=refs[1]-refs[0];
   else if(step.operation==='growth')value=refs[0]?(refs[1]-refs[0])/refs[0]*100:NaN;
   else value=refs[1]?refs[0]/refs[1]*100:NaN;
   values[step.id]=value;out.push({...step,refsValues:refs,value,matches:Number.isFinite(value)&&Math.abs(value-step.expected)<1e-8});
  }
  return out;
 }
 root.CsvProof={buildPlan,calculate,selectionKey};
 if(typeof module!=='undefined')module.exports=root.CsvProof;
})(globalThis);
