# Visual editor preview

`editor-preview.html` opens `editor-maps/index.html?view=1`. This independent Data report presents the five-age growth chart first, then the college-age actual-versus-county-share benchmark, followed by the original walking-distance and routine-route maps. It is intended for sharing with interviewees. The Technician masthead and section links, article narrative, byline and election opening are omitted. Chart captions, source links, map controls, numeric summaries, legends and evidence actions are retained.

The permanent app ID is stored in `identity.json`. `scripts/prepare_editor_maps.py --project-dir <prepared-project>` copies the current article’s reviewed evidence and shared map dependencies, then applies this composition while preserving the preview’s independent identity. Use the authorized source-build and packaging steps below to retain the requested toolbar-free view.

The preview follows the retained Technician article’s 800px story column and 44px desktop headline. Chart reference links open the worked calculations. Map-provider credits and source qualifications remain visible as plain text; source evidence is retained in the Data actions. Both charts reuse the article's exact components and reviewed full-period data, including 4,639 actual college-age ballots and the hypothetical 6,493 county-share benchmark.

The full article remains at `article/index.html?view=1`.

## Preview toolbar exception

Sean explicitly requested removing the entire top toolbar strip. This preview sets `report.hideTopbar=true`; the scoped runtime patch in `hide-topbar.patch` omits `DataAppTopbar` only for an opted-in report in view mode. Editing mode retains the toolbar. The article and all other reports keep their existing chrome. Component source actions remain available.

This requires the authorized source build rather than the prebuilt compiler. The project uses its locked dependencies (installation was approved by Sean). For a fresh prepared project, apply `hide-topbar.patch` to `src/DataAppShell.jsx`, then run the project's `scripts/authorize-protected-change.mjs` with `DATA_APP_USER_CONFIRMED=1`, `--confirmed`, `--scope src/DataAppShell.jsx`, and the explicit removal request as the reason. Do not authorize unrelated files.

Prepare the preview as above, build using `data-app.mjs build --project-dir <prepared-project> --source`, then package with `python scripts/package_editor_maps.py --dist <project>/dist --source-project <project>`. The standalone source build embeds the reviewed snapshot. Packaging verifies the build's snapshot hash and writes `source-build-receipt.json`, replacing the previous split-build receipt. No published ballot values change.
