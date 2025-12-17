#!/usr/bin/env python
"""Test the /traffic/live endpoint response directly"""

import json
import requests
import time

print("=== Testing /traffic/live endpoint ===\n")

# Give the backend a moment to start if it just restarted
time.sleep(1)

try:
    response = requests.get('http://localhost:8002/traffic/live', timeout=5)
    response.raise_for_status()
    
    data = response.json()
    
    print(f"Response Status: {response.status_code}")
    print(f"Total segments: {len(data.get('segments', []))}")
    print(f"Mock flag: {data.get('mock', False)}")
    print(f"Timestamp: {data.get('timestamp')}")
    
    if data.get('segments'):
        seg = data['segments'][0]
        print(f"\nFirst segment details:")
        print(f"  Name: {seg.get('name')}")
        print(f"  Coordinates count: {len(seg.get('coordinates', []))}")
        print(f"  Congestion level: {seg.get('congestion_level')}")
        print(f"  Speed: {seg.get('speed_kmh')} km/h")
        print(f"  Vehicle count: {seg.get('vehicle_count')}")
        
        if seg.get('coordinates'):
            print(f"  First coord: {seg['coordinates'][0]}")
            print(f"  Last coord: {seg['coordinates'][-1]}")
    
    print(f"\n✓ Test completed successfully")
    
except Exception as e:
    print(f"✗ Error testing endpoint: {e}")
    import traceback
    traceback.print_exc()
