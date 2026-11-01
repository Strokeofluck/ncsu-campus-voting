# Modeled walks near the voting sites

This scenario is not an estimate of how many students really pass a voting site or vote there. It models one shortest path for each usable housing-building × destination-building pair. Each pair has equal weight, without occupancy, enrollment or visitation data.

The 36 usable housing entrances come from the existing walking model. Destinations are active local GIS Classroom buildings (excluding closed Poe Hall), the two main library complexes (D. H. Hill's GIS wings are merged and counted once), and GIS Dining buildings plus Talley. NC State identifies Talley as a dining venue: https://studentcenters.ncsu.edu/location/talley/. The library list is at https://www.lib.ncsu.edu/visit. Poe's closure is documented in NC State's 2025–2027 capital priorities: https://committees.provost.ncsu.edu/campus-development/wp-content/uploads/sites/48/2025/01/2025-01-09-Capital-Dev-Plan-2024.pdf. Cherry Building is excluded because no entrance connects within the 30 m threshold. Final scope: 22 destinations and 792 pairs, or 756 pairs when Talley-ending dining trips are excluded. Teaching in buildings classified as offices/labs and all individual cafes are not covered.

For each full-resolution route, calculate the minimum projected distance in metres to each voting-site building footprint. A route counts as near at 25, 50 or 100 m if its minimum distance is at most that threshold. The share is near pairs ÷ eligible pairs × 100. The same eligible pairs form both site denominators. The default excludes trips ending at Talley, so a visit to Talley's dining facilities is not presented as incidental passing. The inclusion checkbox provides sensitivity.

GIS paths and building access assumptions are the same as the walking comparison: current EPSG:32119 network, not historical traffic or verified election doors. No road crossing waits, student route preferences, alternative equal-length paths or opening hours are modeled. Proximity to a footprint does not establish visibility or entrance access. A modeled zero is not evidence that nobody passes the site.

`passby.json` retains origin/destination selection, exclusions, per-pair distances, simplified map geometry and threshold summaries. `passby-routes.csv` and `passby-summary.csv` retain unrounded calculations. Map lines are simplified within 1 m; full-resolution paths are used for calculations. Original GIS is preserved in `official-gis-snapshot.zip`.

Reproduce with `python scripts/build_campus_passby.py --library-dir optional/path`, using shapely, pyproj and networkx. The base route builder's `--network-only` mode loads the same graph without overwriting prior reviewed route evidence.

The map defaults to the checked Show all routes view, fitted to the complete eligible network. Repeated semi-transparent paths darken where modeled routes overlap; darkness is not observed pedestrian flow. Unchecking hides other routes and shows the selected pair. Checking pauses autoplay and restores all eligible routes. The All halls → every destination button resets the destination-type filter and includes Talley-ending trips explicitly, updating both percentage denominators. Hover a route for its origin, destination, length and proximity classification; a tooltip identifies one displayed trip, not all trips sharing that segment.

## Equal circles and reviewable matching routes

An optional sensitivity view uses equal ground-radius circles around the same mapped entrance points used by the walking model: Talley entrance OBJECTID 414 and Western Boulevard entrance OBJECTID 210. These are GIS building access points, not confirmed election-room doors. Each route's new `talley_entrance_nearest_m` and `western_entrance_nearest_m` fields measure minimum distance to those points on the full-resolution modeled path. Both use the same 25, 50 or 100 m radius. The default is now the original GIS footprint basis for both buildings, with the same outward buffer distance. All prior distances and geometry remain unchanged.

The choice materially changes Talley's count: at 50 m, excluding Talley-ending trips, entrance circles count 25 / 756 (3.3%), while the original whole-footprint buffer counts 334 / 756 (44.2%). Both report zero matching Western routes in that scenario. These are different geographic definitions; do not compare their percentages without naming the basis.

Purple routes, count, percentage, paginated route list and matching-route download all use the exact same current destination filters, Talley-trip inclusion setting, basis and radius. “Entering the zone” means minimum distance is at most the radius; it includes touches and, if enabled, trips ending at Talley. It does not establish student behavior, building visibility or voting.

## Exact destination classifications and audit

The selected destinations comprise 16 GIS Classroom buildings, 3 GIS Dining buildings, Talley (GIS Student Center; dining established separately from NC State's Student Centers website), and 2 selected main library destinations. “Teaching” and “Dining” in the model are our labels. The university did not publish this 22-building grouping or the modeled route percentages. This is neither an exhaustive set of campus teaching/dining/library locations nor a verification of hours, current class schedules, access restrictions or actual visits.

`destination-sources.csv` and `destination-sources.json` provide each exact GIS USE_NAME, USECODE, BLDG_NUM and original BLDG_NAME, plus the inclusion rationale and a live official query URL. `destination-gis-records.json` preserves the 22 full original feature records from the hash-checked frozen dataset. The entire original Buildings dataset is preserved in official-gis-snapshot.zip. Regenerate this audit with scripts/build_campus_destination_sources.py. A live 22-record official query was checked against the frozen USE_NAME values on 2026-11-01; all matched. Live source records may subsequently change, so retain the frozen snapshot for reproduction.


Route-distance displays use miles (metres / 1609.344), while proximity-zone labels use meters; saved raw distances and thresholds remain in metres. Both original voting-site footprints are drawn inside their proximity buffers. Nearby parking overlays do not enter any proximity calculation. Accelerated autoplay visits all eligible destinations for an origin before advancing to the next origin. The 4 building-edge estimates are separate from the 36-origin routine-route model.


Autoplay displays only the active route, colored purple if the full route enters the selected Talley zone and gray otherwise. It defaults to one second per route with a quarter-second arrival pause. The camera fits all eligible routes once on starting playback and stays fixed across destinations and origins. Zone size remains 50 meters by default, an exploratory threshold applied equally to both sites, not a validated visibility boundary.


## Why 50 meters?

The 50-meter default is an exploratory short-walk proximity measure: at the model’s default 80 m/min walking pace, 50 / 80 = 0.625 min; multiplying by 60 gives 37.5 seconds (about 38 seconds). This interprets the chosen threshold; it is not an official boundary or a validated visibility measure. Footprint proximity is minimum straight-line distance to the building outline, not a pedestrian route to the voting door. Barriers, street crossings, entrance location and access restrictions can make the actual walk longer. Entering a zone does not establish reaching the voting entrance within a minute. Both sites use the same threshold and 25/100-meter sensitivity options remain available.


The current routine-map display starts autoplay on; the same source rows and defaults for threshold, footprint basis and Talley exclusion remain. The chooser and playback switch are inside the left floating key. The basemap is OpenFreeMap Positron, matching the housing-affordability style. Stationary building markers use frozen-footprint display centers; measured routes and their entrance endpoints remain unchanged.
