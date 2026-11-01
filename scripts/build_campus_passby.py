"""Model equally weighted housing-to-destination routes, not real pedestrian probabilities."""
import argparse,csv,json,math,runpy,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--library-dir');args=p.parse_args()
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
if args.library_dir:sys.path.append(args.library_dir)
import networkx as nx
from shapely.geometry import LineString,Point,mapping
from shapely.ops import unary_union
saved=sys.argv;sys.argv=[str(ROOT/'scripts/build_campus_walking_routes.py'),'--network-only']+(['--library-dir',args.library_dir] if args.library_dir else [])
env=runpy.run_path(sys.argv[0]);sys.argv=saved
g=env['g'];access=env['access'];edges=env['edges'];segments=env['segments'];unproject=env['unproject'];project=env['project'];buildings=env['buildings'];polygons=env['polygons']
walk=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));origins=[r for r in walk['rows'] if r['available']]
site_points={s['id']:Point(project.transform(*s['coordinates'])) for s in walk['sites']}
# D. H. Hill is one destination: merge its GIS building wings rather than count them as separate libraries.
polygons['047']=unary_union([poly for code,poly in polygons.items() if code in ['047','047A','047B','047C']])
destinations=[];excluded=[]
for code,f in buildings.items():
 a=f['attributes'];use=a.get('USE_NAME');name=a.get('MAPNAME') or a.get('BLDG_NAME');kind=None
 if a.get('STATUSCODE')!='A' or a.get('SITECODE') not in ['NORTH','CENTRAL','WEST','SOUTH','CENTENNIAL']:continue
 if use=='Classroom':kind='Teaching'
 if code in ['047','783A']:kind='Library'
 if use=='Dining' or code=='102':kind='Dining'
 if not kind:continue
 if code=='024':excluded.append({'id':code,'name':name,'reason':'Poe Hall closed; excluded despite GIS Classroom classification'});continue
 entry,reason=access(code)
 if not entry:excluded.append({'id':code,'name':name,'reason':reason});continue
 destinations.append({'id':code,'name':name,'kind':kind,'coordinates':list(unproject.transform(entry['point'].x,entry['point'].y))})
destinations.sort(key=lambda r:(r['kind'],r['name']))
accesses={}
for code in set([r['id'] for r in origins]+[r['id'] for r in destinations]):
 a,reason=access(code);assert a,reason;accesses[code]=a
byedge={}
for code,a in accesses.items():byedge.setdefault(a['edge_index'],[]).append((code,a))
for ei,values in byedge.items():
 u,v=edges[ei];line=segments[ei];g.remove_edge(u,v);chain=[(0,u),(line.length,v)]
 for code,a in values:
  node=tuple(a['snap'].coords[0]);a['node']=node;chain.append((a['offset'],node))
 chain.sort(key=lambda v:v[0])
 for (d1,n1),(d2,n2) in zip(chain,chain[1:]):
  if n1!=n2:g.add_edge(n1,n2,weight=d2-d1)
rows=[]
for origin in origins:
 a=accesses[origin['id']];assert a['entrance_id']==origin['entrance_id'];lengths,paths=nx.single_source_dijkstra(g,a['node'],weight='weight')
 for destination in destinations:
  b=accesses[destination['id']];path=paths[b['node']];xy=[tuple(a['point'].coords[0])]+path+[tuple(b['point'].coords[0])];line=LineString(xy)
  # Proximity uses the complete modeled route; simplified geometry is display only.
  simple=line.simplify(1,preserve_topology=True)
  rows.append({'origin_id':origin['id'],'origin_name':origin['name'],'housing_group':origin['group'],'destination_id':destination['id'],'destination_name':destination['name'],'destination_kind':destination['kind'],'gis_use_name':buildings[destination['id']]['attributes']['USE_NAME'],'ends_at_talley':destination['id']=='102','route_m':lengths[b['node']]+a['connector_m']+b['connector_m'],'talley_nearest_m':line.distance(polygons['102']),'western_nearest_m':line.distance(polygons['131']),'talley_entrance_nearest_m':line.distance(site_points['102']),'western_entrance_nearest_m':line.distance(site_points['131']),'geometry':{'type':'LineString','coordinates':[list(unproject.transform(*p)) for p in simple.coords]}})
site_buffers=[]
for code,site in [('102','Talley (2022)'),('131','Western Boulevard (2026)')]:
 for radius in [25,50,100]:
  poly=polygons[code].buffer(radius,quad_segs=12);site_buffers.append({'site':site,'site_id':code,'radius_m':radius,'geometry':{'type':'Polygon','coordinates':[[list(unproject.transform(*p)) for p in poly.exterior.coords]]}})
summary=[]
for basis in ['footprint','entrance']:
 for radius in [25,50,100]:
  for include_talley in [False,True]:
   eligible=[r for r in rows if include_talley or not r['ends_at_talley']]
   for field in ['talley','western']:
    key=field+('_entrance_nearest_m' if basis=='entrance' else '_nearest_m')
    hits=sum(r[key]<=radius for r in eligible);summary.append({'distance_basis':basis,'radius_m':radius,'include_talley_destinations':include_talley,'site':field,'near_routes':hits,'total_routes':len(eligible),'share_pct':hits/len(eligible)*100})

data={'gis_retrieved_at':walk['retrieved_at'],'origins':[{'id':r['id'],'name':r['name'],'group':r['group'],'coordinates':r['entrance_coordinates']} for r in origins],'destinations':destinations,'excluded_destinations':excluded,'site_buffers':site_buffers,'site_points':walk['sites'],'rows':rows,'summary':summary,'definition':'Equal weight per usable housing-building Ã— destination-building pair. One deterministic shortest GIS route per pair. Minimum distance to either a mapped entrance point (equal-circle view) or the building footprint (original view). No counts of actual students, trips, occupancy, course enrollment, visits or route choices. Default excludes trips ending at Talley; inclusion sensitivity is explicit.','selection_sources':['https://studentcenters.ncsu.edu/location/talley/','https://www.lib.ncsu.edu/visit','https://committees.provost.ncsu.edu/campus-development/wp-content/uploads/sites/48/2025/01/2025-01-09-Capital-Dev-Plan-2024.pdf']}
(OUT/'passby.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
with (OUT/'passby-routes.csv').open('w',newline='',encoding='utf-8') as f:
 fields=[k for k in rows[0] if k!='geometry'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
with (OUT/'passby-summary.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
print('Origins',len(origins),'destinations',len(destinations),'modeled pairs',len(rows),'excluded destinations',excluded)
print([r for r in summary if r['radius_m']==50])
