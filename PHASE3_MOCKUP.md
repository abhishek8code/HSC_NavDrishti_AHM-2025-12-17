# Phase 3 — UI Mockups and Interaction Design

## Overview
Phase 3 adds interactive Route Analysis, Real-Time Traffic, Alternatives ranking, and Scenario comparison to the Dashboard. This mockup defines the UI layout, interaction flows, and backend bindings.

---

## Dashboard Layout (Updated)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Top Metrics Row                                                              │
│ ┌───────────────┐ ┌────────────────┐ ┌────────────────┐                      │
│ │ Active Proj   │ │ Critical Alerts│ │ CO2 Saved      │                      │
│ └───────────────┘ └────────────────┘ └────────────────┘                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ Main Work Area                                                               │
│ ┌───────────────────────────┬──────────────────────────────────────────────┐ │
│ │ Route Picker Panel        │ Map (Mapbox GL)                             │ │
│ │                           │                                              │ │
│ │ • Start:  [Click on map]  │ • Base layer: city style                     │ │
│ │ • End:    [Click on map]  │ • Overlays: selected route, alternatives     │ │
│ │ • Mode:   [Driving▼]      │ • Live traffic heat overlay                  │ │
│ │ • Analyze [button]        │ • Lane-width/constraints markers             │ │
│ │                           │ • Detour suggestions (dashed lines)          │ │
│ │ ───────────────────────── │                                              │ │
│ │ Metrics                   │                                              │ │
│ │ • Length: 12.4 km         │                                              │ │
│ │ • Segments: 18            │                                              │ │
│ │ • Congestion: Medium      │                                              │ │
│ │ • Avg Speed: 32 km/h      │                                              │ │
│ │ • Emissions: 14.2 kg CO2  │                                              │ │
│ └───────────────────────────┴──────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ Bottom Panels                                                                 │
│ ┌───────────────────────────┬───────────────────────────┬──────────────────┐ │
│ │ Alternatives (Ranked)     │ Traffic Alerts            │ Scenario Compare │ │
│ │ 1) Route A  Score 0.82    │ • Alert: Density > limit  │ • Baseline        │ │
│ │ 2) Route B  Score 0.78    │ • Suggest detour via ...  │ • Project Impact   │ │
│ │ 3) Route C  Score 0.61    │ • Lane closure: seg #12   │ • % change: +12%   │ │
│ │ [Select] [Simulate]       │ [Mute] [Details]          │ [Compare ▶]        │ │
│ └───────────────────────────┴───────────────────────────┴──────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Key UI Components

- **Route Picker Panel**: Start/end selection (map clicks), travel mode, Analyze button.
- **Metrics Box**: Length, segments, congestion, speed, emissions.
- **Map Overlays**:
  - Selected route (bold solid line)
  - Alternatives (thin colored lines, ranked)
  - Live traffic heatmap (red = high congestion)
  - Lane constraints icons (narrow lanes, closures)
  - Detour suggestions (dashed lines)
- **Alternatives Panel**: Ranked list with suitability score, actions: Select, Simulate.
- **Traffic Alerts Panel**: Real-time alerts, mute and details.
- **Scenario Compare Panel**: Baseline vs. Project impact summary, Compare action.

---

## Interaction Flows

### Flow A: Route Analysis
1. User clicks map to set Start.
2. User clicks map to set End.
3. User clicks Analyze.
4. System calls backend for analysis and alternatives.
5. Map renders route + alternatives; Metrics box updates.
6. Alternatives list shows ranked routes.

### Flow B: Live Traffic Updates
1. Every 30s, frontend polls `/traffic/live/{route_id}`.
2. Heatmap and congestion state update on map.
3. Alerts panel lists threshold breaches.

### Flow C: Select Alternative & Simulate
1. User clicks Select on an alternative.
2. Map highlights selected alternative.
3. User clicks Simulate to estimate emissions and travel time.
4. Scenario panel shows baseline vs. simulated metrics.

### Flow D: Scenario Comparison
1. User clicks Compare.
2. System computes deltas (travel time, emissions, throughput).
3. Panel shows % change and recommendation note.

---

## API Bindings (Backend)

- Route Analyze (POST)
  - Endpoint: `/routes/analyze`
  - Payload: `{ "coordinates": [[lon, lat], ...] }`
  - Returns: `{ length_degrees, num_segments, approximate_length_km }`

- Alternatives (GET/POST)
  - Endpoint: `POST /routes/{id}/recommend?start_lon&start_lat&end_lon&end_lat`
  - Returns: `{ recommended_alternative_id, all_alternatives: [{ route_id, length_km, num_segments, suitability_score, rank }] }`

- Live Traffic (GET)
  - Endpoint: `GET /routes/{id}/traffic` (proxy of `/traffic/live/{id}`)
  - Returns: `{ route_id, timestamp, vehicle_count, average_speed, congestion_state }`

- Threshold Alerts (GET)
  - Endpoint: `GET /traffic/threshold/{road_segment_id}`
  - Returns: `{ vehicle_count_limit, density_limit, alert_type, is_active }`

- Notifications (POST)
  - Endpoint: `POST /notifications/send`
  - Payload: `{ project_id, recipient_type, message }`

---

## UI States & Edge Cases

- Missing Start/End: Disable Analyze until both are set.
- Backend down: Show banner "Backend unavailable", retry button.
- No alternatives: Show info "No viable alternatives found"; propose detour.
- High congestion: Color route segments red; show alert badge.
- Lane closures: Display caution icon on affected segments.

---

## Component-Level Tasks

- Mapbox interactions: click-to-set markers, draw line, style layers.
- Panels: Razor partial views for Alternatives, Alerts, Scenario.
- JS modules: `routeAnalysis.js`, `trafficOverlay.js`, `scenarioCompare.js`.
- Service methods: add DTOs for metrics/alternatives; reuse BackendApiService.
- Controller actions: add endpoints to serve scenario comparison results.

---

## Minimal Visual Styles (Tokens)

- Colors: Primary `#1b6ec2`, Success `#28a745`, Danger `#dc3545`, Warning `#ffc107`.
- Route line: 4px, Alternatives: 2px.
- Heatmap intensity: scaled by vehicle_count and congestion_state.
- Icons: lane constraint ⚠️, detour ➡️, simulate ▶️, compare ⇄.

---

## Implementation Notes

- All new panels should be modular Razor partials.
- Use `apiClient.js` for all browser-side calls to `/api/...` endpoints.
- Add new C# methods to `BackendApiService` only if needed; reuse existing routes/traffic bindings.
- Respect JWT auth for any protected actions (e.g., notifications, admin thresholds).
- Polling interval for traffic: 30 seconds (configurable).

---

## Success Criteria

- Users can select start/end on map and see analysis metrics.
- Ranked alternatives are shown and selectable.
- Live traffic overlays update automatically.
- Scenario comparison displays baseline vs. simulated impacts.
- Errors handled gracefully with clear UI messaging.
