# Post-election data, November 4, 2026

2026 results are unofficial. These aggregates include current reported all-method ballot totals, accepted early/mail extracts, provisional status, and Election Day choice votes by contest. They do not yet provide Election Day or all-method age-18–24 participation. NCSBE updates current voter history weekly, and county finalization can take multiple weeks.

`county_ballots_and_turnout.csv` preserves the dashboard ballot/registration/turnout fields for all 100 counties plus the statewide aggregate in each year. STATE is an aggregate: do not add it to counties. `state_and_wake_comparison.csv` compares 2022 official with 2026 unofficial results. Rates shown are the dashboard's rounded rates, not an age-specific denominator.

`accepted_early_and_mail.csv` and `accepted_mail_demographics.csv` use the official county absentee files. Accepted mail includes ACCEPTED, ACCEPTED - CURED and ACCEPTED - EXCEPTION where present. Status counts remain separate. The 2026 Wake totals independently match NCSBE's demographic aggregate file. Early and mail extracts are separate from the later results-dashboard snapshot, and must not be subtracted from it to assert an Election Day voter count.

`wake_contest_votes_by_method.csv` contains votes for choices within each contest. Never sum different contests as voters. Multi-seat races permit multiple choices; undervotes also prevent treating a single contest as unique ballot counts. The Election Day column is evidence of votes cast in that method, not demographic turnout. `wake_provisional_status.csv` counts pending records; pending is not accepted.

`availability.json` records the missing 2026 demographic history release and the pre-election timestamp of current statewide voter history. The available Nov. 3 registration statistics group ages 18–25, which do not match the article's 18–24 group. They are not substituted for the missing election participation data.

Sources: [NCSBE results dashboard](https://er.ncsbe.gov/), [historical election result layouts](https://www.ncsbe.gov/results-data/election-results/historical-election-results-data), [voter history availability and release schedule](https://www.ncsbe.gov/results-data/voter-history-data). Download timestamps, source URLs and SHA-256 values are in source_manifest.json. Raw voter files stay outside published artifacts.
