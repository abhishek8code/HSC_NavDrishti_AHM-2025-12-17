import mapboxgl from 'mapbox-gl';

/**
 * Interface for coordinate points
 */
export interface Coordinate {
    latitude: number;
    longitude: number;
}

/**
 * Interface for bounding box
 */
export interface BoundingBox {
    minLng: number;
    minLat: number;
    maxLng: number;
    maxLat: number;
}

/**
 * Interface for space analysis result
 */
export interface SpaceAnalysisResult {
    coordinate: Coordinate;
    boundingBox: BoundingBox;
    buildingCount: number;
    isEmpty: boolean;
    analysisTimestamp: Date;
}

/**
 * SpaceAnalyzer class that utilizes Mapbox GL JS queryRenderedFeatures API
 * to analyze empty space by counting building features in a bounding box.
 * This serves as a proxy for satellite analysis.
 */
export class SpaceAnalyzer {
    private map: mapboxgl.Map;
    private boundingBoxSize: number; // Size of bounding box in degrees

    /**
     * Creates an instance of SpaceAnalyzer
     * @param map - Mapbox GL JS map instance
     * @param boundingBoxSize - Size of bounding box in degrees (default: 0.001, approximately 111 meters)
     */
    constructor(map: mapboxgl.Map, boundingBoxSize: number = 0.001) {
        if (!map) {
            throw new Error('Map instance is required');
        }
        this.map = map;
        this.boundingBoxSize = boundingBoxSize;
    }

    /**
     * Creates a bounding box around a given coordinate
     * @param coordinate - The center coordinate (latitude, longitude)
     * @returns BoundingBox object with min/max lat/lng
     */
    private createBoundingBox(coordinate: Coordinate): BoundingBox {
        const halfSize = this.boundingBoxSize / 2;
        
        return {
            minLng: coordinate.longitude - halfSize,
            minLat: coordinate.latitude - halfSize,
            maxLng: coordinate.longitude + halfSize,
            maxLat: coordinate.latitude + halfSize
        };
    }

    /**
     * Converts bounding box to Mapbox format (array of [lng, lat] pairs)
     * @param bbox - BoundingBox object
     * @returns Array of coordinate pairs in Mapbox format
     */
    private boundingBoxToMapboxFormat(bbox: BoundingBox): [[number, number], [number, number]] {
        return [
            [bbox.minLng, bbox.minLat],
            [bbox.maxLng, bbox.maxLat]
        ];
    }

    /**
     * Analyzes space at a given coordinate by counting building features
     * within a bounding box. This is a proxy for satellite analysis.
     * 
     * @param coordinate - The coordinate to analyze (latitude, longitude)
     * @returns Promise resolving to SpaceAnalysisResult
     */
    public async analyzeSpace(coordinate: Coordinate): Promise<SpaceAnalysisResult> {
        // Create bounding box around the coordinate
        const boundingBox = this.createBoundingBox(coordinate);

        // Convert bounding box to Mapbox format
        const mapboxBbox = this.boundingBoxToMapboxFormat(boundingBox);

        // Query rendered features for 'building' layer within the bounding box
        const features = this.map.queryRenderedFeatures(mapboxBbox, {
            layers: ['building'] // Query only building layer
        });

        // Count building features
        const buildingCount = features.length;

        // Infer empty space: if building count is 0 or very low, space is likely empty
        // Threshold can be adjusted based on requirements
        const isEmpty = buildingCount === 0;

        return {
            coordinate: coordinate,
            boundingBox: boundingBox,
            buildingCount: buildingCount,
            isEmpty: isEmpty,
            analysisTimestamp: new Date()
        };
    }

    /**
     * Analyzes multiple coordinates in batch
     * @param coordinates - Array of coordinates to analyze
     * @returns Promise resolving to array of SpaceAnalysisResult
     */
    public async analyzeMultipleSpaces(coordinates: Coordinate[]): Promise<SpaceAnalysisResult[]> {
        const results: SpaceAnalysisResult[] = [];

        for (const coordinate of coordinates) {
            try {
                const result = await this.analyzeSpace(coordinate);
                results.push(result);
            } catch (error) {
                console.error(`Error analyzing coordinate (${coordinate.latitude}, ${coordinate.longitude}):`, error);
                // Continue with other coordinates even if one fails
            }
        }

        return results;
    }

    /**
     * Sets the bounding box size for analysis
     * @param size - Size in degrees
     */
    public setBoundingBoxSize(size: number): void {
        if (size <= 0) {
            throw new Error('Bounding box size must be greater than 0');
        }
        this.boundingBoxSize = size;
    }

    /**
     * Gets the current bounding box size
     * @returns Current bounding box size in degrees
     */
    public getBoundingBoxSize(): number {
        return this.boundingBoxSize;
    }

    /**
     * Checks if a specific layer exists on the map
     * @param layerId - The layer ID to check
     * @returns True if layer exists, false otherwise
     */
    public hasLayer(layerId: string): boolean {
        return this.map.getLayer(layerId) !== undefined;
    }

    /**
     * Gets all available layer IDs that can be queried
     * @returns Array of layer IDs
     */
    public getAvailableLayers(): string[] {
        const style = this.map.getStyle();
        if (!style || !style.layers) {
            return [];
        }
        return style.layers.map(layer => layer.id);
    }
}

