# Visual editor preview

`editor-preview.html` opens `editor-maps/index.html?view=1`. This independent Data report presents the original walking-distance and routine-route maps, followed by the five-age growth chart and the college-age actual-versus-county-share benchmark. It is intended for sharing with interviewees. Article narrative, byline and election opening are omitted. Chart captions, source links, map controls, numeric summaries, legends and evidence actions are retained.

The permanent app ID is stored in `identity.json`. `scripts/prepare_editor_maps.py --project-dir <prepared-project>` copies the current article’s reviewed evidence and shared map dependencies, then applies this composition while preserving the preview’s independent identity. Build with the installed Data compiler using `--separate-data`, and package with `python scripts/package_editor_maps.py --dist <project>/dist`.

The preview follows the retained Technician article’s 800px story column and 44px desktop headline. Chart reference links open the worked calculations. Map-provider credits and source qualifications remain visible as plain text; source evidence is retained in the Data actions. Both charts reuse the article's exact components and reviewed full-period data, including 4,639 actual college-age ballots and the hypothetical 6,493 county-share benchmark.

The full article remains at `article/index.html?view=1`.
