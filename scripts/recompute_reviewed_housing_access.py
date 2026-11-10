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
(R/'work/pullen-corridor-model/endpoint-joins.json').write_text(json.dumps(joins,indent=2))
print('Supplement endpoint alignment connectors',joins,flush=True)


greek=json.loads((R/'data/sources/greek-rear-access/walking-supplement.geojson').read_text())
sg=nx.Graph()
for f in greek['features']:
 points=[tuple(P.transform(*p)) for p in f['geometry']['coordinates']]
 for a,b in zip(points,points[1:]):
  if a!=b:sg.add_edge(a,b,weight=math.dist(a,b),source='reviewed Greek parking access')
for point in greek['join_coordinates']:
 endpoint=tuple(P.transform(*point));assert endpoint in sg
 graph_edges=list(g.edges);lines=[LineString([a[:2],b[:2]]) for a,b in graph_edges];gt=STRtree(lines);i=int(gt.nearest(Point(endpoint)));line=lines[i];u,v=graph_edges[i];snap=line.interpolate(line.project(Point(endpoint)));gap=Point(endpoint).distance(snap);assert gap<=3,('Greek supplement join too far',gap)
 offset=line.project(snap)
 if offset<1e-6:node=u
 elif line.length-offset<1e-6:node=v
 else:
  node=tuple(snap.coords[0])+('greek-join',);g.remove_edge(u,v);g.add_edge(u,node,weight=offset);g.add_edge(node,v,weight=line.length-offset)
 g.add_edge(endpoint,node,weight=gap)
 print('Greek join',point,'gap',gap,flush=True)
for access in greek['estimated_rear_access_points']:
 p=Point(P.transform(*access['point']));snap=Point(P.transform(*access['aisle_point']));edge_list=list(sg.edges);lines=[LineString([a[:2],b[:2]]) for a,b in edge_list];gt=STRtree(lines);i=int(gt.nearest(snap));line=lines[i];u,v=edge_list[i];q=line.interpolate(line.project(snap));offset=line.project(q);node=tuple(q.coords[0]);assert snap.distance(q)<.01
 if offset<1e-6:node=u
 elif line.length-offset<1e-6:node=v
 else:
  sg.remove_edge(u,v);sg.add_edge(u,node,weight=offset);sg.add_edge(node,v,weight=line.length-offset)
 connector=LineString([p,q]);assert not any(connector.intersection(poly).length>2.5 for poly in polys.values())
 entries[access['building_id']].append({'id':'estimated-rear-parking-access','point':p,'node':node,'gap':p.distance(q)})
g.update(sg)


import xml.etree.ElementTree as ET
source=ET.parse(R/'data/sources/greek-area/pedestrian-source.xml').getroot();osm_nodes={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in source.findall('node')};pg=nx.Graph();join_candidates=set();selected_features=[];rejected=[]
for way in source.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
 if tags.get('highway') not in ['footway','path','pedestrian','steps','cycleway']:continue
 if tags.get('highway')=='cycleway' and tags.get('foot') not in ['yes','designated']:continue
 if tags.get('access') in ['private','no'] or tags.get('foot')=='no':continue
 nd=[n.attrib['ref'] for n in way.findall('nd')];coords=[osm_nodes[n] for n in nd]
 if not any(-78.6855<lon<-78.6770 and 35.7775<lat<35.7828 for lon,lat in coords):continue
 points=[tuple(P.transform(*p)) for p in coords];kept=False
 for a,b in zip(points,points[1:]):
  if a==b:continue
  line=LineString([a,b])
  if any(line.intersection(polys[e['polykeys'][int(i)]]).length>2.5 for i in e['polytree'].query(line)):
   rejected.append({'osm_way_id':way.attrib['id'],'reason':'intersects building footprint'});continue
  pg.add_edge(a,b,weight=math.dist(a,b));kept=True
 if kept:
  selected_features.append({'type':'Feature','properties':{'osm_way_id':way.attrib['id'],'source_url':'https://www.openstreetmap.org/way/'+way.attrib['id'],**tags},'geometry':{'type':'LineString','coordinates':coords}})
  if tags.get('bridge')!='yes' and tags.get('tunnel')!='yes' and tags.get('layer','0')=='0':join_candidates.update([points[0],points[-1]])
