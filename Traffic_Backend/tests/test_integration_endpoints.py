import requests
import os


BASE = os.getenv('BACKEND_TEST_URL', 'http://127.0.0.1:8001')


def test_recommend_endpoint():
    payload = {
        'start_lat': 23.0225,
        'start_lon': 72.5714,
        'end_lat': 23.035,
        'end_lon': 72.58,
        'waypoints': []
    }
    r = requests.post(f"{BASE}/routes/recommend", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert 'routes' in data
    assert isinstance(data['routes'], list)
    assert len(data['routes']) >= 1


def test_analyze_endpoint():
    payload = {
        'start_lat': 23.0225,
        'start_lon': 72.5714,
        'end_lat': 23.035,
        'end_lon': 72.58,
        'waypoints': []
    }
    r = requests.post(f"{BASE}/routes/analyze", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Basic shape checks
    assert 'distance_km' in data
    assert 'road_properties' in data
    assert 'traffic_counts' in data


def test_projects_dev_create_and_list():
    payload = {
        'name': 'pytest dev project',
        'status': 'planned',
        'start_lat': 23.0225,
        'start_lon': 72.5714,
        'end_lat': 23.035,
        'end_lon': 72.58
    }
    r = requests.post(f"{BASE}/projects/dev-create", json=payload, timeout=5)
    assert r.status_code == 201
    created = r.json()
    assert 'id' in created

    # Now list projects and ensure created project is present by name
    r2 = requests.get(f"{BASE}/projects/", timeout=5)
    assert r2.status_code == 200
    projects = r2.json()
    names = [p.get('name') for p in projects]
    assert 'pytest dev project' in names
