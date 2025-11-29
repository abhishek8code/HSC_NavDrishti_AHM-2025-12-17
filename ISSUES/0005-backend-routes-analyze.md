Title: Backend — /routes/analyze implementation (B2)

Summary:
Implement `/routes/analyze` to accept start/end/waypoints and return per-segment metrics (distance_km, speed_kmh estimates, vehicle counts) and enhanced road properties.

Acceptance Criteria:
- [ ] POST `/routes/analyze` accepts JSON payload with start/end/waypoints
- [ ] Returns GeoJSON LineString and `distance_km`, `road_properties`, `traffic_counts`
- [ ] Unit tests cover typical and edge cases

Files to modify:
- Traffic_Backend/routers/routes.py
- Traffic_Backend/road_analytics.py
- tests/test_routes_analyze.py

Estimate: 6h
Priority: P0

Notes:
- Provide a simple fallback implementation using mocked traffic/road properties for dev until real data is available.
