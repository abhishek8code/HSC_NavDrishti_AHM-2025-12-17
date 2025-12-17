# Test script for updated /routes/recommend endpoint
# This script tests the integration of mapbox_service.py with routes.py

import requests
import json

# Test coordinates (Ahmedabad, Gujarat)
test_payload = {
    "start_lat": 23.0225,
    "start_lon": 72.5714,
    "end_lat": 23.035,
    "end_lon": 72.58,
    "waypoints": []
}

print("=" * 60)
print("Testing /routes/recommend endpoint")
print("=" * 60)
print(f"\nRequest payload:")
print(json.dumps(test_payload, indent=2))

try:
    # Call the endpoint
    response = requests.post(
        "http://localhost:8002/routes/recommend",
        json=test_payload,
        timeout=15
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\nSuccess! Retrieved {len(data.get('routes', []))} routes")
        
        for route in data.get('routes', []):
            print(f"\n  Route: {route.get('name', 'Unknown')}")
            print(f"    ID: {route.get('id')}")
            print(f"    Distance: {route.get('distance_km')} km")
            print(f"    Travel Time: {route.get('travel_time_min')} min")
            print(f"    Traffic Score: {route.get('traffic_score')}")
            print(f"    Emissions: {route.get('emission_g')} g CO₂")
            print(f"    Rank: {route.get('rank')}")
            print(f"    Coordinates: {len(route.get('coordinates', []))} points")
            
            # Check if this is real Mapbox data or mock
            route_id = route.get('id', '')
            if route_id.startswith('mapbox-'):
                print(f"    ✅ REAL MAPBOX DATA")
            elif route_id.startswith('mock-'):
                print(f"    ⚠️  MOCK DATA (Mapbox unavailable)")
        
        # Summary
        print(f"\n{'='*60}")
        route_ids = [r.get('id', '') for r in data.get('routes', [])]
        if all(rid.startswith('mapbox-') for rid in route_ids):
            print("✅ SUCCESS: Using real Mapbox Directions API via mapbox_service.py")
        elif all(rid.startswith('mock-') for rid in route_ids):
            print("⚠️  WARNING: Using mock data (check MAPBOX_ACCESS_TOKEN)")
        else:
            print("⚠️  WARNING: Mixed data sources")
        print(f"{'='*60}")
        
    else:
        print(f"\nError Response:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend at http://localhost:8002")
    print("   Make sure the backend is running!")
    
except requests.exceptions.Timeout:
    print("\n❌ ERROR: Request timed out")
    print("   Mapbox API may be slow or unavailable")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
