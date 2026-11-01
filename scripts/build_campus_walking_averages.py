"""Calculate paired, equally weighted building averages from reviewed route distances."""
import csv,json,math,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
d=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));rows=[]
for group in ['All housing','Residence halls','Wolf Village apartments','Wolf Ridge apartments']:
 candidates=[r for r in d['rows'] if group=='All housing' or r['group']==group]
 paired=[r for r in candidates if r['available'] and all(isinstance(r.get(k),(int,float)) for k in ['talley_m','western_m','difference_m'])]
 count=len(paired);old=math.fsum(r['talley_m'] for r in paired);new=math.fsum(r['western_m'] for r in paired)
 row={'group':group,'total_buildings':len(candidates),'included_buildings':count,'excluded_buildings':len(candidates)-count,'sum_talley_m':old,'sum_western_m':new,'mean_talley_m':old/count,'mean_western_m':new/count,'mean_change_m':(new-old)/count,'median_change_m':statistics.median(r['difference_m'] for r in paired),'farther_buildings':sum(r['difference_m']>0 for r in paired),'closer_buildings':sum(r['difference_m']<0 for r in paired),'unchanged_buildings':sum(r['difference_m']==0 for r in paired)}
 assert math.isclose(row['mean_change_m'],math.fsum(r['difference_m'] for r in paired)/count,abs_tol=1e-9)
 rows.append(row)
payload={'gis_retrieved_at':d['retrieved_at'],'weighting':'One equal weight per building with usable routes to BOTH sites; no occupancy weights. Four unavailable buildings are excluded, never assigned zero.','rows':rows}
(OUT/'averages.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'averages.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
p=ROOT/'report-source/snapshot.json';s=json.loads(p.read_text(encoding='utf-8'))
s['queries']['campus_walk_averages']={'rows':rows,'source':{'label':'Paired building-average walking distances from the NC State GIS model','provider':'Project calculations from public NC State GIS','executedAt':d['retrieved_at'],'period':'Same current GIS route snapshot for both Talley (2022) and Western Boulevard (2026) destinations','files':['data/processed/campus-walk/distances.csv','data/processed/campus-walk/averages.csv'],'filters':['Same buildings with usable routes to BOTH destinations','Equal weight per building; no student-occupancy weighting','Missing routes excluded from both denominators, never zero'],'metricDefinitions':[{'label':'Paired average walking change','formula':'mean_talley_m = sum(talley_m) / paired_building_count; mean_western_m = sum(western_m) / same_paired_building_count; mean_change_m = mean_western_m - mean_talley_m = mean(western_m - talley_m); minutes = metres / selected_pace_m_per_min','definition':'A mean across included housing buildings, not students. Each included building contributes once regardless of beds, occupancy, footprint or apartments. All-housing totals pool residence halls, Wolf Village and Wolf Ridge; show the subgroup results because housing types have different changes. Four buildings lack usable routes and remain excluded. The route and endpoint uncertainties of the original walking model also apply to these averages.','componentIds':['voting-campus-walking-average']}],'evidenceFlow':[{'title':'Reproducible building arithmetic','detail':'scripts/build_campus_walking_averages.py; data/processed/campus-walk/averages.json and averages.csv. Independent CSV/Decimal audit: scripts/test_campus_walking_averages.py.'}]}}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in rows:print(r['group'],r['included_buildings'],'of',r['total_buildings'],'mean change',round(r['mean_change_m'],3),'m')
