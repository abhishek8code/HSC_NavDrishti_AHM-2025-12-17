# Phase 5 Implementation Plan

## 🎯 Overview

Phase 5 focuses on **Real Sensor Integration & Optimization** - transitioning from mock data to real-world data sources and implementing advanced route optimization.

---

## 📋 Phase 5 Objectives

### 1. Real Sensor Integration
- Replace mock traffic data with real IoT sensors
- Implement GPS vehicle tracking
- Live traffic data aggregation
- Sensor data validation and filtering

### 2. Route Optimization
- Mapbox Optimization API (TSP solver)
- Multi-stop route planning
- Fleet routing and dispatch
- Dynamic route re-optimization

### 3. Static Map Images
- PDF report generation
- Email notifications with maps
- Downloadable route snapshots
- Branded map exports

### 4. Advanced Analytics
- Historical traffic analysis
- Speed analytics and trends
- Congestion pattern detection
- Performance dashboards

---

## 🚀 Feature Breakdown

### Feature 1: IoT Sensor Integration (Week 1-2)

**Backend:**
- `POST /sensors/register` - Register new sensor
- `POST /sensors/data` - Receive sensor readings
- `GET /sensors/status` - Get all sensor statuses
- `GET /sensors/{id}/history` - Get sensor historical data
- Database schema for sensor data
- Real-time data validation

**Frontend:**
- Sensor management UI
- Live sensor status indicators
- Sensor location markers on map
- Historical data charts

**Database Schema:**
```sql
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY,
    sensor_id VARCHAR(50) UNIQUE,
    type VARCHAR(20),  -- 'speed', 'volume', 'gps'
    location_lat REAL,
    location_lon REAL,
    status VARCHAR(20),  -- 'active', 'inactive', 'error'
    last_reading TIMESTAMP
);

CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY,
    sensor_id VARCHAR(50),
    timestamp TIMESTAMP,
    speed_kmh REAL,
    vehicle_count INTEGER,
    congestion_level REAL,
    raw_data TEXT
);
```

---

### Feature 2: GPS Vehicle Tracking (Week 2-3)

**Backend:**
- `POST /vehicles/register` - Register vehicle
- `POST /vehicles/{id}/location` - Update GPS location
- `GET /vehicles/active` - Get all active vehicles
- `GET /vehicles/{id}/track` - Get vehicle path
- WebSocket support for real-time updates

**Frontend:**
- Vehicle tracking dashboard
- Real-time vehicle markers
- Vehicle path visualization
- Speed and status indicators
- Fleet overview panel

**WebSocket Events:**
```javascript
// Server → Client
{
  "event": "vehicle_update",
  "vehicle_id": "V123",
  "location": [72.5714, 23.0225],
  "speed": 45.5,
  "heading": 135
}
```

---

### Feature 3: Optimization API (Week 3-4)

**Backend:**
- `POST /routes/optimize` - Multi-stop optimization
- Mapbox Optimization API integration
- Support for time windows
- Vehicle capacity constraints
- Priority handling

**Frontend:**
- Multi-stop route planner
- Drag-to-reorder stops
- Optimization results comparison
- Save optimized routes

**Request Format:**
```json
{
  "coordinates": [
    {"lon": 72.5714, "lat": 23.0225, "name": "Depot"},
    {"lon": 72.5820, "lat": 23.0332, "name": "Stop 1"},
    {"lon": 72.5550, "lat": 23.0550, "name": "Stop 2"}
  ],
  "source": "first",  // Start from first point
  "destination": "last",  // End at last point
  "roundtrip": true
}
```

---

### Feature 4: Static Images API (Week 4)

**Backend:**
- `POST /maps/snapshot` - Generate map image
- Mapbox Static Images API
- Custom styling and overlays
- Multiple export formats (PNG, JPG)

**Frontend:**
- "Download Map" button
- Email with map attachment
- PDF report generation
- Custom map configurations

