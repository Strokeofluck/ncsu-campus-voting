#!/usr/bin/env python3
"""Build exact, public aggregate evidence targets without exporting voter rows."""
import json,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
audit=json.loads((ROOT/'data/processed/comparison/reference_audit.json').read_text(encoding='utf-8'))['checks']
sources={r['year']:r['source'] for r in audit}
summaries={(r['year'],r['scope']):r for r in d['summary']}
records={}
def slug(value):return re.sub(r'[^a-z0-9]+','-',str(value).lower()).strip('-')
def sid(y,scope,field):return f'summary-{y}-{slug(scope)}-{slug(field)}'
def did(y,dim,value):return f'demographic-{y}-{slug(dim)}-{slug(value)}'
def filters(y,scope):
    r=summaries[y,scope]
    conditions=['county_desc = WAKE','ballot_req_type ∈ ONE-STOP, ONE STOP, EARLY VOTING','ballot_rtn_status = ACCEPTED',f"{r['start_date']} ≤ ballot_rtn_dt ≤ {r['end_date']} (inclusive)"]+([] if scope=='Wake County' else [f"site_name {'=' if scope=='Campus site' else '≠'} {d['site_mapping'][str(y)]}"])
    return [f'{y}: {condition}' for condition in conditions]
def source(y):
    return {'year':y,**sources[y],'catalog':f'https://www.ncsbe.gov/results-data/absentee-and-provisional-data#:~:text={y}%20Nov%20'+{2022:'08',2024:'05',2026:'03'}[y]+',Absentee%20by%20County'}
def add(key,label,value,unit,formula,inputs,years,where,breakdown=None):
    assert key not in records,key
    assert math.isfinite(value)
    records[key]={'id':key,'label':label,'value':value,'unit':unit,'formula':formula,'inputs':inputs,'sources':[source(y) for y in years],'filters':where,'breakdown':breakdown or [],'cutoff':d['as_of'],'matched_days':d['matched_days']}
def inp(label,value,unit='ballots',target=None):return {'label':label,'value':value,'unit':unit,**({'target':target} if target else {})}
fields={'all_ages':'All ages','age_18_24':'Ages 18–24','age_18_22':'Ages 18–22','age_18_24_share':'Ages 18–24 share','same_day_registration':'Same-day registration'}
for (year,scope),r in summaries.items():
    for field,label in fields.items():
        where=filters(year,scope)
        if field.startswith('age_18_24'):where+=['18 ≤ source age ≤ 24 for the numerator']
        elif field=='age_18_22':where+=['18 ≤ source age ≤ 22']
        elif field=='same_day_registration':where+=['sdr ∈ Y, YES (all ages)']
        is_share=field=='age_18_24_share';key=sid(year,scope,field)
        if is_share:
            formula=f"{r['age_18_24']:,} ÷ {r['all_ages']:,} × 100 = {r[field]:.6f}%"
            inputs=[inp('Accepted ballots, ages 18–24',r['age_18_24'],target=sid(year,scope,'age_18_24')),inp('All accepted ballots, same scope and period',r['all_ages'],target=sid(year,scope,'all_ages'))]
        else:
            formula=f'Count accepted records satisfying the filters = {r[field]:,}'
            inputs=[inp(f'{label}, {scope}, {year}',r[field])]
        add(key,f'{label} · {scope} · {year}',r[field],'%' if is_share else 'ballots',formula,inputs,[year],where)

