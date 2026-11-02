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

## Building averages

`averages.json` and `averages.csv` use only buildings with routes to both sites. Every building has weight 1, so each mean uses the same paired denominator. The all-housing mean is based on 36 of 40 buildings, not all 40, and not all students. Missing routes are excluded, never replaced with zero. Mean change = (sum Western distances − sum Talley distances) / paired count. This equals mean(Western − Talley). Subgroups are residence halls (22/26), Wolf Village (8/8) and Wolf Ridge (6/6). The grouped results are important because pooling housing types can hide opposite changes. Occupancy weights are not available in these inputs.

Reproduce the averages without GIS libraries using `python scripts/build_campus_walking_averages.py`; independently audit the decimal sums against the individual CSV using `python scripts/test_campus_walking_averages.py`.

The timing map defaults to All housing routes: both site routes for each usable building in the selected housing group. The Selected building mode retains individual route inspection. Housing-area changes restore the group overview; changing the starting building or clicking a marker switches to its individual view. Geometry and calculations are identical in both views.


## Estimated access, display and preservation updates

The timing map offers all 40 housing comparisons. Four original failures have supplemental routes in `estimated-access-routes.json`, reproduced by `scripts/build_estimated_housing_access.py`: Aurora uses recovered original entrance 216; Gold, University Towers and Welch retain explicitly labeled estimated boundary starts. The connectors are at most 30 m and reject building-interior crossings. These supplemental comparisons are separate from the frozen baseline averages and routine-trip denominators. No original source entrance is invented or edited.

Route distances display miles (metres / 1609.344), while proximity-zone labels use meters; calculations retain metres. Autoplay is accelerated, not real student movement. The routine map defaults to both GIS building footprints, with optional entrance circles. Ten whole parking polygons around Talley and Western are contextual overlays, not voter-reserved boundaries or inputs to distance/route calculations. References distinguish the documented election dates, the unverified fall 2022 allotment and the reported relocation rationale.

`scripts/archive_campus_gis.py` verifies and unpacks all four existing snapshots to `data/sources/ncsu-gis/2026-11-01/` with a hash catalog. Both parking queries and the original university reservation-map image are retained with provenance. The `SPACES` field gives 2,192 in the three deck-type Coliseum records and 660 in the four McKimmon records; these are inventory totals, not vacant or voter-reserved spaces. A hypothetical 660-space deck allotment is 30.1%, leaving 1,532 (69.9%) outside that allotment. The actual McKimmon voter-reserved count remains unconfirmed. `scripts/build_parking_reference_block.py` builds the record-level arithmetic and dated source notes; `scripts/test_parking_inventory.py` audits the totals and exclusions.

Site display dots are centered on the bounding boxes of the original GIS building outlines. Route endpoints retain the original GIS entrances. Both maps use collapsible floating keys with aligned symbols. The Show all routes checkbox pauses autoplay and shows the full network; when off, the routine map shows only the selected trip. Route hover tooltips identify one displayed trip; multiple trips may overlap the same path.


## Current display and click controls

Both campus maps use the housing article’s OpenFreeMap Positron vector style, with pinned MapLibre browser assets under `vendor/maplibre/`. The housing map’s left floating key contains map options and parking inventory. The independent routine map retains autoplay and playback options. The walking map is click-driven: a site click shows all 40 housing origins to that site; a housing click immediately shows both complete routes, with times in the summary and on hover. The all-sites view now includes 80 displayed routes, including the four supplemental origins (Aurora’s recovered mapped entrance and three estimated building-edge starts). Estimated origins remain excluded from the original averages and routine-trip model. Point hovers show names and original GIS use labels. The full housing list remains available for keyboard route selection.

`display-centers.json` and `scripts/build_campus_display_centers.py` derive all 63 stationary building centers from the frozen footprints. These visual centers do not replace route entrances or change lengths/proximity. The moving autoplay dot follows the route. The campus frame stays fixed during normal selection/playback; Fit shown routes is optional.

## Supplemental access audit and compact browsers

`access-recovery-audit.json` retains the original failure reason for each of the four supplemental buildings. Aurora now uses original enabled entrance 216 with a 25.60 m unblocked connector to another nearby source edge. Gold, Welch and University Towers still use labeled estimated building-edge access. No paths or source entrance records were invented. All 40 buildings have selectable two-site comparisons; the original 36-building averages and 756 default routine pairs are preserved as the frozen baseline. `scripts/test_estimated_housing_access.py` checks every supplemental route, connector, length and source hash.

Both maps have a compact four-preview pager (two on mobile) and a building selector. The routine browser adds a destination selector and an optional collapsed 36 × 21 route matrix. Routine previews replay the selected route once; housing previews immediately show both complete site walks. Full galleries no longer occupy multiple article-length rows.

## Static housing comparison

The housing timing map now draws both site routes immediately when a residence, table row or compact preview is selected. Housing autoplay, click-to-replay, speed controls, moving dots, progress counters and permanent on-map time boxes have been removed. Estimates stay in the detail summary, route hovers, comparison cards and table. Housing thumbnails are static. The independent routine-trip model retains its playback controls. Route coordinates, supplemental access classifications and all calculations are unchanged.
