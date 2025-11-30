/**
 * Example usage of TrafficLineRenderer
 * This demonstrates how to use the traffic line renderer with Flow Stability
 */

// Example: Initialize traffic line renderer after map loads
function initializeTrafficLines(map) {
    // Create renderer instance
    const trafficRenderer = new TrafficLineRenderer(map);

    // Example traffic line data
    const exampleTrafficLines = [
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
                [72.6100, 23.0250],
                [72.6200, 23.0300]
            ],
            flowStability: FlowStability.UNSTABLE  // Yellow pulsing line
        },
        {
            id: 'line-3',
            coordinates: [
                [72.5500, 23.0100],
                [72.5600, 23.0150],
                [72.5700, 23.0200]
            ],
            flowStability: FlowStability.CONGESTED  // Red solid line
        }
    ];

    // Add traffic lines
    trafficRenderer.updateTrafficLines(exampleTrafficLines);

    // Example: Update a single line's flow stability
    setTimeout(() => {
        trafficRenderer.addTrafficLine({
            id: 'line-2',
            coordinates: [
                [72.6000, 23.0200],
                [72.6100, 23.0250],
                [72.6200, 23.0300]
            ],
            flowStability: FlowStability.CONGESTED  // Change from unstable to congested
        });
    }, 5000);

    return trafficRenderer;
}

// Example: Integrate with SignalR for real-time updates
function setupTrafficLineUpdates(map, connection) {
    const trafficRenderer = new TrafficLineRenderer(map);

    // Listen for traffic line updates via SignalR
    connection.on("UpdateTrafficLines", function (data) {
        // Expected format: { lines: [{ id, coordinates, flowStability }] }
        if (data.lines && Array.isArray(data.lines)) {
            trafficRenderer.updateTrafficLines(data.lines);
        }
    });

    return trafficRenderer;
}

// Example: Convert road network GeoJSON to traffic lines
function convertRoadNetworkToTrafficLines(geojson, flowStabilityData) {
    // flowStabilityData: Map of segment ID to FlowStability
    const features = geojson.features || [];
    
    return features.map((feature, index) => {
        const segmentId = feature.properties?.id || `segment-${index}`;
        const flowStability = flowStabilityData[segmentId] || FlowStability.STABLE;
        
        return {
            id: segmentId,
            coordinates: feature.geometry.coordinates,  // Already in [lng, lat] format
            flowStability: flowStability,
            properties: feature.properties
        };
    });
}

// Export for use
if (typeof window !== 'undefined') {
    window.initializeTrafficLines = initializeTrafficLines;
    window.setupTrafficLineUpdates = setupTrafficLineUpdates;
    window.convertRoadNetworkToTrafficLines = convertRoadNetworkToTrafficLines;
}

