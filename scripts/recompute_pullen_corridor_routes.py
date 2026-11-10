"""Reproduce per-trip mapped-entrance route candidates from frozen GIS and preserved fallback accesses. Requires networkx, shapely and pyproj. Outputs working audit files; does not publish or overwrite the frozen baseline. b9148ac supplies the original selected-access connectors and Google observations."""
import sys,runpy,json,math,collections,pathlib
W=pathlib.Path(__file__).resolve().parents[1]
import argparse,zipfile,subprocess,re
parser=argparse.ArgumentParser();parser.add_argument('--library-dir');args=parser.parse_args()
if args.library_dir:sys.path.insert(0,args.library_dir)
import networkx as nx
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
R=W
if not (R/'data/raw/campus-walk/manifest.json').exists():
 with zipfile.ZipFile(R/'data/processed/campus-walk/official-gis-snapshot.zip') as frozen:frozen.extractall(R/'data/raw/campus-walk')
sys.argv=['audit','--network-only'];e=runpy.run_path(str(R/'scripts/build_campus_walking_routes.py'));g=e['g'];polys=e['polygons'];P=e['project'];U=e['unproject'];polys['047']=unary_union([p for k,p in polys.items() if k in ['047','047A','047B','047C']]);d=json.loads((R/'data/processed/expanded-housing/all-housing-passby.json').read_text(encoding='utf-8'));original_destinations={r['id'] for r in d['destinations']};western=next(r for r in d['site_points'] if r['id']=='131');d['destinations'].append({'id':'131','name':'Western Boulevard Business Services','kind':'Voting site','coordinates':western['coordinates']});snapshot=json.loads(re.search(r'<script[^>]*id="data-app-reviewed-snapshot"[^>]*>(.*?)</script>',subprocess.check_output(['git','show','b9148ac:article/editor-preview-20261109-v2.html'],cwd=R).decode('utf-8'),re.S)[1]);walks=snapshot['queries']['campus_walking_routes']['rows']
for w in walks:
 route=w['western_route'];line=LineString([P.transform(*p) for p in route['geometry']['coordinates']]);d['rows'].append({'origin_id':w['id'],'destination_id':'131','route_m':route['total_m'],'talley_nearest_m':line.distance(polys['102']),'western_nearest_m':line.distance(polys['131']),'ends_at_talley':False,'geometry':route['geometry'],'manual_trace':w['id'] in {r['origin_id'] for r in d['rows'] if r.get('manual_trace')}})
manual={r['origin_id'] for r in d['rows'] if r.get('manual_trace')};origins=d['origins'];buildings={o['id']:dict(o,coordinates=o.get('coordinates') or next(r['geometry']['coordinates'][0] for r in d['rows'] if r['origin_id']==o['id'])) for o in origins+d['destinations']};entries={};byedge=collections.defaultdict(list)
traces=json.loads((R/'data/processed/expanded-housing/manual-connections.json').read_text(encoding='utf-8'))
from shapely.ops import nearest_points
manualpaths={'291':traces['pi'],'127H':traces['johnston'],'western_spine':traces['western_spine'],**traces['branches']};manualpaths={k:[tuple(P.transform(*p)) for p in path] for k,path in manualpaths.items()}
for key in ['291','127H','western_spine']:
 point=Point(manualpaths[key][-1]);edge=int(e['tree'].nearest(point));line=e['segments'][edge];snap=line.interpolate(line.project(point));assert point.distance(snap)<.1
 node=e['edges'][edge][0] if line.project(snap)<1e-6 else e['edges'][edge][1] if line.length-line.project(snap)<1e-6 else tuple(snap.coords[0])+(edge,)
 byedge[edge].append({'offset':line.project(snap),'node':node});manualpaths[key][-1]=node
for key in manual:
 poly=polys[key];path=manualpaths[key]
 while len(path)>1 and poly.contains(Point(path[0][:2])):path.pop(0)
 start=nearest_points(poly.boundary,Point(path[0][:2]))[0];path.insert(0,tuple(start.coords[0]))
for key,path in manualpaths.items():
 for a,b in zip(path,path[1:]):
  if a!=b:g.add_edge(a,b,weight=math.dist(a[:2],b[:2]))
