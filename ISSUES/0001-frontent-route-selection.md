Title: Frontend — Map-based Route Selection (P0)

Summary:
Implement click-to-select start/end points on the dashboard map, show route preview, display distance and basic metrics, and allow clearing the selection.

Acceptance Criteria:
- [ ] User can click "Draw Route" then click multiple points on the map to create a route
- [ ] Start and end markers are visible
- [ ] Route length (km) and points count are shown in the Route Info panel
- [ ] "Clear Route" removes the drawing and resets the panel
- [ ] "Create Project" uses selected route coordinates to create a project via `/api/projects`

Files to modify:
- Traffic_Frontend/Views/Home/Dashboard.cshtml
- Traffic_Frontend/wwwroot/js/routeSelection.js

Estimate: 3h
Priority: P0

Notes:
- Reuse Mapbox GL Draw instance from `dashboard.js` where possible.
- Use Turf.js for distance calculation.
- If backend `/routes/analyze` available, call it for enriched metrics.
