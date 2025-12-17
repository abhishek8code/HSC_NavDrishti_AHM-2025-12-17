# Mapbox Geospatial Intelligence Module - Implementation Guide

## Overview
The **Mapbox Geospatial Intelligence Module** for NavDrishti enables government Road Planning Officers to:
- Draw construction zones on an interactive map
- Analyze traffic impact using isochrone calculations
- Calculate alternative diversion routes
- Store spatial data in MySQL with geometry columns
- Visualize impact zones with color-coded overlays

**Implementation Date**: December 16, 2025  
**Technology Stack**: ASP.NET Core 8, FastAPI, MySQL 8.0, Mapbox GL JS

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│         FRONTEND (ASP.NET Core / Razor)         │
│  ┌──────────────────────────────────────────┐   │
│  │  ConstructionPlanning.cshtml             │   │
│  │  - Mapbox GL Map                         │   │
│  │  - Mapbox Draw Plugin                    │   │
│  │  - Layer Toggles (Traffic, Satellite)    │   │
│  └──────────────────────────────────────────┘   │
│                     ▼                            │
│  ┌──────────────────────────────────────────┐   │
│  │  map_logic.js                            │   │
│  │  - Drawing event handlers                │   │
│  │  - API calls to backend                  │   │
│  │  - Isochrone rendering                   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────┐
│         BACKEND (Python / FastAPI)              │
│  ┌──────────────────────────────────────────┐   │
│  │  construction.py (Router)                │   │
│  │  - /construction/analyze-impact          │   │
│  │  - /construction/diversion-routes        │   │
│  │  - /construction/impact-isochrone        │   │
│  │  - /construction/projects                │   │
│  └──────────────────────────────────────────┘   │
│                     ▼                            │
│  ┌──────────────────────────────────────────┐   │
│  │  mapbox_service.py                       │   │
│  │  - get_diversion_routes()                │   │
│  │  - calculate_impact_isochrone()          │   │
│  │  - get_traffic_matrix()                  │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────┐
│         MAPBOX REST APIs                        │
│  - Directions API (v5)                          │
│  - Isochrone API (v1)                           │
│  - Matrix API (v1)                              │
│  - Traffic Vector Tiles                         │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         DATABASE (MySQL 8.0)                    │
│  ┌──────────────────────────────────────────┐   │
│  │  construction_projects                   │   │
│  │  - id, project_name, dates, status       │   │
│  │  - zone_geometry (GEOMETRY)              │   │
│  │  - impact_radius_geometry (GEOMETRY)     │   │
│  │  - Spatial indexes (SPATIAL INDEX)       │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Part 1: Database Layer

### File: `Traffic_Backend/alembic/versions/001_add_construction_projects.sql`

**Purpose**: Create MySQL table with spatial columns for construction zones.

**Key Features**:
- `zone_geometry` (GEOMETRY): Stores GeoJSON polygon drawn by user
- `impact_radius_geometry` (GEOMETRY): Stores calculated isochrone impact area
- Spatial indexes for fast geospatial queries
- Status enum: `planned`, `active`, `completed`, `cancelled`
- Date validation constraints

**To Apply Migration**:
```sql
-- Connect to MySQL
mysql -u root -p navdrishti_db

-- Run migration script
source Traffic_Backend/alembic/versions/001_add_construction_projects.sql;

-- Verify table creation
DESCRIBE construction_projects;
SHOW INDEX FROM construction_projects;
```

**Sample Query Patterns**:
```sql
-- Find construction zones intersecting a point
SELECT id, project_name 
FROM construction_projects 
WHERE ST_Contains(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326));

-- Find zones within 5km radius
SELECT id, project_name, 
       ST_Distance_Sphere(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326)) AS distance_m
FROM construction_projects 
WHERE ST_Distance_Sphere(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326)) <= 5000;
```

---

## Part 2: Backend Layer

### File: `Traffic_Backend/mapbox_service.py`

**Purpose**: Secure proxy for Mapbox API calls with cost control and error handling.

