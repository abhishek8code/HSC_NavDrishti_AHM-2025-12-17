"""
Example usage of the Damaged Roads Service

This script demonstrates how to use the FastAPI service endpoints.
Run the service first with: uvicorn main:app --reload
"""

import requests

# Base URL of the FastAPI service
BASE_URL = "http://localhost:8000"

# Example 1: Upload road network GeoJSON
def upload_road_network(geojson_path: str):
    """Upload a GeoJSON file containing road network LineStrings"""
    with open(geojson_path, 'rb') as f:
        files = {'file': (geojson_path, f, 'application/json')}
        response = requests.post(f"{BASE_URL}/upload-road-network", files=files)
        print("Road Network Upload Response:")
        print(response.json())
        return response.json()

# Example 2: Ingest damaged roads CSV
def ingest_damaged_roads(csv_path: str):
    """Upload a CSV file with damaged roads (columns: Lat, Lon, Severity)"""
    with open(csv_path, 'rb') as f:
        files = {'file': (csv_path, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/ingest-damaged-roads", files=files)
        print("\nDamaged Roads Ingestion Response:")
        print(response.json())
        return response.json()

# Example 3: Check road network status
def check_status():
    """Check the status of the loaded road network"""
    response = requests.get(f"{BASE_URL}/road-network-status")
    print("\nRoad Network Status:")
    print(response.json())
    return response.json()

if __name__ == "__main__":
    # Example usage (uncomment and provide file paths)
    # upload_road_network("road_network.geojson")
    # ingest_damaged_roads("damaged_roads.csv")
    # check_status()
    pass