before_edges=list(g.edges);before_lines=[LineString([a[:2],b[:2]]) for a,b in before_edges];before_tree=STRtree(before_lines);by_existing_edge=collections.defaultdict(list);joins=[]
for point in join_candidates:
 if point not in pg:continue
 i=int(before_tree.nearest(Point(point)));line=before_lines[i];snap=line.interpolate(line.project(Point(point)));gap=Point(point).distance(snap)
 if gap>1.5:continue
 connector=LineString([point,snap])
 if any(connector.intersection(polys[e['polykeys'][int(j)]]).length>2.5 for j in e['polytree'].query(connector)):continue
 offset=line.project(snap);u,v=before_edges[i]
 node=u if offset<1e-6 else v if line.length-offset<1e-6 else tuple(snap.coords[0])+('greek-pedestrian-alignment',i)
 by_existing_edge[i].append((offset,node));g.add_edge(point,node,weight=gap);joins.append({'source_point':list(U.transform(*point)),'network_point':list(U.transform(*node[:2])),'gap_m':gap})
for i,values in by_existing_edge.items():
 u,v=before_edges[i];g.remove_edge(u,v);chain=sorted([(0,u),(before_lines[i].length,v)]+values,key=lambda x:x[0])
 for (d1,a),(d2,b) in zip(chain,chain[1:]):
  if a!=b:g.add_edge(a,b,weight=d2-d1)
g.update(pg)
# Two reviewed same-grade path seams: source GIS vertices meet the interior
# of the supplementary pedestrian line within one metre. Explicitly split
# those two lines, rather than connecting arbitrary geometric crossings.
junction_repairs=[]
for lonlat in [(-78.68254740347713,35.78007045283193),(-78.68267135305007,35.78360721287468)]:
 point=Point(P.transform(*lonlat));node=min(g,key=lambda n:point.distance(Point(n[:2])))
 assert point.distance(Point(node[:2]))<.01
 ped_edges=list(pg.edges);ped_lines=[LineString([a[:2],b[:2]]) for a,b in ped_edges];ped_tree=STRtree(ped_lines);idx=int(ped_tree.nearest(point));line=ped_lines[idx];a,b=ped_edges[idx];snap=line.interpolate(line.project(point));gap=point.distance(snap)
 assert gap<1 and g.has_edge(a,b)
 connector=LineString([point,snap]);assert not any(connector.intersection(poly).length>2.5 for poly in polys.values())
 split=tuple(snap.coords[0])+('reviewed-greek-path-seam',len(junction_repairs));offset=line.project(snap)
 for graph in [g,pg]:
  graph.remove_edge(a,b);graph.add_edge(a,split,weight=offset);graph.add_edge(split,b,weight=line.length-offset)
 g.add_edge(node,split,weight=gap)
 junction_repairs.append({'gis_vertex':list(lonlat),'pedestrian_line_point':list(U.transform(snap.x,snap.y)),'alignment_m':gap,'reason':'Reviewed same-grade pedestrian junction; avoid source-alignment backtrack'})
# Existing campus walkway termini at a building boundary provide additional
# mapped path access options, not assumptions that all sides have doors.
termini=[]
original_degree=collections.Counter(n for edge in e['edges'] for n in edge)
for o in origins:
 if o['group']!='Greek Village' or o['id'] in manual:continue
 code=o['id'];poly=polys[code]
 for node,degree in original_degree.items():
  if degree!=1 or node not in g:continue
  p=Point(node)
  if poly.distance(p)>1:continue
  if not any(a['point'].distance(p)<.25 for a in entries[code]):
   entries[code].append({'id':'mapped-GIS-walkway-terminus','point':p,'node':node,'gap':0});termini.append({'building_id':code,'point':list(U.transform(*node)),'status':'Mapped path terminus at footprint; door permissions not verified'})
