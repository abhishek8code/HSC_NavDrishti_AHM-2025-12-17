# Dashboard Feature

The Dashboard provides real-time traffic monitoring with metrics and heatmap visualization.

## Features

- **3-Column Metrics Row**: 
  - Active Projects (counter)
  - Critical Alerts (red counter)
  - CO2 Saved (green text)
  
- **Full-width Mapbox Map**: Interactive map with heatmap overlay

- **Real-time Updates**: SignalR integration for live dashboard updates

- **Heatmap Visualization**: Renders heatmap from JSON data with lat/lon/severity

## Usage

### Access the Dashboard

Navigate to: `/Home/Dashboard`

### Dashboard Update Function

The `updateDashboard(data)` function accepts a data object with the following structure:

```javascript
{
    activeProjects: 5,           // Number of active projects
    criticalAlerts: 3,          // Number of critical alerts
    co2Saved: 1250.5,           // CO2 saved in kg
    heatmapData: [              // Array of heatmap points
        {
            lat: 23.0225,
            lon: 72.5714,
            severity: 3.5
        },
        {
            lat: 23.0300,
            lon: 72.5800,
            severity: 2.0
        }
    ]
}
```

### Sending Updates via SignalR

#### From Server-Side (C#)

```csharp
using Microsoft.AspNetCore.SignalR;
using Traffic_Frontend.Hubs;

// Inject IHubContext<DashboardHub>
private readonly IHubContext<DashboardHub> _hubContext;

// Send update
await _hubContext.Clients.All.SendAsync("UpdateDashboard", new {
    activeProjects = 5,
    criticalAlerts = 3,
    co2Saved = 1250.5,
    heatmapData = new[] {
        new { lat = 23.0225, lon = 72.5714, severity = 3.5 },
        new { lat = 23.0300, lon = 72.5800, severity = 2.0 }
    }
});
```

#### From Client-Side (JavaScript)

```javascript
// The updateDashboard function is automatically called via SignalR
// But you can also call it directly:
updateDashboard({
    activeProjects: 5,
    criticalAlerts: 3,
    co2Saved: 1250.5,
    heatmapData: [
        { lat: 23.0225, lon: 72.5714, severity: 3.5 },
        { lat: 23.0300, lon: 72.5800, severity: 2.0 }
    ]
});
```

### Heatmap Data Format

The heatmap accepts data in two formats:

#### Format 1: Array of Objects
```javascript
[
    { lat: 23.0225, lon: 72.5714, severity: 3.5 },
    { lat: 23.0300, lon: 72.5800, severity: 2.0 }
]
```

#### Format 2: GeoJSON FeatureCollection
```javascript
{
    type: "FeatureCollection",
    features: [
        {
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [72.5714, 23.0225]  // [lon, lat]
            },
            properties: {
                severity: 3.5
            }
        }
    ]
}
```

### Testing the Dashboard

Use the Test API endpoints to send sample data:

#### Send Dashboard Update
```bash
POST /api/test/dashboard-update
Content-Type: application/json

{
    "activeProjects": 5,
    "criticalAlerts": 3,
    "co2Saved": 1250.5
}
```

#### Send Heatmap Data
```bash
POST /api/test/heatmap-data
Content-Type: application/json

[
    { "lat": 23.0225, "lon": 72.5714, "severity": 3.5 },
    { "lat": 23.0300, "lon": 72.5800, "severity": 2.0 }
]
```

### Heatmap Severity Scale

The heatmap uses a severity scale from 0 to 5:
- 0: No severity (transparent)
- 1: Low (light blue)
- 2-3: Medium (yellow/orange)
- 4-5: High (red)

The heatmap intensity and radius adjust based on zoom level for optimal visualization.

## SignalR Hub

The dashboard uses the `DashboardHub` located at `/dashboardHub`.

To send updates from any part of your application:

1. Inject `IHubContext<DashboardHub>` into your service/controller
2. Call `SendAsync("UpdateDashboard", data)` on `Clients.All`

## Configuration

Make sure to set your Mapbox access token in `appsettings.json`:

```json
{
  "Mapbox": {
    "AccessToken": "your-mapbox-token-here"
  }
}
```

