#!/usr/bin/env python3
"""Bind validated comparison aggregates to the existing report identity."""
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
path=ROOT/'report-source/snapshot.json'
snapshot=json.loads(path.read_text(encoding='utf-8'))
days=data['matched_days']; cutoff=data['as_of']
campus={r['year']:r for r in data['summary'] if r['scope']=='Campus site'}
period='Matched first '+str(days)+' early-voting days: '+'; '.join(f"{r['start_date']} through {r['end_date']}" for r in campus.values())
snapshot.update(comparison=data,generatedAt=datetime.now(timezone.utc).isoformat(),buildStatus='updating')
snapshot['report']['asOf']=cutoff
for key,field in [('summary','summary'),('daily','daily'),('demographics','demographics'),('sites','sites')]:
    query=snapshot['queries'][key];query['rows']=data[field];source=query['source']
    source.update(label=f'NCSBE accepted Wake County early-voting records; matched first {days} days',period=period,
                  executedAt=data['sources'][-1]['retrieved_at_utc'])
    source['filters'][-1]=f'First {days} calendar days from each early-voting opening Thursday'
    source['caveats']=[f'2022/2024 finalized records versus 2026 live records through {cutoff}; historical daily reporting lags are not reconstructed.' if 'historical daily reporting lags' in c else c for c in source['caveats']]
    source['evidenceFlow']=[{'title':'Official source snapshots','detail':json.dumps(data['sources'])},
      {'title':'Matched-day aggregation','detail':f'scripts/build_early_voting_comparison.py --cutoff-date {cutoff}; exact site mapping; ACCEPTED early-voting records only. scripts/validate_early_voting_comparison.py reconciles days, scopes and demographics. scripts/audit_campus_figures.py independently recounts campus records and checks source archive/member hashes.'}]
    for definition in source.get('metricDefinitions',[]):
        definition['definition']=definition['definition'].replace('First 11 early-voting days',f'First {days} early-voting days')
    query['methods']=[{'language':'python','code':f'python scripts/build_early_voting_comparison.py --cutoff-date {cutoff}\npython scripts/validate_early_voting_comparison.py\npython scripts/audit_campus_figures.py\npython scripts/refresh_report_snapshot.py'}]
# Built-in formats remain available; plugin destinations are resolved at build time.
snapshot['exportPreferences']={'selected':None,'destinations':snapshot.get('exportPreferences',{}).get('destinations',[])}
path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Report {snapshot["id"]}: {days} matched days through {cutoff}')