outaudit=R/'work/greek-area-recalculation';outaudit.mkdir(parents=True,exist_ok=True)
(outaudit/'neighborhood-supplement.geojson').write_text(json.dumps({'type':'FeatureCollection','features':selected_features,'retrieved_at':'2026-11-10','alignment_joins':joins,'reviewed_junction_repairs':junction_repairs,'maximum_alignment_m':1.5,'rejected_segments':rejected,'additional_mapped_path_access':termini,'limitations':'Only public mapped pedestrian paths; residential and arterial road centerlines are not imported. Parking access is separately documented. Source alignment does not certify field conditions, door permissions, crossing safety or accessibility.'},indent=2))
print('Greek-area public pedestrian ways',len(selected_features),'short alignment joins',len(joins),'additional mapped path termini',len(termini),flush=True)


from shapely.geometry import box
from shapely import set_precision
from shapely.ops import unary_union,nearest_points,substring
before_nodes=len(g)
review={'removed_building_interior_edges':[],'removed_manual_manor_edges':0,'access_points':[],'manor_source_segments':[]}
# Aerial-confirmed ground-level plazas and residential parking areas only.
# This does not node campus-wide crossings or join bridges to roads below.
greek_area=box(*P.transform(-78.68165,35.77975),*P.transform(-78.6795,35.78145))
manor_area=box(*P.transform(-78.6820,35.7752),*P.transform(-78.6784,35.7792))
manor_service_area=box(*P.transform(-78.6818,35.7757),*P.transform(-78.6788,35.7784))
targets=['252X','252Y','252Z']
for a,b in list(g.edges):
 line=LineString([a[:2],b[:2]])
 if any(line.intersection(polys[code]).length>2.5 for code in targets):
  review['removed_building_interior_edges'].append([list(U.transform(*a[:2])),list(U.transform(*b[:2]))]);g.remove_edge(a,b)
official={frozenset((a,b)) for a,b in e['edges']}
for code in ['282','283','284','285','286','287','288']:
 for a,b in zip(manualpaths[code],manualpaths[code][1:]):
  if g.has_edge(a,b) and frozenset((a,b)) not in official:g.remove_edge(a,b);review['removed_manual_manor_edges']+=1
root=ET.parse(R/'data/sources/reviewed-access/western-manor-osm.xml').getroot();wnodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')};new_lines=[];roads=[]
for way in root.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')};cs=[wnodes[n.attrib['ref']] for n in way.findall('nd') if n.attrib['ref'] in wnodes]
 if len(cs)<2:continue
 points=[tuple(P.transform(*p)) for p in cs]
 if tags.get('highway') in ['primary','secondary','tertiary','residential','trunk']:roads.append(LineString(points));continue
 if tags.get('highway') not in ['footway','path','pedestrian','steps','service']:continue
 if tags.get('access') in ['private','no'] or tags.get('foot')=='no' or tags.get('bridge')=='yes' or tags.get('tunnel')=='yes' or tags.get('layer','0')!='0':continue
 for a,b in zip(points,points[1:]):
  line=LineString([a,b])
  if a==b or not line.intersects(manor_area):continue
  if tags.get('highway')=='service' and not line.intersects(manor_service_area):continue
  if any(line.intersection(poly).length>2.5 for poly in polys.values()):continue
  new_lines.append(line);review['manor_source_segments'].append({'osm_way_id':way.attrib['id'],'tags':tags,'coordinates':[list(U.transform(*a)),list(U.transform(*b))]})

def node_reviewed_area(area,extra=()):
 local=[(a,b) for a,b in g.edges if LineString([a[:2],b[:2]]).intersects(area)]
 lines=[LineString([a[:2],b[:2]]) for a,b in local]+list(extra)
 # Millimetre precision prevents floating-point near-misses at exact joins.
 aliases=collections.defaultdict(list)
 for node in g:aliases[(round(node[0],3),round(node[1],3))].append(node)
 for a,b in local:g.remove_edge(a,b)
 merged=unary_union([set_precision(line,.001) for line in lines]);pieces=list(merged.geoms) if hasattr(merged,'geoms') else [merged]
 def node_for(p):
  key=(round(p[0],3),round(p[1],3))
  if aliases[key]:return aliases[key][0]
  n=tuple(p);aliases[key].append(n);return n
 for line in pieces:
  if line.geom_type!='LineString':continue
  nodes=[node_for(p) for p in line.coords]
  for a,b in zip(nodes,nodes[1:]):
   if a!=b:g.add_edge(a,b,weight=math.dist(a[:2],b[:2]))
 for same in aliases.values():
  for other in same[1:]:
   if other!=same[0]:g.add_edge(same[0],other,weight=math.dist(same[0][:2],other[:2]))
