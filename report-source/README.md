# Report authoring source

`snapshot.json` is the complete aggregate-only reviewed snapshot with stable artifact ID. `report/ReportContent.jsx` and `report/report.css` are the authored content. The compiled root `index.html` uses the verified Codex Data shared runtime; it requires the root content-addressed snapshot JSON sidecar.

To revise in Codex, use the installed Data app preparer with `--surface report --snapshot report-source/snapshot.json --output <new-project>`, read its AGENTS.md, copy these report files into `src/content/report/`, preserve the existing snapshot and artifact ID in `src/data.json`, and build with the installed `data-app.mjs build --project-dir <project> --separate-data`. Copy its verified `dist` files to the repository root. Keep all data and date-specific narrative synchronized on refresh. For a portable offline file use `data-app.mjs export-offline` and deliver the result locally; the deployed split build is retained in Git.

After rebuilding and validating the comparison, run `scripts/audit_campus_figures.py`, `scripts/build_reference_page.py` and `scripts/refresh_report_snapshot.py`. The audit reads the comparison's current matched dates, and the report derives displayed date ranges from those rows. Refresh the README, reporting notes, references freshness and saved chart images before publication. Keep `buildStatus` as `updating` during checks and set it to `complete` for the final verified build.

`figure-source.html` in this source folder is the standalone evidence-page template. Run `python scripts/build_figure_sources.py` from the repository after refreshing validated data; it writes the public root evidence page and aggregate JSON. Publish those files alongside the compiled report. The original report identity remains unchanged.
