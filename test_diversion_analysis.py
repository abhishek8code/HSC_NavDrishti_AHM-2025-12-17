#!/usr/bin/env python3

"""
Test script for Diversion Analysis Backend
Tests construction zone analysis and diversion route calculation
"""

import requests
import json
from datetime import date, timedelta
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Backend configuration
BACKEND_URL = "http://localhost:8002"

# Test data - Construction zone polygon (GeoJSON)
CONSTRUCTION_ZONE_POLYGON = {
    "type": "Polygon",
    "coordinates": [[
        [72.5700, 23.0200],
        [72.5750, 23.0200],
        [72.5750, 23.0250],
        [72.5700, 23.0250],
        [72.5700, 23.0200]
    ]]
}

# Test data - Analysis center point
ANALYSIS_CENTER = [72.5725, 23.0225]

# Test data - Origin and destination for diversion routes
ORIGIN = [72.5700, 23.0200]
DESTINATION = [72.5800, 23.0300]

def test_analyze_construction_impact():
    """Test the construction impact analysis endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Construction Impact Analysis")
    print("="*80)
    
    payload = {
        "project_name": "Emergency Construction - Test Zone",
        "description": "Test construction zone for diversion analysis",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "zone_polygon": CONSTRUCTION_ZONE_POLYGON,
        "analysis_center": ANALYSIS_CENTER
    }
    
    print("\n📤 Sending request to /construction/analyze-impact")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/construction/analyze-impact",
            json=payload,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS - Impact Analysis Response:")
            print(json.dumps(data, indent=2))
            
            # Extract key information
            if data.get("success"):
                project_id = data.get("project_id")
                print(f"\n✓ Project ID: {project_id}")
                print(f"✓ Analysis Status: {data.get('status')}")
                
                if data.get("impact_analysis"):
                    print(f"✓ Isochrone Data Received: Yes")
                    isochrones = data.get("impact_analysis", {}).get("isochrones", {})
                    if isochrones:
                        features = isochrones.get("features", [])
                        print(f"✓ Number of Isochrone Rings: {len(features)}")
                        for i, feature in enumerate(features):
                            props = feature.get("properties", {})
                            print(f"  - Ring {i+1}: {props.get('contour')} min travel time")
                
                return True
        else:
            print(f"\n❌ ERROR - {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False


def test_calculate_diversion_routes():
    """Test the diversion routes calculation endpoint"""
    print("\n" + "="*80)
    print("TEST 2: Calculate Diversion Routes")
    print("="*80)
    
    payload = {
        "origin": ORIGIN,
        "destination": DESTINATION,
        "avoid_polygon": CONSTRUCTION_ZONE_POLYGON
    }
    
    print("\n📤 Sending request to /construction/diversion-routes")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/construction/diversion-routes",
            json=payload,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS - Diversion Routes Response:")
            print(json.dumps(data, indent=2))
            
            # Extract key information
            if data.get("success"):
                routes = data.get("routes", [])
                print(f"\n✓ Total Routes Found: {len(routes)}")
                
                for i, route in enumerate(routes):
                    print(f"\n  Route {i+1}:")
                    print(f"    - Distance: {route.get('distance_km', 'N/A')} km")
                    print(f"    - Duration: {route.get('duration_minutes', 'N/A')} min")
                    print(f"    - Turn Count: {route.get('turn_count', 'N/A')}")
                    print(f"    - Road Classes: {', '.join(route.get('road_classes', []))}")
                
                analysis = data.get("analysis", {})
                print(f"\n✓ Fastest Route: {analysis.get('fastest_route_id')}")
                print(f"✓ Shortest Route: {analysis.get('shortest_route_id')}")
                
                return True
        else:
            print(f"\n❌ ERROR - {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False


def test_impact_isochrone():
    """Test the isochrone impact calculation endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Impact Isochrone Calculation")
    print("="*80)
    
    payload = {
        "center_point": ANALYSIS_CENTER,
        "time_intervals": [5, 10, 15, 20]
    }
    
    print("\n📤 Sending request to /construction/impact-isochrone")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/construction/impact-isochrone",
            json=payload,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            if data.get("success"):
                isochrones = data.get("isochrones", {})
                features = isochrones.get("features", [])
                
                print(f"\n✅ SUCCESS - Isochrone Response:")
                print(f"✓ Total Isochrone Rings: {len(features)}")
                
                for i, feature in enumerate(features):
                    props = feature.get("properties", {})
                    geom = feature.get("geometry", {})
                    coords_count = len(geom.get("coordinates", [[]])[0]) if geom.get("type") == "Polygon" else 0
                    
                    print(f"\n  Isochrone {i+1}:")
                    print(f"    - Time Contour: {props.get('contour')} minutes")
                    print(f"    - Geometry Type: {geom.get('type')}")
                    print(f"    - Polygon Points: {coords_count}")
                
                return True
            else:
                print(f"\n⚠️  Partial Response:")
                print(json.dumps(data, indent=2))
                return False
        else:
            print(f"\n❌ ERROR - {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False


def test_backend_health():
    """Test backend health endpoint"""
    print("\n" + "="*80)
    print("TEST 0: Backend Health Check")
    print("="*80)
    
    print(f"\n📤 Checking backend at {BACKEND_URL}/health")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=10
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend is ONLINE and responding")
            return True
        else:
            print(f"⚠️  Backend returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend is OFFLINE: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "DIVERSION ANALYSIS BACKEND TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Test 0: Health check
    if not test_backend_health():
        print("\n⛔ Backend is not running! Start the backend first with: python -m uvicorn main:app --reload --port 8002")
        return
    
    # Test 1: Construction impact analysis
    test1_pass = test_analyze_construction_impact()
    
    # Test 2: Diversion routes calculation
    test2_pass = test_calculate_diversion_routes()
    
    # Test 3: Isochrone impact
    test3_pass = test_impact_isochrone()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Test 1 (Impact Analysis): {'PASS ✅' if test1_pass else 'FAIL ❌'}")
    print(f"✓ Test 2 (Diversion Routes): {'PASS ✅' if test2_pass else 'FAIL ❌'}")
    print(f"✓ Test 3 (Isochrone): {'PASS ✅' if test3_pass else 'FAIL ❌'}")
    
    total_pass = sum([test1_pass, test2_pass, test3_pass])
    print(f"\nTotal: {total_pass}/3 tests passed")
    
    if total_pass == 3:
        print("\n🎉 All tests PASSED! Diversion Analysis is working correctly.")
    else:
        print(f"\n⚠️  {3 - total_pass} test(s) failed. Check the output above for details.")


if __name__ == "__main__":
    main()
