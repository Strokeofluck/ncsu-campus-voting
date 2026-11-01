# Article — work in progress

Published route: `article/index.html?view=1`. The article has a separate stable Data app identity from the prototype. Its reviewed snapshot is `../article-snapshot.json`.

The five maps use residential precinct age-group growth relative to the same-age full Wake County total. Polling-site counts directly beneath them compare Talley in 2022 with Western Boulevard in 2026, regardless of home precinct. Ages 18–24 appear first. The article deliberately omits the prototype’s residential-count tables; those remain available in the prototype.

The article opens with a sourced statewide introduction and an explicitly marked Latin draft placeholder. Its main visual is the ages 18–24 map, followed by the worked actual-versus-constant-share benchmark chart. A short comparison paragraph introduces three compact middle-age maps on the left and a larger 65+ map on the right; these stack on smaller screens. `authoredRevision = 1` records the requested rearrangement. The new `statewide_early_voting_context` query preserves NC Election Live’s October 31 snapshot through October 30: 2,612,240 accepted early ballots, 32% ahead of 2022 at the same point. That context includes mail and is distinct from the Wake in-person comparisons. No completed-election, statewide-doubling or turnout-decline claim is made.

To revise, use a prepared Data report project, copy this authored content into `src/content/report/` and `../article-snapshot.json` into `src/data.json`, preserving its ID. Follow the prepared project’s `AGENTS.md`; compile with the installed Data app build command and `--separate-data`. Set `buildStatus` to `complete` only when authoring is finished. Package the verified compiled directory with:

```text
python scripts/package_article.py --dist /absolute/article-project/dist
```

That preserves the compiler’s HTML, data-sidecar and manifest bytes under `article/`. Do not replace the prototype’s root `data-app-build.json` with the article manifest.

References are built with `python scripts/build_reporting_references.py` from `article-references.html` and the reviewed five-age benchmark rows. `python scripts/test_reporting_references.py` verifies the focused counts, arithmetic, source periods and local links.
