"""Independent audit of all observed Google pairs and rounded-input means."""
import csv,json,math
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs,urlparse
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));raw=json.loads((ROOT/'data/sources/google-maps/2026-11-01/browser-observations.json').read_text(encoding='utf-8'))['rows'];checks=json.loads((ROOT/'data/sources/google-maps/2026-11-01/walking-checks.json').read_text(encoding='utf-8'))['rows']
supp={r['id']:r for r in s['queries']['campus_estimated_access']['rows']};model={r['id']:r if r['available'] else supp[r['id']] for r in s['queries']['campus_walking_routes']['rows']};sites={r['id']:r for r in s['queries']['campus_walk_sites']['rows']}
assert len(checks)==len(raw)==80
assert {(r['building_id'],r['site']) for r in checks}=={(code,site) for code in model for site in ['talley','western']}
for r in checks:
 row=model[r['building_id']];origin=row.get('entrance_coordinates') or row['access_coordinates'];dest=sites['102' if r['site']=='talley' else '131']['coordinates'];q=parse_qs(urlparse(r['google_walking_url']).query)
 assert q['api']==['1'] and q['travelmode']==['walking'] and r['walking_mode_selected']
 assert list(map(float,q['origin'][0].split(',')))==origin[::-1] and list(map(float,q['destination'][0].split(',')))==dest[::-1]
 assert r['origin_coordinates_lon_lat']==origin and r['destination_coordinates_lon_lat']==dest
 assert math.isclose(r['gis_route_miles'],row[r['site']+'_m']/1609.344,abs_tol=1e-12)
 original=next(o for o in raw if o['building_id']==r['building_id'] and o['site']==r['site'])
 assert r['google_display_miles']==original['google_display_miles'] and r['google_display_minutes']==original['google_display_minutes']
 assert round(r['google_display_miles'],1)==r['google_display_miles'] and r['entrance_verified'] is False and r['observed_on']=='2026-11-01'
for a in s['queries']['campus_google_averages']['rows']:
 selected=[r for r in raw if a['group']=='All housing' or model[r['building_id']]['group']==a['group']];n=len(selected)//2
 assert a['included_buildings']==a['total_buildings']==n and a['excluded_buildings']==0
 for unit in ['miles','minutes']:
  sums={site:sum(Decimal(str(r['google_display_'+unit])) for r in selected if r['site']==site) for site in ['talley','western']}
  for site in sums:assert abs(Decimal(str(a['mean_'+site+'_'+unit]))-sums[site]/n)<Decimal('0.000000001')
  assert abs(Decimal(str(a['mean_change_'+unit]))-(sums['western']-sums['talley'])/n)<Decimal('0.000000001')
 assert a['farther_buildings']+a['closer_buildings']+a['unchanged_buildings']==n
assert len(list(csv.DictReader((OUT/'google-walking-comparison.csv').open(encoding='utf-8'))))==80
assert len(s['queries']['campus_google_walks']['rows'])==40
assert [(r['included_buildings'],r['total_buildings']) for r in s['queries']['campus_walk_averages']['rows']]==[(40,40),(26,26),(8,8),(6,6)]
assert sum(r['available'] for r in s['queries']['campus_walking_routes']['rows'])==36 and len(s['queries']['campus_passby']['rows'])==792
print('PASS: all 80 observed Google routes, walking mode, exact pin order and miles/minutes reconcile; independent Decimal means cover all 40 buildings; GIS prototype and routine inputs remain separate.')
