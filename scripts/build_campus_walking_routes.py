"""Reproduce building-entrance route comparisons from frozen public NC State GIS.

Requires shapely, pyproj, networkx. --library-dir permits workspace-local libraries.
The graph uses source vertices; it never joins geometric crossings or bridges gaps.
"""
import argparse,csv,hashlib,json,math,sys,zipfile
from collections import defaultdict
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library-dir');p.add_argument('--network-only',action='store_true');args=p.parse_args()
if args.library_dir:sys.path.append(args.library_dir)
import networkx as nx
from pyproj import Transformer,Geod
from shapely.geometry import LineString,Point,Polygon
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw/campus-walk';OUT=ROOT/'data/processed/campus-walk';OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((RAW/'manifest.json').read_text())
sources={}
for key,source in manifest['sources'].items():
 raw=(RAW/(key+'.json')).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256'];sources[key]=json.loads(raw)['features'];assert len(sources[key])==source['features']
project=Transformer.from_crs(4326,32119,always_xy=True);unproject=Transformer.from_crs(32119,4326,always_xy=True)
g=nx.Graph();missing_geometry=0
for key in ['walks','accessible_paths']:
 for feature in sources[key]:
  if feature['attributes'].get('Enabled')!=1:continue
  paths=feature.get('geometry',{}).get('paths',[])
  if not paths:missing_geometry+=1
  for path in paths:
   points=[tuple(round(v,2) for v in project.transform(*c[:2])) for c in path]
   for a,b in zip(points,points[1:]):
    if a!=b:g.add_edge(a,b,weight=math.dist(a,b))
# Source polylines often end at the middle of another edge. Node those existing
# vertices (2.5 cm rounding tolerance), without joining arbitrary line crossings.
node_list=list(g);node_tree=STRtree([Point(n) for n in node_list]);noded=nx.Graph();t_junctions=0
for u,v in g.edges:
 line=LineString([u,v]);chain=[(0,u),(line.length,v)]
 for ni in node_tree.query(line,predicate='dwithin',distance=.025):
  node=node_list[int(ni)]
  if node==u or node==v:continue
  offset=line.project(Point(node))
  if .025<offset<line.length-.025:chain.append((offset,node));t_junctions+=1
 chain.sort(key=lambda v:v[0])
 for (_,a),(_,b) in zip(chain,chain[1:]):
  if a!=b:noded.add_edge(a,b,weight=math.dist(a,b))
g=noded
component_sizes=sorted([len(c) for c in nx.connected_components(g)],reverse=True);full_nodes=len(g)
# Only route within the largest observed connected network. Do not manufacture links.
g=g.subgraph(max(nx.connected_components(g),key=len)).copy();edges=list(g.edges);segments=[LineString(edge) for edge in edges];tree=STRtree(segments)
buildings={f['attributes']['BLDG_NUM']:f for f in sources['buildings'] if f.get('geometry')}
polygons={code:Polygon([project.transform(*c[:2]) for c in f['geometry']['rings'][0]]) for code,f in buildings.items()}
polykeys=list(polygons);polytree=STRtree([polygons[k] for k in polykeys])
entrances=[]
for e in sources['entrances']:
 if e['attributes'].get('Enabled')==1 and e.get('geometry'):
  entrances.append((e['attributes']['OBJECTID'],Point(project.transform(e['geometry']['x'],e['geometry']['y']))))

def access(code):
 """Fixed mapped entrance nearest the building point, subject to conservative checks."""
 f=buildings[code];a=f['attributes'];poly=polygons[code];center=Point(project.transform(a['LONGITUDE'],a['LATITUDE']))
 candidates=[];reasons=[]
 for eid,point in entrances:
  if poly.distance(point)>10:continue
  edge_i=int(tree.nearest(point));line=segments[edge_i];offset=line.project(point);snap=line.interpolate(offset);gap=point.distance(snap)
  if gap>30:reasons.append('Mapped entrance more than 30 m from connected path network');continue
  connector=LineString([point,snap]);blocked=False
  for pi in polytree.query(connector):
   if connector.intersection(polygons[polykeys[int(pi)]]).length>2.5:blocked=True;break
  if blocked:reasons.append('Straight entrance connector intersects a building footprint');continue
  candidates.append((point.distance(center),eid,point,edge_i,offset,snap,gap))
 if not candidates:return None,('; '.join(sorted(set(reasons))) or 'No enabled mapped entrance within 10 m of building footprint')
 _,eid,point,ei,offset,snap,gap=min(candidates,key=lambda v:(v[0],v[1]))
 return {'entrance_id':eid,'point':point,'edge_index':ei,'offset':offset,'snap':snap,'connector_m':gap},None

