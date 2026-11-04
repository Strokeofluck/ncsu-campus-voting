# Talley to Western Boulevard: worked Excel audit

The primary download on `references.html#excel-download` recalculates the article's 2022–2026 comparison and five nonoverlapping age groups from the latest official NCSBE Wake CSV members. Readers can also choose downloaded CSVs using the adjacent official ZIP links and numbered instructions. No original voter records or populated workbook are published to the website.

The ZIP separates untouched input bytes in `01 Original files/2022/` and `01 Original files/2026/`, the editable workbook in `02 Working copy/`, and the source manifest in `03 Source checks/`. Updated mode records the input hashes and freshly calculated counts; snapshot mode requires both hashes and all 20 counts to match the saved article. The matched windows remain October 20–November 5, 2022 and October 15–31, 2026.

NCSBE replaces the live 2026 archive. Updated mode (the default) accepts changed source bytes and computes new counts, growth and gaps while retaining the complete matched 17-day windows. It records actual input CSV hashes, retrieval/read time, input kind, original snapshot metadata and both old/new result sets in the manifest. The workbook cover, source sheet, README and separate updated-results note clearly identify the revised calculation. An additional CSV exports the five updated result rows. The dated article and its reference figures are not refreshed by this calculator.

The optional **Article snapshot** calculation for chosen CSVs still requires both original hashes and all 20 saved age/scope/year counts to match. Choose the saved CSVs from `01 Original files` in the original download for that mode. Files stay local. Historical S3 versions are listed but return HTTP 403 for public downloads, so the default updated mode does not depend on recovering an older upstream file.

## Workbook sequence

1. **Growth gaps** links the five completed results.
2. **0 Sources** documents exact locations, dates, source URLs, hashes and original record totals. Relative hyperlinks open the separate untouched CSVs after the entire ZIP is extracted.
3. **Copy 2022 / Copy 2026** contain every input row and all source columns, in order, stored as text. Six highlighted headers identify the fields used. Original record totals are recorded in each package manifest; updated input lengths are determined at export time.
4. **1 Fields 2022 / 1 Fields 2026** retain every original record. Six actual blank-preserving Excel formulas link to the corresponding Copy cells; the added record number identifies the original CSV record, with header as record 1.
5. **2 Rules 2022 / 2 Rules 2026** parse dates and ages and test county, early-voting type, acceptance, matched dates and exact location. County and named-site contributions add 1 or 0, with conditional highlights and running SUMs. These flags include all ages; the next step applies each age band's limits.
6. **3 Counts** uses bounded COUNTIFS for the five inclusive age ranges, separately by year and county/site scope.
7. **4 Growth math** links those counts, subtracts 2022 from 2026, divides by 2022, multiplies by 100, then subtracts county growth from location growth. Rows 15–17 separately show the countywide college-age share and its percentage-point change.

All original records remain in the fields and rules tabs, including rejected, mail and outside-window records. Changing a copied source value updates the affected links, rules, counts and formulas; there is no fixed candidate extract. Adding records requires rebuilding or extending all relevant ranges. Original CSV files remain unchanged.

## Snapshot example: exact worked cells

`4 Growth math!B6:C6 links 3,402 and 4,639 site ballots, giving 36.3609641% growth. G6:H6 links 13,398 and 25,570 Wake ballots, giving 90.8493805% growth. L6 is =F6-K6, yielding −54.4884164 percentage points.

The county-share calculation is 3,402 / 13,398 = 25.3918495% and 4,639 / 25,570 = 18.1423543%. The unrounded change is −7.2494952 percentage points. These shares use the same age group across Wake County, not a registered-student denominator.

## Build and checks

`article-excel-plan.js` owns the shared native formulas and inclusion rules. `scripts/build_article_excel_template.mjs` authors and recalculates the template using the bundled Artifact Tool; it verifies an edit to a copied age propagates through counts and growth. Pass an absolute scratch directory. The checked, non-sensitive template is embedded in `article-excel-template.json`. Source field names are recorded in `report-source/article-excel-headers.json`.

`article-excel-worker.js` reads only the official ZIP members using the existing HTTP-range reader, then `article-excel-export.js` streams full copied worksheets and native formula rows into the workbook. Cached results match the verified counts; automatic full Excel recalculation is requested. No macros or uploads are used. Opening and recalculating this large workbook can take several minutes in desktop Excel.

`python scripts/test_article_excel_export.py /absolute/package.zip` verifies every copied cell, linked field, cached inclusion flag and running sum against the separate original CSVs, then checks counts, growth, share formulas and full-range highlights. `--summary-only` checks finished counts, arithmetic, share formulas and recalculation metadata without repeating every unchanged source row. The browser workflow is also checked with small source fixtures, including range reads, source-hash checks, count mismatch rejection, retry and a real ZIP download.

Full-workbook recalculation in desktop Microsoft Excel was not run. The Artifact Tool boundary fixture was recalculated, including a source-cell edit; the populated export's formula XML and cached results are checked separately.
