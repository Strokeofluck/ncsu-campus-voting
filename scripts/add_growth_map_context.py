"""Document derived precinct count growth without changing reviewed count rows."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def add_growth_map_context(snapshot):
    source=snapshot['queries']['geography']['source']
    label='Precinct ballot growth, 2022 to 2026'
    source['metricDefinitions']=[m for m in source.get('metricDefinitions',[]) if m.get('label')!=label]+[{
        'label':label,'formula':'growth = (2026 count - 2022 count) / 2022 count * 100; absolute change = 2026 count - 2022 count',
        'definition':'Join the same recorded residential precinct code and selected age cohort in both years. The count is either all accepted early ballots at any Wake location (wake_ballots) or ballots at Talley in 2022 and Western Boulevard in 2026 (site_ballots). Match the full 17-day early-voting periods. Missing area/year is unavailable, never zero. A zero baseline has undefined percentage growth; a positive current count with zero baseline is separately marked new from zero. Current GIS polygons are a reference, not harmonized historical boundaries; changes may reflect redistricting or population changes as well as voting behavior. No turnout denominator, student identifier or causal estimate is supplied.',
        'componentIds':['voting-precinct-map']}]
if __name__=='__main__':
    p=ROOT/'report-source/snapshot.json';s=json.loads(p.read_text(encoding='utf-8'));add_growth_map_context(s);s['buildStatus']='updating';p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
