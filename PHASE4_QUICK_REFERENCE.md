# Phase 4 Quick Reference - Mapbox API Enhancements

## 🚀 Quick Start

**Access Dashboard:**
```
http://localhost:5000/Home/Dashboard
```

**Backend API:**
```
http://localhost:8002
```

---

## 📍 1. Geocoding API - Address Search

### Forward Geocoding (Address → Coordinates)

**Endpoint:**
```
GET /routes/geocode/forward?query=<address>
```

**Example:**
```bash
curl "http://localhost:8002/routes/geocode/forward?query=SG%20Highway%20Ahmedabad"
```

**Response:**
```json
{
  "query": "SG Highway Ahmedabad",
  "results": [
    {
      "place_name": "Sola Overbridge, Ahmedabad, Gujarat, India",
      "lon": 72.5714,
      "lat": 23.0225,
      "type": "address",
      "relevance": 0.95
    }
  ]
}
```

### Reverse Geocoding (Coordinates → Address)

**Endpoint:**
```
GET /routes/geocode/reverse?lon=<lon>&lat=<lat>
```

**Example:**
```bash
curl "http://localhost:8002/routes/geocode/reverse?lon=72.5714&lat=23.0225"
```

**Response:**
```json
{
  "address": "Ashram Road, Ahmedabad, Gujarat, India",
  "lon": 72.5714,
  "lat": 23.0225,
  "type": "address"
}
```

---

## 🕐 2. Isochrone API - Reachability Analysis

**Endpoint:**
```
GET /routes/isochrone?lon=<lon>&lat=<lat>&minutes=<time>&profile=<mode>
```

**Parameters:**
- `lon`, `lat` - Center point coordinates
- `minutes` - Travel time (5-60 minutes)
- `profile` - `driving-traffic`, `driving`, `walking`, `cycling`

**Example:**
```bash
curl "http://localhost:8002/routes/isochrone?lon=72.5714&lat=23.0225&minutes=15&profile=driving-traffic"
```

**Response:**
```json
{
  "isochrone": {
    "type": "FeatureCollection",
    "features": [...]
  },
  "center": {"lon": 72.5714, "lat": 23.0225},
  "minutes": 15,
  "profile": "driving-traffic"
}
```

**Use Cases:**
- Emergency response coverage areas
- Delivery zone feasibility
- School catchment areas
- Service area planning

---

## 🔢 3. Matrix API - Travel Time Matrix

**Endpoint:**
```
POST /routes/matrix
```

**Request Body:**
```json
{
  "coordinates": [
    {"lon": 72.5714, "lat": 23.0225},
    {"lon": 72.5820, "lat": 23.0332},
    {"lon": 72.5550, "lat": 23.0550}
  ],
  "profile": "driving-traffic"
}
```

**Response:**
```json
{
  "durations": [
    [0, 420, 680],
    [430, 0, 550],
    [690, 560, 0]
  ],
  "distances": [
    [0, 3500, 5800],
    [3600, 0, 4700],
    [5900, 4800, 0]
  ]
}
```

**Matrix Interpretation:**
- `durations[i][j]` = travel time from point i to j (seconds)
- `distances[i][j]` = distance from point i to j (meters)
- Diagonal = 0 (same origin/destination)

**Use Cases:**
- Origin-Destination (O-D) analysis
- Fleet routing optimization
- Multi-site coordination
- School bus routing

**Limits:**
- Maximum 25 points per request
- 60 requests per minute

---

## 🛣️ 4. Map Matching API - GPS Trace Cleaning

**Endpoint:**
```
POST /routes/map-matching
```

**Request Body:**
```json
{
  "coordinates": [
    {"lon": 72.5714, "lat": 23.0225},
    {"lon": 72.5716, "lat": 23.0227},
    {"lon": 72.5718, "lat": 23.0229},
    {"lon": 72.5720, "lat": 23.0231}
  ],
  "timestamps": ["2024-01-15T10:00:00Z", "2024-01-15T10:00:05Z", ...]
}
```

**Response:**
```json
{
  "matched_route": {
    "type": "LineString",
    "coordinates": [[72.5714, 23.0225], ...]
  },
  "distance": 70,
  "duration": 8,
  "confidence": 0.348,
  "speeds": [12.5, 15.3, 18.2]
}
```

**Use Cases:**
- Clean noisy GPS tracks
- Snap vehicle positions to roads
- Calculate speeds from GPS traces
- Detect traffic from probe data

**Requirements:**
- Minimum 2 coordinates
- Maximum 100 coordinates
- Closer points = better matching (use 5-10m apart)
- Timestamps improve accuracy

---

## 🚗 5. Traffic-Aware Routing

**Change:**
```
OLD: mapbox/driving/{coordinates}
NEW: mapbox/driving-traffic/{coordinates}
```

**Endpoint:**
```
POST /routes/recommend
```

**Request Body:**
```json
{
  "start_lat": 23.0225,
  "start_lon": 72.5714,
  "end_lat": 23.0550,
  "end_lon": 72.6050
}
```

**Benefits:**
- Real-time traffic consideration
- Better ETA predictions
- Automatic congestion avoidance
- More realistic alternative routes

---

## 🎨 Frontend UI Components

### Address Search Bar
- **Location:** Top-left of map
- **Usage:** Type address, click result, set as start/end
- **Shortcut:** Auto-focus with search box

