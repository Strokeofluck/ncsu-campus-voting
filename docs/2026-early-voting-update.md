# November 4, 2026: complete early-voting comparison

Preliminary NCSBE accepted in-person early-voting records. All 17 days: October 20–November 5, 2022, and October 15–31, 2026. The article compares two midterms. The prototype retains the complete 2024 presidential period as a separately labeled benchmark.

## Findings for the article

The NC State-area location recorded 14,496 accepted early ballots at Western Boulevard Business Services, compared with 10,390 at Talley Student Union in 2022, an increase of 39.5%. Wake County increased from 219,169 to 334,088, or 52.4%.

Ages 18–24 at the location increased from 3,402 to 4,639 (+36.4%), while Wake increased from 13,398 to 25,570 (+90.8%). The site grew 54.5 percentage points more slowly. Its share of Wake’s same-age early ballots fell from 25.39% to 18.14%.

Holding the 2022 county share constant gives a hypothetical benchmark of 6,492.6959 ballots, or about 6,493. Actual ballots were 1,854 below that benchmark. This is not a count of nonvoters, a forecast or a causal estimate.

| Age | Site 2022 | Site 2026 | Site growth | Wake 2022 | Wake 2026 | Wake growth | Site minus Wake |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18–24 | 3,402 | 4,639 | +36.4% | 13,398 | 25,570 | +90.8% | -54.5 pp |
| 25–34 | 2,203 | 3,043 | +38.1% | 24,757 | 43,350 | +75.1% | -37.0 pp |
| 35–44 | 1,132 | 1,597 | +41.1% | 30,892 | 48,620 | +57.4% | -16.3 pp |
| 45–64 | 2,443 | 3,115 | +27.5% | 85,819 | 118,322 | +37.9% | -10.4 pp |
| 65+ | 1,210 | 2,102 | +73.7% | 64,303 | 98,226 | +52.8% | +21.0 pp |

## Registration and composition

Same-day-registration ballots at the site rose from 763 to 993 (+30.1%). Their share of all site ballots changed from 7.34% to 6.85%. They are already included in all ballots.

| Registered party | Talley 2022 | Western 2026 | Share 2022 | Share 2026 |
|---|---:|---:|---:|---:|
| DEM | 4,596 | 6,270 | 44.23% | 43.25% |
| GRE | 4 | 30 | 0.04% | 0.21% |
| LIB | 47 | 38 | 0.45% | 0.26% |
| NLB | 0 | 0 | 0.00% | 0.00% |
| REP | 1,119 | 955 | 10.77% | 6.59% |
| UNA | 4,624 | 7,203 | 44.50% | 49.69% |
| WTP | 0 | 0 | 0.00% | 0.00% |

Party registration does not show candidate choices. Ages are not verified enrollment. Race, ethnicity and gender use the source categories, retaining undesignated values.

## All available reporting cuts

- [Site, county and other-site counts](../data/processed/comparison/matched_summary.csv)
- [All age, party-registration, race, ethnicity and gender categories](../data/processed/comparison/matched_demographics.csv)
- [Daily and cumulative ballot counts](../data/processed/comparison/matched_daily.csv)
- [Daily party-registration counts](../data/processed/comparison/matched_party_daily.csv)
- [Daily same-day-registration counts and same-cohort denominators](../data/processed/comparison/matched_sdr_daily.csv)
- [Home precinct and ZIP site-use comparisons](../data/processed/comparison/matched_geography.csv)
- [All five ages by home precinct](../data/processed/comparison/precinct_age_changes.csv)
- [Exact five-age site and county growth benchmarks](../data/processed/comparison/age_growth_benchmarks.csv)
- [Independent full-period two-year analysis](../data/processed/nov2026/research_summary.json)

## Source freeze and limits

The 2026 archive was last modified November 4, 2026 at 10:28:57 UTC (5:28:57 a.m. Eastern). Original source ZIPs and extracted Wake CSV hashes are verified. The independent November 4 analysis and the article pipeline agree on their overlapping exact counts. Raw voter-identifying records remain in ignored local storage; only aggregate results are published.

The 2022 baseline reconciles exactly to 10,390 Talley and 219,169 Wake accepted early ballots. The 2026 counts have unique accepted voter identifiers. All 17 days, age partitions, site-versus-other-site partitions and county denominators reconcile.

Election Day and mail voting are excluded. A completed early-voting period is not a certified final election dataset. The underlying 2026 source may be corrected during canvass. Do not infer turnout among enrolled or eligible students, individual voters switching locations, or a causal effect of relocation. Current precinct outlines do not reconstruct historical boundaries.

The original October 31 statewide screenshot remains a dated historical reference. Its 2,612,240 early-plus-mail figure through October 30 is not the current statewide total and must not be combined with Wake’s in-person-only counts.

The parking inventory, housing walks and routine-route simulations retain their original November 1 GIS sources and definitions. They are modeled/inventory evidence, not observations of movement or available voter parking.

### Exact source files

- [WAKE_absentee_20221108.csv](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip) — archive last modified Sat, 19 Nov 2022 10:33:49 GMT; retrieved 2026-11-04T23:17:57.229413+00:00; archive SHA-256 `929aa047d71207270a4030a99ee472bc6b49d020ec818e9a2c38333f2cc8f11e`.
- [WAKE_absentee_20241105.csv](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/absentee_county_20241105.zip) — archive last modified Mon, 09 Dec 2024 18:15:10 GMT; retrieved 2026-11-04T23:18:07.370985+00:00; archive SHA-256 `98791bda4aec6eb07d7816bcac5a0d79dd46391a39a0f0d4b71cd367b6b74a30`.
- [WAKE_absentee_20261103.csv](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_county_20261103.zip) — archive last modified Wed, 04 Nov 2026 10:28:57 GMT; retrieved 2026-11-04T23:18:15.985934+00:00; archive SHA-256 `1b76f903f2732fdf668953550f43aabeb8d3166b0d4ef5ba7935b1811f5a755c`.

### Rebuild

```sh
python scripts/download_early_voting_sources.py
python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-31
python scripts/validate_early_voting_comparison.py
python scripts/audit_campus_figures.py
python scripts/refresh_report_snapshot.py
python scripts/build_source_previews.py
python scripts/refresh_article_for_full_period.py
python scripts/write_full_period_notes.py
python scripts/build_article_references.py
```

Rebuild the existing article and prototype apps and the Excel template after changing the reviewed data. Retain the established app identities.