if not args.network_only:
 housing=[]
 for code,f in buildings.items():
  a=f['attributes'];name=a.get('BLDG_NAME','')
  if a.get('STATUSCODE')!='A' or a.get('USE_NAME')!='Residence':continue
  if 'Residence Hall' in name:group='Residence halls'
  elif code.startswith('222'):group='Wolf Village apartments'
  elif code.startswith('780'):group='Wolf Ridge apartments'
  else:continue
  housing.append({'id':code,'name':a.get('MAPNAME') or name,'group':group,'latitude':a['LATITUDE'],'longitude':a['LONGITUDE']})
 housing.sort(key=lambda r:(r['group'],r['name']))
 accesses={};unavailable={}
 for code in ['102','131']+[r['id'] for r in housing]:
  found,reason=access(code)
  if found:accesses[code]=found
  else:unavailable[code]=reason
 assert '102' in accesses and '131' in accesses,'Site endpoint missing'
 # Split each source edge at all entrance projections before shortest-path calculations.
 by_edge=defaultdict(list)
 for code,a in accesses.items():by_edge[a['edge_index']].append((code,a))
 for ei,values in by_edge.items():
  u,v=edges[ei];line=segments[ei];g.remove_edge(u,v);chain=[(0,u),(line.length,v)]
  for code,a in values:
   node=tuple(a['snap'].coords[0]);a['node']=node;chain.append((a['offset'],node))
  chain.sort(key=lambda v:v[0])
  for (d1,n1),(d2,n2) in zip(chain,chain[1:]):
   if n1!=n2:g.add_edge(n1,n2,weight=d2-d1)

 def coords(point):return list(unproject.transform(point.x,point.y))
 def route(origin,dest):
  a,b=accesses[origin],accesses[dest];path=nx.shortest_path(g,a['node'],b['node'],weight='weight');length=sum(g[u][v]['weight'] for u,v in zip(path,path[1:]))
  line=[unproject.transform(*p) for p in path]
  return {'network_m':length,'origin_connector_m':a['connector_m'],'destination_connector_m':b['connector_m'],'total_m':length+a['connector_m']+b['connector_m'],'geometry':{'type':'LineString','coordinates':line},'origin_connector':{'type':'LineString','coordinates':[coords(a['point']),coords(a['snap'])]},'destination_connector':{'type':'LineString','coordinates':[coords(b['snap']),coords(b['point'])]}}
 rows=[]
 for row in housing:
  code=row['id'];a=accesses.get(code);result={**row,'available':bool(a),'unavailable_reason':unavailable.get(code)}
  if a:
   old,new=route(code,'102'),route(code,'131');result.update({'entrance_id':a['entrance_id'],'entrance_coordinates':coords(a['point']),'talley_m':old['total_m'],'western_m':new['total_m'],'difference_m':new['total_m']-old['total_m'],'talley_route':old,'western_route':new})
  rows.append(result)
 sites=[]
 for code,year,name in [('102',2022,'Talley Student Union'),('131',2026,'Western Boulevard Business Services')]:
  a=accesses[code];sites.append({'id':code,'year':year,'name':name,'entrance_id':a['entrance_id'],'coordinates':coords(a['point']),'connector_m':a['connector_m']})
 benchmark=route('102','131')
 audit={'full_network_nodes':full_nodes,'connected_component_sizes':component_sizes,'routing_component_nodes':component_sizes[0],'missing_enabled_geometries':missing_geometry,'housing_count':len(rows),'routed_count':sum(r['available'] for r in rows),'unavailable':unavailable,'talley_to_western_m':benchmark['total_m'],'coordinate_system':'EPSG:32119, NAD83 / North Carolina, metres','maximum_entry_to_network_connector_m':30,'maximum_entry_to_footprint_distance_m':10,'maximum_connector_inside_footprints_m':2.5,'rounding_m':0.01,'source_vertex_noding_tolerance_m':.025,'source_t_junction_splits':t_junctions,'planar_intersections_joined':False,'network_gaps_bridged':False,'walking_pace_m_per_min':80}
 data={'retrieved_at':manifest['retrieved_at'],'rows':rows,'sites':sites,'audit':audit,'sources':manifest['sources'],'talley_to_western':benchmark}
 (OUT/'routes.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 fields=['id','name','group','available','unavailable_reason','entrance_id','talley_m','western_m','difference_m']
 with (OUT/'distances.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
 (OUT/'method.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
 with zipfile.ZipFile(OUT/'official-gis-snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
  for name in ['walks.json','accessible_paths.json','entrances.json','buildings.json','manifest.json']:z.write(RAW/name,name)
 print(json.dumps({k:v for k,v in audit.items() if k!='connected_component_sizes'},indent=2))
 for r in rows:print(r['name'],round(r.get('talley_m',0)),round(r.get('western_m',0)),round(r.get('difference_m',0)),r.get('unavailable_reason') or '')
