# The move from Talley: early-voting update

Updated October 29, 2026. Voting records through October 28; preliminary.

The question is whether moving the NC State early-voting site from Talley Student Union to Western Boulevard Business Services changed college-age voting patterns.

## Primary 2022 midterm comparison

Match the first 14 days of each midterm: **October 20, 2022–November 2, 2022** and **October 15, 2026–October 28, 2026**. Both windows begin Thursday and end Wednesday. Ages 18–24 are a proxy for college age, not confirmed students.

| Measure | Talley, 2022 | Western Boulevard, 2026 | Change |
| --- | ---: | ---: | ---: |
| Accepted early ballots, all ages | 7,007 | 10,498 | +49.8% |
| Accepted early ballots, ages 18–24 | 2,057 | 2,966 | +44.2% |
| Ages 18–24 share of site ballots | 29.4% | 28.3% | -1.1 percentage points |
| Site share of Wake’s 18–24 early ballots | 26.3% | 17.0% | -9.3 percentage points |
| Accepted early ballots, ages 18–22 | 1,590 | 2,316 | +45.7% |

Wake County’s 18–24 early ballots increased from 7,831 to 17,460 (+123.0%). At all other Wake sites combined, they increased from 5,774 to 14,494 (+151.0%). Campus-site voting grew, but its share of the county's college-age early votes fell. The younger 18–22 proxy gives a similar site growth result.

## 2024 presidential-election benchmark

The report defaults to the 2022-to-2026 midterm comparison and retains 2024 as a presidential-election benchmark. Selectors update counts, cumulative curves, county share, age distribution and individual ages 18–24 charts together.

Match **October 17, 2024–October 30, 2024** with **October 15, 2026–October 28, 2026**, each the first **14 calendar days**, opening Thursday through the second Wednesday.

| Measure | Talley, 2024 | Western Boulevard, 2026 | Change |
| --- | ---: | ---: | ---: |
| Accepted early ballots, all ages | 17,339 | 10,498 | -39.5% |
| Accepted early ballots, ages 18–24 | 7,194 | 2,966 | -58.8% |
| Ages 18–24 share of site ballots | 41.5% | 28.3% | -13.2 percentage points |
| Site share of Wake’s 18–24 early ballots | 22.2% | 17.0% | -5.2 percentage points |
| Accepted early ballots, ages 18–22 | 5,888 | 2,316 | -60.7% |

Wake County’s 18–24 early ballots were 32,419 in the matched 2024 window and 17,460 in 2026 (-46.1%). At other Wake sites they were 25,225 and 14,494 (-42.5%). College-age early voting fell across Wake as well as at the campus site, and the decrease at the campus site was larger.

**2024 is a presidential election and 2026 is a midterm.** The charts do not adjust away that difference or estimate the move’s effect. College-age counts are site users, not an enrolled-student cohort. The full 17-day 2024 source contains 21,624 accepted Talley ballots across all ages; that full total is not used in matched-period changes. Exact-age counts and shares are exported as `dimension=age` in `matched_demographics.csv`.

## What cannot be concluded

This does not establish that moving the site reduced or increased student participation. There is no enrollment flag, eligible-student denominator, linked same-person cohort, or credible counterfactual. Countywide mobilization, population change, expanded site availability (15 Wake sites in 2022, 18 in 2026), and voting timing can change these measures. Early voting is still underway. Mail and Election Day participation are outside this comparison. The analysis counts accepted ballots; it does not measure turnout as a percentage of eligible or registered voters, or candidate preferences.

## Sources and filters

