# Report authoring source

`snapshot.json` is the complete aggregate-only reviewed snapshot with stable artifact ID. `report/ReportContent.jsx` and `report/report.css` are the authored content. The compiled root `index.html` uses the verified Codex Data shared runtime; it requires the root content-addressed snapshot JSON sidecar.

To revise in Codex, use the installed Data app preparer with `--surface report --snapshot report-source/snapshot.json --output <new-project>`, read its AGENTS.md, copy these report files into `src/content/report/`, preserve the existing snapshot and artifact ID in `src/data.json`, and build with the installed `data-app.mjs build --project-dir <project> --separate-data`. Copy its verified `dist` files to the repository root. Keep all data and date-specific narrative synchronized on refresh. For a portable offline file use `data-app.mjs export-offline` and deliver the result locally; the deployed split build is retained in Git.
