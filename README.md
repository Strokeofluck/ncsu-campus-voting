# NC State Campus Voting

Data and reporting workspace for a Technician follow-up on voting at NC State.

**[Open the interactive report](https://strokeofluck.github.io/ncsu-campus-voting/)** · [Findings and methods](docs/2026-early-voting-update.md) · [References](references.html)

## October 29, 2026 update: Talley to Western Boulevard

The latest downloaded NCSBE file covers voting through **October 28, 2026**. The report opens with **Talley Student Union in 2022 versus Western Boulevard Business Services in 2026**, using the same first **14 early-voting days**. **2022 and 2026 are midterms.** A selector retains 2024 as a presidential-election benchmark. Early voting and Election Day remain separate.

The primary midterm comparison shows **44.2% more ages 18–24 ballots at the campus site** and **123.0% more across Wake County** than in 2022. All-age Wake early voting grew **61.6%**.

### Retained 2024 presidential-election benchmark

| Measure | Talley, 2024 | Western Boulevard, 2026 | Change |
| --- | ---: | ---: | ---: |
| Accepted early ballots, all ages | 17,339 | 10,498 | -39.5% |
| Accepted early ballots, ages 18–24 | 7,194 | 2,966 | -58.8% |
| Ages 18–24 share of site ballots | 41.5% | 28.3% | -13.2 percentage points |
| Site share of Wake’s 18–24 early ballots | 22.2% | 17.0% | -5.2 percentage points |
| Accepted early ballots, ages 18–22 | 5,888 | 2,316 | -60.7% |

College-age ballots at the campus site were **58.8% lower** than in the matched 2024 period, while Wake County’s college-age ballots were **46.1% lower**. The site’s college-age share fell **13.2 percentage points**. These descriptive comparisons cannot isolate the move from election-cycle or other changes. Ages 18–24 are an age proxy, not verified NC State students.

### Exact campus-site counts, all three years

| Site / year | All ages | Ages 18–24 | Ages 18–22 | 18–24 share | Same-day registration |
| --- | ---: | ---: | ---: | ---: | ---: |
| Talley Student Union · 2022 | 7,007 | 2,057 | 1,590 | 29.4% | 378 |
| Talley Student Union · 2024 | 17,339 | 7,194 | 5,888 | 41.5% | 1,467 |
| Western Boulevard · 2026 | 10,498 | 2,966 | 2,316 | 28.3% | 535 |

Dates: **October 20, 2022–November 2, 2022**; **October 17, 2024–October 30, 2024**; **October 15, 2026–October 28, 2026**. Each row covers 14 days. 2026 is preliminary; same-day registrations include all ages. The 18–24 share uses all site ballots as its denominator.

**[Verify every highlighted figure against its source and arithmetic](https://strokeofluck.github.io/ncsu-campus-voting/verify-figures.html).** Campus totals and percentages are project calculations from NCSBE records. [Download the campus-site CSV](data/processed/comparison/campus_site_matched_counts.csv).

![Age composition at Talley in 2022 and 2024 and Western Boulevard in 2026, matched first 14 days](docs/images/campus-age-composition-2022-2024-2026.png)

Underlined figures in the exact-count, age, voter-profile and benchmark tables open a dedicated evidence page showing the selected calculation, exact inputs, record filters, original CSV member and NCSBE download. The executive-summary figures are linked too. [Example: verify the 2024 ages 18–24 share](figure-source.html#demographic-2024-age-group-18-24). Choose **Preview the original file** to see the actual ZIP member list and CSV header, a filtered grouped extract retaining original field values, and an embedded live NCSBE file listing. Names, addresses and voter IDs are omitted. NCSBE does not print these calculated percentages on its download catalog; the official archive is the underlying record source.

The report compares ballot volume, age composition, individual ages 18 through 24, cumulative voting and the site's share of countywide college-age early votes. The individual-age chart switches between counts and share of all site ballots. The age-group table switches between 2026 versus 2024 and 2026 versus 2022, keeping rows in age order and showing the count and denominator behind each share. Party registration, gender, race and ethnicity remain separate selectable site-user breakdowns. [Download both age-group comparisons](data/processed/comparison/age_group_changes.csv).

![Individual ages 18–24 at Talley in 2024 and Western Boulevard in 2026, matched first 14 days](docs/images/talley-2024-vs-western-2026-college-ages.png)

### Retained 2022 midterm comparison

- Campus-site ballots, ages 18–24: **2,057 → 2,966 (+44.2%)**.
- Campus site share of Wake’s 18–24 early ballots: **26.3% → 17.0% (-9.3 percentage points)**.
- Ages 18–24 share of the site’s ballots: **29.4% → 28.3%**.

More college-age ballots were recorded at the replacement site, while countywide college-age early voting grew faster. The records cannot establish the move’s causal effect on student participation: enrollment and eligible-student denominators are unavailable, and mail/Election Day voting is outside this comparison.

![Talley versus Western Boulevard: accepted early ballots from ages 18–24, matched first 14 days](docs/images/talley-to-western-comparison.png)

### Rebuild the comparison

```bash
python scripts/download_early_voting_sources.py
python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-28
python scripts/validate_early_voting_comparison.py
python scripts/audit_campus_figures.py
python scripts/build_reference_page.py
python scripts/build_figure_sources.py
python scripts/build_source_previews.py
python scripts/refresh_report_snapshot.py
```

Use a complete voting day covered by the downloaded file. The report is a dated snapshot and does not fetch live data. After refreshing the snapshot, rebuild the interactive app and update date-specific narrative and chart exports as described in [report-source/README.md](report-source/README.md). Raw voter-level data stay ignored; the locked full-period 2022 baseline remains unchanged.

## Main research questions

- How many people used the NC State early-voting site in 2022 and 2026?
- Who used it by age, party registration, race, ethnicity and gender / sex field?
- How did the campus-area site compare with Wake County early voting overall?
- After the early-voting location changed, did site use, voter composition or voting method change?
- What happened in nearby Election Day precincts, without assuming precinct residents are NC State students?

## Project structure

- `references.html` — reporting source sheet with direct links and notes
- `methodology.md` — short methodology index
- `docs/early-voting-methodology.md` — early-voting source, filters and outputs
- `docs/election-day-methodology.md` — Election Day source, filters and outputs
- `docs/story-plan.md` — exact 2022-to-2026 reporting plan
- `scripts/build_2022_early_voting.py` — builds the Talley / Wake early-voting baseline
- `scripts/build_2022_election_day.py` — builds Wake Election Day precinct and polling-place baseline
- `data/processed/early_voting/` — publication-safe early-voting aggregates
- `data/processed/election_day/` — publication-safe Election Day aggregates
- `data/raw/` — ignored by Git; downloaded source files live here locally or temporarily in Actions

## 2022 early-voting source

North Carolina State Board of Elections, November 8, 2022 Absentee by County file:

https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip

The early-voting pipeline validates the Talley total against Wake County's published **10,390 ballots**.

## 2022 Election Day sources

NCSBE historical voter-history statistics:

https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/history_stats_20221108.zip

NCSBE polling places:

https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/polling_place_20221108.csv

## Reproducibility

Run the two baselines separately:

```bash
python scripts/build_2022_early_voting.py
python scripts/build_2022_election_day.py
```

GitHub Actions also rebuilds each side separately when its script or workflow changes. Raw voter-level data are not committed to this public repository.
