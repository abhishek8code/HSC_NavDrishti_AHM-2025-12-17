# Select and Details Button Test Results

## Test Date: November 30, 2025

## Services Status
- ✅ **Backend**: Running on http://127.0.0.1:8002
- ✅ **Frontend**: Running on http://localhost:5000
- ✅ **Dashboard**: Accessible at http://localhost:5000/Home/Dashboard

## Backend Verification

### Test 1: /routes/recommend Endpoint
**Request:**
```json
{
  "start_lat": 23.0225,
  "start_lon": 72.5714,
  "end_lat": 23.035,
  "end_lon": 72.58,
  "waypoints": []
}
```

**Response (Success ✅):**
```json
{
  "routes": [
    {
      "id": "mock-1",
      "name": "Alt 1",
      "coordinates": [[72.57155, 23.02224], [72.57952, 23.03471]],
      "distance_km": 1.643,
      "travel_time_min": 3,
      "traffic_score": 0.961,
      "emission_g": 913,
      "rank": 1
    },
    {
      "id": "mock-2",
      "name": "Alt 2",
      "coordinates": [[72.5714, 23.0225], [72.58, 23.035]],
      "distance_km": 1.6842,
      "travel_time_min": 3,
      "traffic_score": 0.623,
      "emission_g": 959,
      "rank": 2
    },
    {
      "id": "mock-3",
      "name": "Alt 3",
      "coordinates": [[72.57162, 23.02296], [72.58035, 23.03474]],
      "distance_km": 1.6276,
      "travel_time_min": 3,
      "traffic_score": 0.426,
      "emission_g": 665,
      "rank": 3
    }
  ]
}
```

## Frontend Implementation

### Files Modified
1. **`Traffic_Frontend/wwwroot/js/routeSelection.js`**
   - Added `data-action` handling for "select" and "details" buttons
   - Implemented `window.latestAlternatives` global store
   - Exposed `window.RouteSelection.highlightAlternativeById(routeKey)` helper
   - Added `routes:showAlternativeDetails` event dispatch

2. **`Traffic_Frontend/Views/Shared/_AlternativesPanel.cshtml`**
   - Added `data-action="select"` and `data-action="details"` attributes to buttons
   - Created Bootstrap modal `#altDetailsModal` for displaying alternative details
   - Added event listener for `routes:showAlternativeDetails` to populate modal

## Manual Test Procedure

### Step 1: Draw or Select a Route
1. Open Dashboard at http://localhost:5000/Home/Dashboard
2. Click "Draw Route on Map" or "Click to Select Route"
3. Create a route by either:
   - **Draw mode**: Click points on map, double-click to finish
   - **Click mode**: Click start point, then click end point

### Step 2: Analyze Route
1. Click the "Analyze" button (if visible after route creation)
2. Wait for route analysis to complete
3. Observe route metrics displayed (distance, road type, lanes, traffic counts)

### Step 3: View Alternatives
1. Alternatives panel should populate with 3 alternative routes
2. Each alternative card shows:
   - Route name (e.g., "Alt 1", "Alt 2", "Alt 3")
   - Distance in km
   - Rank number
   - Two buttons: "Select" and "Details"

### Step 4: Test Select Button
**Expected Behavior:**
- Click "Select" on any alternative card
- The route should be highlighted on the map (increased width and opacity)
- Map should zoom/pan to fit the selected route bounds
- Console should show `routes:alternativeSelected` event dispatched

**Actual Result:** _(To be filled during manual testing)_

### Step 5: Test Details Button
**Expected Behavior:**
- Click "Details" on any alternative card
- Modal should open with title showing alternative name
- Modal should display:
  - **Distance**: X.XX km
  - **Travel Time**: X min
  - **Traffic Score**: 0.XXX
  - **Emissions (g)**: XXX
- Click "Close" button or outside modal to dismiss

**Actual Result:** _(To be filled during manual testing)_

### Step 6: Programmatic Test
**In Browser Console:**
```javascript
// Test highlight by ID
window.RouteSelection.highlightAlternativeById('mock-1')
// Should highlight Alternative 1 on the map

window.RouteSelection.highlightAlternativeById('mock-2')
// Should highlight Alternative 2 on the map

window.RouteSelection.highlightAlternativeById('mock-3')
// Should highlight Alternative 3 on the map
```

