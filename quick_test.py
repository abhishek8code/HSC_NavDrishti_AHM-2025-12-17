#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8002"

# Test 1: Construction Impact Analysis
print("\n" + "="*80)
print("TEST 1: Construction Impact Analysis")
print("="*80)

payload = {
    "project_name": "Test Zone",
    "description": "Test construction zone for analysis",
    "start_date": "2025-12-17",
    "end_date": "2026-01-16",
    "zone_polygon": {
        "type": "Polygon",
        "coordinates": [[[
            [72.5700, 23.0200],
            [72.5710, 23.0200],
            [72.5710, 23.0210],
            [72.5700, 23.0210],
            [72.5700, 23.0200]
        ]]]
    },
    "analysis_center": [72.5705, 23.0205]
}

try:
    response = requests.post(f"{BASE_URL}/construction/analyze-impact", json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✓ TEST 1 PASSED - Construction impact analysis successful")
            print(f"  Project ID: {data.get('project_id')}")
        else:
            print("✗ TEST 1 FAILED - Response indicated failure")
            print(f"  Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ TEST 1 FAILED - Status {response.status_code}")
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ TEST 1 FAILED - Exception: {str(e)}")

# Test 2: Diversion Routes
print("\n" + "="*80)
print("TEST 2: Diversion Routes")
print("="*80)

payload = {
    "origin": [72.5700, 23.0200],
    "destination": [72.5800, 23.0300],
    "avoid_polygon": {
        "type": "Polygon",
        "coordinates": [[[
            [72.5700, 23.0200],
            [72.5710, 23.0200],
            [72.5710, 23.0210],
            [72.5700, 23.0210],
            [72.5700, 23.0200]
        ]]]
    }
}

try:
    response = requests.post(f"{BASE_URL}/construction/diversion-routes", json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            routes = data.get("routes", [])
            print(f"✓ TEST 2 PASSED - Found {len(routes)} diversion routes")
        else:
            print("✗ TEST 2 FAILED - Response indicated failure")
            print(f"  Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ TEST 2 FAILED - Status {response.status_code}")
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ TEST 2 FAILED - Exception: {str(e)}")

# Test 3: Isochrone
print("\n" + "="*80)
print("TEST 3: Impact Isochrone")
print("="*80)

payload = {
    "center_point": [72.5705, 23.0205],
    "time_intervals": [5, 10, 15, 20]
}

try:
    response = requests.post(f"{BASE_URL}/construction/impact-isochrone", json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            rings = len(data.get("isochrones", {}).get("features", []))
            print(f"✓ TEST 3 PASSED - Generated {rings} isochrone rings")
        else:
            print("✗ TEST 3 FAILED - Response indicated failure")
            print(f"  Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ TEST 3 FAILED - Status {response.status_code}")
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ TEST 3 FAILED - Exception: {str(e)}")

print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)
