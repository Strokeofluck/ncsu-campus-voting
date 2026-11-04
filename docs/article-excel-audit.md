# Talley to Western Boulevard: worked Excel audit

The primary download on `references.html#excel-download` covers only the article's 2022–2026 comparison and five nonoverlapping age groups. It is generated locally from the official NCSBE Wake CSV members. No original voter records or populated workbook are published to the website.

The ZIP separates untouched bytes in `01 Original files/2022/` and `01 Original files/2026/`, the editable workbook in `02 Working copy/`, and the source manifest in `03 Source checks/`. Both original CSV SHA-256 hashes and all 20 age/scope/year counts must match the saved article before export succeeds. The matched windows remain October 20–November 4, 2022 and October 15–30, 2026. The 2026 evidence is preliminary through October 30.

NCSBE replaces the live 2026 archive. Its historical S3 versions are listed but return HTTP 403 for public downloads. The live file checked November 3 changes three of the saved age/site/county counts, so it cannot reproduce this snapshot. If a source hash has changed, the page opens **Rebuild from saved original CSVs**. Choose both untouched CSVs from `01 Original files` in the original download. They are passed directly to the local worker, never uploaded, and the existing hash and all 20 count checks remain mandatory. Both source hashes are checked before expensive workbook generation begins. A changed source or count cannot produce a success download.

## Workbook sequence

1. **Growth gaps** links the five completed results.
2. **0 Sources** documents exact locations, dates, source URLs, hashes and original record totals. Relative hyperlinks open the separate untouched CSVs after the entire ZIP is extracted.
3. **Copy 2022 / Copy 2026** contain every original row and all 42 original columns, in order, stored as text. Six highlighted headers identify the fields used. There are 267,949 and 327,240 data records respectively.
4. **1 Fields 2022 / 1 Fields 2026** retain every original record. Six actual blank-preserving Excel formulas link to the corresponding Copy cells; the added record number identifies the original CSV record, with header as record 1.
5. **2 Rules 2022 / 2 Rules 2026** parse dates and ages and test county, early-voting type, acceptance, matched dates and exact location. County and named-site contributions add 1 or 0, with conditional highlights and running SUMs. These flags include all ages; the next step applies each age band's limits.
6. **3 Counts** uses bounded COUNTIFS for the five inclusive age ranges, separately by year and county/site scope.
7. **4 Growth math** links those counts, subtracts 2022 from 2026, divides by 2022, multiplies by 100, then subtracts county growth from location growth. Rows 15–17 separately show the countywide college-age share and its percentage-point change.

All original records remain in the fields and rules tabs, including rejected, mail and outside-window records. Changing a copied source value updates the affected links, rules, counts and formulas; there is no fixed candidate extract. Adding records requires rebuilding or extending all relevant ranges. Original CSV files remain unchanged.

## Exact worked cells

`4 Growth math!B6:C6` link the ages 18–24 Talley/Western counts, 2,999 and 4,214. D6 subtracts, E6 divides by B6 and F6 multiplies by 100, yielding 40.5135045…%. G6:H6 link the Wake counts, 11,287 and 22,980. I6 subtracts, J6 divides by G6 and K6 multiplies by 100, yielding 103.5970586…%. L6 is `=F6-K6`, yielding −63.0835541… percentage points.

The supporting share calculation uses `D15=B15/C15` (2,999 / 11,287, formatted as 26.6%) and `D16=B16/C16` (4,214 / 22,980, formatted as 18.3%). D17 is `=(D16-D15)*100`, yielding −8.2327058… percentage points. Only displays are rounded. These are shares of the same age group's early ballots across the whole county, not turnout rates or shares of a single precinct.

## Build and checks

`article-excel-plan.js` owns the shared native formulas and inclusion rules. `scripts/build_article_excel_template.mjs` authors and recalculates the template using the bundled Artifact Tool; it verifies an edit to a copied age propagates through counts and growth. Pass an absolute scratch directory. The checked, non-sensitive template is embedded in `article-excel-template.json`. Source field names are recorded in `report-source/article-excel-headers.json`.

`article-excel-worker.js` reads only the official ZIP members using the existing HTTP-range reader, then `article-excel-export.js` streams full copied worksheets and native formula rows into the workbook. Cached results match the verified counts; automatic full Excel recalculation is requested. No macros or uploads are used. Opening and recalculating this large workbook can take several minutes in desktop Excel.

`python scripts/test_article_excel_export.py /absolute/package.zip` verifies every copied cell, linked field, cached inclusion flag and running sum against the separate original CSVs, then checks counts, growth, share formulas and full-range highlights. `--summary-only` checks finished counts, arithmetic, share formulas and recalculation metadata without repeating every unchanged source row. The browser workflow is also checked with small source fixtures, including range reads, source-hash checks, count mismatch rejection, retry and a real ZIP download.

Full-workbook recalculation in desktop Microsoft Excel was not run. The Artifact Tool boundary fixture was recalculated, including a source-cell edit; the populated export's formula XML and cached results are checked separately.
