# NC State Campus Voting

Data and reporting workspace for a Technician follow-up on voting at NC State.

The interactive report compares **Talley Student Union in 2024 with Western Boulevard Business Services in 2026**, using the same first 11 early-voting days. **2024 was a presidential election; 2026 is a midterm.** A selector retains the 2022-to-2026 midterm comparison. Early voting and Election Day are kept separate.

## 2024 Talley versus the new 2026 location

**[Open the interactive demographic charts](https://strokeofluck.github.io/ncsu-campus-voting/)** · [Methods and all three years](docs/2026-early-voting-update.md)

| Campus-site measure, matched first 11 days | Talley, 2024 | Western Boulevard, 2026 |
| --- | ---: | ---: |
| Accepted ballots, ages 18–24 | 4,939 | 1,866 |
| Ages 18–24 share of all site ballots | 38.0% | 25.0% |
| Site share of Wake's 18–24 early ballots | 21.5% | 14.8% |
| Accepted ballots, all ages | 12,990 | 7,463 |

College-age ballots at the site were **62.2% lower than in the matched 2024 period**, while Wake County's college-age ballots were **45.1% lower**. The site’s college-age share fell **13.0 percentage points**. This descriptive comparison cannot isolate the location move from presidential-versus-midterm participation or other changes. Ages 18–24 are an age proxy, not verified NC State students.

The charts compare ballot volume, age composition, individual ages 18 through 24, daily cumulative voting and the site's share of countywide college-age early votes. The individual-age chart switches between counts and share of all site ballots. The older 2022 midterm baseline remains available.

### Exact campus-site counts, all three years

The interactive report includes this campus-only table above the charts. [Download the campus-site CSV](data/processed/comparison/campus_site_matched_counts.csv).

**[Verify every highlighted figure against its source and arithmetic](https://strokeofluck.github.io/ncsu-campus-voting/verify-figures.html).** The reference page links to the real NCSBE download entries and labels the site totals and percentages as project calculations from official records.

| Site / year | All ages | Ages 18–24 | Ages 18–22 | 18–24 share | Same-day registration |
| --- | ---: | ---: | ---: | ---: | ---: |
| Talley Student Union · 2022 | 4,863 | 1,259 | 970 | 25.9% | 204 |
| Talley Student Union · 2024 | 12,990 | 4,939 | 3,983 | 38.0% | 842 |
| Western Boulevard · 2026 | 7,463 | 1,866 | 1,448 | 25.0% | 297 |

Each row covers the first 11 early-voting days. Dates are October 20–30, 2022; October 17–27, 2024; and October 15–25, 2026. 2026 is preliminary. Same-day registrations include all ages. The age share is a share of site ballots; 2024 was presidential and the other two elections are midterms.

![Age composition at Talley in 2022 and 2024 and Western Boulevard in 2026, matched first 11 days](docs/images/campus-age-composition-2022-2024-2026.png)

![Individual ages 18–24 at Talley in 2024 and Western Boulevard in 2026, matched first 11 days](docs/images/talley-2024-vs-western-2026-college-ages.png)

## October 26, 2026 update: Talley to Western Boulevard

**[Open the interactive comparison](https://strokeofluck.github.io/ncsu-campus-voting/)** · [Findings and methods](docs/2026-early-voting-update.md) · [Aggregate downloads](data/processed/comparison/)

The latest NCSBE file covers early voting through **October 25**. Compare the first **11 days** of 2022 Talley voting with the first 11 days at **NCSU Western Boulevard Business Services**, 1220 Varsity Drive.

- Ages 18–24 at the campus site: **1,259 → 1,866 (+48.2%)**.
- Campus site share of Wake's 18–24 early ballots: **23.3% → 14.8% (−8.4 percentage points)**.
- Ages 18–24 share of the site's own ballots: **25.9% → 25.0%**.

More college-age ballots were recorded at the replacement site, while countywide college-age early voting grew faster. These preliminary records cannot establish the move's causal effect on NC State student participation: ages 18–24 are an age proxy, enrollment and eligible-student denominators are unavailable, and mail/Election Day voting is outside this comparison.

![Talley versus Western Boulevard: accepted early ballots from ages 18–24, matched first 11 days](docs/images/talley-to-western-comparison.png)

Rebuild the aggregate comparison:

```bash
python scripts/download_early_voting_sources.py
python scripts/build_early_voting_comparison.py --cutoff-date 2026-10-25
python scripts/validate_early_voting_comparison.py
```

The cutoff is a complete voting day, not the time this page was opened. The report is a dated snapshot and does not fetch live data. The locked full-period 2022 baseline is preserved. Raw voter-level data stay ignored.

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
