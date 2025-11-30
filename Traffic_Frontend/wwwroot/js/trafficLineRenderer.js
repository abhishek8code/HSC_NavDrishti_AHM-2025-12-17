// Compiled JavaScript version - This will be generated from TypeScript
// For immediate use, here's a JavaScript implementation:

/**
 * Traffic Line Renderer for Mapbox GL JS
 * Renders traffic lines with Flow Stability visualization
 */

// Flow Stability states
const FlowStability = {
    STABLE: 'stable',
    UNSTABLE: 'unstable',
    CONGESTED: 'congested'
};

class TrafficLineRenderer {
    constructor(map) {
        if (!map) {
            throw new Error('Map instance is required');
        }
        this.map = map;
        this.sourceId = 'traffic-lines-source';
        this.layerId = 'traffic-lines-layer';
        this.trafficLines = new Map();
        this.animationFrameId = null;
        this.pulsePhase = 0;
        this.initializeLayers();
        this.startAnimation();
    }

    initializeLayers() {
        if (!this.map.isStyleLoaded()) {
            this.map.on('load', () => this.initializeLayers());
            return;
        }

        // Remove existing layers and sources if they exist
        if (this.map.getLayer(this.layerId)) {
            this.map.removeLayer(this.layerId);
        }
        if (this.map.getSource(this.sourceId)) {
            this.map.removeSource(this.sourceId);
        }

        // Add source for traffic lines
        this.map.addSource(this.sourceId, {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: []
            }
        });

        // Add main layer for traffic lines
        this.map.addLayer({
            id: this.layerId,
            type: 'line',
            source: this.sourceId,
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-width': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    10, 2,
                    15, 4,
                    20, 6
                ],
                'line-color': [
                    'match',
                    ['get', 'flowStability'],
                    FlowStability.STABLE, '#00FF00',      // Solid Green
                    FlowStability.UNSTABLE, '#FFFF00',     // Yellow
                    FlowStability.CONGESTED, '#FF0000',    // Solid Red
                    '#808080'                              // Default gray
                ],
                'line-opacity': [
                    'match',
                    ['get', 'flowStability'],
                    FlowStability.UNSTABLE, [
                        'interpolate',
                        ['linear'],
                        ['get', 'animationPhase'],
                        0, 0.6,
                        0.5, 1.0,
                        1, 0.6
                    ],
                    1.0  // Full opacity for stable and congested
                ]
            }
        });

        // Add pulsing layer for unstable flow using line-gradient
        this.map.addLayer({
            id: this.layerId + '-unstable-pulse',
            type: 'line',
            source: this.sourceId,
            filter: ['==', ['get', 'flowStability'], FlowStability.UNSTABLE],
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-width': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    10, 3,
                    15, 5,
                    20, 7
                ],
                'line-gradient': [
                    'interpolate',
                    ['linear'],
                    ['line-progress'],
                    0, 'rgba(255, 255, 0, 0.3)',
                    0.5, 'rgba(255, 255, 0, 0.8)',
                    1, 'rgba(255, 255, 0, 0.3)'
                ],
                'line-opacity': [
                    'interpolate',
                    ['linear'],
                    ['get', 'animationPhase'],
                    0, 0.4,
                    0.5, 0.9,
                    1, 0.4
                ]
            }
        }, this.layerId);
    }

    updateTrafficLines(lines) {
        lines.forEach(line => {
            this.trafficLines.set(line.id, line);
        });
        this.updateMapSource();
    }

    addTrafficLine(line) {
        this.trafficLines.set(line.id, line);
        this.updateMapSource();
    }

    removeTrafficLine(id) {
        this.trafficLines.delete(id);
        this.updateMapSource();
    }

    clearTrafficLines() {
        this.trafficLines.clear();
        this.updateMapSource();
    }

    updateMapSource() {
        if (!this.map.isStyleLoaded()) {
            return;
        }

        const source = this.map.getSource(this.sourceId);
        if (!source) {
            return;
        }

        const features = Array.from(this.trafficLines.values()).map(line => ({
            type: 'Feature',
            geometry: {
                type: 'LineString',
                coordinates: line.coordinates
            },
            properties: {
                id: line.id,
                flowStability: line.flowStability,
                animationPhase: this.pulsePhase,
                ...line.properties
            }
        }));

        source.setData({
            type: 'FeatureCollection',
            features: features
        });
    }

    startAnimation() {
        const animate = () => {
            this.pulsePhase = (this.pulsePhase + 0.02) % 1;
            
            if (this.map.isStyleLoaded()) {
                const source = this.map.getSource(this.sourceId);
                if (source) {
                    const data = source._data;
                    if (data && data.features) {
                        data.features.forEach(feature => {
                            if (feature.properties && 
                                feature.properties.flowStability === FlowStability.UNSTABLE) {
                                feature.properties.animationPhase = this.pulsePhase;
                            }
                        });
                        source.setData(data);
                    }
                }
            }
            
            this.animationFrameId = requestAnimationFrame(animate);
        };
        
        this.animationFrameId = requestAnimationFrame(animate);
    }

    stopAnimation() {
        if (this.animationFrameId !== null) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    destroy() {
        this.stopAnimation();
        
        if (this.map.isStyleLoaded()) {
            if (this.map.getLayer(this.layerId + '-unstable-pulse')) {
                this.map.removeLayer(this.layerId + '-unstable-pulse');
            }
            if (this.map.getLayer(this.layerId)) {
                this.map.removeLayer(this.layerId);
            }
            if (this.map.getSource(this.sourceId)) {
                this.map.removeSource(this.sourceId);
            }
        }
        
        this.trafficLines.clear();
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TrafficLineRenderer, FlowStability };
}