for code,o in buildings.items():
 poly=polys[code];candidates=[]
 if code in manual:
  node=manualpaths[code][0];entries[code]=[{'id':'preserved-manual-access','point':Point(node[:2]),'node':node,'gap':0}];continue
 for eid,p in e['entrances']:
  if poly.distance(p)>10:continue
  edge=int(e['tree'].nearest(p));line=e['segments'][edge];snap=line.interpolate(line.project(p));gap=p.distance(snap)
  if gap>30:continue
  connector=LineString([p,snap])
  if any(connector.intersection(polys[e['polykeys'][int(i)]]).length>2.5 for i in e['polytree'].query(connector)):continue
  a={'id':eid,'point':p,'node':(e['edges'][edge][0] if line.project(snap)<1e-6 else e['edges'][edge][1] if line.length-line.project(snap)<1e-6 else tuple(snap.coords[0])+(edge,)),'gap':gap,'offset':line.project(snap),'edge':edge};candidates.append(a);byedge[edge].append(a)
 if not candidates:
  record=next(w for w in walks if w['id']==code);connector=record['talley_route']['origin_connector']['coordinates'];p=Point(P.transform(*connector[0]));old_snap=Point(P.transform(*connector[-1]));options=list(e['tree'].query(old_snap,predicate='dwithin',distance=.05));assert options,('Preserved connection not on frozen network',code)
  edge=min((int(i) for i in options),key=lambda i:e['segments'][i].distance(old_snap));line=e['segments'][edge];snap=line.interpolate(line.project(old_snap));assert p.distance(snap)<=30
  test=LineString([p,snap]);assert not any(test.intersection(polys[e['polykeys'][int(i)]]).length>2.5 for i in e['polytree'].query(test)),('Preserved connector crosses footprint',code)
  node=e['edges'][edge][0] if line.project(snap)<1e-6 else e['edges'][edge][1] if line.length-line.project(snap)<1e-6 else tuple(snap.coords[0])+(edge,)
  a={'id':'preserved-selected-access','point':p,'node':node,'gap':p.distance(snap),'offset':line.project(snap),'edge':edge};candidates.append(a);byedge[edge].append(a)
 entries[code]=candidates
for edge,items in byedge.items():
 u,v=e['edges'][edge];g.remove_edge(u,v);chain=sorted([(0,u),(e['segments'][edge].length,v)]+[(a['offset'],a['node']) for a in items])
 for (d1,n1),(d2,n2) in zip(chain,chain[1:]):
  if n1!=n2:g.add_edge(n1,n2,weight=d2-d1)

# Add only the reviewed pedestrian corridor. Join its two endpoints to the
# existing graph using measured alignment connectors; never join line crossings.
supplement=json.loads((R/'data/sources/pullen-corridor/walking-supplement.geojson').read_text())
suppcoords=[tuple(P.transform(*p)) for p in supplement['route_coordinates']]
from shapely.strtree import STRtree
joins=[]
for endpoint in [suppcoords[0],suppcoords[-1]]:
 graph_edges=list(g.edges);graph_lines=[LineString([a[:2],b[:2]]) for a,b in graph_edges];gt=STRtree(graph_lines)
 idx=int(gt.nearest(Point(endpoint)));edge=graph_edges[idx];line=graph_lines[idx];snap=line.interpolate(line.project(Point(endpoint)));gap=Point(endpoint).distance(snap)
 assert gap<=3,('Supplement endpoint too far from existing path',gap)
 connector=LineString([endpoint,snap]);assert not any(connector.intersection(poly).length>2.5 for poly in polys.values())
 offset=line.project(snap)
 if offset<1e-6:node=edge[0]
 elif line.length-offset<1e-6:node=edge[1]
 else:
  node=tuple(snap.coords[0])+('pullen-join',);g.remove_edge(*edge);g.add_edge(edge[0],node,weight=offset);g.add_edge(node,edge[1],weight=line.length-offset)
 g.add_edge(endpoint,node,weight=gap,source='reviewed endpoint alignment')
 joins.append({'coordinates':list(U.transform(*endpoint)),'gap_m':gap,'network_coordinates':list(U.transform(*node[:2]))})
for a,b in zip(suppcoords,suppcoords[1:]):g.add_edge(a,b,weight=math.dist(a,b),source='Bilyeuâ€“Pullen supplement')
(R/'work/pullen-corridor-model').mkdir(parents=True,exist_ok=True)
(W/'outputs/pullen-corridor-model/endpoint-joins.json').write_text(json.dumps(joins,indent=2))
print('Supplement endpoint alignment connectors',joins,flush=True)

