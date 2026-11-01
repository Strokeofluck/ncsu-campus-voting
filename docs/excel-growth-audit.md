# College-age growth: CSV to Excel audit

The two primary figures compare the first 16 early-voting days of 2022 and 2026. Ages 18–24 are an age proxy, not confirmed students. The 2026 snapshot is preliminary through October 30. Wake County includes the named site.

| Scope | 2022 count | 2026 count | Subtract | Divide by 2022 | Multiply by 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Talley to Western | 2,999 | 4,214 | 1,215 | 0.405135045 | 40.513504502% |
| Wake County | 11,287 | 22,980 | 11,693 | 1.035970586 | 103.597058563% |

Only the displayed result is rounded to 40.5% or 103.6%. The workbook retains full precision and an alternate 2024 baseline.

## Exact workbook cells

`8 Growth proof!B6` links to `'3 Counts'!D7` (the 2022 site count); C6 links to `'3 Counts'!F7` (2026). B7 and C7 link to `'7 County counts'!B6` and B8 respectively. Each result then has separate actual formula cells:

- D6: `=C6-B6`
- E6: `=IF(B6=0,"",D6/B6)`
- F6: `=IF(B6=0,"",E6*100)`
- Row 7 uses the same sequence for the countywide counts.

G–I quote those formulas as readable text. They are separate from the actual formulas in B–F.

`7 County counts!B6` is `=SUM('6 County flags'!$J$6:$J$19834)`. B7 sums J19835:J77883; B8 sums J77884:J102714. The included-record contribution in J is 1 or 0. E independently counts the 1s with COUNTIFS; F sums the site and other-Wake parts. G and H compare these totals and equal zero in all three years.

## What was verified

- All three separate original CSVs have the exact recorded government-file SHA-256 hashes.
- All 47,703,726 Excel Copy cells, including the original headers, match the original CSVs in order: 1,135,800 data records, 42 columns per year. Original CSV bytes are not edited or formatted.
- All 45,398 campus extract rows link to their exact Copy cells. All original site fields remain text; dates, numeric ages and inclusion flags are calculated separately.
- All 102,709 county age-18–24 candidate rows retain their original record numbers and seven exact source values, including rejected and outside-window candidates. Every linked cell, contribution and running sum was checked.
- County sums are 11,287, 40,465 and 22,980. Their independently recounted site parts are 2,999, 8,950 and 4,214. Other-Wake parts reconcile exactly.
- Every final growth formula, cached result, SUM/COUNTIFS reconciliation and full-range highlight was checked in the exported XLSX.
- The authored formulas were recalculated on boundary fixtures, including edits to copied ages and dates. The full browser download finished with matching source hashes and counts. Full-workbook Microsoft Excel recalculation was not run during this audit; the file requests automatic full recalculation when opened.

The source extracts have fixed membership for the verified snapshot. Editing a referenced copied value recalculates its downstream formulas, but adding candidates requires rebuilding the download. The original CSV files in `01 Original files` remain unchanged. Populated workbooks, ZIPs and individual voter records are never published in this repository; the website builds the download locally in the reader’s browser.

Audited local XLSX SHA-256: `4f0591959b0b06ae10e4b9918b92322a7e3ba499c5310805079839fa0c2e7c89`.

## Individual ages and the comparison of shares

The workbook now has thirteen tabs. The five usual age bands stay in `3 Counts` and `4 Math`; the overlapping 18–22 row has been removed from those worksheets. Same-day registration is row 12 and remains a separate subset. `9 Individual ages!A6:D108` lists ages 18–120 and each year’s site counts. The new count cells use real bounded COUNTIFS over the year, included-ballot flag and exact parsed age in `2 Filter flags`. B109:D109 use SUM over those counts and reconcile to 9,339, 20,350 and 13,266. Ages above 99 currently have zero ballots.

`8 Growth proof!B22:C22` links to the college-age shares already calculated in `4 Math`. B23 and C23 divide the site college-age count by the corresponding county college-age count; D22 and D23 subtract unrounded shares and multiply by 100. The site’s age mix changes from 32.1% to 31.8%, while its share of Wake’s college-age early ballots changes from 26.6% to 18.3%. These are different denominators. The two growth rows still show 40.5% for the site and 103.6% for Wake.

The updated template was recalculated with Artifact Tool, including an individual-age edit that moved a ballot between age rows. All 309 age COUNTIFS results, three SUM results, shifted SDR formulas and new share formulas were checked in the saved XLSX. The browser-built ZIP completed with matching source hashes and counts; the age/count formula XML was compared with the independently validated local export. The populated share rows were also checked to preserve the authored percentage and percentage-point number formats. All original-copy cells and both source extracts were checked again. Full-workbook Microsoft Excel recalculation was not run; automatic full recalculation remains enabled.