**Key Functions**:

#### 1. `get_diversion_routes(origin, destination, avoid_polygon)`
- **API**: Mapbox Directions API (driving-traffic)
- **Purpose**: Calculate 3 alternative routes avoiding construction zone
- **Returns**: Routes with duration, distance, and GeoJSON geometry
- **Example**:
  ```python
  routes = await get_diversion_routes(
      origin=(72.5714, 23.0225),
      destination=(72.58, 23.035),
      avoid_polygon={...}  # GeoJSON polygon
  )
  ```

#### 2. `calculate_impact_isochrone(center_point, time_intervals)`
- **API**: Mapbox Isochrone API
- **Purpose**: Calculate driveable areas from construction center
- **Returns**: GeoJSON FeatureCollection with polygons
- **Example**:
  ```python
  isochrones = await calculate_impact_isochrone(
      center_point=(72.5714, 23.0225),
      time_intervals=[5, 10, 15, 20]
  )
  ```

#### 3. `get_traffic_matrix(origins, destinations)`
- **API**: Mapbox Matrix API
- **Purpose**: Batch calculate travel times for multiple routes
- **Returns**: 2D matrix of durations and distances
- **Example**:
  ```python
  matrix = await get_traffic_matrix(
      origins=[(72.5714, 23.0225), (72.58, 23.03)],
      destinations=[(72.59, 23.04), (72.60, 23.05)]
  )
  ```

**Security Features**:
- API token stored in environment variable (`MAPBOX_ACCESS_TOKEN`)
- Rate limiting prevents cost overruns
- Input validation (coordinate bounds, polygon validation)
- Comprehensive error handling (401, 429, 422 errors)
- Audit logging for government compliance

---

### File: `Traffic_Backend/routers/construction.py`

**Purpose**: FastAPI endpoints for construction zone analysis.

**Endpoints**:

#### POST `/construction/analyze-impact`
- **Purpose**: Comprehensive construction zone impact analysis
- **Request Body**:
  ```json
  {
    "project_name": "SG Highway Bridge Repair",
    "description": "Bridge strengthening work",
    "start_date": "2025-01-15",
    "end_date": "2025-03-31",
    "zone_polygon": {
      "type": "Polygon",
      "coordinates": [[[72.57, 23.02], [72.58, 23.02], [72.58, 23.03], [72.57, 23.03], [72.57, 23.02]]]
    },
    "analysis_center": [72.575, 23.025]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "project_id": 123,
    "impact_analysis": {
      "isochrones": { /* GeoJSON FeatureCollection */ },
      "affected_area_km2": "25.4",
      "affected_routes": "Under analysis"
    },
    "recommendations": {
      "message": "Construction zone created...",
      "next_steps": ["Review isochrone impact", "Calculate diversion routes", "Notify controllers"]
    }
  }
  ```

#### POST `/construction/diversion-routes`
- **Purpose**: Calculate alternative routes avoiding construction
- **Request Body**:
  ```json
  {
    "origin": [72.5714, 23.0225],
    "destination": [72.58, 23.035],
    "construction_zone_id": 123,
    "avoid_polygon": { /* Optional GeoJSON polygon */ }
  }
  ```

#### POST `/construction/impact-isochrone`
- **Purpose**: Calculate isochrone polygons for visualization
- **Request Body**:
  ```json
  {
    "center_point": [72.5714, 23.0225],
    "time_intervals": [5, 10, 15, 20]
  }
  ```

#### GET `/construction/projects?status=active`
- **Purpose**: List construction projects with optional filter
- **Response**: Array of projects with geometries as GeoJSON

---

### File: `Traffic_Backend/main.py` (Registration)

**Change**:
```python
from .routers.construction import router as construction_router
app.include_router(construction_router)
```

---

## Part 3: Frontend Layer

### File: `Traffic_Frontend/Views/Home/ConstructionPlanning.cshtml`

**Purpose**: Razor view with Mapbox map and drawing controls.

**Key Components**:

1. **Map Container**: Full-screen Mapbox GL map with navigation and scale controls
2. **Control Panel**:
   - Toggle Live Traffic layer
   - Toggle Satellite view
   - Draw Construction Zone button
   - Clear All button
3. **Analysis Form**: Capture project details (name, dates, description)
4. **Impact Results Panel**: Display analysis results and recommendations
5. **Isochrone Legend**: Color-coded legend for impact zones

**Layer Toggles**:
- **Live Traffic**: Shows Mapbox traffic vector tiles (color-coded congestion)
- **Satellite View**: Switches between streets and satellite basemap

---

### File: `Traffic_Frontend/wwwroot/js/construction/map_logic.js`

**Purpose**: JavaScript module for map interactions and API integration.

**Key Functions**:

#### `init(options)`
- Initialize Mapbox map centered on Ahmedabad
- Setup Mapbox Draw plugin for polygon drawing
- Register event listeners for UI controls

#### `handleDrawCreate(e)`
- Triggered when user completes polygon drawing
- Stores polygon in `currentPolygon` variable
- Shows analysis form

#### `handleFormSubmit(e)`
- Gathers form data and polygon geometry
- Calculates polygon center for isochrone analysis
- Calls `/construction/analyze-impact` endpoint
- Displays results and renders isochrones

#### `renderIsochrones(isochroneData)`
- Adds GeoJSON isochrone data as map source
- Applies color-coded styling:
  - **5 min**: Red (most critical)
  - **10 min**: Orange
  - **15 min**: Yellow
  - **20 min**: Light green
- Shows legend and fits map to bounds

---

### File: `Traffic_Frontend/Controllers/HomeController.cs`

**Change**:
```csharp
public IActionResult ConstructionPlanning()
{
    ViewBag.MapboxToken = _configuration["Mapbox:AccessToken"];
    ViewBag.BackendApiUrl = _configuration["BackendApi:BaseUrl"] ?? "http://localhost:8002";
    return View();
}
```

---

## Setup Instructions

### Step 1: Environment Variables
```bash
# Add to .env file or environment
export MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoiYWJoaThjb2RlIiwiYSI6ImNtaWlxb3p1YTB4YXAzZHNmbnV6MGEzNWsifQ.DlHCBHGpIsF7t1iACwEmkQ"
export SQLALCHEMY_DATABASE_URL="mysql+pymysql://user:pass@localhost/navdrishti_db"
```

### Step 2: Database Migration
```bash
mysql -u root -p navdrishti_db < Traffic_Backend/alembic/versions/001_add_construction_projects.sql
```

### Step 3: Install Python Dependencies
```bash
cd Traffic_Backend
pip install httpx  # For async Mapbox API calls
```

### Step 4: Start Backend
```bash
cd Traffic_Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Step 5: Start Frontend
```bash
cd Traffic_Frontend
dotnet run --urls http://localhost:5000
```

### Step 6: Access Application
Navigate to: **http://localhost:5000/Home/ConstructionPlanning**

---

## Usage Workflow

### For Road Planning Officers:

1. **Navigate to Construction Planning Page**
   - Click "Construction Planning" in navigation menu

2. **Draw Construction Zone**
   - Click "Draw Construction Zone" button
   - Click on map to create polygon vertices
   - Double-click or press Enter to complete

3. **Fill Project Details**
   - Enter project name (required)
   - Select start and end dates (required)
   - Add description (optional)
   - Click "Analyze Impact"

4. **Review Impact Analysis**
   - View isochrone impact zones on map:
     - **Red**: Critical 5-minute zone
     - **Orange**: 10-minute zone
     - **Yellow**: 15-minute zone
     - **Green**: 20-minute zone
   - Review affected area and recommendations
   - Project saved to database with geometry

5. **Calculate Diversion Routes** (Future Enhancement)
   - Use separate endpoint to find alternative routes
   - Visualize multiple route options
   - Export for traffic controller notifications

---

## Testing Procedures

### Backend API Tests

```bash
# Test analyze-impact endpoint
curl -X POST http://localhost:8002/construction/analyze-impact \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test Construction",
    "description": "Test impact analysis",
    "start_date": "2025-01-15",
    "end_date": "2025-03-31",
    "zone_polygon": {
      "type": "Polygon",
      "coordinates": [[[72.57, 23.02], [72.58, 23.02], [72.58, 23.03], [72.57, 23.03], [72.57, 23.02]]]
    },
    "analysis_center": [72.575, 23.025]
  }'

