import mapboxgl from 'mapbox-gl';

/**
 * Flow Stability states
 */
export enum FlowStability {
    STABLE = 'stable',
    UNSTABLE = 'unstable',
    CONGESTED = 'congested'
}

/**
 * Interface for traffic line data
 */
export interface TrafficLineData {
    id: string;
    coordinates: number[][]; // Array of [lng, lat] pairs
    flowStability: FlowStability;
    properties?: Record<string, any>;
}

/**
 * TrafficLineRenderer class for rendering traffic lines with Flow Stability visualization
 */
export class TrafficLineRenderer {
    private map: mapboxgl.Map;
    private sourceId: string = 'traffic-lines-source';
    private layerId: string = 'traffic-lines-layer';
    private trafficLines: Map<string, TrafficLineData> = new Map();
    private animationFrameId: number | null = null;
    private pulsePhase: number = 0;

    constructor(map: mapboxgl.Map) {
        if (!map) {
            throw new Error('Map instance is required');
        }
        this.map = map;
        this.initializeLayers();
        this.startAnimation();
    }

    /**
     * Initialize Mapbox layers for traffic lines
     */
    private initializeLayers(): void {
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

        // Add layer for traffic lines with different styles based on flow stability
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
                    FlowStability.UNSTABLE, '#FFFF00',     // Yellow (will be animated)
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

        // Add a second layer for unstable flow with pulsing effect using line-gradient
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
                    0, 'rgba(255, 255, 0, 0.3)',  // Yellow with low opacity
                    0.5, 'rgba(255, 255, 0, 0.8)', // Yellow with high opacity
                    1, 'rgba(255, 255, 0, 0.3)'     // Yellow with low opacity
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
        }, this.layerId); // Insert after main layer
    }

    /**
     * Add or update traffic lines
     * @param lines Array of traffic line data
     */
    public updateTrafficLines(lines: TrafficLineData[]): void {
        lines.forEach(line => {
            this.trafficLines.set(line.id, line);
        });
        this.updateMapSource();
    }

    /**
     * Add a single traffic line
     * @param line Traffic line data
     */
    public addTrafficLine(line: TrafficLineData): void {
        this.trafficLines.set(line.id, line);
        this.updateMapSource();
    }

    /**
     * Remove a traffic line
     * @param id Line ID
     */
    public removeTrafficLine(id: string): void {
        this.trafficLines.delete(id);
        this.updateMapSource();
    }

    /**
     * Clear all traffic lines
     */
    public clearTrafficLines(): void {
        this.trafficLines.clear();
        this.updateMapSource();
    }

    /**
     * Update the Mapbox source with current traffic lines
     */
    private updateMapSource(): void {
        if (!this.map.isStyleLoaded()) {
            return;
        }

        const source = this.map.getSource(this.sourceId) as mapboxgl.GeoJSONSource;
        if (!source) {
            return;
        }

        const features = Array.from(this.trafficLines.values()).map(line => ({
            type: 'Feature' as const,
            geometry: {
                type: 'LineString' as const,
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

    /**
     * Start animation loop for pulsing effects
     */
    private startAnimation(): void {
        const animate = () => {
            this.pulsePhase = (this.pulsePhase + 0.02) % 1;
            
            // Update animation phase in source data for unstable lines
            if (this.map.isStyleLoaded()) {
                const source = this.map.getSource(this.sourceId) as mapboxgl.GeoJSONSource;
                if (source) {
                    const data = source._data as GeoJSON.FeatureCollection;
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

    /**
     * Stop animation loop
     */
    public stopAnimation(): void {
        if (this.animationFrameId !== null) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    /**
     * Cleanup resources
     */
    public destroy(): void {
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

