"""Audit coordinate order, units and scope of the separate browser observations."""
import csv,json,math
from pathlib import Path
from urllib.parse import parse_qs,urlparse
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
observed=json.loads((ROOT/'data/sources/google-maps/2026-11-01/walking-checks.json').read_text(encoding='utf-8'))
checks=observed['rows'];supp={r['id']:r for r in s['queries']['campus_estimated_access']['rows']};sites={r['id']:r for r in s['queries']['campus_walk_sites']['rows']}
assert len(checks)==8
assert {(r['building_id'],r['site']) for r in checks}=={(code,site) for code in ['271A','012','079','013'] for site in ['talley','western']}
for r in checks:
 q=parse_qs(urlparse(r['google_walking_url']).query);origin=supp[r['building_id']]['access_coordinates'];dest=sites['102' if r['site']=='talley' else '131']['coordinates']
 assert q['api']==['1'] and q['travelmode']==['walking']
 assert all(abs(a-b)<1e-12 for a,b in zip(map(float,q['origin'][0].split(',')),origin[::-1]))
 assert all(abs(a-b)<1e-12 for a,b in zip(map(float,q['destination'][0].split(',')),dest[::-1]))
 assert r['origin_coordinates_lon_lat']==origin and r['destination_coordinates_lon_lat']==dest
 assert math.isclose(r['gis_route_miles'],supp[r['building_id']][r['site']+'_m']/1609.344,abs_tol=1e-12)
 assert round(r['google_display_miles'],1)==r['google_display_miles'] and r['entrance_verified'] is False
 assert r['observed_on']=='2026-11-01'
csv_rows=list(csv.DictReader((ROOT/'data/processed/campus-walk/google-walking-comparison.csv').open(encoding='utf-8')))
assert len(csv_rows)==8 and [r['google_walking_url'] for r in csv_rows]==[r['google_walking_url'] for r in checks]
assert sum(r['available'] for r in s['queries']['campus_walking_routes']['rows'])==36
assert len(s['queries']['campus_passby']['rows'])==792
print('PASS: all eight Google observations use correct same-pin walking links, coordinate order and meter/mile conversion; rounded external values remain separate and unverified; original model denominators unchanged.')
