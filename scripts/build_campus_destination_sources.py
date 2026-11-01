"""Expose the exact frozen GIS classifications behind the curated 22 destinations."""
import csv,hashlib,json,zipfile
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
BASE='https://gismaps.oit.ncsu.edu/arcgis/rest/services/Buildings/Buildings_OnlineCampusMap/MapServer/1'
FIELDS='BLDG_NUM,BLDG_NAME,MAPNAME,USE_NAME,USECODE,STATUS_DESCR,ADDRESS'
d=json.loads((OUT/'passby.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:
 raw=z.read('buildings.json');manifest=json.loads(z.read('manifest.json'));assert hashlib.sha256(raw).hexdigest()==manifest['sources']['buildings']['sha256'];features=json.loads(raw)['features']
bycode={f['attributes']['BLDG_NUM']:f for f in features};rows=[];records=[]
for destination in d['destinations']:
 code=destination['id'];record=bycode[code];a=record['attributes'];kind=destination['kind'];extra=None
 if kind=='Teaching':
  assert a['USE_NAME']=='Classroom';why='GIS USE_NAME = Classroom; used as a teaching-building proxy. Not verified class schedules.'
 elif kind=='Dining' and code=='102':
  assert a['USE_NAME']=='Student Center';why='Analyst addition: GIS says Student Center. NC State Student Centers independently identifies dining at Talley.';extra='https://studentcenters.ncsu.edu/location/talley/'
 elif kind=='Dining':
  assert a['USE_NAME']=='Dining';why='GIS USE_NAME = Dining. Current hours and access restrictions are not verified.'
 else:
  assert a['USE_NAME']=='Library';why='Selected main library destination; not an exhaustive list of campus libraries.';extra='https://www.lib.ncsu.edu/visit'
 if code=='047':why+=' Hill footprint codes 047/047A/047B/047C are merged and count as one destination.'
 url=BASE+'/query?'+urlencode({'where':"BLDG_NUM = '"+code+"'",'outFields':FIELDS,'returnGeometry':'false','f':'pjson'})
 rows.append({'building_number':code,'model_name':destination['name'],'model_category':kind,'gis_building_name':a['BLDG_NAME'],'gis_use_name':a['USE_NAME'],'gis_use_code':a['USECODE'],'gis_status':a['STATUS_DESCR'],'selection_reason':why,'official_gis_record_url':url,'additional_official_source_url':extra or ''});records.append(record)
codes=[r['building_number'] for r in rows]
batch=BASE+'/query?'+urlencode({'where':'BLDG_NUM IN ('+','.join("'"+code+"'" for code in codes)+')','outFields':FIELDS,'returnGeometry':'false','f':'pjson'})
payload={'gis_snapshot_date':d['gis_retrieved_at'],'classification_field':'USE_NAME','official_layer_url':BASE,'official_22_record_query_url':batch,'source_snapshot_sha256':manifest['sources']['buildings']['sha256'],'scope':'Curated model of 22 destinations: 16 GIS Classroom buildings, 3 GIS Dining buildings plus Talley (GIS Student Center; dining verified by university website), and 2 selected main libraries. Not all campus teaching/dining/library locations and not observed student destinations.','rows':rows,'hill_geometry_components':[bycode[c] for c in ['047','047A','047B','047C']]}
comparisons=[]
for code,year in [('102',2022),('131',2026)]:
 a=bycode[code]['attributes'];url=BASE+'/query?'+urlencode({'where':"BLDG_NUM = '"+code+"'",'outFields':FIELDS,'returnGeometry':'false','f':'pjson'})
 comparisons.append({'building_number':code,'year':year,'gis_building_name':a['BLDG_NAME'],'gis_use_name':a['USE_NAME'],'official_gis_record_url':url})
payload['comparison_sites']=comparisons
(OUT/'comparison-site-gis-records.json').write_text(json.dumps({'features':[bycode['102'],bycode['131']]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'destination-sources.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'destination-gis-records.json').write_text(json.dumps({'source_snapshot_sha256':payload['source_snapshot_sha256'],'features':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'destination-sources.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
p=ROOT/'report-source/snapshot.json';s=json.loads(p.read_text(encoding='utf-8'));s['queries']['campus_destination_sources']={'rows':rows,'source':{'label':'Exact NC State GIS destination classifications and explicit model additions','url':BASE,'executedAt':d['gis_retrieved_at'],'files':[batch,'data/processed/campus-walk/destination-gis-records.json','data/processed/campus-walk/official-gis-snapshot.zip'],'metricDefinitions':[{'label':'Destination membership and original GIS type','definition':payload['scope']+' Verbatim USE_NAME, BLDG_NAME, BLDG_NUM, USECODE and STATUS_DESCR come from the frozen official GIS snapshot; every row links its live official JSON query. GIS active status does not establish current access, opening hours or schedules. Talley is not classified Dining by GIS.','componentIds':['voting-campus-passby','voting-campus-destination-sources']}],'evidenceFlow':[{'title':'Original GIS record audit','detail':'scripts/build_campus_destination_sources.py; source snapshot SHA-256 '+payload['source_snapshot_sha256']}]}}
s['queries']['campus_site_gis_uses']={'rows':comparisons,'source':{'label':'Original NC State GIS use labels for the two voting-site buildings','url':BASE,'executedAt':d['gis_retrieved_at'],'files':['data/processed/campus-walk/comparison-site-gis-records.json'],'metricDefinitions':[{'label':'Original building use','definition':'Talley building 102 has USE_NAME Student Center; Western Boulevard building 131 has USE_NAME Office. Voting-site years describe the election comparison, not the building-use category.','componentIds':['voting-campus-passby']}]}}
s['campusPassby']['destinationSourceQueryUrl']=batch;s['campusPassby']['destinationLayerUrl']=BASE;p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Audited 22 exact GIS records: 16 Classroom, 3 Dining, 1 Student Center (Talley), 2 selected Library destinations.')
