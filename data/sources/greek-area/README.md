# Greek-area pedestrian network review

Shortest connected modeled walk among eligible mapped entrances and retained estimated building access points, using the frozen November 1 NC State GIS network plus November 10 pedestrian supplements. The Greek-area supplement uses public OpenStreetMap footways, pedestrian-designated cycleways and steps; private/no-foot ways and building-interior shortcuts are excluded. Source endpoints are aligned to existing paths by at most 1.5 m, without joining arbitrary geometric crossings. Separately documented parking aisles and a shared access-drive crossing of Varsity Drive are included, with four explicitly estimated rear building-edge options, not verified doors. Existing front access remains eligible. The Bilyeu–Pullen supplement includes a reviewed bridge and a 24.1 m approximate marked-crossing approach. Public arterial road centerlines are not added. Door permissions, crossing safety, accessibility and October-specific conditions are not certified.

All 18 Greek-group housing origins were checked (414 origin/destination pairs including the two voting sites). Pi Kappa Phi is outside the main Greek neighborhood; its previously traced access remains in use. This review does not establish all door locations or public access hours.

OpenStreetMap source: public pedestrian ways retrieved November 10, 2026. Attribution: © OpenStreetMap contributors, ODbL 1.0. Raleigh data is corroborating sidewalk evidence, not the geometry source for every link. Public Esri aerial capture date is unknown and some newer buildings are absent; it is not evidence for unpictured entrances. Four west-row rear points remain explicitly estimated.

Google walking spot check: Chi Omega to the fixed Talley comparison pin, November 10: 0.8 mi / 18 min via Dan Allen Drive. The model gives approximately 0.79 mi. This is one route check, not certification of every route or historic October conditions.

Sources and file hashes:
- pedestrian-source.xml: e6d27d36f2666804a5a7b7c8ae1d5f6f26dc3373194a938e90f8cae8e94b3064
- raleigh-sidewalks.json: f8f505ed4d3727d495211b448b2d5d0257bebbd65a84b97296328f3717041ed2
- reviewed-aerial.png: 69c142cd9e310e98fc1e604d47b0e9b680c25599cb06519fe174a9b270861211
- walking-supplement.geojson: 6e7e50261b5d3e75841759951d260c6d9f0742815044f620125a8d17f24e8b35

Two explicitly reviewed same-grade GIS-to-pedestrian-line junction seams were split and aligned by 0.4405 m and 0.6129 m. Coordinates are retained in walking-supplement.geojson under reviewed_junction_repairs. An independent destination-to-origin shortest-path calculation validates all 1,932 pairs; see ../../processed/expanded-housing/shortest-path-stress-test.json.
