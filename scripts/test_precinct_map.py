#!/usr/bin/env python3
"""Verify the exact official geometries, marker coordinates and count joins."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));bundle=json.loads((ROOT/'data/processed/comparison/precinct_map_sources.json').read_text(encoding='utf-8'))
shapes=s['queries']['precinct_shapes']['rows'];points=s['queries']['voting_site_points']['rows']
original={f['properties']['PRECINCT']:f for f in bundle['sources']['boundaries']['data']['features']}
assert len(shapes)==len(original)==216 and len(points)==2
for row in shapes:
 assert set(row)=={'area','code','geometry','created_date','last_edited_date'}
 assert row['area']=='PRECINCT '+row['code'] and row['geometry']==original[row['code']]['geometry']
 polygons=[row['geometry']['coordinates']] if row['geometry']['type']=='Polygon' else row['geometry']['coordinates']
 for polygon in polygons:
  for ring in polygon:
   assert len(ring)>=4 and ring[0]==ring[-1]
   for lon,lat in ring:assert math.isfinite(lon) and math.isfinite(lat) and -79.1<lon<-78.0 and 35.4<lat<36.2
by_building={f['attributes']['BLDG_NUM']:f['attributes'] for f in bundle['sources']['building_points']['data']['features']}
def in_ring(point,ring):
 x,y=point;inside=False
 for (ax,ay),(bx,by) in zip(ring,ring[1:]):
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
 return inside
def in_shape(point,geometry):
 polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates']
 return any(in_ring(point,p[0]) and not any(in_ring(point,h) for h in p[1:]) for p in polygons)
for point in points:
 original_point=by_building[point['building_number']]
 assert point['latitude']==original_point['LATITUDE'] and point['longitude']==original_point['LONGITUDE']
 assert point['years']==([2026] if point['id']=='western' else [2022,2024])
 assert any(in_shape([point['longitude'],point['latitude']],r['geometry']) for r in shapes)
areas={r['area'] for r in shapes};geo=s['queries']['geography']['rows']
assert 'PRECINCT 01-23' in areas and 'PRECINCT 01-07A' not in areas
for cohort in ['All ages','18–24','25–34','35–44','45–64','65+','Unknown / outside range']:
 all_rows=[r for r in geo if r['dimension']=='Precinct' and r['year']==2026 and r['cohort']==cohort and r['area_present']]
 mapped=[r for r in all_rows if r['area'] in areas];unmapped=[r for r in all_rows if r['area'] not in areas]
 assert all(r['area']=='Unknown / blank' for r in unmapped)
 for field in ['site_ballots','other_wake_ballots','wake_ballots']:assert sum(r[field] for r in all_rows)==sum(r[field] for r in mapped)+sum(r[field] for r in unmapped)
comparison=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
assert comparison==s['comparison'] and s['id']=='report:280801c5-2e0b-43cf-b10c-322b5c90a10e'
for key in ['summary','daily','demographics','sites']:assert s['queries'][key]['rows']==comparison[key]
print('Passed 216 exact official polygon geometries, two exact university pin coordinates, valid closed rings, count joins and disclosed unmapped totals. Existing comparison queries reconcile unchanged.')
