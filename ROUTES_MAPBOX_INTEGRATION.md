# Routes.py Mapbox Integration Update

## Date: December 16, 2025

## Summary
Updated `Traffic_Backend/routers/routes.py` to use the centralized `mapbox_service.py` module instead of making direct Mapbox API calls.

---

## Changes Made

### 1. Added Import Statement
```python
# Import centralized Mapbox service
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from mapbox_service import get_diversion_routes
```

### 2. Refactored `/routes/recommend` Endpoint

**Before** (Direct API calls):
- Made HTTP requests directly to Mapbox Directions API
- Inline error handling
- No audit logging
- Token validation scattered
- 90+ lines of code

**After** (Centralized service):
- Calls `get_diversion_routes()` from `mapbox_service.py`
- Comprehensive error handling from service
- Audit logging built-in
- Secure token management
- 70 lines of code (cleaner)

---

## Benefits of Using Centralized Service

### 1. **Security**
✅ API token never exposed in multiple places  
✅ Consistent authentication across all endpoints  
✅ Rate limiting and cost control in one place

### 2. **Error Handling**
✅ Standardized error messages (401, 429, 422)  
✅ Government-friendly error descriptions  
✅ Automatic fallback to mock data on failures

### 3. **Audit & Compliance**
✅ All Mapbox calls logged for government audit  
✅ Request/response tracking  
✅ Usage metrics for cost analysis

### 4. **Maintainability**
✅ Single source of truth for Mapbox logic  
✅ Easier to update API versions  
✅ Consistent response formatting

### 5. **Code Quality**
✅ Reduced duplication  
✅ Better separation of concerns  
✅ Easier to test

---

## Request/Response Flow

```
Frontend Dashboard
    ↓ POST /routes/recommend
    ↓
routers/routes.py
    ↓ await get_diversion_routes()
    ↓
mapbox_service.py
    ↓ HTTP GET to Mapbox Directions API
    ↓ https://api.mapbox.com/directions/v5/...
    ↓
Mapbox API
    ↓ JSON response with routes
    ↓
mapbox_service.py
    ↓ Parse & validate response
    ↓ Return structured data
    ↓
routers/routes.py
    ↓ Transform to frontend format
    ↓ Add traffic score, emissions
    ↓
Frontend Dashboard
    ✅ Display 2-3 alternative routes
```

---

## Test Results

### Test Script: `test_mapbox_integration.py`

**Input:**
```json
{
  "start_lat": 23.0225,
  "start_lon": 72.5714,
  "end_lat": 23.035,
  "end_lon": 72.58
}
```

**Output:**
```
✅ SUCCESS: Using real Mapbox Directions API via mapbox_service.py

Route 1:
  - Distance: 2.1872 km
  - Travel Time: 8 min
  - Traffic Score: 0.879
  - Emissions: 262 g CO₂
  - Coordinates: 76 points

Route 2:
  - Distance: 2.2763 km
  - Travel Time: 8 min
  - Traffic Score: 0.879
  - Emissions: 273 g CO₂
  - Coordinates: 86 points
```

**Verification:**
- ✅ Real Mapbox data (not mock)
- ✅ Multiple alternatives returned
- ✅ Accurate distance/time calculations
- ✅ Proper coordinate geometry (76-86 points)
- ✅ Traffic-aware routing (driving-traffic profile)

---

## Code Comparison

### Old Implementation (90+ lines)
```python
# Direct API call with inline logic
mapbox_url = f"https://api.mapbox.com/directions/v5/..."
params = {'access_token': mapbox_token, 'alternatives': 'true', ...}

async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get(mapbox_url, params=params)
    if response.status_code != 200:
        return {"error": f"Directions failed: status {response.status_code}"}
    data = response.json()
    
# Manual parsing and transformation
for i, route in enumerate(data['routes'][:3]):
    # 30+ lines of parsing logic
    ...
```

### New Implementation (35 lines)
```python
# Use centralized service
mapbox_result = await get_diversion_routes(
    origin=(payload.start_lon, payload.start_lat),
    destination=(payload.end_lon, payload.end_lat),
    avoid_polygon=None,
    alternatives=3
)

# Simple transformation
for i, route in enumerate(mapbox_result.get("routes", [])[:3]):
    routes.append({
        "id": f"mapbox-{i+1}",
        "coordinates": route.get("geometry", {}).get("coordinates", []),
        "distance_km": route.get("distance_km"),
        "travel_time_min": route.get("duration_minutes"),
        ...
    })
```