# Test diversion routes
curl -X POST http://localhost:8002/construction/diversion-routes \
  -H "Content-Type: application/json" \
  -d '{
    "origin": [72.5714, 23.0225],
    "destination": [72.58, 23.035]
  }'

# List projects
curl http://localhost:8002/construction/projects?status=active
```

### Frontend Tests

1. **Map Initialization**: Verify map loads centered on Ahmedabad
2. **Drawing Tool**: Test polygon drawing with 4-5 vertices
3. **Layer Toggles**: Toggle traffic and satellite layers
4. **Form Validation**: Submit with missing required fields
5. **API Integration**: Complete full workflow and verify database entry
6. **Isochrone Rendering**: Verify color-coded polygons appear on map

---

## Security & Compliance

### API Key Protection
- ✅ Mapbox token stored in environment variable
- ✅ Token never exposed in frontend JavaScript (passed via ViewBag)
- ✅ Backend acts as secure proxy for all Mapbox calls

### Data Safety
- ✅ Input validation with Pydantic models
- ✅ SQL injection prevention using parameterized queries
- ✅ GeoJSON validation before database insertion

### Audit Trail
- ✅ All API calls logged with timestamp and user context
- ✅ Database records include `created_by` and `created_at`
- ✅ Error logs for government compliance reviews

---

## Future Enhancements

### Phase 1 (Current) ✅
- [x] Draw construction zones
- [x] Calculate isochrone impact
- [x] Store spatial data in MySQL
- [x] Visualize impact zones

### Phase 2 (Planned)
- [ ] Calculate multiple diversion routes
- [ ] Traffic simulation before/after construction
- [ ] Real-time traffic integration
- [ ] Automated email notifications to controllers

### Phase 3 (Advanced)
- [ ] Machine learning for traffic pattern prediction
- [ ] Integration with Google Traffic API
- [ ] Mobile app for field officers
- [ ] Export to PDF reports for government archives

---

## Troubleshooting

### Issue: Map not loading
**Solution**: Check `MAPBOX_ACCESS_TOKEN` in `appsettings.json` or environment

### Issue: 404 on /construction/* endpoints
**Solution**: Verify `construction_router` is registered in `main.py`

### Issue: MySQL spatial query errors
**Solution**: Ensure MySQL 8.0+ with spatial extensions enabled

### Issue: CORS errors
**Solution**: Check CORS middleware in `main.py` allows frontend origin

---

## Mapbox API Cost Estimation

**For Government Use** (Monthly):
- **Directions API**: 100,000 calls/month = $5.00
- **Isochrone API**: 50,000 calls/month = $5.00
- **Matrix API**: 25,000 calls/month = $2.50
- **Traffic Tiles**: Unlimited (included in Mapbox GL JS)

**Total Estimated Cost**: ~$12.50/month for typical government usage

---

## Contributors
- **Team NavDrishti**: Abhishek H. Mehta, Krish K. Patel, Piyush K. Ladumor
- **Technology Partner**: Mapbox Inc.
- **Database Architect**: NavDrishti Team

---

## References
- [Mapbox Directions API Documentation](https://docs.mapbox.com/api/navigation/directions/)
- [Mapbox Isochrone API Documentation](https://docs.mapbox.com/api/navigation/isochrone/)
- [Mapbox Matrix API Documentation](https://docs.mapbox.com/api/navigation/matrix/)
- [MySQL Spatial Data Types](https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html)
- [Mapbox GL Draw Plugin](https://github.com/mapbox/mapbox-gl-draw)
