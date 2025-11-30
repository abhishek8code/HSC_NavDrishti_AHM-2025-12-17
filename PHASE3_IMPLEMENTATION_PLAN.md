# Phase 3 Implementation Plan

## 🎯 Objective
Implement advanced traffic visualization and route optimization features with real-time data.

## ✅ Phase 2 Completion Status

**Completed:**
- Backend API fully functional (FastAPI + SQLAlchemy)
- Frontend integrated with backend (ASP.NET Core + HttpClient)
- Authentication and authorization working
- Projects CRUD operations
- API controllers routing correctly
- Integration tests: 6/7 passing
- Dashboard UI scaffolded with placeholders

## 📋 Phase 3 Tasks

### 1. Map-Based Route Selection ⚡ Priority: HIGH

**Backend Requirements:**
- ✅ Route analysis endpoint exists (`/routes/analyze`)
- ✅ Route recommendation endpoint exists (`/routes/recommend`)
- Need: Enhance response with detailed route geometries

**Frontend Implementation:**
- [ ] Implement click-to-select start/end points on map
- [ ] Add visual markers for selected points
- [ ] Draw straight line preview between points
- [ ] Show coordinates and distance in UI
- [ ] Add "Clear Selection" button

**Files to modify:**
- `wwwroot/js/routeAnalysis.js` - Already scaffolded
- `Views/Home/Dashboard.cshtml` - Route picker panel exists

**Estimated time:** 2-3 hours

---

### 2. Render Alternative Routes 🗺️ Priority: HIGH

**Backend Enhancement:**
```python
# Traffic_Backend/routers/routes.py
# Enhance /routes/recommend to return:
{
  "routes": [
    {
      "id": 1,
      "name": "Fastest Route",
      "coordinates": [[lon, lat], ...],  # GeoJSON LineString
      "distance_km": 5.2,
      "travel_time_min": 12,
      "traffic_score": 0.7,
      "emission_g": 850
    },
    // ... more alternatives
  ]
}
```

**Frontend Implementation:**
- [ ] Parse route coordinates from backend response
- [ ] Draw each route as a colored line on map
- [ ] Add route layers with unique IDs
- [ ] Implement hover effects (highlight route)
- [ ] Click route to select and show details
- [ ] Legend showing route colors and metrics
- [ ] Toggle routes on/off

**Files to modify:**
- `wwwroot/js/scenarioCompare.js` - Render alternatives list
- `wwwroot/js/routeAnalysis.js` - Draw routes on map
- `Views/Shared/_AlternativesPanel.cshtml` - Route cards with metrics

**Mapbox GL JS code:**
```javascript
map.addSource('route-1', {
  type: 'geojson',
  data: {
    type: 'Feature',
    geometry: {
      type: 'LineString',
      coordinates: routeData.coordinates
    }
  }
});

map.addLayer({
  id: 'route-1-line',
  type: 'line',
  source: 'route-1',
  paint: {
    'line-color': '#3b82f6',
    'line-width': 4,
    'line-opacity': 0.8
  }
});
```

**Estimated time:** 4-5 hours

---

### 3. Real-Time Traffic Overlay 🚦 Priority: MEDIUM

**Backend Enhancement:**
```python
# Traffic_Backend/routers/traffic.py
# Enhance /traffic/live to return per-segment data:
{
  "segments": [
    {
      "segment_id": "seg_001",
      "coordinates": [[lon, lat], ...],
      "congestion_level": 0.8,  # 0.0 - 1.0
      "speed_kmh": 15,
      "vehicle_count": 45,
      "timestamp": "2025-11-29T22:30:00Z"
    }
  ]
}
```

**Frontend Implementation:**
- [ ] Create traffic heatmap layer on map
- [ ] Color-code segments by congestion (green/yellow/red)
- [ ] Update every 30 seconds (already scaffolded)
- [ ] Add traffic layer toggle button
- [ ] Show segment details on hover
- [ ] Traffic legend (low/medium/high)
- [ ] Historical traffic comparison slider

