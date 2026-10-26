# NC State Campus Voting

Data and reporting workspace for a Technician follow-up on voting at NC State.

The main comparison is intentionally simple: **2022 general election vs. 2026 general election**. Early voting and Election Day are kept separate because the voting rules and source data are different.

## October 26, 2026 update: Talley to Western Boulevard

**[Open the interactive comparison](https://strokeofluck.github.io/ncsu-campus-voting/)** · [Findings and methods](docs/2026-early-voting-update.md) · [Aggregate downloads](data/processed/comparison/)

The latest NCSBE file covers early voting through **October 25**. Compare the first **11 days** of 2022 Talley voting with the first 11 days at **NCSU Western Boulevard Business Services**, 1220 Varsity Drive.

- Ages 18–24 at the campus site: **1,259 → 1,866 (+48.2%)**.
- Campus site share of Wake's 18–24 early ballots: **23.3% → 14.8% (−8.4 percentage points)**.
- Ages 18–24 share of the site's own ballots: **25.9% → 25.0%**.

More college-age ballots were recorded at the replacement site, while countywide college-age early voting grew faster. These preliminary records cannot establish the move's causal effect on NC State student participation: ages 18–24 are an age proxy, enrollment and eligible-student denominators are unavailable, and mail/Election Day voting is outside this comparison.

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
