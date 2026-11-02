"""Publish manually observed Google UI checks separately from the GIS route model.

Observed in the browser on 2026-11-01 using the same public endpoint coordinates.
Google displayed rounded mileages; this is not an API response or a field survey.
"""
import csv,json
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';SOURCE=ROOT/'data/sources/google-maps/2026-11-01';SOURCE.mkdir(parents=True,exist_ok=True)
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));supp={r['id']:r for r in s['queries']['campus_estimated_access']['rows']};sites={r['id']:r for r in s['queries']['campus_walk_sites']['rows']}
# Primary suggested walking route visibly reported by Google Maps. Names are
# Google's resolved public place labels, not proof of the intended room/door.
observed=[
 ('271A','talley',.7,16,'Morrill Dr','Avent Ferry Residence Halls, 2110 Avent Ferry Rd'),
 ('271A','western',.8,18,'Western Blvd and Rocky Branch Trl','Avent Ferry Residence Halls, 2110 Avent Ferry Rd'),
 ('012','talley',.4,9,'Dunn Ave','Gold Residence Hall, 70 Pullen Rd'),
 ('012','western',1.5,33,'Western Blvd','Gold Residence Hall, 70 Pullen Rd'),
 ('079','talley',.5,10,'Dan Allen Dr','Frankly Insightful, 111 Friendly Dr'),
 ('079','western',.9,21,'Dan Allen Dr and Rocky Branch Trl','Frankly Insightful, 111 Friendly Dr'),
 ('013','talley',.4,9,'Dunn Ave','Welch Residence Hall, 80 Pullen Rd'),
 ('013','western',1.4,32,'Western Blvd','Welch Residence Hall, 80 Pullen Rd'),
]
checks=[]
for code,site,miles,minutes,via,resolved in observed:
 row=supp[code];dest=sites['102' if site=='talley' else '131'];origin=row['access_coordinates'];end=dest['coordinates'];pin=lambda xy:f'{xy[1]},{xy[0]}'
 checks.append({'building_id':code,'building_name':row['name'],'site':site,'site_name':dest['name'],'observed_on':'2026-11-01','gis_route_meters':row[site+'_m'],'gis_route_miles':row[site+'_m']/1609.344,'google_display_miles':miles,'google_display_minutes':minutes,'google_suggested_via':via,'google_resolved_origin':resolved,'google_resolved_destination':'Port City Java, 2610 Cates Ave' if site=='talley' else 'Western Boulevard Buisness Services, 1220 Varsity Dr','origin_coordinates_lon_lat':origin,'destination_coordinates_lon_lat':end,'google_walking_url':'https://www.google.com/maps/dir/?'+urlencode({'api':1,'origin':pin(origin),'destination':pin(end),'travelmode':'walking'}),'entrance_verified':False})
payload={'checked_on':'2026-11-01','collection_method':'Manually observed primary suggested walking route in the Google Maps browser UI. No API, private account data or field measurement is included.','coordinate_order':'longitude, latitude','scope':'Eight walks for the four original supplemental buildings, using the same access points and site pins as the GIS explorer.','precision_and_limits':'Google mileages were displayed to one decimal mile and times to whole minutes. They are routing estimates for Google suggested paths, not measurements of the GIS polylines. Google resolved some pins to a complex, cafe or nearby business; actual residence door and election-room entrance remain unverified. No Google value replaces GIS path distance, geometry, baseline average or routine-trip input.','rows':checks}
(SOURCE/'walking-checks.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields=['building_name','site_name','observed_on','gis_route_miles','google_display_miles','google_display_minutes','google_suggested_via','google_resolved_origin','google_resolved_destination','google_walking_url','entrance_verified']
with (OUT/'google-walking-comparison.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(checks)
rows=''.join(f'<tr><th>{r["building_name"]}</th><td>{"Talley (2022)" if r["site"]=="talley" else "Western (2026)"}</td><td>{r["gis_route_miles"]:.2f} mi</td><td><a href="{r["google_walking_url"].replace("&","&amp;")}">{r["google_display_miles"]:.1f} mi · {r["google_display_minutes"]} min</a></td></tr>' for r in checks)
block='''<!-- BEGIN GOOGLE WALKING CHECKS -->
<details id="google-walking-checks"><summary>Google walking-map checks and what “accurate mileage” means</summary><p>Checked November 1, 2026. The explorer’s mileage measures the actual displayed GIS route, including its modeled endpoint connectors: miles = route meters ÷ 1,609.344. It is rounded to two decimals. Google links use the same public coordinate pins with walking mode, but Google may suggest a different path and displays rounded mileage. Its numbers are therefore a separate check, not a replacement label for a different line.</p><table><thead><tr><th>Building</th><th>Destination</th><th>GIS path shown</th><th>Google suggested walk</th></tr></thead><tbody>'''+rows+'''</tbody></table><p>For example, Aurora → Western is 0.69 mile on the GIS path and 0.8 mile on Google’s suggested walk. These are different modeled paths, not a measured 0.11-mile error. Google’s displayed values are rounded to tenths of a mile. Exact coordinates and extra decimals do not verify which doorway is actually used. Google resolved the Talley pin to Port City Java and the University Towers start to a business at 111 Friendly Drive; those labels are retained in the audit so they cannot be mistaken for confirmed election-room or residence entrances. Gold, Welch and University Towers retain their estimated-access labels; Aurora uses its recovered GIS entrance. A field check or confirmed door locations would be needed for an entrance-to-entrance measurement.</p><p>The expanded housing lists now show both mileages for every building and offer Google walking links for each site. Those links are comparisons, not claims that the displayed GIS line is Google’s route. Original baseline averages and routine-route counts are unchanged. <a href="data/processed/campus-walk/google-walking-comparison.csv">Comparison CSV</a> · <a href="data/sources/google-maps/2026-11-01/walking-checks.json">Observed values, resolved labels and exact pins</a> · <a href="https://developers.google.com/maps/documentation/urls/get-started">Google Maps walking-link documentation</a> · <a href="https://packthepolls.dasa.ncsu.edu/elections/early-voting/">NC State’s own walking guidance</a>.</p></details>
<!-- END GOOGLE WALKING CHECKS -->'''
p=ROOT/'report-source/article-references.html';text=p.read_text(encoding='utf-8');start='<!-- BEGIN GOOGLE WALKING CHECKS -->';end='<!-- END GOOGLE WALKING CHECKS -->'
if start in text:a=text.index(start);b=text.index(end,a)+len(end);text=text[:a]+block+text[b:]
else:text=text.replace('<!-- END CAMPUS DISPLAY INTERACTIONS -->',block+'\n<!-- END CAMPUS DISPLAY INTERACTIONS -->')
p.write_text(text,encoding='utf-8');print('Prepared eight independently observed Google walking comparisons; model inputs unchanged.')
