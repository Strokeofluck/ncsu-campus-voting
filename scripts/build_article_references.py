"""Build the focused 2022–2026 article reference page from reviewed counts."""
import json,re
from datetime import date
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
AGES=['18–24','25–34','35–44','45–64','65+']
def nice(day):
 d=date.fromisoformat(day)
 return f'{d:%B} {d.day}, {d.year}'
def rate(value):return f'{value:+.1f}%'
def steps(before,after):
 difference=after-before;growth=difference/before*100
 return ''.join(f'<li>{escape(text)}</li>' for text in [f'{after:,} − {before:,} = {difference:,} ballots',f'{difference:,} ÷ {before:,} × 100 ≈ {growth:.1f}%'])

def main():
 s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
 rows=s['queries']['age_growth_benchmarks']['rows']
 assert [r['cohort'] for r in rows]==AGES
 for r in rows:
  growth={name:float(Fraction(r[f'{name}_ballots_2026']-r[f'{name}_ballots_2022'],r[f'{name}_ballots_2022'])*100) for name in ['site','county']}
  for name in growth:assert abs(r[name+'_growth_pct']-growth[name])<1e-10
  assert abs(r['site_growth_gap_pp']-(growth['site']-growth['county']))<1e-10
 periods={y:next(r for r in s['queries']['summary']['rows'] if r['year']==y and r['scope']=='Campus site') for y in [2022,2026]}
 period=f"Talley: {nice(periods[2022]['start_date'])}–{nice(periods[2022]['end_date'])}. Western Boulevard: {nice(periods[2026]['start_date'])}–{nice(periods[2026]['end_date'])}. First 16 days in both years; 2026 is preliminary."
 records=json.loads((ROOT/'data/processed/comparison/figure_sources.json').read_text(encoding='utf-8'))['records']
 sources=[]
 for year in [2022,2026]:
  original=records[f'summary-{year}-campus-site-all-ages']['sources'][0]
  details=''.join(f'<dt>{label}</dt><dd><code>{escape(str(original[key]))}</code></dd>' for label,key in [('Source last modified (UTC)','last_modified'),('Downloaded (UTC)','downloaded_at'),('Archive SHA-256','sha256'),('Wake CSV SHA-256','wake_csv_sha256')])
  sources.append(f'<article class="source-card"><h3>{year} · {"Talley Student Union" if year==2022 else "Western Boulevard Business Services"}</h3><p>Extract <code>{escape(original["member"])}</code> from the original ZIP.</p><p><a href="{escape(original["url"],quote=True)}">Download original NCSBE ZIP</a> · <a href="{escape(original["listing_url"],quote=True)}" target="_blank" rel="noopener">Official file listing</a></p><details><summary>Source snapshot and hashes</summary><dl>{details}</dl></details></article>')
 first=rows[0]
 multiplier=Fraction(first['county_ballots_2026'],first['county_ballots_2022'])
 benchmark=first['site_ballots_2022']*multiplier
 shortfall=benchmark-first['site_ballots_2026']
 benchmark_steps=[
  f"Wake multiplier: {first['county_ballots_2026']:,} ÷ {first['county_ballots_2022']:,} ≈ {float(multiplier):.4f}",
  f"Benchmark: {first['site_ballots_2022']:,} × ({first['county_ballots_2026']:,} ÷ {first['county_ballots_2022']:,}) ≈ {round(benchmark):,} ballots",
  f"Actual: {first['site_ballots_2026']:,} ballots",
  f"Difference: {float(benchmark):,.4f} − {first['site_ballots_2026']:,} ≈ {round(shortfall):,} ballots"]
 google_groups=[]
 for a in s['queries']['campus_google_averages']['rows']:
  group=a['group'];pairs=[r for r in s['queries']['campus_google_walks']['rows'] if group=='All housing' or r['group']==group]
  body=''.join('<tr><th scope="row">'+escape(r['name'])+'</th>'+''.join(f'<td><a href="{escape(r[key+"_url"],quote=True)}" target="_blank" rel="noopener">{r[key+"_miles"]:.1f} mi · {r[key+"_minutes"]} min</a></td>' for key in ['talley','western'])+f'<td>{r["difference_miles"]:+.1f} mi · {r["difference_minutes"]:+d} min</td></tr>' for r in pairs)
  direction='farther' if a['mean_change_miles']>=0 else 'closer'
  mean_display=Decimal(str(abs(a['mean_change_miles']))).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
  google_groups.append(f'<details class="google-verification-group" data-housing="{escape(group,quote=True)}"><summary>{escape(group)} · {len(pairs)} / {a["total_buildings"]} buildings · {mean_display} mi {direction}</summary><div class="table-wrap"><table><thead><tr><th>Housing building</th><th>Talley (2022)</th><th>Western (2026)</th><th>Western − Talley</th></tr></thead><tbody>{body}</tbody></table></div></details>')
 count_rows=f'<tr><th scope="row">Talley → Western Boulevard<small>Early-voting location changed</small></th><td>{first["site_ballots_2022"]:,}</td><td>{first["site_ballots_2026"]:,}</td></tr><tr><th scope="row">Wake County<small>Every early-voting site, including Talley / Western Boulevard</small></th><td>{first["county_ballots_2022"]:,}</td><td>{first["county_ballots_2026"]:,}</td></tr>'
 all_rows=[]
 for r in rows:
  age=escape(r['cohort']);gap=r['site_growth_gap_pp']
  all_rows.append(f'<tr data-age="{age}"><th scope="row"><a data-age="{age}" href="?age={quote(r["cohort"],safe="")}#math">{age}</a></th><td>{r["site_ballots_2022"]:,}</td><td>{r["site_ballots_2026"]:,}</td><td>{rate(r["site_growth_pct"])}</td><td>{rate(r["county_growth_pct"])}</td><td>{gap:+.1f} pp</td></tr>')
 payload={'rows':rows,'as_of':s['report']['asOf'],'matched_days':16,'periods':{str(y):{k:periods[y][k] for k in ['start_date','end_date']} for y in periods}}
 replacements={'__PERIOD_NOTE__':period,'__AGE_OPTIONS__':''.join(f'<option value="{a}">{a}</option>' for a in AGES),'__COUNT_ROWS__':count_rows,
 '__YOUNGEST_BENCHMARK_STEPS__':''.join(f'<li>{escape(step)}</li>' for step in benchmark_steps),
 '__YOUNGEST_BENCHMARK_RESULT__':f"{round(benchmark):,} benchmark − {first['site_ballots_2026']:,} actual ≈ {round(shortfall):,} below benchmark.",
 '__GOOGLE_VERIFICATION_GROUPS__':''.join(google_groups),
 '__SITE_STEPS__':steps(first['site_ballots_2022'],first['site_ballots_2026']),'__COUNTY_STEPS__':steps(first['county_ballots_2022'],first['county_ballots_2026']),
 '__SITE_RESULT__':'Talley → Western Boulevard growth: '+rate(first['site_growth_pct']),'__COUNTY_RESULT__':'Wake County growth: '+rate(first['county_growth_pct']),
 '__GAP_FORMULA__':f'{first["site_growth_pct"]:.1f}% − {first["county_growth_pct"]:.1f}% ≈ {first["site_growth_gap_pp"]:.1f} pp',
 '__GAP_RESULT__':f'Talley → Western Boulevard growth was {abs(first["site_growth_gap_pp"]):.1f} percentage points behind Wake’s growth.',
 '__ALL_AGE_ROWS__':''.join(all_rows),'__SOURCE_CARDS__':''.join(sources),'__REFERENCE_DATA__':json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')}
 html=(ROOT/'report-source/article-references.html').read_text(encoding='utf-8')
 for key,value in replacements.items():
  assert key in html,key
  html=html.replace(key,value)
 assert not re.search(r'__[A-Z_]+__',html)
 (ROOT/'references.html').write_text(html,encoding='utf-8')
 print('Built focused references: five age groups, four original counts each, site/county growth and percentage-point gaps; two election sources.')

if __name__=='__main__':main()
