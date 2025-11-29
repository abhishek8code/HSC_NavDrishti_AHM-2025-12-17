# Traffic Frontend - ASP.NET Core MVC with Mapbox GL JS

This project contains an ASP.NET Core MVC application with a TypeScript `SpaceAnalyzer` class that uses Mapbox GL JS to analyze empty space by counting building features.

## Features

- **SpaceAnalyzer Class**: TypeScript class that utilizes Mapbox GL JS `queryRenderedFeatures` API
- **Bounding Box Analysis**: Creates bounding boxes around coordinates and counts building features
- **Empty Space Detection**: Infers empty space as a proxy for satellite analysis

## Prerequisites

- .NET 8.0 SDK or later
- Node.js and npm (for TypeScript compilation)
- Mapbox access token (get one at https://account.mapbox.com/)

## Setup Instructions

1. **Install .NET dependencies** (if needed):
   ```bash
   dotnet restore
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Configure Mapbox Access Token**:
   - Open `appsettings.json`
   - Replace `YOUR_MAPBOX_ACCESS_TOKEN_HERE` with your actual Mapbox access token
   - Or set it via environment variable: `Mapbox:AccessToken`

4. **Compile TypeScript**:
   ```bash
   npm run build
   ```
   
   Or watch for changes:
   ```bash
   npm run watch
   ```

5. **Run the application**:
   ```bash
   dotnet run
   ```

6. **Open in browser**:
   - Navigate to `https://localhost:5001` or `http://localhost:5000`
   - Click on the map to analyze space at that coordinate

## SpaceAnalyzer Class Usage

The `SpaceAnalyzer` class is located in `wwwroot/js/spaceAnalyzer.ts`. Here's how to use it:

```typescript
import { SpaceAnalyzer, Coordinate } from './spaceAnalyzer';

// After map is loaded
const analyzer = new SpaceAnalyzer(map, 0.001); // 0.001 degrees bounding box

// Analyze a single coordinate
const coordinate: Coordinate = {
    latitude: 23.0225,
    longitude: 72.5714
};

const result = await analyzer.analyzeSpace(coordinate);
console.log(`Building count: ${result.buildingCount}`);
console.log(`Is empty: ${result.isEmpty}`);

// Analyze multiple coordinates
const coordinates: Coordinate[] = [
    { latitude: 23.0225, longitude: 72.5714 },
    { latitude: 23.0300, longitude: 72.5800 }
];
const results = await analyzer.analyzeMultipleSpaces(coordinates);
```

## API Reference

### SpaceAnalyzer Class

#### Constructor
```typescript
constructor(map: mapboxgl.Map, boundingBoxSize: number = 0.001)
```

#### Methods

- **analyzeSpace(coordinate: Coordinate)**: Analyzes space at a given coordinate
- **analyzeMultipleSpaces(coordinates: Coordinate[])**: Analyzes multiple coordinates in batch
- **setBoundingBoxSize(size: number)**: Sets the bounding box size for analysis
- **getBoundingBoxSize()**: Gets the current bounding box size
- **hasLayer(layerId: string)**: Checks if a layer exists on the map
- **getAvailableLayers()**: Gets all available layer IDs

## Project Structure

```
Traffic_Frontend/
├── Controllers/
│   └── HomeController.cs          # MVC controller
├── Views/
│   ├── Home/
│   │   └── Index.cshtml           # Main view with map
│   ├── _Layout.cshtml             # Layout template
│   └── _ViewStart.cshtml          # View start
├── wwwroot/
│   ├── js/
│   │   ├── spaceAnalyzer.ts       # SpaceAnalyzer TypeScript class
│   │   └── mapInitializer.ts      # Map initialization script
│   └── css/
│       └── site.css               # Styles
├── Properties/
│   └── launchSettings.json        # Launch configuration
├── Program.cs                     # Application entry point
├── appsettings.json               # Configuration (Mapbox token)
├── package.json                   # Node.js dependencies
├── tsconfig.json                  # TypeScript configuration
└── Traffic_Frontend.csproj        # .NET project file
```

## Notes

- The bounding box size is in degrees (0.001 degrees ≈ 111 meters)
- The analysis uses the 'building' layer from Mapbox styles
- Empty space is inferred when building count is 0
- The map uses Mapbox Satellite style for better building visibility

