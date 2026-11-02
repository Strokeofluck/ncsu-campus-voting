"""Supplement original missing routes with audited entrance or estimated edge access.

These supplemental comparisons never silently revise the frozen baseline averages or routine-trip model.
No official entrance feature is invented or edited.
"""
import argparse,json,runpy,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--library-dir');args=p.parse_args()
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
saved=sys.argv;sys.argv=[str(ROOT/'scripts/build_campus_walking_routes.py'),'--network-only']+(['--library-dir',args.library_dir] if args.library_dir else [])
e=runpy.run_path(sys.argv[0]);sys.argv=saved
import networkx as nx
from shapely.geometry import LineString
from shapely.ops import nearest_points
g=e['g'];edges=e['edges'];segments=e['segments'];polygons=e['polygons'];unproject=e['unproject']
walk=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));accesses={};notes=[]
for code in ['102','131']:accesses[code]=e['access'](code)[0]
for row in walk['rows']:
 if row['available']:continue
 code=row['id'];poly=polygons[code];found=[];recovered=[]
 # The original matcher checks only the nearest connected edge. If blocked,
 # try every edge within the SAME 30 m limit from an original enabled entrance.
 for eid,point in e['entrances']:
  if poly.distance(point)>10:continue
  for ei in e['tree'].query(point,predicate='dwithin',distance=30):
   ei=int(ei);line=segments[ei];snap=line.interpolate(line.project(point));connector=LineString([point,snap])
   if any(connector.intersection(polygons[e['polykeys'][int(pi)]]).length>2.5 for pi in e['polytree'].query(connector)):continue
   recovered.append((point.distance(snap),eid,ei,point,snap))
 # All candidates within the original 30 m connector ceiling; choose the shortest
 # straight connection which crosses no building interior (>2.5 m tolerance).
 for ei,line in enumerate(segments):
  if poly.distance(line)>30:continue
  point,snap=nearest_points(poly.boundary,line);gap=point.distance(snap);connector=LineString([point,snap])
  if any(connector.intersection(polygons[e['polykeys'][int(pi)]]).length>2.5 for pi in e['polytree'].query(connector)):continue
  found.append((gap,ei,point,snap))
 assert found,code
 entrance_id=None
 if recovered:gap,entrance_id,ei,point,snap=min(recovered,key=lambda v:(v[0],v[1],v[2]))
 else:gap,ei,point,snap=min(found,key=lambda v:(v[0],v[1]))
 accesses[code]={'point':point,'snap':snap,'edge_index':ei,'offset':segments[ei].project(snap),'connector_m':gap}
 notes.append({**row,'estimated_access':not bool(recovered),'recovered_mapped_entrance':bool(recovered),'entrance_id':entrance_id,'access_basis':'Original enabled GIS entrance; shortest unblocked connection within 30 m' if recovered else 'Estimated nearest building-edge connection; no qualifying mapped entrance connection','access_coordinates':list(unproject.transform(point.x,point.y)),'estimated_connector_m':gap})
byedge={}
for code,a in accesses.items():byedge.setdefault(a['edge_index'],[]).append(a)
for ei,values in byedge.items():
 u,v=edges[ei];line=segments[ei];g.remove_edge(u,v);chain=[(0,u),(line.length,v)]
 for a in values:a['node']=tuple(a['snap'].coords[0]);chain.append((a['offset'],a['node']))
 chain.sort(key=lambda v:v[0])
 for (d1,n1),(d2,n2) in zip(chain,chain[1:]):
  if n1!=n2:g.add_edge(n1,n2,weight=d2-d1)
def coords(p):return list(unproject.transform(p.x,p.y))
for row in notes:
 a=accesses[row['id']]
 for field,code in [('talley','102'),('western','131')]:
  b=accesses[code];path=nx.shortest_path(g,a['node'],b['node'],weight='weight');network=sum(g[u][v]['weight'] for u,v in zip(path,path[1:]));total=network+a['connector_m']+b['connector_m'];row[field+'_m']=total
  row[field+'_route']={'network_m':network,'origin_connector_m':a['connector_m'],'destination_connector_m':b['connector_m'],'total_m':total,'geometry':{'type':'LineString','coordinates':[list(unproject.transform(*xy)) for xy in path]},'origin_connector':{'type':'LineString','coordinates':[coords(a['point']),coords(a['snap'])]},'destination_connector':{'type':'LineString','coordinates':[coords(b['snap']),coords(b['point'])]}}
 row['difference_m']=row['western_m']-row['talley_m']
payload={'retrieved_at':walk['retrieved_at'],'method':'For the four original failures, try all connected edges within 30 m of each enabled mapped entrance within 10 m of the footprint; reject connectors intersecting more than 2.5 m of a building interior. This recovers Aurora entrance 216. When no qualifying entrance exists, use a separately estimated nearest unblocked building-edge connection, at most 30 m. Gold, Welch and University Towers remain estimates. Network and both site entrances are unchanged. These supplemental routes do not silently revise the frozen 36-building baseline averages or routine-route denominators.','rows':notes}
(OUT/'estimated-access-routes.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sfile=ROOT/'report-source/snapshot.json';s=json.loads(sfile.read_text(encoding='utf-8'));s['queries']['campus_estimated_access']={'rows':notes,'source':{'label':'Supplemental access: recovered Aurora mapped entrance and three labeled building-edge estimates','executedAt':walk['retrieved_at'],'files':['data/processed/campus-walk/estimated-access-routes.json','data/processed/campus-walk/official-gis-snapshot.zip'],'metricDefinitions':[{'label':'Supplemental access routes','definition':payload['method'],'componentIds':['voting-campus-walking-map']} ]}};sfile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print([(r['name'],round(r['estimated_connector_m'],2),round(r['talley_m']),round(r['western_m'])) for r in notes])
