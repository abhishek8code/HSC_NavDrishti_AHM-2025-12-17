Title: Backend — /routes/recommend enhancement (B1)

Summary:
Enhance `/routes/recommend` to return multiple route alternatives as GeoJSON LineStrings with metadata fields: `distance_km`, `travel_time_min`, `traffic_score`, and `emission_g`.

Acceptance Criteria:
- [ ] Endpoint returns JSON with `routes` array
- [ ] Each route contains `id`, `name`, `coordinates` (LineString), and metadata
- [ ] Unit tests validate output structure and sample data
- [ ] Performance: endpoint returns within 1s for small requests

Files to modify:
- Traffic_Backend/routers/routes.py
- Traffic_Backend/models.py (if persistence required)
- tests/test_routes_recommend.py

Estimate: 6h
Priority: P0

Notes:
- Use GeoJSON `coordinates` as [[lon, lat], ...]
- Include a small sample fixture for tests