**Files to modify:**
- `wwwroot/js/trafficOverlay.js` - Already scaffolded, needs enhancement
- `Views/Home/Dashboard.cshtml` - Traffic controls

**Mapbox GL JS code:**
```javascript
map.addSource('traffic-heatmap', {
  type: 'geojson',
  data: trafficGeoJSON
});

map.addLayer({
  id: 'traffic-heatmap-layer',
  type: 'line',
  source: 'traffic-heatmap',
  paint: {
    'line-color': [
      'interpolate',
      ['linear'],
      ['get', 'congestion'],
      0.0, '#22c55e',  // green (low)
      0.5, '#eab308',  // yellow (medium)
      1.0, '#ef4444'   // red (high)
    ],
    'line-width': 6,
    'line-opacity': 0.7
  }
});
```

**Estimated time:** 3-4 hours

---

### 4. Traffic Alerts Integration 🚨 Priority: MEDIUM

**Backend Enhancement:**
```python
# Traffic_Backend/routers/traffic.py
# Add /traffic/alerts endpoint:
{
  "alerts": [
    {
      "id": 1,
      "type": "accident",  # accident, construction, congestion
      "severity": "high",
      "location": [lon, lat],
      "message": "Multi-vehicle accident on SG Highway",
      "timestamp": "2025-11-29T22:15:00Z",
      "affected_routes": [1, 2]
    }
  ]
}
```

**Frontend Implementation:**
- [ ] Poll alerts endpoint every 30 seconds
- [ ] Display alerts in Traffic Alerts card (already exists)
- [ ] Add alert markers on map
- [ ] Alert icon based on type
- [ ] Click alert to center map and show details
- [ ] Alert notifications (browser notification API)
- [ ] Filter alerts by severity

**Files to modify:**
- `wwwroot/js/trafficOverlay.js` - Add alerts polling
- `Views/Home/Dashboard.cshtml` - Traffic Alerts card (exists)

**Estimated time:** 2-3 hours

---

### 5. Scenario Comparison 📊 Priority: LOW

**Frontend Implementation:**
- [ ] Multi-select routes for comparison
- [ ] Side-by-side metrics table
- [ ] Chart comparing travel time, emissions, cost
- [ ] Highlight differences
- [ ] Export comparison as PDF/image
- [ ] Save scenarios for later review

**Files to modify:**
- `wwwroot/js/scenarioCompare.js` - Already scaffolded
- `Views/Shared/_ScenarioPanel.cshtml` - Comparison UI

**Chart.js integration:**
```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Route 1', 'Route 2', 'Route 3'],
    datasets: [{
      label: 'Travel Time (min)',
      data: [12, 15, 10]
    }]
  }
});
```

**Estimated time:** 3-4 hours

---

### 6. Backend Data Enhancements 🗄️ Priority: MEDIUM

**Required backend work:**
- [ ] NetworkX graph construction from real road network data
- [ ] Load Ahmedabad road network shapefile
- [ ] Integrate traffic weights into graph edges
- [ ] Implement Dijkstra with traffic weights
- [ ] Add emission calculation per route
- [ ] Cache route computations
- [ ] Add route history tracking

**Files to modify:**
- `Traffic_Backend/main.py` - Graph initialization
- `Traffic_Backend/routers/routes.py` - Enhanced algorithms
- `Traffic_Backend/models.py` - Add Route model for persistence

**Estimated time:** 5-6 hours

---

## 🎨 UI/UX Enhancements

- [ ] Add loading spinners for async operations
- [ ] Toast notifications for user actions
- [ ] Better error handling and user feedback
- [ ] Responsive design for mobile
- [ ] Dark mode toggle
- [ ] Map style switcher (streets/satellite)
- [ ] Print-friendly route reports

**Estimated time:** 3-4 hours

---

## 🧪 Testing Strategy

**Integration Tests:**
- [ ] Test route selection flow end-to-end
- [ ] Test route alternatives rendering
- [ ] Test traffic overlay updates
- [ ] Test alerts polling and display
- [ ] Test scenario comparison

**Unit Tests (Frontend):**
- [ ] JavaScript module tests with Jest
- [ ] API client mock tests
- [ ] Map interaction tests