old={(r['origin_id'],r['destination_id']):r for r in d['rows']};result=[];fixed_errors=[]
for o in origins:
 o=buildings[o['id']];code=o['id'];oa=entries[code];virtual='origin-'+code
 for a in oa:g.add_edge(virtual,a['node'],weight=a['gap'])
 lengths,paths=nx.single_source_dijkstra(g,virtual,weight='weight');g.remove_node(virtual)
 fixed=min(oa,key=lambda a:a['point'].distance(Point(P.transform(*o['coordinates']))));fl,fp=nx.single_source_dijkstra(g,fixed['node'],weight='weight')
 for dest in d['destinations']:
  key=(code,dest['id']);base=old[key];da=entries[dest['id']];target=min(da,key=lambda a:lengths[a['node']]+a['gap']);path=paths[target['node']][1:];source=min((a for a in oa if a['node']==path[0]),key=lambda a:a['gap']);line=LineString([tuple(source['point'].coords[0])]+[p[:2] for p in path]+[tuple(target['point'].coords[0])]);distance=lengths[target['node']]+target['gap'];fixed_dest=min(da,key=lambda a:a['point'].distance(Point(P.transform(*dest['coordinates']))));fixed_dist=fl[fixed_dest['node']]+fixed['gap']+fixed_dest['gap'];fixed_errors.append(abs(fixed_dist-base['route_m']))
  if o['name']=='Tucker Hall' and dest['name']=='Nelson Hall':print('DEBUG FIXED',fixed['id'],fixed['point'].distance(Point(P.transform(*o['coordinates']))),fixed_dest['id'],fixed_dest['point'].distance(Point(P.transform(*dest['coordinates']))),fixed_dist,base['route_m'],flush=True)
  result.append({'origin_id':code,'origin':o['name'],'destination':dest['name'],'destination_id':dest['id'],'fixed_error_m':abs(fixed_dist-base['route_m']),'old_m':base['route_m'],'new_m':distance,'saved_m':base['route_m']-distance,'old_talley':base['talley_nearest_m']<=50,'new_talley':line.distance(polys['102'])<=50,'old_western':base['western_nearest_m']<=50,'new_western':line.distance(polys['131'])<=50,'origin_entrance':source['id'],'destination_entrance':target['id'],'network_geometry':{'type':'LineString','coordinates':[list(U.transform(*p[:2])) for p in path]},'origin_connector':{'type':'LineString','coordinates':[list(U.transform(*source['point'].coords[0])),list(U.transform(*path[0][:2]))]},'destination_connector':{'type':'LineString','coordinates':[list(U.transform(*path[-1][:2])),list(U.transform(*target['point'].coords[0]))]},'network_m':distance-source['gap']-target['gap'],'origin_connector_m':source['gap'],'destination_connector_m':target['gap'],'talley_nearest_m':line.distance(polys['102']),'western_nearest_m':line.distance(polys['131']),'geometry':{'type':'LineString','coordinates':[list(U.transform(*p)) for p in line.coords]}})

print('Fixed-endpoint max error',max(fixed_errors));print('Largest fixed-endpoint differences',[(r['origin'],r['destination'],round(r['fixed_error_m'],2)) for r in sorted(result,key=lambda r:r['fixed_error_m'],reverse=True)[:8]]);print('Wolf Ridge baseline maximum',max(r['fixed_error_m'] for r in result if r['origin_id'].startswith('780')));assert all(r['saved_m']>=-.1 for r in result if r['fixed_error_m']<.1)
eligible=[r for r in result if r['destination_id']!='102' and r['destination_id'] in original_destinations];held=[];summary={'tested_origins':len(origins),'held_manual_origins':0,'preserved_manual_access_origins':len(manual),'tested_pairs':len(result),'multiple_entrance_buildings':sum(len(v)>1 for v in entries.values()),'fixed_endpoint_max_error_m':max(fixed_errors),'pairs_shorter_over_10m':sum(r['saved_m']>10 for r in result),'max_saving_m':max(r['saved_m'] for r in result),'talley_old':sum(r['talley_nearest_m']<=50 for r in d['rows'] if not r['ends_at_talley'] and r['destination_id'] in original_destinations),'talley_new_partial_sensitivity':sum(r['new_talley'] for r in eligible)+sum(r['talley_nearest_m']<=50 for r in held),'western_new_partial_sensitivity':sum(r['new_western'] for r in eligible)+sum(r['western_nearest_m']<=50 for r in held),'denominator':len(eligible)+len(held),'limits':'All 84 origins recomputed on the same augmented network; 9 manually traced origin accesses preserved, destination entrances optimized. Entrance enabled flag does not verify public access, opening hours, locked doors or current path conditions. Not a replacement published estimate.'};out=W/'work/pullen-corridor-model';out.mkdir(parents=True,exist_ok=True);(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'routes.json').write_text(json.dumps(result));(out/'entrance-counts.json').write_text(json.dumps({code:{'name':buildings[code]['name'],'eligible_entrances':len(a)} for code,a in entries.items()},indent=2));print(json.dumps(summary));print('Wolf Ridge examples',json.dumps(sorted([r for r in result if r['origin_id'].startswith('780')],key=lambda r:r['saved_m'],reverse=True)[:3],default=str)[:1200])
