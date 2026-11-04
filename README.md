# NC State Campus Voting

Updated November 4, 2026. The article, charts, references and Excel calculator now compare **all 17 early-voting days** in 2022 and 2026. The 2026 NCSBE records remain preliminary during canvass.

**[Article draft](https://strokeofluck.github.io/ncsu-campus-voting/article/index.html?view=1) · [References and step-by-step math](https://strokeofluck.github.io/ncsu-campus-voting/references.html) · [Interactive research report](https://strokeofluck.github.io/ncsu-campus-voting/index.html?view=1) · [Map editor preview](https://strokeofluck.github.io/ncsu-campus-voting/editor-maps/index.html?view=1)**

College-age early ballots at the campus-area location increased **3,402 → 4,639 (+36.4%)**, while Wake County increased **13,398 → 25,570 (+90.8%)**. The growth gap is **54.5 percentage points**. The site's share of Wake's ages 18–24 early ballots fell **25.4% → 18.1%**. These are site-use counts and county shares, not turnout rates among enrolled or eligible students.

All-age campus-site early ballots increased **10,390 → 14,496 (+39.5%)**. Wake County increased **219,169 → 334,088 (+52.4%)**. Campus-site same-day registrations increased **763 → 993 (+30.1%)**, and are already included in the total ballots.

Periods: **October 20–November 5, 2022**, and **October 15–31, 2026**. 2024 is retained only as a separate presidential-election benchmark in the research prototype. The old first-16-day article figures are superseded; the uploaded October 31 statewide screenshot remains explicitly labeled as historical.

## Sources and reporting files

- [Current reporting notes, all five ages, sources and rebuild commands](docs/2026-early-voting-update.md)
- [Independent November 4 two-year research](docs/nov2026-reporting-notes.md)
- [All reviewed comparison CSVs](data/processed/comparison/)
- [Independent two-year CSVs](data/processed/nov2026/)
- [Methodology](methodology.md)
- [Article/Excel calculations and audit design](docs/article-excel-audit.md)
- [Authored report and build instructions](report-source/README.md)

The references page provides both a live official-file recalculation and an exact saved-snapshot mode. Both use the complete 17-day windows. Excel contains untouched source CSVs, full original-record copies, linked fields, rule flags, COUNTIFS totals and worked percentage/gap formulas. Later source corrections may produce different results; input hashes and calculation dates remain visible.

## Interpretation and privacy

Early voting and Election Day are separate analyses. Election Day and mail ballots are excluded from this comparison. A complete early period does not mean certified final results. Age does not verify student enrollment, party registration does not identify candidate choices, and current precinct polygons do not reconstruct historical boundaries. These descriptive comparisons cannot isolate the effect of relocating the site.

Public outputs contain aggregates only. Names, addresses and voter identifiers remain in ignored `data/raw/` storage and browser-local downloads. No original voter-level records or populated workbooks are hosted in this public repository.