node_reviewed_area(greek_area)
node_reviewed_area(manor_area,new_lines)

def reconnect(code,use_recorded=True):
 poly=polys[code];recorded=[(eid,p) for eid,p in e['entrances'] if poly.distance(p)<=10] if use_recorded else []
 if recorded:
  points=[]
  for eid,p in recorded:
   status='Mapped GIS entrance'
   if poly.contains(p) and poly.boundary.distance(p)>.5:
    boundary=nearest_points(poly.boundary,p)[0];shift=p.distance(boundary)
    assert shift<=10,('Mapped entrance too far inside footprint',code,eid,shift)
    status='Mapped GIS entrance aligned to adjacent footprint boundary by '+str(round(shift,3))+' m';p=boundary
   points.append((eid,p,status))
 else:
  p=entries[code][0]['point']
  if poly.contains(p):p=nearest_points(poly.boundary,p)[0]
  points=[('retained-estimated-access-reconnected',p,'Retained estimated building-edge point, not a verified door')]
 candidates=[]
 for eid,p,status in points:
  component=nx.node_connected_component(g,entries['102'][0]['node'])
  edges=[(a,b) for a,b in g.edges if a in component and b in component];lines=[LineString([a[:2],b[:2]]) for a,b in edges];tree=STRtree(lines)
  options=sorted((int(i) for i in tree.query(p,predicate='dwithin',distance=30)),key=lambda i:lines[i].distance(p))
  for i in options:
   line=lines[i];snap=line.interpolate(line.project(p));link=LineString([p,snap]);gap=p.distance(snap)
   if any(link.intersection(q).length>2.5 for q in polys.values()):continue
   if code.startswith('28') and any(link.crosses(road) for road in roads):continue
   a,b=edges[i];offset=line.project(snap)
   if offset<1e-6:node=a
   elif line.length-offset<1e-6:node=b
   else:
    node=tuple(snap.coords[0])+('reviewed-access',code,eid);g.remove_edge(a,b);g.add_edge(a,node,weight=offset);g.add_edge(node,b,weight=line.length-offset)
   candidates.append({'id':eid,'point':p,'node':node,'gap':gap});review['access_points'].append({'building_id':code,'access_id':eid,'status':status,'coordinates':list(U.transform(p.x,p.y)),'network_coordinates':list(U.transform(*node[:2])),'connector_m':gap});break
 if not candidates and recorded:
  review.setdefault('mapped_entrances_without_usable_connection',[]).append({'building_id':code,'entrance_ids':[eid for eid,p in recorded],'reason':'No outside-footprint connector within 30 m; keep the documented estimated frontage access instead of inventing an indoor/perimeter shortcut'})
  reconnect(code,False);return
 if not candidates and not recorded and code in manualpaths:
  # Keep the existing estimated paved access only until its first junction
  # with the newly mapped parking network, rather than its old forced exit.
  trace=LineString([n[:2] for n in manualpaths[code]]);hits=[]
  for a,b in edges:
   line=LineString([a[:2],b[:2]]);hit=trace.intersection(line)
   pts=[hit] if hit.geom_type=='Point' and not hit.is_empty else list(hit.geoms) if hit.geom_type=='MultiPoint' else []
   pts += [Point(v) for v in trace.coords if Point(v).distance(line)<=3]
   for q in pts:
    offset=trace.project(q)
    snap=line.interpolate(line.project(q));gap=q.distance(snap);link=LineString([q,snap])
    if any(link.intersection(poly2).length>2.5 for poly2 in polys.values()):continue
    if any(link.crosses(road) for road in roads):continue
    if offset>.01:hits.append((offset,q,a,b,line,snap,gap))
  for offset,q,a,b,line,snap,gap in sorted(hits,key=lambda x:x[0]+x[-1]):
   prefix=substring(trace,0,offset)
   if any(prefix.intersection(poly2).length>2.5 for poly2 in polys.values()):continue
   split=tuple(snap.coords[0])+('retained-manor-prefix',code);dist=line.project(snap)
   g.remove_edge(a,b);g.add_edge(a,split,weight=dist);g.add_edge(split,b,weight=line.length-dist)
   ns=[tuple(p) for p in prefix.coords]
   if gap>1e-6:ns.append(split)
   else:ns[-1]=split
   for u,v in zip(ns,ns[1:]):
    if u!=v:g.add_edge(u,v,weight=math.dist(u[:2],v[:2]))
   candidates.append({'id':'retained-estimated-access-reconnected','point':Point(ns[0][:2]),'node':ns[0],'gap':0})
   review['access_points'].append({'building_id':code,'access_id':'retained-estimated-access-reconnected','status':'Retained estimated paved access prefix joined at its first mapped parking-path junction, not a verified door','coordinates':list(U.transform(*ns[0][:2])),'connector_m':0,'retained_prefix_m':prefix.length+gap,'junction_alignment_m':gap,'retained_prefix_coordinates':[list(U.transform(*n[:2])) for n in ns]});break
 if not candidates:
  print('ACCESS GAP',code,'closest any path',min(LineString([a[:2],b[:2]]).distance(points[0][1]) for a,b in g.edges),'closest main path',min(line.distance(points[0][1]) for line in lines),flush=True)
 assert candidates,('No defensible connected access option',code)
 entries[code]=candidates
