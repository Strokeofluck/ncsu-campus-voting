"""Make the already-frozen public GIS evidence browseable without ZIP software."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';DEST=ROOT/'data/sources/ncsu-gis/2026-11-01';DEST.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:
 manifest=json.loads(z.read('manifest.json'))
 for name in ['buildings.json','walks.json','accessible_paths.json','entrances.json','manifest.json']:
  raw=z.read(name)
  if name!='manifest.json':assert hashlib.sha256(raw).hexdigest()==manifest['sources'][name[:-5]]['sha256']
  (DEST/name).write_bytes(raw)
parking=json.loads((OUT/'parking-gis-raw.json').read_text(encoding='utf-8'));(DEST/'parking-query.json').write_bytes((OUT/'parking-gis-raw.json').read_bytes())
features=[]
for f in parking['data']['features']:
 a=f['attributes']
 if a['OBJECTID'] not in [34,38,55,56,82]:continue
 features.append({'type':'Feature','properties':{'objectid':a['OBJECTID'],'name':a['NAME'],'site_id':'131','spaces':a['SPACES'],'type':a['Type'],'zone':a['ZONE_'],'scope':'Whole GIS parking area; not the voter-reserved subsection'},'geometry':{'type':'Polygon','coordinates':f['geometry']['rings']}})
assert len(features)==5
talley=json.loads((OUT/'talley-parking-gis-raw.json').read_text(encoding='utf-8'));(DEST/'talley-parking-query.json').write_bytes((OUT/'talley-parking-gis-raw.json').read_bytes())
assert {f['attributes']['OBJECTID'] for f in talley['data']['features']}=={26,92,143,144,166}
for f in talley['data']['features']:
 a=f['attributes'];features.append({'type':'Feature','properties':{'objectid':a['OBJECTID'],'name':a['NAME'],'site_id':'102','spaces':a['SPACES'],'type':a['Type'],'zone':a['ZONE_'],'scope':'Whole current GIS parking area. Voter use is documented for other election dates; fall 2022 reservation details unverified.'},'geometry':{'type':'Polygon','coordinates':f['geometry']['rings']}})
parking_data={'type':'FeatureCollection','features':features}
(OUT/'nearby-parking.geojson').write_text(json.dumps(parking_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sites=json.loads((OUT/'comparison-site-gis-records.json').read_text(encoding='utf-8'))
footprints=[{'type':'Feature','properties':{'id':f['attributes']['BLDG_NUM'],'name':f['attributes']['MAPNAME']},'geometry':{'type':'Polygon','coordinates':f['geometry']['rings']}} for f in sites['features']]
catalog={'retrieved_at':manifest['retrieved_at'],'archive_note':'These are the original frozen, paginated GIS feature snapshots used in the model, not byte-for-byte HTTP page responses. Their exact original saved bytes and SHA-256 hashes are preserved. Parking comprises two additional queries collected November 1, 2026; neither replaces any routing input.','original_bundle_sha256':hashlib.sha256((OUT/'official-gis-snapshot.zip').read_bytes()).hexdigest(),'routing_manifest':manifest,'parking_query_url':parking['url'],'talley_parking_query_url':talley['url'],'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(DEST.glob('*')) if p.name!='catalog.json' and p.suffix.lower() in ['.json','.jpg']]}
(DEST/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DEST/'README.md').write_text('# Frozen NC State GIS evidence\n\nDownloaded November 1, 2026. `catalog.json` and `manifest.json` retain exact query URLs, counts, retrieval time and SHA-256 hashes. Buildings, walking paths, accessible paths and entrances are exact extracts of the existing frozen ZIP. `parking-query.json` preserves the 41-feature Western-area spatial query; five McKimmon/Business Services polygons are displayed. `talley-parking-query.json` preserves five Coliseum/Jeter features, all displayed. These current GIS polygons do not identify reserved levels/bays, voter capacity, or fall 2022 parking arrangements. Dated evidence and its limits are in `parking-evidence.json`.\n\nThe public original GIS classifications and geometries are retained without relabeling. University source ownership is unchanged. Model-derived routes and estimates remain separately in `data/processed/campus-walk/`.\n',encoding='utf-8')
sfile=ROOT/'report-source/snapshot.json';s=json.loads(sfile.read_text(encoding='utf-8'));s['campusSiteFootprints']=footprints;s['campusParking']=parking_data
s['queries']['campus_parking']={'rows':[f['properties'] for f in features],'source':{'label':'NC State GIS parking near both sites; whole areas, not voter reservations','url':parking['url'],'executedAt':'2026-11-01','files':['data/sources/ncsu-gis/2026-11-01/parking-query.json','data/sources/ncsu-gis/2026-11-01/talley-parking-query.json','data/sources/ncsu-gis/2026-11-01/parking-evidence.json','data/processed/campus-walk/nearby-parking.geojson','data/sources/ncsu-gis/2026-11-01/Voting-Reserved-Spaces.jpg'],'metricDefinitions':[{'label':'Parking outlines','definition':'Ten original GIS polygons: Western-area OBJECTIDs 34,38,55,56,82 and Coliseum/Jeter OBJECTIDs 26,92,143,144,166. These are whole current GIS parking areas, not reserved subsections or deck levels. Official university notices identify Jeter voter bays for February/March 2024, Coliseum second-level voter parking for February 2026, and a reserved McKimmon subsection for October 2026. Fall 2022 reservation details have not been verified. No voter-capacity or availability claims are inferred from polygons.','componentIds':['voting-campus-walking-map','voting-campus-passby']} ]}}
definition=s['queries']['campus_passby']['source']['metricDefinitions'][0]
s['queries']['campus_parking']['source']['metricDefinitions'].append({'label':'GIS-listed parking inventory','formula':'Coliseum Deck = SPACES for OBJECTIDs 26+92+166 = 275+1694+223 = 2192; McKimmon = OBJECTIDs 34+38+55+56 = 45+62+266+287 = 660.','definition':'Source-record inventory, not voter-reserved spaces, vacancies or independently verified current physical capacity. Uses each distinct OBJECTID once and excludes Jeter Bays (226), Coliseum surface visitor area (66) and Business Services lot (15) from the two main totals. Other university publications give differing counts; references disclose the unresolved differences.','componentIds':['voting-campus-walking-map','voting-campus-passby']})
definition['formula']=definition['formula'].replace('mapped entrance point (equal circles, default) or whole building footprint (original buffers)','whole building footprint (default) or mapped entrance point (optional equal circles)')
definition['definition']=definition['definition'].replace('Display distances are miles; calculations retain metres (1 mile = 1609.344 metres).','Route distances display miles, while proximity zones use meters; calculations retain metres (1 mile = 1609.344 metres).')
sfile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Archived four routing layers and two parking queries; ten whole parking polygons; all original routing inputs unchanged.')
