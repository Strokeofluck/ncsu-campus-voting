# Article — work in progress

Published route: `article/index.html?view=1`. The article has a separate stable Data app identity from the prototype. Its reviewed snapshot is `../article-snapshot.json`.

The five article maps show actual votes cast at Talley in 2022 and Western Boulevard in 2026. `SiteAgeMaps.jsx` uses official university building coordinates and two proportional circles per age group, with one shared area scale (radius = 40 × sqrt(ballots / 4214)). Direct labels and pointer/keyboard tooltips give exact counts. Neutral precinct outlines provide context only. Reviewed counts, matched periods and growth comparisons are unchanged. The prototype retains its original home-precinct choropleths; article maps do not group voters by home address.

The article opens with a sourced statewide introduction and an explicitly marked Latin draft placeholder. Its main visual is the ages 18–24 map, followed by the worked actual-versus-constant-share benchmark chart. A short comparison paragraph introduces three middle-age maps together, with the larger 65+ map centered below them. `authoredRevision = 2` records this requested rearrangement. Each map’s numbers show the location and Wake growth rates side by side, emphasize their percentage-point gap, and retain a secondary line of exact location counts. The new `statewide_early_voting_context` query preserves NC Election Live’s October 31 snapshot through October 30: 2,612,240 accepted early ballots, 32% ahead of 2022 at the same point. That context includes mail and is distinct from the Wake in-person comparisons. No completed-election, statewide-doubling or turnout-decline claim is made.

Widths follow the measured full-story layout of [this Technician article](https://technicianonline.com/165762/news/did-you-know-that-theres-a-pool-under-thompson-hall/): an 800px editorial column within a 1200px page frame at desktop size. Prose, the featured map, the chart and the 65+ panel share that column. The three-map comparison now shares the same 800px editorial column, and reflows at smaller widths. The article-specific layout override is scoped to this app’s authored page; it does not restyle the prototype or shared top bar.

To revise, use a prepared Data report project, copy this authored content into `src/content/report/` and `../article-snapshot.json` into `src/data.json`, preserving its ID. Follow the prepared project’s `AGENTS.md`; compile with the installed Data app build command and `--separate-data`. Set `buildStatus` to `complete` only when authoring is finished. Package the verified compiled directory with:

```text
python scripts/package_article.py --dist /absolute/article-project/dist
```

That preserves the compiler’s HTML, data-sidecar and manifest bytes under `article/`. Do not replace the prototype’s root `data-app-build.json` with the article manifest.

References are built with `python scripts/build_reporting_references.py` from `article-references.html` and the reviewed five-age benchmark rows. `python scripts/test_reporting_references.py` verifies the focused counts, arithmetic, source periods and local links.
