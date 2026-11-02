"""Independent decimal audit of paired means against the published per-building CSV."""
import csv,json
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
with (OUT/'distances-all-40.csv').open(encoding='utf-8',newline='') as f:raw=list(csv.DictReader(f))
d=json.loads((OUT/'averages.json').read_text(encoding='utf-8'))
with localcontext() as ctx:
 ctx.prec=40
 for row in d['rows']:
  candidates=[r for r in raw if row['group']=='All housing' or r['group']==row['group']]
  paired=[r for r in candidates if r['talley_m'] and r['western_m']]
  assert len(candidates)==row['total_buildings'] and len(paired)==row['included_buildings']
  assert len(candidates)-len(paired)==row['excluded_buildings']
  old=sum(Decimal(r['talley_m']) for r in paired);new=sum(Decimal(r['western_m']) for r in paired);count=Decimal(len(paired))
  for key,v in [('sum_talley_m',old),('sum_western_m',new),('mean_talley_m',old/count),('mean_western_m',new/count),('mean_change_m',(new-old)/count)]:assert abs(Decimal(str(row[key]))-v)<Decimal('0.000000001'),(row['group'],key)
  assert row['farther_buildings']+row['closer_buildings']+row['unchanged_buildings']==len(paired)
all_rows=d['rows'];assert [(r['included_buildings'],r['total_buildings']) for r in all_rows]==[(40,40),(26,26),(8,8),(6,6)]
assert all_rows[0]['estimated_access_buildings']==3 and all_rows[0]['recovered_entrance_buildings']==1
assert all_rows[1]['estimated_access_buildings']==3 and all_rows[1]['recovered_entrance_buildings']==1
assert all_rows[2]['mean_change_m']<0 and all_rows[3]['mean_change_m']<0
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));assert s['queries']['campus_walk_averages']['rows']==all_rows
print('PASS: all four paired means reconcile independently to complete per-building CSV sums; equal building weights, same denominators and 40-building coverage and estimated-access counts verified.')
