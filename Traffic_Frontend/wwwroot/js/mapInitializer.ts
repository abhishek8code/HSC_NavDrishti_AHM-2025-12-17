import mapboxgl from 'mapbox-gl';
import { SpaceAnalyzer, Coordinate } from './spaceAnalyzer';

// Initialize Mapbox access token from window variable set by server-side
// This is set in the Index.cshtml view from appsettings.json
const MAPBOX_ACCESS_TOKEN = (window as any).MAPBOX_ACCESS_TOKEN || 'YOUR_MAPBOX_ACCESS_TOKEN_HERE';

// Initialize map
let map: mapboxgl.Map;
let spaceAnalyzer: SpaceAnalyzer;

/**
 * Initialize the Mapbox map
 */
export function initializeMap(): void {
    if (!MAPBOX_ACCESS_TOKEN || MAPBOX_ACCESS_TOKEN === 'YOUR_MAPBOX_ACCESS_TOKEN_HERE') {
        console.error('Mapbox access token is not set. Please configure it in mapInitializer.ts');
        return;
    }

    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-v9', // Using satellite style for better building visibility
        center: [72.5714, 23.0225], // Default to Ahmedabad, India
        zoom: 13
    });

    map.on('load', () => {
        console.log('Map loaded successfully');
        
        // Initialize SpaceAnalyzer after map is loaded
        spaceAnalyzer = new SpaceAnalyzer(map, 0.001); // 0.001 degrees ≈ 111 meters
        
        // Example: Analyze space on map click
        map.on('click', async (e) => {
            const coordinate: Coordinate = {
                latitude: e.lngLat.lat,
                longitude: e.lngLat.lng
            };

            try {
                const result = await spaceAnalyzer.analyzeSpace(coordinate);
                console.log('Space Analysis Result:', result);
                
                // Display result (you can customize this)
                alert(
                    `Space Analysis:\n` +
                    `Building Count: ${result.buildingCount}\n` +
                    `Is Empty: ${result.isEmpty ? 'Yes' : 'No'}\n` +
                    `Coordinate: (${coordinate.latitude}, ${coordinate.longitude})`
                );
            } catch (error) {
                console.error('Error analyzing space:', error);
            }
        });
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
}

// Initialize map when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMap);
} else {
    initializeMap();
}

// Export for use in other scripts
export { map, spaceAnalyzer };

