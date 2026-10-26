#!/usr/bin/env python3
"""Validate the actual aggregate files consumed by the visual comparison."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
for year in [2022,2024,2026]:
    sr={r['scope']:r for r in d['summary'] if r['year']==year}
    for cohort,key in [('All ages','all_ages'),('18–24','age_18_24'),('18–22','age_18_22')]:
        assert sr['Campus site'][key]+sr['Other Wake sites'][key]==sr['Wake County'][key]
        for scope,r in sr.items():
            days=[v for v in d['daily'] if v['year']==year and v['scope']==scope and v['cohort']==cohort]
            assert len(days)==d['matched_days']
            assert sum(v['votes'] for v in days)==r[key]==days[-1]['cumulative']
            assert all(v['cumulative']==sum(t['votes'] for t in days[:i+1]) for i,v in enumerate(days))
        for scope in ['Campus site','Wake County','Other Wake sites']:
            for dim in ['age_group','age','party','race','ethnicity','gender']:
                rows=[v for v in d['demographics'] if v['year']==year and v['scope']==scope and v['dimension']==dim]
                assert sum(v['votes'] for v in rows)==sr[scope]['all_ages']
                assert math.isclose(sum(v['share'] for v in rows),100)
    for r in sr.values():
        assert 0<=r['age_18_22']<=r['age_18_24']<=r['all_ages']
    assert d['qa'][str(year)]['duplicate_accepted_ncid']==0
assert d['full_file_context']['2022']['wake_accepted_early']==219169
assert d['full_file_context']['2022']['campus_accepted_early']==10390
for r in d['summary']:
    exact=[v for v in d['demographics'] if v['year']==r['year'] and v['scope']==r['scope'] and v['dimension']=='age' and v['value'].isdigit() and 18<=int(v['value'])<=24]
    assert sum(v['votes'] for v in exact)==r['age_18_24']
assert d['as_of']<=max(d['qa']['2026']['accepted_early_by_date'])
print('PASS: matched days, cumulative totals, disjoint scopes, demographic sums, age bounds, duplicate checks and locked 2022 baseline.')
