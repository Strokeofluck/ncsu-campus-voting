#!/usr/bin/env python3
"""Bind reviewed public precinct geometry and university site points to this report."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed/comparison'

def add_precinct_map(snapshot):
 bundle=json.loads((DATA/'precinct_map_sources.json').read_text(encoding='utf-8'));sources=bundle['sources']
 geometry=sources['boundaries']['data'];assert geometry['type']=='FeatureCollection'
 boundaries=[];seen=set()
 for feature in geometry['features']:
  prop=feature['properties'];code=prop['PRECINCT'];assert code not in seen;seen.add(code)
  shape=feature['geometry'];assert shape['type'] in ['Polygon','MultiPolygon']
  boundaries.append({'area':'PRECINCT '+code,'code':code,'geometry':shape,'created_date':prop.get('CREATED_DATE'),'last_edited_date':prop.get('LAST_EDITED_DATE')})
 boundaries.sort(key=lambda r:r['code'])
 points=[]
 for feature in sources['building_points']['data']['features']:
  a=feature['attributes'];year=2026 if a['BLDG_NUM']=='131' else 2022
  assert a['BLDG_NUM'] in ['102','131'] and 35.7<a['LATITUDE']<35.9 and -78.8<a['LONGITUDE']<-78.6
  points.append({'id':'western' if year==2026 else 'talley','name':'Western Boulevard Business Services' if year==2026 else 'Talley Student Union','latitude':a['LATITUDE'],'longitude':a['LONGITUDE'],'address':a['ADDRESS'],'building_number':a['BLDG_NUM'],'years':[2026] if year==2026 else [2022,2024]})
 assert len(points)==2 and {p['id'] for p in points}=={'talley','western'}
 ids=['voting-precinct-map','voting-map-intro']
 metadata=[{'label':key,'href':value['url'],'sha256':value['sha256']} for key,value in sources.items()]
 boundary_source={'label':'Wake County GIS voting precinct polygons','url':'https://data.wake.gov/datasets/Wake::precincts','tables':[{'name':'Wake County Precincts FeatureServer/0','href':sources['boundary_layer']['url']}],'period':'Current downloaded boundary snapshot, not election-year boundary reconstructions','executedAt':bundle['retrieved_at'],'filters':['Wake County polygons; all published precincts; GeoJSON WGS84 coordinates'],'metricDefinitions':[
  {'label':'Precinct outlines','definition':'Original Wake County GIS PRECINCT codes and GeoJSON geometries from its published layer. The server query uses maxAllowableOffset 0.000015 degrees for browser display. Shapes are projected to Web Mercator by the map; no invented geography or individual addresses.','componentIds':ids},
  {'label':'Joining counts','definition':'Join PRECINCT 01-23 in ballot aggregates to GIS code 01-23 by removing only the literal PRECINCT prefix. Historical labels absent from this snapshot remain unmapped, never merged with another precinct. Counts retain their original election-year codes.','componentIds':ids},
  {'label':'Map shading','formula':'same-area named-site share = site_ballots / wake_ballots * 100','definition':'For the selected year and age band, color is the fraction of accepted early ballots from this precinct cast at Talley in 2022/2024 or Western Boulevard in 2026. Zero differs from unavailable/zero-denominator shares. This is location use, not resident turnout.','componentIds':ids}],
  'caveats':['Current outlines are a geographic reference; historical precinct boundaries may differ. Selecting a historical year does not reconstruct its boundaries.','Unmapped precinct codes and unknown labels remain counted in the CSV and full tables; map coverage is disclosed for the selected year and age band.','Only the first 16 early-voting days are compared. 2024 was presidential; 2022 and 2026 are midterms.'],
  'evidenceFlow':[{'title':'Public map-source snapshot','detail':json.dumps(metadata)},{'title':'Coordinates and layer provenance','detail':'scripts/download_precinct_map_sources.py downloads official public GIS data. scripts/build_precinct_map.py retains each polygon, exact join code, metadata dates and official building coordinates; geography ballot counts remain unchanged.'}]}
 point_source={'label':'NC State official campus-map building coordinates','url':'https://maps.ncsu.edu/','tables':[{'name':'NC State Buildings_OnlineCampusMap/MapServer/1','href':sources['building_points']['url']}],'period':'Official building coordinates; site years identify the electoral comparison','executedAt':bundle['retrieved_at'],'filters':["BLDG_NUM IN ('102','131')"],'metricDefinitions':[{'label':'Voting-site pins','definition':'Talley building 102 and Western Boulevard Business Services building 131. Pin latitude and longitude come directly from the university GIS LATITUDE/LONGITUDE attributes; these are public building points, not voter residences. Talley is the compared site in 2022/2024, Western Boulevard in 2026.','componentIds':ids}],'evidenceFlow':[{'title':'University building source','detail':json.dumps(next(m for m in metadata if m['label']=='building_points'))}]}
 snapshot['queries']['precinct_shapes']={'rows':boundaries,'source':boundary_source,'methods':[{'language':'python','code':'python scripts/download_precinct_map_sources.py\npython scripts/build_precinct_map.py\n# Preserve geometry snapshot and all original count-query rows.'}]}
 snapshot['queries']['voting_site_points']={'rows':points,'source':point_source}
 snapshot['precinctMap']={'basemap_url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}','basemap_attribution':sources['basemap']['data']['copyrightText'],'boundary_snapshot_retrieved_at':bundle['retrieved_at'],'boundary_data_last_edit':sources['boundary_layer']['data'].get('editingInfo',{}).get('dataLastEditDate'),'inspiration':'https://strokeofluck.github.io/sean-data-portfolio/projects/housing-affordability.html'}
 print(f'Bound {len(boundaries)} official polygons and {len(points)} university site pins; existing ballot counts unchanged.')

if __name__=='__main__':
 path=ROOT/'report-source/snapshot.json';snapshot=json.loads(path.read_text(encoding='utf-8'));add_precinct_map(snapshot);snapshot['buildStatus']='updating';path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