### Isochrone Panel
- **Location:** Right side of map
- **Controls:**
  - Time slider (5-60 minutes)
  - Mode selector (driving/walking/cycling)
  - Generate/Clear buttons
- **Visual:** Blue polygon overlay

### Travel Matrix Panel
- **Location:** Top-right corner
- **Controls:**
  - Click map to add points
  - Point list with remove buttons
  - Calculate button → Modal with results
  - Export CSV button

---

## 🧪 Quick Testing

### PowerShell Test Script
```powershell
# Test Geocoding
Invoke-RestMethod "http://localhost:8002/routes/geocode/forward?query=SG+Highway"

# Test Isochrone
Invoke-RestMethod "http://localhost:8002/routes/isochrone?lon=72.5714&lat=23.0225&minutes=15"

# Test Matrix
$body = '{"coordinates":[{"lon":72.5714,"lat":23.0225},{"lon":72.5820,"lat":23.0332}]}'
Invoke-RestMethod -Uri "http://localhost:8002/routes/matrix" -Method POST -Body $body -ContentType "application/json"

# Test Map Matching
$body = '{"coordinates":[{"lon":72.5714,"lat":23.0225},{"lon":72.5716,"lat":23.0227}]}'
Invoke-RestMethod -Uri "http://localhost:8002/routes/map-matching" -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Rate Limits & Performance

| API | Rate Limit | Response Time |
|-----|-----------|---------------|
| Geocoding | 600/min | ~150ms |
| Isochrone | 300/min | ~300ms |
| Matrix | 60/min | ~500ms |
| Map Matching | 300/min | ~800ms |
| Directions | 300/min | ~200ms |

**Free Tier:**
- 100,000 requests/month for most APIs
- Matrix: 100 elements per request
- No credit card required for testing

---

## 🔧 Configuration

### Environment Variable
```powershell
$env:MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiYWJoaThjb2RlIiwiYSI6ImNtaWlxb3p1YTB4YXAzZHNmbnV6MGEzNWsifQ.DlHCBHGpIsF7t1iACwEmkQ"
```

### Backend Dependencies
```
httpx==0.25.2
```

### Frontend Scripts (Dashboard.cshtml)
```html
<script src="~/js/addressSearch.js?v=1"></script>
<script src="~/js/isochrone.js?v=1"></script>
<script src="~/js/travelMatrix.js?v=1"></script>
```

---

## 🆘 Troubleshooting

### "Mapbox token not configured"
**Solution:** Set environment variable before starting backend

### "No matching found" (Map Matching)
**Solution:** Use closer GPS points (5-10m apart) along a real road

### "Maximum 25 coordinates allowed" (Matrix)
**Solution:** Reduce points or split into batches

### Geocoding returns no results
**Solution:** Add context (city/state): "Highway, Ahmedabad, Gujarat"

### Isochrone too small/large
**Solution:** Adjust time slider or change profile (walking vs driving)

---

## 💡 Sample Use Cases

### Emergency Response
```javascript
// Find fire stations within 10 minutes
Isochrone.generateIsochrone(72.5714, 23.0225, 10, 'driving-traffic');
// Overlay fire station locations
// Check which are within polygon
```

### School Bus Routing
```javascript
// Add all student pickup points
students.forEach(s => TravelMatrix.addPoint(s.lon, s.lat, s.name));
// Calculate O-D matrix
TravelMatrix.calculateMatrix('driving');
// Export CSV for optimization
TravelMatrix.exportCSV();
```

### Traffic Data Collection
```javascript
// Clean GPS traces from vehicles
const gpsPoints = [{lon: 72.5714, lat: 23.0225}, ...];
const matched = await mapMatchGPS(gpsPoints);
// Extract speeds
const speeds = matched.speeds; // [12.5, 15.3, ...] m/s
// Identify congestion (< 15 km/h)
const congested = speeds.filter(s => s * 3.6 < 15);
```

### Site Selection
```javascript
// Click map to get address
map.on('click', async (e) => {
  const address = await AddressSearch.reverseGeocode(e.lngLat.lng, e.lngLat.lat);
  console.log(`Site address: ${address}`);
});
```

---

## 🎯 Success Metrics

✅ **All Endpoints Working:**
- Geocoding Forward: ✓
- Geocoding Reverse: ✓
- Isochrone: ✓
- Matrix: ✓
- Map Matching: ✓

✅ **Performance:**
- Average response time: <500ms
- No rate limit errors
- Mapbox token valid

✅ **UI Integration:**
- Address search bar functional
- Isochrone panel renders correctly
- Matrix modal displays results
- CSV export working

---

## 🔮 Next Steps (Phase 5)

1. **Static Images API** - Map exports for PDF reports
2. **Optimization API** - Multi-stop TSP solver
3. **Real Sensor Integration** - Replace mock traffic data
4. **AI Traffic Prediction** - Use matrix data for ML models

---

## 📞 Support

**Mapbox Docs:**
- https://docs.mapbox.com/api/

**Token Management:**
- https://account.mapbox.com/access-tokens/

**Rate Limits:**
- https://docs.mapbox.com/api/overview/#rate-limits

---

*NavDrishti Phase 4 - Quick Reference*
*Last Updated: November 2024*
