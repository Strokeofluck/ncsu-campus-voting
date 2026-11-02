"""Remeasure all 80 displayed housing walks from coordinates, not saved lengths."""
import argparse,csv,json,math,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library-dir',type=Path);args=p.parse_args()
 if args.library_dir:sys.path.insert(0,str(args.library_dir))
 from pyproj import Transformer,Geod
 transform=Transformer.from_crs(4326,32119,always_xy=True).transform;geod=Geod(ellps='WGS84')
 s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
 supplements={r['id']:r for r in s['queries']['campus_estimated_access']['rows']}
 sites={r['id']:r for r in s['queries']['campus_walk_sites']['rows']};out=[]
 def length(coords):
  points=[transform(*p) for p in coords]
  return sum(math.dist(a,b) for a,b in zip(points,points[1:]))
 for original in s['queries']['campus_walking_routes']['rows']:
  r=original if original['available'] else supplements[original['id']]
  for key,site_id in [('talley','102'),('western','131')]:
   route=r[key+'_route'];network=route['geometry']['coordinates'];start=route['origin_connector']['coordinates'];end=route['destination_connector']['coordinates']
   parts=[length(coords) for coords in [network,start,end]];total=sum(parts)
   geo=sum(geod.line_length(*zip(*coords)) for coords in [network,start,end])
   origin=r.get('entrance_coordinates') or r['access_coordinates']
   gaps=[math.dist(transform(*a),transform(*b)) for a,b in [(start[0],origin),(start[-1],network[0]),(network[-1],end[0]),(end[-1],sites[site_id]['coordinates'])]]
   assert abs(total-route['total_m'])<.002,(r['name'],key,total,route['total_m'])
   assert max(gaps)<.002 and abs(geo-total)/total<.001
   assert f'{total/1609.344:.2f}'==f'{r[key+"_m"]/1609.344:.2f}'
   out.append(dict(building_id=r['id'],building=r['name'],destination=key,access='estimated building edge' if r.get('estimated_access') else 'recovered GIS entrance' if r.get('recovered_mapped_entrance') else 'mapped GIS entrance',network_remeasured_m=parts[0],origin_connector_remeasured_m=parts[1],destination_connector_remeasured_m=parts[2],remeasured_total_m=total,saved_total_m=route['total_m'],absolute_difference_m=abs(total-route['total_m']),geodesic_total_m=geo,max_endpoint_gap_m=max(gaps),display_miles=f'{total/1609.344:.2f}',display_minutes_at_80_m_per_min=f'{total/80:.1f}'))
 assert len(out)==80
 destination=ROOT/'data/processed/campus-walk';destination.mkdir(parents=True,exist_ok=True)
 with (destination/'route-length-audit.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(out[0]));writer.writeheader();writer.writerows(out)
 summary={'routes_checked':len(out),'max_saved_length_difference_m':max(r['absolute_difference_m'] for r in out),'max_geodesic_difference_pct':max(abs(r['geodesic_total_m']-r['remeasured_total_m'])/r['remeasured_total_m']*100 for r in out),'max_endpoint_gap_m':max(r['max_endpoint_gap_m'] for r in out),'all_displayed_mile_values_match':True,'formula':'Sum projected lengths of network geometry plus both dotted entrance connectors (EPSG:32119, metres). Miles = total / 1609.344. Minutes = total / 80. Independently cross-check WGS84 ellipsoidal length.','limits':'Checks distance along the drawn coordinates and endpoint continuity, not present-day walkability, best real-world path, door accuracy, crossing delays or historical 2022 conditions. Three origins are building-edge estimates.','example':next(r for r in out if r['building']=='Wood Hall A' and r['destination']=='western')}
 (destination/'route-length-audit.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