**Example:**
```
https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/
  pin-s-a+FF0000(72.5714,23.0225),
  pin-s-b+00FF00(72.5820,23.0332)/
  72.5750,23.0300,12,0/
  800x600@2x?access_token=<token>
```

---

### Feature 5: Advanced Analytics Dashboard (Week 4-5)

**Backend:**
- `GET /analytics/traffic-trends` - Historical trends
- `GET /analytics/congestion-patterns` - Pattern analysis
- `GET /analytics/speed-profile` - Speed analytics
- `GET /analytics/route-performance` - Route metrics

**Frontend:**
- Analytics dashboard page
- Time-series charts (Chart.js)
- Heatmap visualizations
- Export to CSV/Excel

---

## 📊 Implementation Priority

```
Priority 1 (Critical):
  ✓ Optimization API integration
  ✓ Static Images API
  ✓ Basic sensor data ingestion

Priority 2 (High):
  ✓ GPS vehicle tracking
  ✓ Real-time sensor updates
  ✓ Analytics dashboard

Priority 3 (Medium):
  ✓ WebSocket real-time updates
  ✓ Historical data analysis
  ✓ Advanced sensor management
```

---

## 🗓️ Timeline

**Week 1-2: Sensor Integration**
- Day 1-3: Database schema & backend endpoints
- Day 4-7: Sensor registration & data ingestion
- Day 8-10: Frontend sensor management UI

**Week 2-3: Vehicle Tracking**
- Day 1-4: GPS tracking backend
- Day 5-7: Real-time updates (WebSocket)
- Day 8-10: Vehicle tracking UI

**Week 3-4: Optimization**
- Day 1-3: Mapbox Optimization API
- Day 4-7: Multi-stop planner UI
- Day 8-10: Testing & refinement

**Week 4: Static Images & Analytics**
- Day 1-2: Static Images API
- Day 3-5: Analytics backend
- Day 6-7: Analytics dashboard UI

**Week 5: Integration & Testing**
- Day 1-3: End-to-end testing
- Day 4-5: Performance optimization
- Day 6-7: Documentation

---

## 🔧 Technical Requirements

### Backend Dependencies
```python
# Add to requirements.txt
websockets==12.0
pillow==10.1.0  # For image processing
celery==5.3.4  # For background tasks
redis==5.0.1  # For caching
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "@microsoft/signalr": "^8.0.0",  // Real-time updates
    "xlsx": "^0.18.5",  // Excel export
    "jspdf": "^2.5.1"  // PDF generation
  }
}
```

### Database Migration
```python
# Alembic migration for sensor tables
alembic revision -m "add_sensor_tables"
alembic upgrade head
```

---

## 🧪 Testing Strategy

### Unit Tests
- Sensor data validation
- GPS coordinate processing
- Optimization algorithm
- Image generation

### Integration Tests
- End-to-end sensor data flow
- Vehicle tracking accuracy
- Real-time update latency
- API response times

### Load Tests
- 100+ concurrent sensors
- 1000+ vehicle updates/min
- Analytics query performance

---

## 📈 Success Criteria

- [ ] 100+ sensors registered and active
- [ ] Real-time vehicle tracking < 1s latency
- [ ] Optimization API returns routes < 2s
- [ ] Static images generated < 500ms
- [ ] Analytics dashboard loads < 1s
- [ ] All endpoints tested and documented
- [ ] WebSocket connections stable
- [ ] Historical data retention (30 days)

---

## 🎯 Deliverables

1. **Backend APIs** (10+ new endpoints)
2. **Frontend Modules** (4 new dashboards)
3. **Database Schema** (2 new tables)
4. **WebSocket Server** (Real-time updates)
5. **Documentation** (API docs, user guides)
6. **Test Suite** (80%+ coverage)

---

## 🚀 Let's Start!

**First Implementation: Optimization API** (Fastest ROI)

This will give immediate value by enabling:
- Multi-stop route planning
- Fleet optimization
- Time-window scheduling
- Efficient route ordering

Ready to begin? 🎊