for code in targets+[str(i) for i in range(281,290)]:reconnect(code)
review['method']='Reviewed, ground-level path intersections were noded in the Chapter Commons/Townhomes/Apartments plazas and Western Manor parking area; old GIS segments through the three Greek building interiors and older Western Manor manual parking traces were removed. Public OSM pedestrian ways and service/parking aisles were added for Western Manor; arterial/residential road centerlines, private/no-foot ways and grade-separated ways were excluded. Available mapped GIS entrances are restored for Western Manor; otherwise the retained estimated building-edge point is reconnected without crossing building interiors or arterial-road centerlines. No door or all-sides access is invented.'
outreview=R/'work/reviewed-access-recalculation';outreview.mkdir(parents=True,exist_ok=True);(outreview/'reviewed-access-supplement.json').write_text(json.dumps(review,indent=2));print('ACCESS REPAIR',len(review['removed_building_interior_edges']),'building-interior edges removed;',len(new_lines),'mapped Manor segments;',len(review['access_points']),'access options',flush=True)

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
eligible=[r for r in result if r['destination_id']!='102' and r['destination_id'] in original_destinations];held=[];summary={'tested_origins':len(origins),'held_manual_origins':0,'preserved_manual_access_origins':len(manual),'tested_pairs':len(result),'multiple_entrance_buildings':sum(len(v)>1 for v in entries.values()),'fixed_endpoint_max_error_m':max(fixed_errors),'pairs_shorter_over_10m':sum(r['saved_m']>10 for r in result),'max_saving_m':max(r['saved_m'] for r in result),'talley_old':sum(r['talley_nearest_m']<=50 for r in d['rows'] if not r['ends_at_talley'] and r['destination_id'] in original_destinations),'talley_new_partial_sensitivity':sum(r['new_talley'] for r in eligible)+sum(r['talley_nearest_m']<=50 for r in held),'western_new_partial_sensitivity':sum(r['new_western'] for r in eligible)+sum(r['western_nearest_m']<=50 for r in held),'denominator':len(eligible)+len(held),'limits':'All 84 origins recomputed on the same augmented network; 9 manually traced origin accesses preserved, destination entrances optimized. Entrance enabled flag does not verify public access, opening hours, locked doors or current path conditions. Not a replacement published estimate.'};out=R/'work/reviewed-access-recalculation';out.mkdir(exist_ok=True);(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'routes.json').write_text(json.dumps(result));(out/'entrance-counts.json').write_text(json.dumps({code:{'name':buildings[code]['name'],'eligible_entrances':len(a)} for code,a in entries.items()},indent=2));print(json.dumps(summary));print('Wolf Ridge examples',json.dumps(sorted([r for r in result if r['origin_id'].startswith('780')],key=lambda r:r['saved_m'],reverse=True)[:3],default=str)[:1200])
