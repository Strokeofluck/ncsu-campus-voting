import sys,json,runpy,math,csv,copy
from pathlib import Path
import argparse,zipfile
parser=argparse.ArgumentParser();parser.add_argument('--library-dir');args=parser.parse_args()
if args.library_dir:sys.path.insert(0,args.library_dir)
import networkx as nx
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
R=Path(__file__).resolve().parents[1];O=R/'data/processed/expanded-housing'
raw=R/'data/raw/campus-walk';raw.mkdir(parents=True,exist_ok=True)
if not (raw/'manifest.json').exists():
 with zipfile.ZipFile(R/'data/processed/campus-walk/official-gis-snapshot.zip') as z:z.extractall(raw)
sys.argv=['build','--network-only'];e=runpy.run_path(str(R/'scripts/build_campus_walking_routes.py'))
g=e['g'];P=e['project'];U=e['unproject'];traces=json.loads((O/'manual-connections.json').read_text(encoding='utf-8'));old=json.loads((O/'passby.json').read_text(encoding='utf-8'));inventory=json.loads((O/'routes.json').read_text(encoding='utf-8'))['rows'];extra=[r for r in inventory if not r['available']]
points=lambda vv:[tuple(P.transform(*p)) for p in vv]
paths={'291':points(traces['pi']),'127H':points(traces['johnston']),'western_spine':points(traces['western_spine'])}
paths.update({code:points(v) for code,v in traces['branches'].items()})
coords={n:n for n in g};accesses={};origin_points={};audit=[]
for dest in old['destinations']:
 p=Point(P.transform(*dest['coordinates']));idx=int(e['tree'].nearest(p));line=e['segments'][idx];snap=line.interpolate(line.project(p));assert p.distance(snap)<=30
 accesses[dest['id']]={'point':p,'snap':snap,'edge_index':idx,'offset':line.project(snap),'connector_m':p.distance(snap)}
for key in ['291','127H','western_spine']:
 p=Point(paths[key][-1]);idx=int(e['tree'].nearest(p));line=e['segments'][idx];snap=line.interpolate(line.project(p));assert p.distance(snap)<.1
 accesses['gateway-'+key]={'point':p,'snap':snap,'edge_index':idx,'offset':line.project(snap),'connector_m':p.distance(snap)};paths[key][-1]=tuple(snap.coords[0])
groups={}
for a in accesses.values():groups.setdefault(a['edge_index'],[]).append(a)
for idx,items in groups.items():
 u,v=e['edges'][idx];g.remove_edge(u,v);chain=[(0,u),(e['segments'][idx].length,v)]
 for a in items:a['node']=tuple(a['snap'].coords[0]);chain.append((a['offset'],a['node']))
 chain.sort(key=lambda x:x[0])
 for (d1,n1),(d2,n2) in zip(chain,chain[1:]):
  if n1!=n2:g.add_edge(n1,n2,weight=d2-d1)
for row in extra:
 code=row['id'];poly=e['polygons'][code]
 while len(paths[code])>1 and poly.contains(Point(paths[code][0])):paths[code].pop(0)
 start=nearest_points(poly.boundary,Point(paths[code][0]))[0];paths[code].insert(0,tuple(start.coords[0]));origin_points[code]=start
for code,path in paths.items():
 line=LineString(path);collisions=[]
 for i in e['polytree'].query(line):
  other=e['polykeys'][int(i)];length=line.intersection(e['polygons'][other]).length
  if length>2.5:collisions.append({'building':other,'meters_inside':round(length,2)})
 audit.append({'connection':code,'length_m':line.length,'footprint_intersections':collisions})
 for a,b in zip(path,path[1:]):
  if a!=b:g.add_edge(a,b,weight=math.dist(a,b),manual_trace=True)
(O/'manual-connection-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8');print('AUDIT',json.dumps(audit))
assert not any(r['footprint_intersections'] for r in audit),'Repair footprint intersections before computing results'
rows=[];sites={s['id']:Point(P.transform(*s['coordinates'])) for s in old['site_points']}
for origin in extra:
 code=origin['id'];start=paths[code][0];lengths,shortpaths=nx.single_source_dijkstra(g,start,weight='weight')
 for dest in old['destinations']:
  b=accesses[dest['id']];path=shortpaths[b['node']];line=LineString(path+[tuple(b['point'].coords[0])]);simple=line.simplify(1,preserve_topology=True)
  row={'origin_id':code,'origin_name':origin['name'],'housing_group':origin['group'],'destination_id':dest['id'],'destination_name':dest['name'],'destination_kind':dest['kind'],'gis_use_name':next(r['gis_use_name'] for r in old['rows'] if r['destination_id']==dest['id']),'ends_at_talley':dest['id']=='102','route_m':lengths[b['node']]+b['connector_m'],'geometry':{'type':'LineString','coordinates':[list(U.transform(*xy)) for xy in simple.coords]},'route_source':'Manually traced approximate access paths plus frozen NC State GIS network','manual_trace':True,'estimated_access':True}
  for site,id in [('talley','102'),('western','131')]:row[site+'_nearest_m']=line.distance(e['polygons'][id]);row[site+'_entrance_nearest_m']=line.distance(sites[id])
  rows.append(row)
new=copy.deepcopy(old);new['rows'].extend(rows)
for r in extra:new['origins'].append({'id':r['id'],'name':r['name'],'group':r['group'],'coordinates':list(U.transform(*paths[r['id']][0]))})
for s in new['summary']:
 eligible=[r for r in new['rows'] if s['include_talley_destinations'] or not r['ends_at_talley']];key=s['site']+('_nearest_m' if s['distance_basis']=='footprint' else '_entrance_nearest_m');near=sum(r[key]<=s['radius_m'] for r in eligible);s.update(total_routes=len(eligible),near_routes=near,share_pct=near/len(eligible)*100)
new['manual_connections']=traces;new['manual_connection_audit']=audit;new['definition']='84 housing origins: 75 preserved GIS origin route sets plus nine with manually traced approximate connections to the same frozen GIS network. One shortest path per origin/destination pair, equal pair weights. Traces follow visible Google Maps walking/access paths; not field-surveyed or observed traffic. Both sites retain the same footprint and entrance definitions.'
for name,value in [('all-housing-passby.json',new),('manual-supplement-routes.json',rows),('manual-connections.json',traces),('manual-connection-audit.json',audit)]:(O/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
for name,value in [('all-housing-passby-routes.csv',new['rows']),('all-housing-passby-summary.csv',new['summary'])]:
 fields=[k for k in value[0] if k!='geometry']+(['manual_trace','route_source'] if name.endswith('routes.csv') else [])
 with (O/name).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(value)
print('RESULT',json.dumps([s for s in new['summary'] if s['distance_basis']=='footprint' and s['radius_m']==50 and not s['include_talley_destinations']]))
