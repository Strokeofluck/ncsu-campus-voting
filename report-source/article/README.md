# Article — work in progress

The article follows the earlier `nc-voting-roadmap/editor-preview.html` Technician presentation with the requested white publication palette: dark masthead lettering on white, section navigation, a wrapped serif headline, Sean Ryan’s draft byline, and an 800px story column. `TechnicianHeader.jsx` and `technician-preview.css` own the authored presentation; local font/masthead imports are bundled. `editor-preview.html` now opens the separate maps-only editor preview under `editor-maps/`; the full story stays on its original article route. The Data toolbar, evidence actions, maps, chart interactions, snapshot, app identity and original uploaded reference image remain intact. `../palette.css` supplies the same white theme to the article and prototype through their supported `src/theme.css`; references use the matching fixed light colors in `article-references.css`.

Published route: `article/index.html?view=1`. The article has a separate stable Data app identity from the prototype. Its reviewed snapshot is `../article-snapshot.json`.

The article now uses `AgeGrowthChart.jsx`: five youngest-first pairs of horizontal bars comparing Talley → Western Boulevard's percentage growth with the same-age full Wake total. All ten bars share a zero-based 0–125% scale; direct values, exact site counts and signed gap wording are visible, and pointer/focus tooltips show original counts and the formula. `SiteAgeMaps.jsx` is retained as a prototype experiment at `../index.html?view=1#site-circle-maps`; the original home-precinct choropleths also remain in the prototype. All reviewed counts and matched periods are unchanged.

The article opens with sourced early-voting and parking context, then a compact walking map. The five-age-group growth bar chart follows, with a short comparison paragraph and the worked ages 18–24 actual-versus-constant-share benchmark chart. `authoredRevision = 4` records the requested rearrangement. Each bar pair shows the location and Wake growth rates, their percentage-point gap, and exact site counts. The new `statewide_early_voting_context` query preserves NC Election Live’s October 31 snapshot through October 30: 2,612,240 accepted early ballots, 32% ahead of 2022 at the same point. That context includes mail and is distinct from the Wake in-person comparisons. No completed-election, statewide-doubling or turnout-decline claim is made.

Widths follow the measured full-story layout of [this Technician article](https://technicianonline.com/165762/news/did-you-know-that-theres-a-pool-under-thompson-hall/): an 800px editorial column within a 1200px page frame at desktop size. Prose and both charts share the 800px editorial column and reflow at smaller widths. The article-specific layout override is scoped to this app’s authored page; it does not restyle the prototype or shared top bar.

To revise, use a prepared Data report project, copy this authored content into `src/content/report/` and `../article-snapshot.json` into `src/data.json`, preserving its ID. Follow the prepared project’s `AGENTS.md`; compile with the installed Data app build command and `--separate-data`. Set `buildStatus` to `complete` only when authoring is finished. Package the verified compiled directory with:

```text
python scripts/package_article.py --dist /absolute/article-project/dist
```

That preserves the compiler’s HTML, data-sidecar and manifest bytes under `article/`. Do not replace the prototype’s root `data-app-build.json` with the article manifest.

References are built with `python scripts/build_reporting_references.py` from `article-references.html` and the reviewed five-age benchmark rows. `python scripts/test_reporting_references.py` verifies the focused counts, arithmetic, source periods and local links.

Revision 3: opening now attributes the statewide midterm early-voting record to WRAL (Oct. 31), attributes the parking rationale to NC Newsline, distinguishes whole GIS inventory from voter allocations, and inserts a compact shared housing walking map ahead of the unchanged age-growth chart. The Latin placeholder is replaced with sourced copy. Preserve the Nov. 3 update note and matched Oct. 30 site cutoff. The shared CampusWalkingMap receives `article=true`; all GIS source rows and relevant campus metadata are copied unchanged into the article snapshot. Prototype controls remain in the prototype.

Rebuild authored content with `python scripts/prepare_article_content.py --project-dir ../article-build` before the Data app build. The map reuses prototype source files without duplicating them in this folder; its vector-basemap assets resolve from the existing root `vendor/maplibre/` directory.

Revision 4 adds the routine-walk section and compact pass-by map after the housing map, before ballot growth. It reports 334/756 (44.2%) within 50 m of Talley and 0/756 near Western, using the identical 36-origin × 21-destination baseline and excluding trips ending at Talley. Default shows the whole network; point clicks and the optional autoplay control tour individual routes. Shared route segments can represent both classifications. It does not report percentages of students or actual traffic.

Revision 5 places a compact three-column Google average strip directly above the housing map, with all 40 buildings and separate provenance from the GIS paths. The intro question is removed. The routine map starts with Autoplay checked and a single route; the all-network control is removed. Two-decimal mean miles use decimal-friendly rounding (0.975 → 0.98) in both prototype and article. Source values and route geometry are unchanged.

The age-growth comparison now uses five compact horizontal rows, preserving paired bars on a common zero-based 0–125% axis, the five exact growth gaps, site counts, all five math links and full original counts/formulas on hover or keyboard focus. This replaces repeated series headings and tall stacked age panels.

Latest copy/display revision: impersonal GIS-based routine-route description with named libraries and linked exclusions; 16 px section gaps; original Housing/Destination controls and parking legend retained in the article; autoplay remains on. Behind/ahead words use red/green, and repeated row-level Math links are removed. References now groups all methods by visual and supplies four housing-area Google verification lists.