**Estimated time:** 4-5 hours

---

## 📅 Implementation Timeline

### Week 1: Core Routing Features
- Day 1-2: Map-based route selection
- Day 3-4: Render alternative routes
- Day 5: Backend route enhancements

### Week 2: Traffic Visualization
- Day 1-2: Real-time traffic overlay
- Day 3: Traffic alerts integration
- Day 4-5: Scenario comparison UI

### Week 3: Polish & Testing
- Day 1-2: UI/UX enhancements
- Day 3-4: Testing and bug fixes
- Day 5: Documentation and deployment prep

**Total estimated time:** 30-40 hours

---

## 🚀 Quick Wins (Start Here)

1. **Map route selection** (2-3h) - User can click start/end points
2. **Draw routes on map** (2-3h) - Visualize backend route data
3. **Traffic color coding** (2h) - Basic red/yellow/green segments
4. **Alerts display** (1-2h) - Show alerts in existing card

These 4 tasks give immediate visual impact with ~8-10 hours work.

---

## 📦 Dependencies to Add

**Frontend:**
```json
// package.json (if using npm for frontend assets)
{
  "dependencies": {
    "chart.js": "^4.4.0",
    "@mapbox/mapbox-gl-draw": "^1.4.3",
    "turf": "^3.0.14"  // Geospatial calculations
  }
}
```

**Backend:**
```txt
# Traffic_Backend/requirements.txt (additions)
geopandas>=0.14.0
shapely>=2.0.0
networkx>=3.0
rtree>=1.0.0  # Spatial indexing
```

---

## 🎯 Success Criteria

- [ ] User can select start/end on map with visual feedback
- [ ] 3+ alternative routes displayed with different colors
- [ ] Real-time traffic overlay updates every 30s
- [ ] Traffic alerts appear on map and in alerts card
- [ ] Scenario comparison shows metrics side-by-side
- [ ] All features work without backend errors
- [ ] Integration tests: 100% passing
- [ ] Page load time < 2 seconds
- [ ] Mobile responsive

---

## 🔄 Next Immediate Actions

1. **Test current scaffolding** - Verify Phase 2 UI in browser
2. **Implement route selection** - First interactive feature
3. **Enhance backend routes API** - Return proper GeoJSON
4. **Draw routes on map** - Visual confirmation
5. **Add traffic layer** - Real-time data visualization

Ready to start with Task #1: Map-Based Route Selection?

---

## 🧭 Epics & Tasks (Breakdown)

Below is an actionable breakdown of Phase 3 into epics, concrete tasks, file-level targets, priority (P0 = highest), and estimated effort (hours).

- Epic: Frontend — Route Selection & Visualization
  - Task F1 (P0, 3h): Integrate click-to-select start/end on `Views/Home/Dashboard.cshtml` and wire to `wwwroot/js/routeSelection.js`.
    - Files: `Views/Home/Dashboard.cshtml`, `wwwroot/js/routeSelection.js`
    - Acceptance: start/end markers placed on map, distance shown, Clear Selection button works.
  - Task F2 (P0, 4h): Render alternative routes from backend and allow selecting a route.
    - Files: `wwwroot/js/routeSelection.js`, `wwwroot/js/scenarioCompare.js`, `Views/Shared/_AlternativesPanel.cshtml`
    - Acceptance: 3+ alternatives visualized with hover & click details.
  - Task F3 (P1, 3h): Route drawing UX — enable Mapbox GL Draw for freehand edits and snapping to road network (client-side snapping to returned geometry).
    - Files: `wwwroot/js/routeSelection.js`
  - Task F4 (P1, 2h): Add project creation flow: POST selected route to `Controllers/ProjectsApiController.cs` endpoint via `apiClient`.
    - Files: `wwwroot/js/routeSelection.js`, `Traffic_Frontend/Controllers/ProjectsApiController.cs`