demographic_lookup={}
category_names={'DEM':'Democratic','REP':'Republican','UNA':'Unaffiliated','OTHER_PARTIES':'Other registered parties','F':'Female (F)','M':'Male (M)','U':'Not specified (U)'}
for year in (2022,2024,2026):
    all_rows=[r for r in d['demographics'] if r['year']==year and r['scope']=='Campus site']
    total=summaries[year,'Campus site']['all_ages']
    dimensions={'all':{'all':total}}
    for dim in ['age_group','party','race','ethnicity','gender']:
        values={r['value']:r['votes'] for r in all_rows if r['dimension']==dim}
        assert sum(values.values())==total
        if dim=='party':values={**{v:values.get(v,0) for v in ['DEM','REP','UNA']},'OTHER_PARTIES':sum(count for value,count in values.items() if value not in ['DEM','REP','UNA'])}
        dimensions[dim]=values
    for dim,values in dimensions.items():
        # Every profile category shown for either baseline must have a real zero target if absent.
        universe=set(values)
        if dim not in ['all','party']:
            universe|={r['value'] for r in d['demographics'] if r['scope']=='Campus site' and r['dimension']==dim}
        for value in sorted(universe):
            count=values.get(value,0);rate=count/total*100;where=filters(year,'Campus site')
            if dim=='age_group':where.append(f'Derived age_group = {value}; groups use inclusive source ages 18–24, 25–34, 35–44, 45–64, 65–120; invalid/outside ages remain separate')
            elif dim=='party':where.append('voter_party_code not in DEM, REP, UNA' if value=='OTHER_PARTIES' else f'voter_party_code = {value}')
            elif dim!='all':where.append(f'{dim} = {value}')
            if count==0:where.append('Category absent after the complete dimension reconciles to all site ballots; represented as zero')
            breakdown=[]
            if dim=='age_group':
                for r in all_rows:
                    if r['dimension']!='age':continue
                    try:age=int(r['value'])
                    except ValueError:age=None
                    group=next((name for lo,hi,name in [(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')] if age is not None and lo<=age<=hi),'Unknown / outside range')
                    if group==value:breakdown.append(inp('Source age '+r['value'],r['votes']))
                assert sum(x['value'] for x in breakdown)==count
            if dim=='party' and value=='OTHER_PARTIES':breakdown=[inp('Source party '+r['value'],r['votes']) for r in all_rows if r['dimension']=='party' and r['value'] not in ['DEM','REP','UNA']]
            display='All site ballots' if dim=='all' else category_names.get(value,value)
            inputs=[inp(f'{display}, accepted ballots',count),inp('All accepted campus-site ballots',total,target=sid(year,'Campus site','all_ages'))]
            add(did(year,dim,value),f'{display} · {"Western Boulevard" if year==2026 else "Talley"} · {year}',rate,'%',f'{count:,} ÷ {total:,} × 100 = {rate:.6f}%',inputs,[year],where,breakdown)
            demographic_lookup[year,dim,value]=(count,total,rate)

for base in (2022,2024):
    for (year,dim,value),(before,total,before_rate) in list(demographic_lookup.items()):
        if year!=base:continue
        after,after_total,after_rate=demographic_lookup[2026,dim,value]
        difference=after_rate-before_rate
        add(f'change-{base}-{slug(dim)}-{slug(value)}',f'{category_names.get(value,value)} · change from {base} to 2026',difference,'percentage points',f'({after:,} ÷ {after_total:,} × 100) − ({before:,} ÷ {total:,} × 100) = {difference:+.6f} percentage points',
            [inp(f'{base} share',before_rate,'%',did(base,dim,value)),inp('2026 share',after_rate,'%',did(2026,dim,value))],[base,2026],filters(base,'Campus site')+filters(2026,'Campus site')+[f'Dimension = {dim}; category = {value}; subtract unrounded shares'])
    for scope in ['Campus site','Wake County','Other Wake sites']:
        for field in ['all_ages','age_18_24','age_18_22','same_day_registration']:
            old=summaries[base,scope][field];new=summaries[2026,scope][field];change=(new/old-1)*100
            add(f'growth-{base}-{slug(scope)}-{slug(field)}',f'{fields[field]} · {scope} · 2026 change versus {base}',change,'%',f'({new:,} − {old:,}) ÷ {old:,} × 100 = {change:+.6f}%',
                [inp(f'{base} ballots',old,target=sid(base,scope,field)),inp('2026 ballots',new,target=sid(2026,scope,field))],[base,2026],filters(base,scope)+filters(2026,scope)+[f'Ballot cohort = {fields[field]}'])
for scope in ['Campus site','Wake County']:
    for field in ['all_ages','age_18_24']:
        old=summaries[2024,scope][field];new=summaries[2026,scope][field];ratio=new/old*100
        add(f'benchmark-{slug(scope)}-{slug(field)}',f'{fields[field]} · {scope} · 2026 as a percentage of 2024',ratio,'%',f'{new:,} ÷ {old:,} × 100 = {ratio:.6f}%',[inp('2026 ballots',new,target=sid(2026,scope,field)),inp('2024 ballots',old,target=sid(2024,scope,field))],[2024,2026],filters(2024,scope)+filters(2026,scope)+['A historical ballot-volume ratio, not a turnout rate or forecast'])
for year in (2022,2024,2026):
    campus=summaries[year,'Campus site']['age_18_24'];county=summaries[year,'Wake County']['age_18_24'];share=campus/county*100
    add(f'county-share-{year}',f'Campus site share of Wake’s ages 18–24 early ballots · {year}',share,'%',f'{campus:,} ÷ {county:,} × 100 = {share:.6f}%',
        [inp('Campus-site ballots, ages 18–24',campus,target=sid(year,'Campus site','age_18_24')),inp('Wake County ballots, ages 18–24',county,target=sid(year,'Wake County','age_18_24'))],[year],filters(year,'Wake County')+['18 ≤ source age ≤ 24; numerator also matches the campus-site label'])
payload={'classification':'Project calculations from official NCSBE ballot records; not values printed on the official catalog page','as_of':d['as_of'],'records':records}
json_text=json.dumps(payload,ensure_ascii=False,indent=2)
(ROOT/'data/processed/comparison/figure_sources.json').write_text(json_text+'\n',encoding='utf-8')
template=(ROOT/'report-source/figure-source.html').read_text(encoding='utf-8')
assert template.count('__FIGURE_SOURCES_JSON__')==1
(ROOT/'figure-source.html').write_text(template.replace('__FIGURE_SOURCES_JSON__',json_text.replace('<','\\u003c')),encoding='utf-8')
print(f'Built {len(records)} exact figure-source targets from validated aggregates.')
