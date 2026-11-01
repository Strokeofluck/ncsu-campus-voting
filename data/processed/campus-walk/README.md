# Campus walking comparison — prototype

Published at `/?view=1#campus-walking`. The article's vote-growth measures are separate.

`routes.json` contains 40 active residence-hall, Wolf Village and Wolf Ridge buildings from NC State's official building GIS. Thirty-six have usable routes; four retain missing distances and explicit reasons. No student records, registration addresses or occupancy estimates are used.

The same fixed mapped entrance at each housing building is compared with the selected GIS entrance at Talley (building 102, entrance OBJECTID 414) and Western Boulevard (building 131, entrance OBJECTID 210). The election-specific voting-room doors have not been confirmed. Both destinations use the current downloaded path network; these are not reconstructed 2022 journeys.

The graph combines enabled Campus Walks and Accessible Path features, projected to NAD83 / North Carolina (EPSG:32119, metres). Edges join recorded vertices; existing vertices on other edges are noded within a 2.5 cm rounding tolerance. Arbitrary geometric crossings and gaps are not joined. Routing uses the largest connected component. A usable entrance is within 10 m of its building footprint and within 30 m of the connected paths. Its straight connector must not intersect more than 2.5 m of mapped building footprint. Dotted connectors are modeled, not field checked. This model is not a certified accessible route or a navigation service.

For each building: distance = network path + origin connector + destination connector. Change = Western distance − Talley distance. Walking minutes = metres ÷ selected pace in m/min. The default is 80 m/min (about 3 mph); 60 and 100 m/min are alternatives. Times omit traffic-signal waits, queues, terrain and indoor travel. Missing or closed real-world paths can change which route is best. Differences are not evidence of how many students voted or of a causal effect on turnout.

`official-gis-snapshot.zip` preserves the four original paginated public GIS datasets and their request URLs, retrieval time, counts and SHA-256 hashes in `manifest.json`. `distances.csv` retains unrounded results. `method.json` records thresholds, connected components and exclusions. `routes.json` retains every route vertex and separates mapped paths from the estimated connectors.

Reproduce from the frozen files by extracting the source ZIP to `data/raw/campus-walk/`, installing Python `shapely`, `pyproj`, and `networkx`, then running:

```text
python scripts/build_campus_walking_routes.py
python scripts/test_campus_walking_routes.py
```

Both scripts accept `--library-dir` for workspace-local Python packages. `scripts/download_campus_walking_sources.py` fetches a fresh snapshot in pages and reconciles each layer's full feature count; refreshing changes the source hashes and must be reviewed before replacing this published comparison.

NC State's independent [Pack the Polls guide](https://packthepolls.dasa.ncsu.edu/elections/early-voting/) lists a 25-minute, 1.1-mile Talley-to-new-site walk and describes shuttle and transit options. Our selected GIS entrances produce about 1.05 miles; model times depend on the explicit pace assumption. The guide's distance/time is a reasonableness check, not the input to our calculated routes.