- Epic: Frontend — Traffic Overlay & Alerts
  - Task F5 (P0, 4h): Traffic heatmap/segment rendering; color by congestion; 30s update loop (respecting toggle).
    - Files: `wwwroot/js/trafficOverlay.js`, `Views/Home/Dashboard.cshtml`
    - Acceptance: Layer appears, colors update, toggle persists to `localStorage`.
  - Task F6 (P1, 2h): Traffic alerts: poll `/traffic/alerts` and show markers + list panel.
    - Files: `wwwroot/js/trafficOverlay.js`, `Views/Shared/_AlertsPanel.cshtml`

- Epic: Frontend — Scenario Compare & Charts
  - Task F7 (P2, 4h): Implement scenario compare UI and Chart.js integration.
    - Files: `wwwroot/js/scenarioCompare.js`, `Views/Shared/_ScenarioPanel.cshtml`

- Epic: Backend — Routes & Traffic APIs
  - Task B1 (P0, 6h): Enhance `/routes/recommend` to return GeoJSON LineStrings with metadata (distance_km, travel_time_min, traffic_score, emission_g).
    - Files: `Traffic_Backend/routers/routes.py`, `Traffic_Backend/models.py`
    - Acceptance: Endpoint returns documented JSON; unit tests added.
  - Task B2 (P0, 6h): Implement `/routes/analyze` to compute per-segment metrics, vehicle counts (estimates) and return detailed geometry.
    - Files: `Traffic_Backend/routers/routes.py`, `Traffic_Backend/road_analytics.py`
  - Task B3 (P1, 8h): Build NetworkX graph from shapefile/OSM extract and add traffic weights and Dijkstra implementation.
    - Files: `Traffic_Backend/main.py`, `Traffic_Backend/routers/routes.py`
  - Task B4 (P1, 4h): Add `/traffic/live` that streams or returns current per-segment congestion and `/traffic/alerts` for events.
    - Files: `Traffic_Backend/routers/traffic.py`

- Epic: Backend — Persistence, Caching & History
  - Task B5 (P1, 4h): Add `Route` model and history table to store computed routes and project associations.
    - Files: `Traffic_Backend/models.py`, migrations
  - Task B6 (P1, 3h): Add caching for route computations (LRU or Redis) to speed repeated calls.

- Epic: Testing & QA
  - Task T1 (P0, 3h): Integration test for route selection → backend analyze → frontend render (end-to-end via test harness).
    - Files: `tests/test_route_selection_integration.py`, CI pipeline changes
  - Task T2 (P1, 3h): Unit tests for `Traffic_Backend/routers/routes.py` and `traffic.py` endpoints.
  - Task T3 (P1, 3h): Jest tests for frontend modules `routeSelection.js` and `trafficOverlay.js` (mock backend responses).

- Epic: Infra & Local Dev
  - Task I1 (P0, 2h): Document and script local startup: start backend (uvicorn), start frontend (dotnet run), seed DB (SQLite fallback). Add `start_all.ps1` improvements.
  - Task I2 (P1, 3h): Optional: provide Docker Compose dev stack (FastAPI + DB + frontend static server) for reproducible local runs.

- Epic: Docs & Release
  - Task D1 (P1, 2h): Update `ROUTE_SELECTION_GUIDE.md` with screenshots and exact steps for the new UI.
  - Task D2 (P2, 1h): Add PR template and testing checklist (`.github/PULL_REQUEST_TEMPLATE.md`).

---

## Prioritization Summary (P0 = must-have this sprint)
- P0: F1, F2, F5, B1, B2, T1, I1
- P1: F3, F4, F6, B3, B4, B5, T2, T3, I2
- P2: F7, D2, polishing UX items

## How I'll proceed
1. Implement P0 frontend items (F1, F2, F5) in small PRs, run the frontend locally to verify.
2. Implement B1/B2 backend endpoints with unit tests against sample geometries (use SQLite dev DB if needed).
3. Add integration tests (T1) and iterate until end-to-end is working.
4. Deliver P1 items next, and reserve final sprint for UX polish + docs.

If you'd like, I can now scaffold the high-priority tasks as GitHub issues and create the first PR with `routeSelection.js` adjustments. Which next action do you want me to take? (scaffold issues / implement F1 now / create PR for current JS files)
