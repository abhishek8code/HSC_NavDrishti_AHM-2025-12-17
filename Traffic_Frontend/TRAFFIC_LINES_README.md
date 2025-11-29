# Traffic Line Renderer - Flow Stability Visualization

This module renders traffic lines on Mapbox GL JS with dynamic colors based on Flow Stability metrics.

## Flow Stability States

- **STABLE**: Solid Green line (`#00FF00`)
- **UNSTABLE**: Pulsing Yellow line (`#FFFF00`) with animation
- **CONGESTED**: Solid Red line (`#FF0000`)

## Features

- Dynamic line colors based on Flow Stability
- Pulsing animation for unstable flow using Mapbox `line-gradient` and opacity interpolation
- Real-time updates support
- Efficient rendering with Mapbox GL JS

## Usage

### Basic Usage

```javascript
// After map is loaded
const trafficRenderer = new TrafficLineRenderer(map);

// Add traffic lines
const trafficLines = [
    {
        id: 'line-1',
        coordinates: [
            [72.5714, 23.0225],  // [lng, lat]
            [72.5800, 23.0300],
            [72.5900, 23.0400]
        ],
        flowStability: FlowStability.STABLE  // Green solid line
    },
    {
        id: 'line-2',
        coordinates: [
            [72.6000, 23.0200],
            [72.6100, 23.0250]
        ],
        flowStability: FlowStability.UNSTABLE  // Yellow pulsing line
    },
    {
        id: 'line-3',
        coordinates: [
            [72.5500, 23.0100],
            [72.5600, 23.0150]
        ],
        flowStability: FlowStability.CONGESTED  // Red solid line
    }
];

trafficRenderer.updateTrafficLines(trafficLines);
```

### Update Individual Lines

```javascript
// Update a single line's flow stability
trafficRenderer.addTrafficLine({
    id: 'line-2',
    coordinates: [[72.6000, 23.0200], [72.6100, 23.0250]],
    flowStability: FlowStability.CONGESTED  // Change to congested
});
```

### Remove Lines

```javascript
// Remove a specific line
trafficRenderer.removeTrafficLine('line-1');

// Clear all lines
trafficRenderer.clearTrafficLines();
```

### Integration with SignalR

```javascript
// In your SignalR connection setup
connection.on("UpdateTrafficLines", function (data) {
    if (trafficRenderer && data.lines) {
        trafficRenderer.updateTrafficLines(data.lines);
    }
});
```

### Convert Road Network GeoJSON

```javascript
function convertRoadNetworkToTrafficLines(geojson, flowStabilityData) {
    const features = geojson.features || [];
    
    return features.map((feature, index) => {
        const segmentId = feature.properties?.id || `segment-${index}`;
        const flowStability = flowStabilityData[segmentId] || FlowStability.STABLE;
        
        return {
            id: segmentId,
            coordinates: feature.geometry.coordinates,  // [lng, lat] format
            flowStability: flowStability,
            properties: feature.properties
        };
    });
}

// Usage
const flowStabilityMap = {
    'segment-1': FlowStability.STABLE,
    'segment-2': FlowStability.UNSTABLE,
    'segment-3': FlowStability.CONGESTED
};

const trafficLines = convertRoadNetworkToTrafficLines(roadNetworkGeoJSON, flowStabilityMap);
trafficRenderer.updateTrafficLines(trafficLines);
```

## Visual Implementation Details

### Stable Flow (Green)
- Solid green line (`#00FF00`)
- Full opacity (1.0)
- Standard line width

### Unstable Flow (Yellow - Pulsing)
- Yellow base color (`#FFFF00`)
- Two-layer approach:
  1. Base layer with opacity animation (0.6 to 1.0)
  2. Gradient layer with `line-gradient` for pulsing effect
- Animation uses `requestAnimationFrame` for smooth pulsing
- Opacity interpolates based on animation phase

### Congested (Red)
- Solid red line (`#FF0000`)
- Full opacity (1.0)
- Standard line width

## Technical Details

### Mapbox GL JS Properties Used

1. **line-color**: Uses `match` expression to select color based on `flowStability` property
2. **line-opacity**: Uses `interpolate` expression for pulsing effect on unstable lines
3. **line-gradient**: Used for the pulsing layer on unstable lines
4. **line-width**: Zoom-based interpolation for responsive line width

### Animation

The pulsing effect is achieved through:
- `requestAnimationFrame` loop updating animation phase
- Mapbox expressions using `animationPhase` property
- Opacity interpolation from 0.4 to 0.9 for smooth pulsing
- Gradient interpolation along the line for visual depth

## API Reference

### TrafficLineRenderer Class

#### Constructor
```javascript
new TrafficLineRenderer(map: mapboxgl.Map)
```

#### Methods

- **updateTrafficLines(lines: TrafficLineData[])**: Update all traffic lines
- **addTrafficLine(line: TrafficLineData)**: Add or update a single line
- **removeTrafficLine(id: string)**: Remove a line by ID
- **clearTrafficLines()**: Remove all lines
- **stopAnimation()**: Stop the animation loop
- **destroy()**: Clean up all resources

### TrafficLineData Interface

```typescript
{
    id: string;                    // Unique identifier
    coordinates: number[][];      // Array of [lng, lat] pairs
    flowStability: FlowStability; // 'stable' | 'unstable' | 'congested'
    properties?: Record<string, any>; // Optional additional properties
}
```

## Example: Server-Side Update via SignalR

```csharp
// In your C# controller or service
await _hubContext.Clients.All.SendAsync("UpdateTrafficLines", new {
    lines = new[] {
        new {
            id = "line-1",
            coordinates = new[] {
                new[] { 72.5714, 23.0225 },
                new[] { 72.5800, 23.0300 }
            },
            flowStability = "stable"
        },
        new {
            id = "line-2",
            coordinates = new[] {
                new[] { 72.6000, 23.0200 },
                new[] { 72.6100, 23.0250 }
            },
            flowStability = "unstable"
        }
    }
});
```

## Notes

- The renderer automatically handles map style loading
- Animation runs continuously for unstable lines
- Line width scales with zoom level for better visibility
- The renderer can be integrated with the existing dashboard heatmap

