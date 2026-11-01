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
 features.append({'type':'Feature','properties':{'objectid':a['OBJECTID'],'name':a['NAME'],'scope':'Whole GIS parking area; not the voter-reserved subsection'},'geometry':{'type':'Polygon','coordinates':f['geometry']['rings']}})
assert len(features)==5
parking_data={'type':'FeatureCollection','features':features}
(OUT/'nearby-parking.geojson').write_text(json.dumps(parking_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sites=json.loads((OUT/'comparison-site-gis-records.json').read_text(encoding='utf-8'))
footprints=[{'type':'Feature','properties':{'id':f['attributes']['BLDG_NUM'],'name':f['attributes']['MAPNAME']},'geometry':{'type':'Polygon','coordinates':f['geometry']['rings']}} for f in sites['features']]
catalog={'retrieved_at':manifest['retrieved_at'],'archive_note':'These are the original frozen, paginated GIS feature snapshots used in the model, not byte-for-byte HTTP page responses. Their exact original saved bytes and SHA-256 hashes are preserved. Parking is an additional spatial query collected November 1, 2026; it does not replace any routing input.','original_bundle_sha256':hashlib.sha256((OUT/'official-gis-snapshot.zip').read_bytes()).hexdigest(),'routing_manifest':manifest,'parking_query_url':parking['url'],'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(DEST.glob('*.json')) if p.name!='catalog.json']}
(DEST/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DEST/'README.md').write_text('# Frozen NC State GIS evidence\n\nDownloaded November 1, 2026. `catalog.json` and `manifest.json` retain exact query URLs, counts, retrieval time and SHA-256 hashes. Buildings, walking paths, accessible paths and entrances are exact extracts of the existing frozen ZIP. `parking-query.json` preserves the additional 41-feature spatial query; only five named McKimmon/Business Services parking polygons are displayed. Nearby whole-lot outlines do not identify the voter-reserved subsection, capacity available to voters, or current restrictions.\n\nThe public original GIS classifications and geometries are retained without relabeling. University source ownership is unchanged. Model-derived routes and estimates remain separately in `data/processed/campus-walk/`.\n',encoding='utf-8')
sfile=ROOT/'report-source/snapshot.json';s=json.loads(sfile.read_text(encoding='utf-8'));s['campusSiteFootprints']=footprints;s['campusParking']=parking_data
s['queries']['campus_parking']={'rows':[f['properties'] for f in features],'source':{'label':'NC State GIS nearby parking areas; whole lots, not voter reservations','url':parking['url'],'executedAt':'2026-11-01','files':['data/sources/ncsu-gis/2026-11-01/parking-query.json','data/processed/campus-walk/nearby-parking.geojson'],'metricDefinitions':[{'label':'Parking outlines','definition':'Five original GIS parking-area polygons selected by OBJECTID 34,38,55,56,82: McKimmon North/South, two visitor polygons and Business Services. These are whole mapped parking areas. No claim that all spaces are available or reserved for voters. NC State separately identifies a voter-reserved portion in its published parking plan.','componentIds':['voting-campus-walking-map','voting-campus-passby']} ]}}
definition=s['queries']['campus_passby']['source']['metricDefinitions'][0]
definition['formula']=definition['formula'].replace('mapped entrance point (equal circles, default) or whole building footprint (original buffers)','whole building footprint (default) or mapped entrance point (optional equal circles)')
definition['definition']+=' The default is the full GIS footprint with the same outward buffer distance at both buildings. Display distances are miles; calculations retain metres (1 mile = 1609.344 metres).'
sfile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Archived four complete routing layers and parking query; verified hashes; prepared five parking polygons and both original site footprints.')
