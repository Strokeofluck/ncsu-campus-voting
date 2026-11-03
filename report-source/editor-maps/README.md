# Map editor preview

`editor-preview.html` opens `editor-maps/index.html?view=1`. This independent Data report presents only the two original interactive article maps: walking distances and modeled routine routes. Their controls, numeric map summaries, legends, source captions and evidence actions are retained. No article narrative, byline, election opening, age-growth chart or benchmark chart is mounted. White publication colors are shared with the article and prototype.

The permanent app ID is stored in `identity.json`. `scripts/prepare_editor_maps.py --project-dir <prepared-project>` copies the current article’s reviewed evidence and shared map dependencies, then applies this composition while preserving the preview’s independent identity. Build with the installed Data compiler using `--separate-data`, and package with `python scripts/package_editor_maps.py --dist <project>/dist`.

The full article remains at `article/index.html?view=1`. All paths to source references are shared with it.
