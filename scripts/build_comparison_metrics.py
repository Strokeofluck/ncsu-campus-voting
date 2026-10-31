#!/usr/bin/env python3
"""Expand validated matched counts into auditable baseline comparisons."""
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS={'all_ages':'All ages','age_18_24':'Ages 18–24','age_18_22':'Ages 18–22','same_day_registration':'Same-day registration (all ages)'}

def write_metrics(data):
    lookup={(r['year'],r['scope']):r for r in data['summary']}
    rows=[]
    for baseline in (2022,2024):
        for scope in ('Campus site','Wake County','Other Wake sites'):
            before=lookup[baseline,scope];after=lookup[2026,scope]
            for field,label in FIELDS.items():
                a=before[field];b=after[field]
                old_share=a/before['all_ages']*100;new_share=b/after['all_ages']*100
                old_county=a/lookup[baseline,'Wake County'][field]*100
                new_county=b/lookup[2026,'Wake County'][field]*100
                rows.append({'baseline_year':baseline,'comparison_year':2026,'scope':scope,'metric':label,'field':field,
                    'matched_days':data['matched_days'],'baseline_start':before['start_date'],'baseline_end':before['end_date'],
                    'comparison_start':after['start_date'],'comparison_end':after['end_date'],
                    'baseline_ballots':a,'comparison_ballots':b,'ballot_change':b-a,'ballot_change_pct':(b/a-1)*100,
                    'baseline_share_of_scope_ballots_pct':old_share,'comparison_share_of_scope_ballots_pct':new_share,
                    'scope_share_change_pp':new_share-old_share,
                    'baseline_share_of_wake_same_cohort_pct':old_county,'comparison_share_of_wake_same_cohort_pct':new_county,
                    'wake_cohort_share_change_pp':new_county-old_county})
    path=ROOT/'data/processed/comparison/expanded_matched_comparisons.csv'
    with path.open('w',encoding='utf-8',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return rows

if __name__=='__main__':
    data=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
    print(f'Wrote {len(write_metrics(data))} matched comparisons; all ages and overlapping cohorts remain separate.')
