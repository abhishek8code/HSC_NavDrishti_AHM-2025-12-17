# Phase 3 Quick Reference Guide

## 🚀 Quick Start

### Access the System
**Dashboard URL:** http://localhost:5000/Home/Dashboard

### Services Status
- ✅ Frontend: Port 5000
- ✅ Backend: Port 8002

---

## 📍 How to Use Each Feature

### 1. **Draw and Analyze Routes**

**Steps:**
1. Click on the map to add waypoints
2. Add at least 2 points (start and end)
3. Click **"Analyze"** button
4. Wait 2-3 seconds for results

**Result:** 2-3 alternative routes appear on the map with different colors

---

### 2. **View Traffic Overlay**

**Steps:**
1. Locate **"Traffic Stats"** card in left sidebar
2. Toggle **"Overlay"** switch ON
3. View color-coded roads on map:
   - 🟢 Green = Low congestion (0-30%)
   - 🟡 Yellow = Medium (30-70%)
   - 🔴 Red = High (70-100%)

**Features:**
- Auto-refreshes every 30 seconds
- Hover over roads to see details
- View stats: Congestion %, Avg Speed, Vehicle Count

---

### 3. **View Traffic Alerts**

**Steps:**
1. Alerts appear automatically on map load
2. Look for animated markers (⚠️, 🚧, 🚗, 📅)
3. Click markers for details
4. View list in **"Traffic Alerts"** card

**Alert Types:**
- 🚨 Accident (Red - High severity)
- 🚧 Construction (Orange - Medium)
- 🚗 Congestion (Yellow - Medium)
- 📅 Event (Blue - Low)

**Controls:**
- Toggle "Show" switch to hide/show alerts
- Refreshes every 30 seconds

---

### 4. **Compare Routes**

**Steps:**
1. After analyzing routes, see **"Route Alternatives"** panel
2. Check boxes next to 2 or more routes
3. Click **"Compare Selected"** button
4. View comparison chart and table

**Comparison Includes:**
- Distance (km)
- Travel Time (minutes)
- Average Speed (km/h)
- Traffic Score (%)
- CO₂ Emissions (grams)
- **Recommendations:** Fastest, Shortest, Cleanest route

---

## 🎨 UI Guide

### Left Sidebar Cards

1. **Projects** - Create and manage route projects
2. **Route Info** - Current route metrics
3. **Route Alternatives** - List of alternative routes with checkboxes
4. **Scenario Compare** - Select routes to compare
5. **Traffic Alerts** - Live incident alerts
6. **Traffic Stats** - Real-time traffic overview

### Map Features

- **Click**: Add waypoint
- **Route Lines**: Hover to highlight
- **Alert Markers**: Click for details
- **Traffic Overlay**: Color-coded roads

---

## 🔧 Controls & Toggles

### Traffic Overlay Toggle
- **Location:** Traffic Stats card header
- **Label:** "Overlay"
- **Persistence:** Saved to localStorage

### Alerts Toggle
- **Location:** Traffic Alerts card header
- **Label:** "Show"
- **Persistence:** Saved to localStorage

### Route Actions
- **Analyze** - Process current route
- **Clear Route** - Remove all waypoints
- **Finish Route** - Complete drawing and analyze

### Comparison Actions
- **Compare Selected** - Open comparison modal (requires 2+ routes)
- **Clear Selection** - Uncheck all routes

---

## 📊 Understanding Metrics

### Traffic Score
- **Scale:** 0.0 to 1.0 (displayed as 0-100%)
- **Calculation:** `1.0 / (1.0 + duration_hours)`
- **Higher = Better:** Faster route with less traffic

### Congestion Level
- **Scale:** 0.0 to 1.0 (displayed as 0-100%)
- **Calculation:** `1.0 - (speed / max_speed)`
- **Higher = Worse:** More congested

### Emissions
- **Units:** Grams of CO₂
- **Estimation:** `distance_km × 120 g/km`
- **Lower = Better:** More environmentally friendly

---

## 🐛 Troubleshooting

### "No routes showing"
- ✅ Check backend is running on port 8002
- ✅ Wait 3-5 seconds after clicking Analyze
- ✅ Ensure you have at least 2 waypoints
- ✅ Check browser console for errors (F12)

### "Traffic overlay not visible"
- ✅ Toggle switch is ON
- ✅ Map is loaded (see "Map: loaded" in header)
- ✅ Zoom in to see road segments
- ✅ Wait 2-3 seconds for data fetch

### "Alerts not showing"
- ✅ Alerts toggle is ON
- ✅ Check alerts panel for list
- ✅ Markers may be outside current map view (zoom out)

### "Compare button disabled"
- ✅ Select at least 2 routes using checkboxes
- ✅ Routes must be loaded first (draw and analyze)

---

## 🔍 Sample Test Coordinates (Ahmedabad)

### Short Route (2-3 km)
- **Start:** 23.0225, 72.5714 (Ashram Road area)
- **End:** 23.0336, 72.5843 (Panjrapole)

### Medium Route (5-7 km)
- **Start:** 23.0225, 72.5714
- **End:** 23.0550, 72.6050 (Maninagar)

### Long Route (10+ km)
- **Start:** 23.0300, 72.5200 (Bopal)
- **End:** 23.0700, 72.5800 (Vastrapur)

---

## 📈 Auto-Refresh Intervals

- **Traffic Overlay:** Every 30 seconds
- **Traffic Alerts:** Every 30 seconds
- **Route Data:** On-demand (click Analyze)

---

## 💾 Saved Preferences

The following settings persist across sessions:
- ✅ Traffic overlay ON/OFF
- ✅ Alerts display ON/OFF
- ✅ Last map view position (if implemented)

**Storage:** Browser localStorage

---

## 🎯 Keyboard Shortcuts

*(Currently not implemented - Phase 4 enhancement)*

Potential shortcuts:
- `Ctrl+Z` - Undo last waypoint
- `Escape` - Clear route
- `Enter` - Analyze route

---

## 📞 Getting Help

1. Check browser console (F12) for errors
2. Verify both services running:
   ```powershell
   Get-NetTCPConnection -LocalPort 5000,8002 -State Listen
   ```
3. Review `PHASE3_COMPLETE.md` for detailed documentation
4. Check backend logs in terminal

---

## ✨ Tips & Best Practices

1. **Wait for map to load** before drawing routes
2. **Enable traffic overlay** before analyzing for better context
3. **Compare 2-3 routes** for meaningful comparison (not all)
4. **Zoom to appropriate level** to see traffic segments clearly
5. **Refresh page** if UI becomes unresponsive

---

## 🔄 Restart Services

### Backend
```powershell
# Stop backend
Get-Process python | Where-Object { 
    Get-NetTCPConnection -OwningProcess $_.Id -LocalPort 8002 
} | Stop-Process -Force

# Start backend
$env:MAPBOX_ACCESS_TOKEN='pk.eyJ1IjoiYWJoaThjb2RlIiwiYSI6ImNtaWlxb3p1YTB4YXAzZHNmbnV6MGEzNWsifQ.DlHCBHGpIsF7t1iACwEmkQ'
cd C:\Users\abhis\HSC_NavDrishti_AHM
.\.venv\Scripts\python.exe -m uvicorn Traffic_Backend.main:app --host 0.0.0.0 --port 8002
```

### Frontend
```powershell
cd C:\Users\abhis\HSC_NavDrishti_AHM\Traffic_Frontend
dotnet run --urls http://localhost:5000
```

---

*Last Updated: November 30, 2025*  
*Version: Phase 3.0 FINAL*
