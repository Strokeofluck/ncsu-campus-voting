#!/usr/bin/env python3
"""Export matched same-day-registration counts, growth and ballot shares."""
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def build_rows(data):
    summaries={(row['year'],row['scope']):row for row in data['summary']}
    rows=[]
    for scope in ('Campus site','Wake County','Other Wake sites'):
        current=summaries[2026,scope]
        for baseline in (2022,2024):
            previous=summaries[baseline,scope]
            for row in (previous,current):
                assert row['all_ages']>0 and 0<=row['same_day_registration']<=row['all_ages']
                assert row['matched_days']==data['matched_days']
            old_share=previous['same_day_registration']/previous['all_ages']*100
            new_share=current['same_day_registration']/current['all_ages']*100
            rows.append({
                'scope':scope,'baseline_year':baseline,'comparison_year':2026,
                'matched_days':data['matched_days'],'baseline_start_date':previous['start_date'],
                'baseline_end_date':previous['end_date'],'comparison_start_date':current['start_date'],
                'comparison_end_date':current['end_date'],'baseline_all_ballots':previous['all_ages'],
                'comparison_all_ballots':current['all_ages'],
                'all_ballots_change_pct':(current['all_ages']/previous['all_ages']-1)*100,
                'baseline_same_day_registration':previous['same_day_registration'],
                'comparison_same_day_registration':current['same_day_registration'],
                'same_day_registration_change_pct':(current['same_day_registration']/previous['same_day_registration']-1)*100,
                'baseline_same_day_share_pct':old_share,'comparison_same_day_share_pct':new_share,
                'same_day_share_change_pp':new_share-old_share,
            })
    return rows

def write_comparison(data):
    rows=build_rows(data)
    path=ROOT/'data/processed/comparison/same_day_registration_comparison.csv'
    with path.open('w',encoding='utf-8',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    return rows

if __name__=='__main__':
    data=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
    print(json.dumps(write_comparison(data),indent=2))
