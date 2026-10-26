# The move from Talley: early-voting update

Updated October 26, 2026. Voting records through October 25; preliminary.

The question is whether moving the NC State early-voting site from Talley Student Union to Western Boulevard Business Services changed college-age voting patterns.

## What is observed

Match the first 11 days of each midterm: October 20–30, 2022 and October 15–25, 2026. Both windows begin Thursday and end Sunday. Ages 18–24 are a proxy for college age, not confirmed students.

| Measure | Talley, 2022 | Western Boulevard, 2026 | Change |
| --- | ---: | ---: | ---: |
| Accepted early ballots, all ages | 4,863 | 7,463 | +53.5% |
| Accepted early ballots, ages 18–24 | 1,259 | 1,866 | +48.2% |
| Ages 18–24 share of site ballots | 25.9% | 25.0% | −0.9 percentage points |
| Site share of Wake’s 18–24 early ballots | 23.3% | 14.8% | −8.4 percentage points |
| Accepted early ballots, ages 18–22 | 970 | 1,448 | +49.3% |

Wake County’s 18–24 early ballots increased from 5,412 to 12,583 (+132.5%). At all other Wake sites combined, they increased from 4,153 to 10,717 (+158.1%). Campus-site voting grew, but its share of the county's college-age early votes fell. The younger 18–22 proxy gives a similar site growth result.

## What cannot be concluded

This does not establish that moving the site reduced or increased student participation. There is no enrollment flag, eligible-student denominator, linked same-person cohort, or credible counterfactual. Countywide mobilization, population change, expanded site availability (15 Wake sites in 2022, 18 in 2026), and voting timing can change these measures. Early voting is still underway. Mail and Election Day participation are outside this comparison. The analysis counts accepted ballots; it does not measure turnout as a percentage of eligible or registered voters, or candidate preferences.

## Sources and filters

- [NCSBE official data catalog](https://www.ncsbe.gov/results-data/absentee-and-provisional-data).
- [2022 county archive](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip).
- [2026 county archive](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_county_20261103.zip).
- [NC State’s 2026 early-voting listing](https://packthepolls.dasa.ncsu.edu/event/2026-general-early-voting/) identifies the replacement site, Western Boulevard Business Services, 1220 Varsity Drive.

Select `county_desc=WAKE`, early-voting request types `ONE-STOP`, `ONE STOP` or `EARLY VOTING`, and return status exactly `ACCEPTED`. Site labels are exact matches: `TA - NCSU TALLEY STUDENT CENTER` (2022) and `NCSU WESTERN BLVD BUSINESS SERVICES` (2026). Other sites means all Wake early-voting sites except that year’s campus site. Wake totals contain the campus site and must not be added to it.

Use `ballot_rtn_dt` for the calendar day; subtract each election’s opening date to align days. Use the supplied `age` field with inclusive bounds 18–24 and 18–22. No birthday or enrollment information is inferred. Same-day registrations count `sdr` equal to Y/YES across all ages in the matched period. Unknown age is kept as its own category if present. Source text is decoded as Latin-1; relevant keys and categorical fields are ASCII.

The October 26 source was modified at 09:23:23 UTC (5:23 a.m. EDT), downloaded at 13:24 UTC (9:24 a.m. EDT), and contains accepted early-voting dates through October 25. Live records can be backfilled or corrected. A finalized 2022 snapshot is compared with a live 2026 snapshot; historical reporting lags cannot be reconstructed. Matching days does not equate site hours, site availability or underlying populations. No independent 2026 site-total reconciliation with a separate Wake publication has been completed.

## Rebuild

```bash
python scripts/download_early_voting_sources.py
python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-25
python scripts/validate_early_voting_comparison.py
```

The cutoff is explicit: use a complete voting day covered by the new file, never the unfinished current day. Downloads preserve source freshness and archive hashes in ignored raw storage; `comparison.json` retains the non-personal manifest with the aggregate results. The 2022 baseline is cached with hash validation; 2026 is always downloaded again. The pipeline fails on missing columns, a missing campus site, duplicate accepted voter identifiers, invalid voting dates or a changed locked baseline.

All CSVs and JSON in `data/processed/comparison/` contain aggregates only. Raw names, addresses, voter identifiers and voter-level files remain under ignored `data/raw/`. The 2022 full-period baseline is unchanged at 10,390 Talley ballots and 219,169 Wake ballots.

## Visual report

`index.html` and its content-addressed snapshot sidecar are the compiled interactive report. The same build supplies the local preview and GitHub Pages. Authored report content and reviewed snapshot are kept under `report-source/` for revisions. Rebuild them through the Codex Data app preparer/build workflow, review date-specific narrative and source metadata on every refresh, then copy the verified `dist` files to the repository root. The browser's menus expose source rows and chart export. This report does not fetch live election data when opened.