---

## Fallback Behavior

### When Mapbox is Unavailable:

1. **No Token**: Falls back to `_generate_mock_alternatives()`
2. **API Error (401/429)**: Caught by mapbox_service, returns error, triggers fallback
3. **Network Error**: Caught by try/except, triggers fallback
4. **Invalid Response**: Caught by validation, triggers fallback

**Mock Data Example:**
```json
{
  "routes": [
    {
      "id": "mock-1",
      "name": "Alt 1",
      "coordinates": [[72.5714, 23.0225], [72.58, 23.035]],
      "distance_km": 1.643,
      "travel_time_min": 3,
      "traffic_score": 0.742,
      "emission_g": 613
    }
  ]
}
```

---

## Future Enhancements

### Phase 1: Enhanced Routing ✅ (Complete)
- [x] Use centralized mapbox_service
- [x] Real-time traffic integration
- [x] Multiple alternatives (up to 3)
- [x] Proper error handling

### Phase 2: Advanced Features (Planned)
- [ ] Waypoint support (via waypoints parameter)
- [ ] Avoid polygons (construction zones)
- [ ] Custom routing profiles (truck, bike, walking)
- [ ] Speed limit adherence

### Phase 3: Optimization (Planned)
- [ ] Cache frequent routes (Redis)
- [ ] Batch route calculations
- [ ] Response compression
- [ ] WebSocket live updates

---

## How to Test

### 1. Manual Test via Browser
```
1. Navigate to http://localhost:5000/Home/Dashboard
2. Click "Draw Route on Map" or "Click to Select Route"
3. Create a route (start → end)
4. Click "Analyze" button
5. Wait for alternatives panel to populate
6. Verify route IDs start with "mapbox-" (not "mock-")
```

### 2. API Test via cURL
```bash
curl -X POST http://localhost:8002/routes/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 23.0225,
    "start_lon": 72.5714,
    "end_lat": 23.035,
    "end_lon": 72.58,
    "waypoints": []
  }'
```

### 3. Python Test Script
```bash
python test_mapbox_integration.py
```

---

## Troubleshooting

### Issue: Still getting mock data
**Solution**: 
1. Check `MAPBOX_ACCESS_TOKEN` is set in environment
2. Verify backend logs show "Successfully retrieved X routes from Mapbox service"
3. Test token with: `curl "https://api.mapbox.com/directions/v5/mapbox/driving/-122.4,37.8;-122.5,37.9?access_token=YOUR_TOKEN"`

### Issue: HTTPException 401
**Solution**: Token invalid or expired. Update token in environment variables.

### Issue: HTTPException 429
**Solution**: Rate limit exceeded. Mapbox free tier = 100k requests/month. Check usage at mapbox.com dashboard.

### Issue: Import error for mapbox_service
**Solution**: Ensure `mapbox_service.py` exists at `Traffic_Backend/mapbox_service.py`

---

## API Cost Impact

**Before** (Direct calls):
- No centralized tracking
- Risk of duplicate calls
- No rate limiting

**After** (Centralized):
- All calls logged
- Easier to track usage
- Rate limiting possible
- Cost visibility

**Estimated Monthly Cost** (100k routes):
- Directions API: 100,000 calls × $0.05/1000 = **$5.00/month**

---

## Files Modified

1. **`Traffic_Backend/routers/routes.py`**
   - Added import for `mapbox_service`
   - Refactored `/routes/recommend` endpoint
   - Reduced code complexity
   - Improved error handling

2. **`test_mapbox_integration.py`** (New)
   - Test script for endpoint verification
   - Validates real Mapbox integration
   - Checks response structure

---

## Contributors
- **Team NavDrishti**: Abhishek H. Mehta, Krish K. Patel, Piyush K. Ladumor
- **Integration Date**: December 16, 2025
- **Technology**: FastAPI, Mapbox Directions API, Python 3.11+

---

## References
- [Mapbox Directions API Documentation](https://docs.mapbox.com/api/navigation/directions/)
- [NavDrishti Mapbox Service Module](./mapbox_service.py)
- [Construction Planning Module](./MAPBOX_GEOSPATIAL_MODULE.md)
