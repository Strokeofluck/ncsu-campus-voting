"""Write the reporting handoff from the same reviewed rows as the article."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = json.loads((ROOT / 'report-source/snapshot.json').read_text(encoding='utf-8'))
d = s['comparison']
assert d['matched_days'] == 17
rows = s['queries']['age_growth_benchmarks']['rows']
campus = {r['year']: r for r in d['summary'] if r['scope'] == 'Campus site'}
wake = {r['year']: r for r in d['summary'] if r['scope'] == 'Wake County'}
y = rows[0]
change = lambda a, b: (b/a-1)*100
share = lambda a, b: a/b*100
benchmark = y['site_ballots_2022']*y['county_ballots_2026']/y['county_ballots_2022']
# Preserve the existing three-year workbook's literal formula columns while
# refreshing its public aggregate calculation CSV to the same reviewed period.
calculation_path = ROOT/'data/processed/comparison/campus_age_calculations.csv'
with calculation_path.open(encoding='utf-8-sig',newline='') as stream:
    reader=csv.DictReader(stream); fieldnames=reader.fieldnames; calculation_rows=list(reader)
for row in calculation_rows:
    group=row['Group']; counts={}
    for year in [2022,2024,2026]:
        if group=='All site ballots': count=campus[year]['all_ages']
        elif group.startswith('18–22'): count=campus[year]['age_18_22']
        elif group.startswith('Same-day'): count=campus[year]['same_day_registration']
        else: count=next(r['votes'] for r in d['demographics'] if r['year']==year and r['scope']=='Campus site' and r['dimension']=='age_group' and r['value']==group)
        counts[year]=count
        row[f'{year} '+('Western' if year==2026 else 'Talley')+' ballots']=str(count)
        row[f'{year} share']=f'{share(count,campus[year]["all_ages"]):.1f}%'
    row['Ballot change 2022–26']=str(counts[2026]-counts[2022])
    row['Ballot growth 2022–26']=f'{change(counts[2022],counts[2026]):.1f}%'
    row['Share change (pp)']=f'{share(counts[2026],campus[2026]["all_ages"])-share(counts[2022],campus[2022]["all_ages"]):.1f}'
with calculation_path.open('w',encoding='utf-8-sig',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=fieldnames); writer.writeheader();writer.writerows(calculation_rows)
lines = [
    '# November 4, 2026: complete early-voting comparison', '',
    'Preliminary NCSBE accepted in-person early-voting records. All 17 days: October 20–November 5, 2022, and October 15–31, 2026. The article compares two midterms. The prototype retains the complete 2024 presidential period as a separately labeled benchmark.', '',
    '## Findings for the article', '',
    f'The NC State-area location recorded {campus[2026]["all_ages"]:,} accepted early ballots at Western Boulevard Business Services, compared with {campus[2022]["all_ages"]:,} at Talley Student Union in 2022, an increase of {change(campus[2022]["all_ages"],campus[2026]["all_ages"]):.1f}%. Wake County increased from {wake[2022]["all_ages"]:,} to {wake[2026]["all_ages"]:,}, or {change(wake[2022]["all_ages"],wake[2026]["all_ages"]):.1f}%.', '',
    f'Ages 18–24 at the location increased from {y["site_ballots_2022"]:,} to {y["site_ballots_2026"]:,} (+{y["site_growth_pct"]:.1f}%), while Wake increased from {y["county_ballots_2022"]:,} to {y["county_ballots_2026"]:,} (+{y["county_growth_pct"]:.1f}%). The site grew {abs(y["site_growth_gap_pp"]):.1f} percentage points more slowly. Its share of Wake’s same-age early ballots fell from {share(y["site_ballots_2022"],y["county_ballots_2022"]):.2f}% to {share(y["site_ballots_2026"],y["county_ballots_2026"]):.2f}%.', '',
    f'Holding the 2022 county share constant gives a hypothetical benchmark of {benchmark:,.4f} ballots, or about {round(benchmark):,}. Actual ballots were {round(benchmark-y["site_ballots_2026"]):,} below that benchmark. This is not a count of nonvoters, a forecast or a causal estimate.', '',
    '| Age | Site 2022 | Site 2026 | Site growth | Wake 2022 | Wake 2026 | Wake growth | Site minus Wake |',
    '|---|---:|---:|---:|---:|---:|---:|---:|',
]
for r in rows:
    lines.append(f'| {r["cohort"]} | {r["site_ballots_2022"]:,} | {r["site_ballots_2026"]:,} | {r["site_growth_pct"]:+.1f}% | {r["county_ballots_2022"]:,} | {r["county_ballots_2026"]:,} | {r["county_growth_pct"]:+.1f}% | {r["site_growth_gap_pp"]:+.1f} pp |')
lines += ['', '## Registration and composition', '',
    f'Same-day-registration ballots at the site rose from {campus[2022]["same_day_registration"]:,} to {campus[2026]["same_day_registration"]:,} (+{change(campus[2022]["same_day_registration"],campus[2026]["same_day_registration"]):.1f}%). Their share of all site ballots changed from {share(campus[2022]["same_day_registration"],campus[2022]["all_ages"]):.2f}% to {share(campus[2026]["same_day_registration"],campus[2026]["all_ages"]):.2f}%. They are already included in all ballots.', '',
    '| Registered party | Talley 2022 | Western 2026 | Share 2022 | Share 2026 |',
    '|---|---:|---:|---:|---:|']
demo = {(r['year'],r['value']):r for r in d['demographics'] if r['scope']=='Campus site' and r['dimension']=='party'}
for party in sorted({v for _,v in demo}):
    a,b=demo.get((2022,party)),demo.get((2026,party))
    av,bv=(a['votes'] if a else 0),(b['votes'] if b else 0)
    lines.append(f'| {party} | {av:,} | {bv:,} | {share(av,campus[2022]["all_ages"]):.2f}% | {share(bv,campus[2026]["all_ages"]):.2f}% |')
lines += ['', 'Party registration does not show candidate choices. Ages are not verified enrollment. Race, ethnicity and gender use the source categories, retaining undesignated values.', '',
    '## All available reporting cuts', '',
    '- [Site, county and other-site counts](../data/processed/comparison/matched_summary.csv)',
    '- [All age, party-registration, race, ethnicity and gender categories](../data/processed/comparison/matched_demographics.csv)',
    '- [Daily and cumulative ballot counts](../data/processed/comparison/matched_daily.csv)',
    '- [Daily party-registration counts](../data/processed/comparison/matched_party_daily.csv)',
    '- [Daily same-day-registration counts and same-cohort denominators](../data/processed/comparison/matched_sdr_daily.csv)',
    '- [Home precinct and ZIP site-use comparisons](../data/processed/comparison/matched_geography.csv)',
    '- [All five ages by home precinct](../data/processed/comparison/precinct_age_changes.csv)',
    '- [Exact five-age site and county growth benchmarks](../data/processed/comparison/age_growth_benchmarks.csv)',
    '- [Independent full-period two-year analysis](../data/processed/nov2026/research_summary.json)', '',
    '## Source freeze and limits', '',
    'The 2026 archive was last modified November 4, 2026 at 10:28:57 UTC (5:28:57 a.m. Eastern). Original source ZIPs and extracted Wake CSV hashes are verified. The independent November 4 analysis and the article pipeline agree on their overlapping exact counts. Raw voter-identifying records remain in ignored local storage; only aggregate results are published.', '',
    'The 2022 baseline reconciles exactly to 10,390 Talley and 219,169 Wake accepted early ballots. The 2026 counts have unique accepted voter identifiers. All 17 days, age partitions, site-versus-other-site partitions and county denominators reconcile.', '',
    'Election Day and mail voting are excluded. A completed early-voting period is not a certified final election dataset. The underlying 2026 source may be corrected during canvass. Do not infer turnout among enrolled or eligible students, individual voters switching locations, or a causal effect of relocation. Current precinct outlines do not reconstruct historical boundaries.', '',
    'The original October 31 statewide screenshot remains a dated historical reference. Its 2,612,240 early-plus-mail figure through October 30 is not the current statewide total and must not be combined with Wake’s in-person-only counts.', '',
    'The parking inventory, housing walks and routine-route simulations retain their original November 1 GIS sources and definitions. They are modeled/inventory evidence, not observations of movement or available voter parking.', '',
    '### Exact source files', '']
for source in d['sources']:
    lines += [f'- [{source["member"]}]({source["url"]}) — archive last modified {source["last_modified"]}; retrieved {source["retrieved_at_utc"]}; archive SHA-256 `{source["sha256"]}`.']
lines += ['', '### Rebuild', '', '```sh',
    'python scripts/download_early_voting_sources.py',
    'python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-31',
    'python scripts/validate_early_voting_comparison.py',
    'python scripts/audit_campus_figures.py',
    'python scripts/refresh_report_snapshot.py',
    'python scripts/build_source_previews.py',
    'python scripts/refresh_article_for_full_period.py',
    'python scripts/write_full_period_notes.py',
    'python scripts/build_article_references.py',
    '```', '', 'Rebuild the existing article and prototype apps and the Excel template after changing the reviewed data. Retain the established app identities.']
notes='\n'.join(lines)+'\n'
(ROOT/'docs/2026-early-voting-update.md').write_text(notes,encoding='utf-8')
readme='''# NC State Campus Voting

Updated November 4, 2026. The article, charts, references and Excel calculator now compare **all 17 early-voting days** in 2022 and 2026. The 2026 NCSBE records remain preliminary during canvass.

**[Article draft](https://strokeofluck.github.io/ncsu-campus-voting/article/index.html?view=1) · [References and step-by-step math](https://strokeofluck.github.io/ncsu-campus-voting/references.html) · [Interactive research report](https://strokeofluck.github.io/ncsu-campus-voting/index.html?view=1) · [Map editor preview](https://strokeofluck.github.io/ncsu-campus-voting/editor-maps/index.html?view=1)**

College-age early ballots at the campus-area location increased **3,402 → 4,639 (+36.4%)**, while Wake County increased **13,398 → 25,570 (+90.8%)**. The growth gap is **54.5 percentage points**. The site's share of Wake's ages 18–24 early ballots fell **25.4% → 18.1%**. These are site-use counts and county shares, not turnout rates among enrolled or eligible students.

All-age campus-site early ballots increased **10,390 → 14,496 (+39.5%)**. Wake County increased **219,169 → 334,088 (+52.4%)**. Campus-site same-day registrations increased **763 → 993 (+30.1%)**, and are already included in the total ballots.

Periods: **October 20–November 5, 2022**, and **October 15–31, 2026**. 2024 is retained only as a separate presidential-election benchmark in the research prototype. The old first-16-day article figures are superseded; the uploaded October 31 statewide screenshot remains explicitly labeled as historical.

## Sources and reporting files

- [Current reporting notes, all five ages, sources and rebuild commands](docs/2026-early-voting-update.md)
- [Independent November 4 two-year research](docs/nov2026-reporting-notes.md)
- [All reviewed comparison CSVs](data/processed/comparison/)
- [Independent two-year CSVs](data/processed/nov2026/)
- [Methodology](methodology.md)
- [Article/Excel calculations and audit design](docs/article-excel-audit.md)
- [Authored report and build instructions](report-source/README.md)

The references page provides both a live official-file recalculation and an exact saved-snapshot mode. Both use the complete 17-day windows. Excel contains untouched source CSVs, full original-record copies, linked fields, rule flags, COUNTIFS totals and worked percentage/gap formulas. Later source corrections may produce different results; input hashes and calculation dates remain visible.

## Interpretation and privacy

Early voting and Election Day are separate analyses. Election Day and mail ballots are excluded from this comparison. A complete early period does not mean certified final results. Age does not verify student enrollment, party registration does not identify candidate choices, and current precinct polygons do not reconstruct historical boundaries. These descriptive comparisons cannot isolate the effect of relocating the site.

Public outputs contain aggregates only. Names, addresses and voter identifiers remain in ignored `data/raw/` storage and browser-local downloads. No original voter-level records or populated workbooks are hosted in this public repository.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
print('Updated reporting notes and README from the reviewed 17-day snapshot.')