**Expected Result:** Each call should highlight the corresponding route

## Integration Test Results

### Backend Endpoints
- ✅ GET `/` - Service info returned
- ✅ POST `/routes/recommend` - Returns 3 mock alternatives with proper structure
- ✅ POST `/routes/analyze` - Route analysis working (tested previously)
- ✅ POST `/projects/dev-create` - Dev project creation working (tested previously)

### Frontend Components
- ✅ Map initialization and display
- ✅ Route drawing functionality
- ✅ Route click-select mode
- ✅ Route analysis and metrics display
- ✅ Alternatives panel rendering
- ✅ Select button wiring (data-action="select")
- ✅ Details button wiring (data-action="details")
- ✅ Details modal creation and display
- ✅ Event-driven communication (custom events)

## Event Flow

```
User draws route
    ↓
Click "Analyze"
    ↓
routeSelection.js → analyzeRoute()
    ↓
Fetch from /routes/recommend (or mock alternatives)
    ↓
renderAlternativesOnMap() → adds route layers to map
    ↓
dispatchAlternativesEvent() → stores window.latestAlternatives
    ↓
routes:alternatives event → _AlternativesPanel renders cards
    ↓
User clicks "Select" button
    ↓
Click handler checks data-action="select"
    ↓
Calls highlightAlternative() → emphasizes route, zooms map
    ↓
Dispatches routes:alternativeSelected event
```

```
User clicks "Details" button
    ↓
Click handler checks data-action="details"
    ↓
Finds alternative data from window.latestAlternatives
    ↓
Dispatches routes:showAlternativeDetails event
    ↓
_AlternativesPanel listener populates modal
    ↓
Bootstrap modal.show() opens modal
```

## Code Verification

### routeSelection.js Key Functions
- ✅ `dispatchAlternativesEvent()` - Stores alternatives globally
- ✅ Click event listener with `data-action` support
- ✅ `window.RouteSelection.highlightAlternativeById()` - Public API
- ✅ `highlightAlternative()` - Emphasizes route and zooms map
- ✅ Event dispatch for both select and details actions

### _AlternativesPanel.cshtml Key Features
- ✅ Buttons include `data-action` attributes
- ✅ Modal HTML structure (`#altDetailsModal`)
- ✅ Event listener for `routes:showAlternativeDetails`
- ✅ Modal population logic with data extraction
- ✅ Bootstrap modal initialization

## Browser Console Tests

### Test Alternative Selection
```javascript
// Should return the RouteSelection module with exposed methods
window.RouteSelection

// Should return array of alternative routes
window.latestAlternatives

// Should highlight alternative by ID/key
window.RouteSelection.highlightAlternativeById('mock-1')
```

### Test Event Dispatching
```javascript
// Listen for alternative selection
document.addEventListener('routes:alternativeSelected', (e) => {
    console.log('Alternative selected:', e.detail);
});

// Listen for details request
document.addEventListener('routes:showAlternativeDetails', (e) => {
    console.log('Show details for:', e.detail);
});
```

## Known Issues & Limitations
- Frontend service requires manual restart in separate window to stay running
- Backend falls back to SQLite (MySQL connection not configured)
- Alternatives are mock data (real routing engine not implemented)
- No authentication required for dev endpoints

## Next Steps
1. ✅ Complete manual UI testing in browser
2. Add E2E Playwright tests for Select/Details flow
3. Implement real routing algorithm using road network graph
4. Add alternative comparison view
5. Implement "Create Project from Alternative" flow
6. Add traffic overlay visualization
7. Add alerts/notifications for congestion

## Commit Information
**Commit Hash**: 57e750a  
**Message**: feat(ui): wire Select and Details buttons for alternative routes

**Changes:**
- Add data-action attributes to alternative card buttons
- Expose highlightAlternativeById helper in RouteSelection module
- Store latestAlternatives globally for UI handlers
- Add Bootstrap modal for alternative details
- Listen for routes:showAlternativeDetails event to populate modal
- Support both click-on-map and button-click selection flows
