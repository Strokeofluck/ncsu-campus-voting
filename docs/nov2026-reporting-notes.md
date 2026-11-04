# November 4, 2026 reporting notes: NC State early voting

**Status: PRELIMINARY NCSBE accepted in-person early-voting records.** Comparing all 17 early-voting days in the November 2022 and November 2026 midterm general elections. The 2026 source archive was last modified November 4, 2026, at 10:28:57 UTC (5:28:57 a.m. Eastern). Both comparison sites and the countywide denominators are taken from official NCSBE absentee-by-county ZIPs; no 2024 presidential comparison is used here.

## Possible lead

The NC State-area early-voting location recorded 14,496 accepted ballots in 2026 at Western Boulevard Business Services, versus 10,390 at Talley Student Union in 2022, **a 39.5% increase**. Yet Wake County's early voting rose more quickly, by **52.4%** (219,169 to 334,088). The campus location's share of Wake's accepted early ballots slipped from **4.74% to 4.34%**, a 0.40-percentage-point drop.

For ages **18–24**, the campus-site count increased **3,402 to 4,639 (+36.4%)**, while Wake County's count rose **13,398 to 25,570 (+90.8%)**. The campus site's share of all Wake early ballots cast by people age 18–24 fell from **25.39% to 18.14%**, a **7.25-percentage-point decrease**. This is the strongest descriptive angle, but the age band does not establish NC State enrollment, and early-voting site use is not turnout among eligible students.

Same-day registration was **763 to 993** (+30.1%), but the share of campus-site ballots with same-day registration fell slightly, **7.34% to 6.85%**. This is a subset of accepted ballots, not additional ballots.

## Where campus-site use changed by registered home precinct

These compare **site use among residents who voted early anywhere in Wake County**, not the voting site's physical precinct and not individual voters tracked over time. 2022 uses Talley, 2026 uses Western Boulevard.

| Residential precinct | Site-use share 2022 | Site-use share 2026 | Change (percentage points) | Campus-site ballots 2022 → 2026 |
| --- | ---: | ---: | ---: | ---: |
| 01-31 | 56.14% | 69.51% | +13.38 | 398 → 823 |
| 01-32 | 28.42% | 45.24% | +16.82 | 187 → 451 |
| 01-33 | 41.95% | 15.35% | -26.60 | 198 → 118 |
| 01-16 | 27.49% | 4.62% | -22.87 | 210 → 68 |
| 01-03 | 48.20% | 29.33% | -18.87 | 254 → 239 |
| 01-23 | 76.81% | 77.88% | +1.07 | 967 → 1,542 |

All six have at least 200 accepted early ballots from their residential precinct in each year. These are examples worth mapping, not a comprehensive ranking. The complete precinct table is in the source CSV. Check for precinct boundary and population changes before suggesting neighborhood behavior. The increase near current Western Boulevard precinct 01-31 is consistent with changed site-use geography, but does **not** prove the relocation caused a shift.

## Registered party and other site-user demographics

The registered **unaffiliated** share at the campus site increased from **44.5% to 49.7%**; registered **Republicans** decreased from **10.8% to 6.6%**, while registered **Democrats** were **44.2% to 43.3%**. These are party **registrations**, not votes for candidates. The site's **65+** share increased from **11.6% to 14.5%**, while the **18–24** share changed from **32.7% to 32.0%**. Race, ethnicity and gender are also available as NCSBE categorical counts in the demographics CSV, with many 'undesignated' or unknown records; no identity or enrollment inference is justified.

## Audit trail and follow-up

- [Computed summary and QA](../data/processed/nov2026/research_summary.json)
- [Site and county comparison](../data/processed/nov2026/2022_vs_2026_summary.csv)
- [All demographic categories](../data/processed/nov2026/2022_vs_2026_demographics.csv)
- [Home-precinct/site-use changes](../data/processed/nov2026/2022_vs_2026_residential_precincts.csv)
- [Early voting by day](../data/processed/nov2026/2022_vs_2026_daily.csv)
- [Reproducible source and methodology](../data/processed/nov2026/README.md)
- [2026 original NCSBE ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_county_20261103.zip)
- [2022 original NCSBE ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip)

The public repo contains **aggregates only**. Original names, addresses and NCIDs remain in ignored source storage when the script runs. The 2022 baseline reconciles exactly to 10,390 Talley accepted early ballots, and the 2026 comparison has one unique accepted early-voter ID per counted ballot. The 2026 Wake accepted-early count is two ballots lower than the November 2 public dashboard's 334,090 early-in-person total, which uses a different snapshot and counting basis; investigate only if that difference widens or affects a claimed figure.

The November 3 **Election Day** comparison requires finalized NCSBE voter-history data and should be maintained separately. NCSBE says post-election canvass/certification is still underway; county canvass is November 13 and state canvass November 24, 2026. Revisit published 2026 figures after certification. This comparison is descriptive; site changes, population changes, precinct changes and the broader rise in voting may all contribute.