- [NCSBE official data catalog](https://www.ncsbe.gov/results-data/absentee-and-provisional-data).
- [2022 county archive](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip).
- [2024 county archive](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/absentee_county_20241105.zip).
- [2026 county archive](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_county_20261103.zip).
- [NC State’s 2026 early-voting listing](https://packthepolls.dasa.ncsu.edu/event/2026-general-early-voting/) identifies the replacement site, Western Boulevard Business Services, 1220 Varsity Drive.

Select `county_desc=WAKE`, early-voting request types `ONE-STOP`, `ONE STOP` or `EARLY VOTING`, and return status exactly `ACCEPTED`. Site labels are exact matches: `TA - NCSU TALLEY STUDENT CENTER` (2022 and 2024) and `NCSU WESTERN BLVD BUSINESS SERVICES` (2026). Other sites means all Wake early-voting sites except that year’s campus site. Wake totals contain the campus site and must not be added to it.

Use `ballot_rtn_dt` for the calendar day; subtract each election’s opening date to align days. Use the supplied `age` field with inclusive bounds 18–24 and 18–22. No birthday or enrollment information is inferred. Same-day registrations count `sdr` equal to Y/YES across all ages in the matched period. Unknown age is kept as its own category if present. Source text is decoded as Latin-1; relevant keys and categorical fields are ASCII.

The current source was modified Thu, 29 Oct 2026 09:25:32 GMT and downloaded Fri, 30 Oct 2026 03:11:32 GMT. Accepted Wake early-voting dates extend through 2026-10-28. The source modification date and the last voting date covered are distinct. Live records can be backfilled or corrected. A finalized 2022 snapshot is compared with a live 2026 snapshot; historical reporting lags cannot be reconstructed. Matching days does not equate site hours, site availability or underlying populations. No independent 2026 site-total reconciliation with a separate Wake publication has been completed.

## Rebuild

```bash
python scripts/download_early_voting_sources.py
python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-28
python scripts/validate_early_voting_comparison.py
```

The cutoff is explicit: use a complete voting day covered by the new file, never the unfinished current day. Downloads preserve source freshness and archive hashes in ignored raw storage; `comparison.json` retains the non-personal manifest with the aggregate results. Historical baselines are cached with hash validation; 2026 is always downloaded again. `--years 2024` downloads just the additional historical source while preserving the other manifest entries. Run `python scripts/audit_campus_figures.py`, `python scripts/build_reference_page.py` and `python scripts/refresh_report_snapshot.py` after validation to refresh the independent campus recount, figure-verification page and report snapshot. The pipeline fails on missing columns, a missing campus site, duplicate accepted voter identifiers, invalid voting dates or a changed locked 2022 baseline. No independent 2024 or 2026 site-total reconciliation with a separate Wake publication has been completed.

All CSVs and JSON in `data/processed/comparison/` contain aggregates only. Raw names, addresses, voter identifiers and voter-level files remain under ignored `data/raw/`. The 2022 full-period baseline is unchanged at 10,390 Talley ballots and 219,169 Wake ballots.

## Visual report

`index.html` and its content-addressed snapshot sidecar are the compiled interactive report. The same build supplies the local preview and GitHub Pages. Authored report content and reviewed snapshot are kept under `report-source/` for revisions. Rebuild them through the Codex Data app preparer/build workflow, review date-specific narrative and source metadata on every refresh, then copy the verified `dist` files to the repository root. The browser's menus expose source rows and chart export. This report does not fetch live election data when opened.

## Exact clickable references and the 2024 benchmark

Underlined figures in the report tables and executive summary open `figure-source.html#<stable-figure-id>`. Each target preserves the selected year, population and category. It shows the arithmetic before rounding, underlying aggregate inputs, exact record filters, original archive/CSV member, retrieval dates and snapshot hashes. The source generator uses the reviewed matched-day outputs; an independent recount also verifies every campus demographic category against the original CSVs. `data/processed/comparison/figure_sources.json` contains the aggregate evidence records.

These percentages are project calculations. The NCSBE catalog does not print them, and its ZIP downloads do not support browser anchors to a particular record. The evidence page links directly to the original official ZIP and to the matching catalog entry rather than pretending a derived number appears on the government page. No voter-level rows are published.

Over the first 14 days, 2026 reached 68.3% of the matched 2024 all-age Wake count and 53.9% of its ages 18–24 count. At the campus site the corresponding ratios are 60.5% and 41.2%. These are counts of accepted in-person early ballots, not turnout rates, forecasts or statistical-significance thresholds. A large midterm increase is reportable without requiring a presidential-election total to be reached.

Rebuild the per-figure evidence with `python scripts/build_figure_sources.py` after rebuilding the comparison and running the campus audit. The source HTML template is maintained at `report-source/figure-source.html`.
