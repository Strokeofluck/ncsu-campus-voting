# Talley versus Western Boulevard: comparison inventory

The main reporting question is whether changing NC State's early-voting location affected college-age participation. Investigate negative, neutral and positive findings with the same standards. Site ballot volume is not a turnout rate or an estimate of the move's causal effect.

## Current evidence

The reviewed snapshot covers the first 16 early-voting days: October 20–November 4, 2022; October 17–November 1, 2024; and October 15–30, 2026. The 2026 source is preliminary. Use the latest complete day actually covered by official records on a future refresh. Keep the 2022-to-2026 midterm comparison primary; 2024 is a presidential benchmark.

| Measure | Talley, 2022 | Western Boulevard, 2026 |
| --- | ---: | ---: |
| All accepted early ballots | 9,339 | 13,266 |
| Ages 18–24 accepted early ballots | 2,999 | 4,214 |
| Ages 18–24 / all site ballots | 32.1% | 31.8% |
| Site ages 18–24 / all Wake ages 18–24 early ballots | 26.6% | 18.3% |
| Same-day registration, all ages | 646 | 877 |
| Same-day registration / all site ballots | 6.9% | 6.6% |

College-age site ballots increased 40.5%; the within-site age mix was almost unchanged. The smaller countywide share uses a different denominator and does not establish a decline in resident turnout. Same-day registrations increased 35.8%, versus 42.0% growth in all site ballots.

## Compare now from reviewed aggregates

- **Volume:** all ages, ages 18–24, ages 18–22, and same-day registration, for the campus site, other Wake sites, and Wake overall. Show starting and ending counts, absolute changes and percentage changes for both baselines.
- **Composition:** age groups, each individual age from 18 through 24, and separately party registration, recorded gender, race and ethnicity. Retain exact counts, denominators, unknowns and unrounded shares behind displayed percentages.
- **Timing:** daily and cumulative counts, aligned by day of early voting. Compare weekday/weekend patterns and final-day concentration only for complete, comparable windows. A calendar-day match does not equate opening hours.
- **County context:** each site's share of the same age cohort's Wake ballots, growth at all other sites combined, distribution across individual Wake sites, and changes in that distribution. These can reveal redistribution without proving the same people changed sites.
- **Benchmarks:** 2022 midterm and 2024 presidential comparisons, separately labeled. Full historical periods can be contextual totals, but cannot be used as the denominator of a change against a partial 2026 period.

[`expanded_matched_comparisons.csv`](../data/processed/comparison/expanded_matched_comparisons.csv) contains 24 rows: two baselines × three scopes × four overlapping ballot cohorts. It includes exact counts, absolute and relative changes, shares of all ballots in the selected scope, shares of the same cohort's Wake ballots, and percentage-point changes. Wake contains the campus and other-site scopes; age and registration cohorts overlap. Do not add overlapping rows.

## Further cuts requiring original-record calculations

- Same-day registration by age group and each age 18–24, including its share of each corresponding age cohort's ballots.
- Same-day registrations by date, weekday/weekend and site; age by party, race, ethnicity or gender where fields are complete enough.
- Counts and composition by residential precinct for campus-site users, keeping voting location distinct from residence.
- Campus-area residents using other early-voting locations, where residence geography can be defined consistently and linked to accepted ballots.

Verify the original fields, missingness, duplicate rules, geography and completeness before calculating these. The existing aggregate demographic file does not provide every joint cross-tabulation. Do not infer joint counts from separate marginal totals. These cuts are not yet published as completed results.

## Evidence to acquire before additional claims

- Official opening dates, daily hours and site availability in each election, before computing ballots per open hour or comparing capacity.
- Verified addresses, walking/travel routes, transit service, parking and accessibility information; measure exposure for a defined residence area rather than assuming proximity identifies students.
- Registered residents by age in stable campus-area boundaries, with contemporaneous registration dates and eligibility rules, to supply a resident turnout denominator.
- Complete early, mail and Election Day history for the same residential population; use final accepted voting history when available and avoid double counting.
- Documented student-enrollment linkage or approved aggregate institutional evidence before making claims specifically about NC State students.
- Earlier comparable elections and suitable comparison areas to inspect prior trends, boundary changes, population shifts and election-cycle differences.

## Analysis of impact

Separate site use, population composition, location/method substitution and overall participation. Define the exposed residential population before inspecting its voting outcome. Compare its turnout change with appropriate comparison areas; evaluate pre-trends, population/registration changes, site hours, other sites, mobilization and election differences. Difference-in-differences or similar designs require a defensible counterfactual and cannot create causality from site totals. Report uncertainty and sensitivity to the age proxy and geography. An absence of a demonstrated effect is not proof that the move had no effect.

## Sources and continuation

- [Live report](https://strokeofluck.github.io/ncsu-campus-voting/)
- [Repository](https://github.com/Strokeofluck/ncsu-campus-voting)
- [Official NCSBE absentee and provisional catalog](https://www.ncsbe.gov/results-data/absentee-and-provisional-data)
- [Existing filters, freshness and limitations](2026-early-voting-update.md)
- [Aggregate comparison JSON](../data/processed/comparison/comparison.json)
- [Exact figure evidence](../data/processed/comparison/figure_sources.json)
- [Report authoring source](../report-source/README.md)

Continue in the same report and repository. Preserve its identity, existing figures, source links, baseline selector and verified aggregate data. Refresh all dependent dates and figures together. Keep raw names, addresses, voter IDs and individual rows out of public commits and exports. If the next environment lacks GitHub write access or the required report build tooling, provide a concrete patch and calculations without claiming the live page was updated.
