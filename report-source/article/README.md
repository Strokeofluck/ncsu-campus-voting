# Article — work in progress

Published route: `article/index.html?view=1`. The article has a separate stable Data app identity from the prototype. Its reviewed snapshot is `../article-snapshot.json`.

The article now uses `AgeGrowthChart.jsx`: five youngest-first pairs of horizontal bars comparing Talley → Western Boulevard's percentage growth with the same-age full Wake total. All ten bars share a zero-based 0–125% scale; direct values, exact site counts and signed gap wording are visible, and pointer/focus tooltips show original counts and the formula. `SiteAgeMaps.jsx` is retained as a prototype experiment at `../index.html?view=1#site-circle-maps`; the original home-precinct choropleths also remain in the prototype. All reviewed counts and matched periods are unchanged.

The article opens with a sourced statewide introduction and an explicitly marked Latin draft placeholder. Its main visual is the five-age-group growth bar chart, followed by a short comparison paragraph and the worked ages 18–24 actual-versus-constant-share benchmark chart. `authoredRevision = 2` records this requested rearrangement. Each bar pair shows the location and Wake growth rates, their percentage-point gap, and exact site counts. The new `statewide_early_voting_context` query preserves NC Election Live’s October 31 snapshot through October 30: 2,612,240 accepted early ballots, 32% ahead of 2022 at the same point. That context includes mail and is distinct from the Wake in-person comparisons. No completed-election, statewide-doubling or turnout-decline claim is made.

Widths follow the measured full-story layout of [this Technician article](https://technicianonline.com/165762/news/did-you-know-that-theres-a-pool-under-thompson-hall/): an 800px editorial column within a 1200px page frame at desktop size. Prose and both charts share the 800px editorial column and reflow at smaller widths. The article-specific layout override is scoped to this app’s authored page; it does not restyle the prototype or shared top bar.

To revise, use a prepared Data report project, copy this authored content into `src/content/report/` and `../article-snapshot.json` into `src/data.json`, preserving its ID. Follow the prepared project’s `AGENTS.md`; compile with the installed Data app build command and `--separate-data`. Set `buildStatus` to `complete` only when authoring is finished. Package the verified compiled directory with:

```text
python scripts/package_article.py --dist /absolute/article-project/dist
```

That preserves the compiler’s HTML, data-sidecar and manifest bytes under `article/`. Do not replace the prototype’s root `data-app-build.json` with the article manifest.

References are built with `python scripts/build_reporting_references.py` from `article-references.html` and the reviewed five-age benchmark rows. `python scripts/test_reporting_references.py` verifies the focused counts, arithmetic, source periods and local links.
