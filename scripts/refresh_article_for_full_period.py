"""Synchronize article copy and evidence with the reviewed complete early period.

Run after refresh_report_snapshot.py. This changes no voting filters or GIS data.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def replace_period(text):
    for old, new in [
        ('first 16 early-voting days', 'full 17-day early-voting periods'),
        ('First 16 early-voting days', 'Full 17-day early-voting periods'),
        ('first 16 calendar early-voting days', 'full 17-day early-voting periods'),
        ('first 16 days', 'full 17-day periods'),
        ('First 16 days', 'Full 17-day periods'),
        ('first-16-day counts', 'full-period early-ballot counts'),
        ('October 20–November 4, 2022', 'October 20–November 5, 2022'),
        ('October 15–30, 2026', 'October 15–31, 2026'),
        ('October 15–30', 'October 15–31'),
        ('October 30, 2026', 'October 31, 2026'),
        ('through October 30', 'through October 31'),
        ('through Oct. 30, 2026', 'through Oct. 31, 2026'),
        ('20261102parking5', '20261104full17'),
        ('20261102refs3', '20261104full17'),
    ]:
        text = text.replace(old, new)
    return text


def source_text(value):
    if isinstance(value, str):
        return replace_period(value)
    if isinstance(value, list):
        return [source_text(v) for v in value]
    if isinstance(value, dict):
        return {k: source_text(v) for k, v in value.items()}
    return value


def main():
    prototype_path = ROOT / 'report-source/snapshot.json'
    prototype = json.loads(prototype_path.read_text(encoding='utf-8'))
    comparison = prototype['comparison']
    assert comparison['matched_days'] == 17 and comparison['as_of'] == '2026-10-31'
    for query in prototype['queries'].values():
        query['source'] = source_text(query.get('source', {}))
    write_json(prototype_path, prototype)

    article_path = ROOT / 'report-source/article-snapshot.json'
    article = json.loads(article_path.read_text(encoding='utf-8'))
    for key in list(article['queries']):
        if key in prototype['queries']:
            article['queries'][key] = copy.deepcopy(prototype['queries'][key])
    article['comparison'] = copy.deepcopy(comparison)
    article['generatedAt'] = prototype['generatedAt']
    article['report']['asOf'] = comparison['as_of']
    article['buildStatus'] = 'updating'
    opening = article['queries']['article_opening_context']
    opening['rows'][0] = {
        'claim': 'North Carolina set a midterm early-voting record; voting ended November 3 and the November 4 records remain preliminary.',
        'reported_at': '2026-11-02',
        'source_url': 'https://ncnewsline.com/2026/11/02/democrats-and-unaffiliated-voters-cast-about-73-of-ballots-in-ncs-record-setting-early-turnout/',
    }
    opening['source']['files'][0] = opening['rows'][0]['source_url']
    opening['source'].update(
        label='Midterm early-voting record, site decision coverage and university parking notice',
        provider='NC Newsline; NC State Transportation',
        executedAt=comparison['sources'][-1]['retrieved_at_utc'],
        period='Completed October 15–31 early-voting period; November 3 Election Day has passed; November 4 source is preliminary',
    )
    opening['source']['caveats'][0] = 'The reported record concerns midterm early voting, not certified full-election turnout.'
    # Retain the uploaded historical image and its exact original figures, clearly dated.
    historical = article['queries']['statewide_early_voting_context']['source']
    historical['caveats'] = [c for c in historical['caveats'] if 'Election Day is November' not in c]
    historical['caveats'].append('Historical October 31 screenshot through October 30; retained as an image reference, not the current statewide total or the source for the refreshed Wake comparison.')
    write_json(article_path, article)

    rows = prototype['queries']['age_growth_benchmarks']['rows']
    youth, senior = rows[0], rows[-1]
    n = lambda value: f'{value:,}'
    pct = lambda value: f'{value:.1f}'
    # Update period labels in authored content and their generators, preserving layout.
    paths = [* (ROOT / 'report-source/article').glob('*.jsx'),
             * (ROOT / 'report-source/report').glob('*.jsx'),
             ROOT / 'scripts/add_growth_map_context.py', ROOT / 'scripts/build_precinct_age_changes.py',
             ROOT / 'scripts/build_sdr_trends.py', ROOT / 'article-excel-export.js',
             ROOT / 'article-excel-download.js']
    for path in paths:
        path.write_text(replace_period(path.read_text(encoding='utf-8')), encoding='utf-8')

    path = ROOT / 'report-source/article/ReportContent.jsx'
    text = path.read_text(encoding='utf-8')
    start = text.index('**[Update this opening after the Nov. 3 election.]**') if '**[Update this opening after the Nov. 3 election.]**' in text else -1
    if start >= 0:
        end = text.index('\n\nParking was', start)
        text = text[:start] + ('North Carolina’s midterm election is over, following a record early-voting period, '
            '[NC Newsline reported](https://ncnewsline.com/2026/11/02/democrats-and-unaffiliated-voters-cast-about-73-of-ballots-in-ncs-record-setting-early-turnout/). '
            'The complete early-voting period offers a first look at voting after NC State’s location moved from '
            '**Talley Student Union to Western Boulevard Business Services**. The NCSBE records downloaded November 4 remain preliminary while canvass continues.') + text[end:]
    text = text.replace('**40.5%**', f'**{pct(youth["site_growth_pct"])}%**').replace('**103.6%**', f'**{pct(youth["county_growth_pct"])}%**').replace('**63.1 percentage-point growth gap**', f'**{pct(abs(youth["site_growth_gap_pp"]))} percentage-point growth gap**')
    text = text.replace('**76.0%**', f'**{pct(senior["site_growth_pct"])}%**').replace('**53.4%**', f'**{pct(senior["county_growth_pct"])}%**')
    old = '*Work in progress · Accepted in-person early ballots during the full 17-day periods of each election, through October 31, 2026. These preliminary counts are not full-election turnout. Ages 18–24 do not verify student enrollment.*'
    new = (f'The campus-site count for ages 18–24 increased from **{n(youth["site_ballots_2022"])} to {n(youth["site_ballots_2026"])}**, while Wake’s increased from **{n(youth["county_ballots_2022"])} to {n(youth["county_ballots_2026"])}**. '
           f'The location’s share of Wake’s early ballots in that age group fell from **{pct(youth["site_ballots_2022"]/youth["county_ballots_2022"]*100)}% to {pct(youth["site_ballots_2026"]/youth["county_ballots_2026"]*100)}%**.\n\n'
           '*Accepted in-person early ballots across all 17 days: October 20–November 5, 2022, and October 15–31, 2026. Downloaded November 4; 2026 remains preliminary. Election Day and mail ballots are excluded. Ages 18–24 do not verify student enrollment.*')
    if old in text:
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

    path = ROOT / 'scripts/build_article_references.py'
    text = path.read_text(encoding='utf-8').replace('First 16 days in both years; 2026 is preliminary.', 'All {s["comparison"]["matched_days"]} early-voting days in both years; downloaded November 4, 2026; 2026 is preliminary.')
    # The period is an f-string with double quotes: use single-quoted keys inside it.
    text = text.replace('{s["comparison"]["matched_days"]}', "{s['comparison']['matched_days']}")
    text = text.replace("'matched_days':16", "'matched_days':s['comparison']['matched_days']")
    path.write_text(text, encoding='utf-8')

    path = ROOT / 'report-source/article-references.html'
    text = replace_period(path.read_text(encoding='utf-8'))
    text = text.replace('Oct. 20–Nov. 4, 2022', 'Oct. 20–Nov. 5, 2022').replace('Oct. 15–30, 2026', 'Oct. 15–31, 2026')
    text = text.replace('article-excel-download.js?v=4', 'article-excel-download.js?v=full17')
    marker = '<!-- FULL PERIOD DATA -->'
    if marker not in text:
        sections = []
        for year in [2022, 2026]:
            r = next(r for r in comparison['summary'] if r['year'] == year and r['scope'] == 'Campus site')
            w = next(r for r in comparison['summary'] if r['year'] == year and r['scope'] == 'Wake County')
            sections.append(f'<tr><th>{year}</th><td>{r["all_ages"]:,}</td><td>{r["age_18_24"]:,}</td><td>{r["same_day_registration"]:,}</td><td>{w["all_ages"]:,}</td><td>{w["age_18_24"]:,}</td></tr>')
        extra = marker + '<section id="full-period-data"><h3>November 4 pull: all 17 early-voting days</h3><p>2022: October 20–November 5. 2026: October 15–31. Accepted in-person early ballots only. The 2026 archive was last modified November 4 at 5:28:57 a.m. Eastern; source hashes below identify the downloaded files.</p><div class="table-wrap"><table><thead><tr><th>Year</th><th>Site, all ages</th><th>Site, 18–24</th><th>Site, same-day registration</th><th>Wake, all ages</th><th>Wake, 18–24</th></tr></thead><tbody>' + ''.join(sections) + '</tbody></table></div><p>Same-day-registration ballots are already included in all ballots. Age is not student enrollment. These figures remain preliminary; Election Day and mail voting are excluded.</p><p><a href="data/processed/comparison/matched_demographics.csv">All age, party-registration, race, ethnicity and gender aggregates</a> · <a href="data/processed/comparison/matched_daily.csv">Daily and cumulative counts</a> · <a href="data/processed/comparison/matched_geography.csv">Home precinct and ZIP comparisons</a> · <a href="data/processed/comparison/precinct_age_changes.csv">Age-specific precinct changes</a> · <a href="docs/nov2026-reporting-notes.md">Full-period reporting notes and limitations</a></p></section>'
        text = text.replace('<section aria-labelledby="excel-heading"', extra + '<section aria-labelledby="excel-heading"')
    text = text.replace('Exact uploaded screenshot from', 'Historical image reference, not the current statewide total. Exact uploaded screenshot from')
    path.write_text(text, encoding='utf-8')
    print('Synchronized complete-period article, sources, references, map labels and export copy; preserved historical screenshot and GIS evidence.')


if __name__ == '__main__':
    main()
