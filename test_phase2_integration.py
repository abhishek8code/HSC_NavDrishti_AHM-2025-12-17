#!/usr/bin/env python3
"""
Phase 2 Integration Test Script
Tests end-to-end connectivity between frontend and backend
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5000"
TIMEOUT = 5

# Auth token (will be set after login)
AUTH_TOKEN = None

def get_auth_token():
    """Get or create an admin user and return auth token"""
    global AUTH_TOKEN
    
    if AUTH_TOKEN:
        return AUTH_TOKEN
    
    # Try to register a test admin user
    test_user = {
        "username": "testadmin",
        "password": "testpass123",
        "email": "admin@test.com"
    }
    
    try:
        # Try to register (will fail if user exists, which is fine)
        requests.post(f"{BACKEND_URL}/register", json=test_user, timeout=TIMEOUT)
    except:
        pass
    
    # Login to get token
    try:
        response = requests.post(
            f"{BACKEND_URL}/token",
            data={"username": test_user["username"], "password": test_user["password"]},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            AUTH_TOKEN = response.json()["access_token"]
            return AUTH_TOKEN
    except Exception as e:
        print(f"⚠️  Warning: Could not get auth token: {e}")
    
    return None

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_backend_connectivity():
    """Test 1: Backend is reachable"""
    print_section("TEST 1: Backend Connectivity")
    try:
        response = requests.get(f"{BACKEND_URL}/projects/", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Backend is running and reachable")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_connectivity():
    """Test 2: Frontend is reachable"""
    print_section("TEST 2: Frontend Connectivity")
    try:
        response = requests.get(f"{FRONTEND_URL}/Home/Dashboard", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Frontend is running and reachable")
            return True
        else:
            print(f"❌ Frontend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_backend_projects_endpoint():
    """Test 3: Backend projects endpoint"""
    print_section("TEST 3: Backend Projects Endpoint")
    try:
        response = requests.get(f"{BACKEND_URL}/projects/", timeout=TIMEOUT)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ GET /projects/ returned {len(projects)} projects")
            if projects:
                print(f"   Sample project: {projects[0]}")
            return True
        else:
            print(f"❌ GET /projects/ returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend projects endpoint failed: {e}")
        return False

def test_create_project():
    """Test 4: Create a test project"""
    print_section("TEST 4: Create Test Project")
    
    test_project = {
        "name": f"Integration Test {int(time.time())}",
        "status": "planned"
    }
    
    try:
        # Get auth token
        token = get_auth_token()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Test via backend directly
        response = requests.post(
            f"{BACKEND_URL}/projects/",
            json=test_project,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            created_project = response.json()
            print(f"✅ Project created successfully")
            print(f"   ID: {created_project.get('id')}")
            print(f"   Name: {created_project.get('name')}")
            print(f"   Status: {created_project.get('status')}")
            return True, created_project.get('id')
        else:
            print(f"❌ Create project returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create project failed: {e}")
        return False, None

def test_frontend_projects_api():
    """Test 5: Frontend projects API endpoint"""
    print_section("TEST 5: Frontend Projects API Endpoint")
    try:
        response = requests.get(f"{FRONTEND_URL}/api/projects", timeout=TIMEOUT)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Frontend /api/projects returned {len(projects)} projects")
            return True
        else:
            print(f"❌ Frontend /api/projects returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend projects API failed: {e}")
        return False

def test_create_project_via_frontend():
    """Test 6: Create project through frontend API"""
    print_section("TEST 6: Create Project via Frontend API")
    
    test_project = {
        "name": f"Frontend Test {int(time.time())}",
        "status": "active"
    }
    
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/projects",
            json=test_project,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            created_project = response.json()
            print(f"✅ Project created via frontend API")
            print(f"   ID: {created_project.get('id')}")
            print(f"   Name: {created_project.get('name')}")
            return True, created_project.get('id')
        else:
            print(f"❌ Frontend create project returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Frontend create project failed: {e}")
        return False, None

def test_api_controllers():
    """Test 7: Frontend API controllers exist"""
    print_section("TEST 7: API Controllers Accessibility")
    
    endpoints = [
        "/api/projects",
        "/api/routes/analyze",
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            if endpoint == "/api/projects":
                response = requests.get(f"{FRONTEND_URL}{endpoint}", timeout=TIMEOUT)
            else:
                # POST endpoints return 405 GET
                response = requests.post(f"{FRONTEND_URL}{endpoint}", json={}, timeout=TIMEOUT)
            
            if response.status_code in [200, 201, 405, 400]:
                print(f"✅ {endpoint} is accessible")
            else:
                print(f"❌ {endpoint} returned {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
            all_ok = False
    
    return all_ok

def run_all_tests():
    """Run all tests"""
    print(f"\n{'#'*60}")
    print(f"#  NAVDRISHTI PHASE 2 INTEGRATION TEST SUITE")
    print(f"#  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    results = {
        "Backend Connectivity": test_backend_connectivity(),
        "Frontend Connectivity": test_frontend_connectivity(),
        "Backend Projects Endpoint": test_backend_projects_endpoint(),
        "Frontend Projects API": test_frontend_projects_api(),
        "API Controllers": test_api_controllers(),
    }
    
    # Create project tests
    backend_success, backend_id = test_create_project()
    results["Create Project (Backend)"] = backend_success
    
    frontend_success, frontend_id = test_create_project_via_frontend()
    results["Create Project (Frontend)"] = frontend_success
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} — {test_name}")
    
    print(f"\n{'─'*60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. See details above.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
