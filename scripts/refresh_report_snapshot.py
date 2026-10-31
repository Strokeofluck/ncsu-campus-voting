#!/usr/bin/env python3
"""Bind validated comparison aggregates to the existing report identity."""
import json,re
from datetime import datetime,timezone
from pathlib import Path
from build_registration_comparison import write_comparison
from build_comparison_metrics import write_metrics

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
write_comparison(data)
write_metrics(data)
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
        definition['definition']=re.sub(r'(?i)(first )\d+( early-voting days)',lambda m:f'{m[1]}{days}{m[2]}',definition['definition'])
    query['methods']=[{'language':'python','code':f'python scripts/build_early_voting_comparison.py --cutoff-date {cutoff}\npython scripts/validate_early_voting_comparison.py\npython scripts/audit_campus_figures.py\npython scripts/refresh_report_snapshot.py'}]
summary_source=snapshot['queries']['summary']['source']
summary_source['metricDefinitions']=[m for m in summary_source.get('metricDefinitions',[]) if m.get('label')!='Same-day registration versus ballot volume']+[
    {'label':'Same-day registration versus ballot volume',
     'definition':'All accepted campus-site early ballots, all ages, over the matched first '+str(days)+' days. Same-day registration counts records with sdr equal to Y or YES. Share = same-day-registration ballots / all site ballots * 100. Count change = (2026 count / selected baseline count - 1) * 100; share change = 2026 unrounded share - baseline unrounded share, in percentage points. Registration ballots are a subset of all ballots; do not add them. The measure does not identify students or count all new voter registrations. Source cohorts and counts are unchanged.',
     'componentIds':['voting-summary','voting-campus-exact-table','voting-registration-intro','voting-registration-growth','voting-registration-counts']}]
snapshot['queries']['summary']['methods'].append({'language':'python','code':'python scripts/build_registration_comparison.py\n# Exports exact counts, growth rates and shares for both historical baselines; share differences use unrounded inputs.'})
summary_source['metricDefinitions']=[m for m in summary_source['metricDefinitions'] if m.get('label')!='Distinct denominators and expanded comparisons']+[
    {'label':'Distinct denominators and expanded comparisons',
     'definition':'Site count = accepted ballots in the selected age group at the campus site. Site age mix = campus-site ballots ages 18–24 / all campus-site ballots * 100. Share of Wake college-age ballots = campus-site ballots ages 18–24 / all Wake ballots ages 18–24 * 100. None is turnout among registered or eligible residents. Expanded comparisons retain both baselines, all three disjoint-or-containing scopes, all-age and overlapping age/registration cohorts; count difference = current - baseline; growth = difference / baseline * 100. Shares use the explicit scope or same-cohort county denominator; differences are unrounded percentage points. Never add containing scopes or overlapping cohorts.',
     'componentIds':['voting-denominator-clarity','voting-expanded-counts','voting-expansion-plan']}]
snapshot['queries']['summary']['methods'].append({'language':'python','code':'python scripts/build_comparison_metrics.py\n# Exports 24 matched comparisons with counts, absolute and relative changes, scope shares, and county shares using explicit denominators.'})
# Built-in formats remain available; plugin destinations are resolved at build time.
snapshot['exportPreferences']={'selected':None,'destinations':snapshot.get('exportPreferences',{}).get('destinations',[])}
path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Report {snapshot["id"]}: {days} matched days through {cutoff}')
