// Initialize Mapbox access token from window variable set by server-side
const MAPBOX_ACCESS_TOKEN = window.MAPBOX_ACCESS_TOKEN || 'YOUR_MAPBOX_ACCESS_TOKEN_HERE';

// Initialize map
let map;

/**
 * Initialize the Mapbox map
 */
function initializeMap() {
    if (!MAPBOX_ACCESS_TOKEN || MAPBOX_ACCESS_TOKEN === 'YOUR_MAPBOX_ACCESS_TOKEN_HERE') {
        console.error('Mapbox access token is not set');
        return;
    }

    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

    map = new mapboxgl.Map({
        container: 'map',
        // Use the custom Mapbox style
        style: 'mapbox://styles/abhi8code/cmihl5ebg003p01r184ixfrqb',
        center: [72.5714, 23.0225], // Ahmedabad, India
        zoom: 13
    });

    map.on('load', () => {
        console.log('Map loaded successfully');
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
