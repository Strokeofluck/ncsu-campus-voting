#!/usr/bin/env python3
"""Download public map geography and public university building points only."""
import json,hashlib,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/comparison/precinct_map_sources.json'
BASE='https://services1.arcgis.com/a7CWfuGP5ZnLYE7I/ArcGIS/rest/services/Precincts/FeatureServer/0'
BUILDINGS='https://gismaps.oit.ncsu.edu/arcgis/rest/services/Buildings/Buildings_OnlineCampusMap/MapServer/1'
URLS={
 'boundaries':BASE+'/query?'+urllib.parse.urlencode({'where':'1=1','outFields':'PRECINCT,CREATED_DATE,LAST_EDITED_DATE','outSR':'4326','f':'geojson','returnGeometry':'true','maxAllowableOffset':'0.000015'}),
 'boundary_layer':BASE+'?f=json',
 'boundary_item':'https://www.arcgis.com/sharing/rest/content/items/7c7281ad652143518405cbde1561c585?f=json',
 'building_points':BUILDINGS+'/query?'+urllib.parse.urlencode({'where':"BLDG_NUM IN ('102','131')",'outFields':'BLDG_NAME,MAPNAME,BLDG_ABBR,BLDG_NUM,ADDRESS,LATITUDE,LONGITUDE,ZIP,STATE,CITY','outSR':'4326','returnGeometry':'false','f':'json'}),
 'basemap':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer?f=json'}

def main():
 bundle={'retrieved_at':datetime.now(timezone.utc).isoformat(),'sources':{}}
 for key,url in URLS.items():
  raw=urllib.request.urlopen(url,timeout=45).read();data=json.loads(raw)
  assert not data.get('error'),data.get('error')
  bundle['sources'][key]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'data':data}
 count=json.load(urllib.request.urlopen(BASE+'/query?where=1%3D1&returnCountOnly=true&f=json',timeout=30))['count']
 assert len(bundle['sources']['boundaries']['data']['features'])==count
 OUT.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 print(f'Downloaded {count} public precinct polygons and two university building points; no voter records.')
if __name__=='__main__':main()
