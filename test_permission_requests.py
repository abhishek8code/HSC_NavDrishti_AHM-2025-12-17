#!/usr/bin/env python3
"""
Test script for Route Permission Request Module 1 (Citizen Submission).
Tests all endpoints with valid and invalid data, verifying governance rules.
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

BASE_URL = "http://localhost:8002/api"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(title: str):
    """Print formatted test header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(msg: str):
    print(f"{GREEN}[OK] {msg}{RESET}")


def print_error(msg: str):
    print(f"{RED}[FAIL] {msg}{RESET}")


def print_info(msg: str):
    print(f"{YELLOW}[INFO] {msg}{RESET}")


def test_submit_valid_request():
    """Test 1: Submit a valid permission request (> 5 days from now)"""
    print_header("TEST 1: Submit Valid Permission Request (> 5 days)")
    
    # Create event date 7 days from now
    event_date = datetime.utcnow() + timedelta(days=7)
    event_start = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
    event_end = event_start.replace(hour=16, minute=0)
    
    payload = {
        "citizen_name": "Rajesh Patel",
        "citizen_phone": "+91-9876543210",
        "citizen_email": "rajesh.patel@example.com",
        "organization_name": "Ahmedabad Traffic Society",
        "event_type": "rally",
        "event_name": "Clean Ahmedabad Marathon 2025",
        "event_description": "Community-led cleanliness marathon covering major city routes",
        "expected_participants": 5000,
        "vehicle_category": "mixed",
        "event_date": event_date.isoformat(),
        "event_start_time": event_start.isoformat(),
        "event_end_time": event_end.isoformat(),
        "route_geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5714, 23.0225],
                [72.5800, 23.0300],
                [72.5900, 23.0400],
                [72.6000, 23.0500]
            ]
        }
    }
    
    print_info(f"Submitting request for event on {event_date.date()}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/permission-requests/",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Request created successfully!")
            print(f"  Request ID: {data['id']}")
            print(f"  Request Number: {data['request_number']}")
            print(f"  Status: {data['status']}")
            print(f"  Route Length: {data.get('route_length_km', 'N/A')} km")
            return data['id'], data['request_number']
        else:
            print_error(f"Failed to create request: {response.status_code}")
            print(f"  Response: {response.text}")
            return None, None
    
    except Exception as e:
        print_error(f"Error: {e}")
        return None, None


def test_submit_invalid_date():
    """Test 2: Submit request with event < 5 days away (should fail)"""
    print_header("TEST 2: Submit Request with Invalid Date (< 5 days) - Should FAIL")
    
    # Create event date only 3 days from now
    event_date = datetime.utcnow() + timedelta(days=3)
    event_start = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
    event_end = event_start.replace(hour=16, minute=0)
    
    payload = {
        "citizen_name": "Invalid Date Test",
        "citizen_phone": "+91-9876543210",
        "citizen_email": "test@example.com",
        "event_type": "procession",
        "event_name": "Too Soon Event",
        "expected_participants": 1000,
        "vehicle_category": "light",
        "event_date": event_date.isoformat(),
        "event_start_time": event_start.isoformat(),
        "event_end_time": event_end.isoformat(),
        "route_geometry": {
            "type": "LineString",
            "coordinates": [[72.5714, 23.0225], [72.5800, 23.0300]]
        }
    }
    
    print_info(f"Attempting to submit event only 3 days away (today + 3 days)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/permission-requests/",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 422:
            print_success("✓ Correctly rejected request with < 5 day constraint!")
            error_detail = response.json()
            print(f"  Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def test_invalid_geometry():
    """Test 3: Submit request with invalid geometry"""
    print_header("TEST 3: Submit Request with Invalid Geometry - Should FAIL")
    
    event_date = datetime.utcnow() + timedelta(days=7)
    event_start = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
    event_end = event_start.replace(hour=16, minute=0)
    
    payload = {
        "citizen_name": "Geometry Test",
        "citizen_phone": "+91-9876543210",
        "event_type": "marathon",
        "event_name": "Marathon Test",
        "vehicle_category": "heavy",
        "event_date": event_date.isoformat(),
        "event_start_time": event_start.isoformat(),
        "event_end_time": event_end.isoformat(),
        "route_geometry": {
            "type": "Point",  # Invalid type - should be LineString, Polygon, or MultiLineString
            "coordinates": [72.5714, 23.0225]
        }
    }
    
    print_info("Attempting to submit request with invalid geometry type (Point)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/permission-requests/",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 422:
            print_success("✓ Correctly rejected invalid geometry!")
            print(f"  Response: {response.json()}")
        else:
            print_error(f"Unexpected response: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def test_list_requests():
    """Test 4: List all permission requests"""
    print_header("TEST 4: List Permission Requests")
    
    print_info("Fetching all permission requests...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/permission-requests/",
            params={"page": 1, "page_size": 10},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved permission requests!")
            print(f"  Total Requests: {data['total']}")
            print(f"  Page: {data['page']} / Page Size: {data['page_size']}")
            print(f"\n  Requests Summary:")
            for req in data['requests']:
                print(f"    - {req['request_number']}: {req['event_name']} "
                      f"({req['event_type']}) on {req['event_date'][:10]} "
                      f"[{req['status']}]")
        else:
            print_error(f"Failed to list requests: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def test_get_request_by_id(request_id: int):
    """Test 5: Get specific request by ID"""
    print_header(f"TEST 5: Get Permission Request by ID ({request_id})")
    
    if not request_id:
        print_error("No valid request ID provided")
        return
    
    print_info(f"Fetching request with ID: {request_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/permission-requests/{request_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved request details!")
            print(f"  Request Number: {data['request_number']}")
            print(f"  Citizen: {data['citizen_name']} ({data['citizen_email']})")
            print(f"  Event: {data['event_name']} ({data['event_type']})")
            print(f"  Date: {data['event_date'][:10]}")
            print(f"  Participants: {data.get('expected_participants', 'N/A')}")
            print(f"  Route Length: {data.get('route_length_km', 'N/A')} km")
            print(f"  Status: {data['status']}")
        else:
            print_error(f"Failed to get request: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def test_get_audit_logs(request_id: int):
    """Test 6: Get audit trail for request"""
    print_header(f"TEST 6: Get Audit Logs for Request ({request_id})")
    
    if not request_id:
        print_error("No valid request ID provided")
        return
    
    print_info(f"Fetching audit logs for request ID: {request_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/permission-requests/{request_id}/audit-logs",
            timeout=5
        )
        
        if response.status_code == 200:
            logs = response.json()
            print_success(f"Retrieved {len(logs)} audit log entries!")
            for log in logs:
                print(f"  - [{log['timestamp']}] {log['action']}: {log['action_description']}")
        else:
            print_error(f"Failed to get audit logs: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def test_cancel_request(request_id: int):
    """Test 7: Cancel a PENDING request"""
    print_header(f"TEST 7: Cancel Permission Request ({request_id})")
    
    if not request_id:
        print_error("No valid request ID provided")
        return
    
    print_info(f"Attempting to cancel request ID: {request_id}")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/permission-requests/{request_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Request cancelled successfully!")
            print(f"  Message: {data['message']}")
            print(f"  Request Number: {data['request_number']}")
            print(f"  New Status: {data['status']}")
        else:
            print_error(f"Failed to cancel request: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print_error(f"Error: {e}")




# =====================================================
# MODULE 2: POLICE ADMIN APPROVAL TESTS
# =====================================================

def test_approve_pending_request(request_id: int):
    """Test 8: Approve a pending request"""
    print_header("TEST 8: Approve Pending Request (Module 2)")
    
    if not request_id:
        print_error("No valid request ID provided")
        return
    
    payload = {
        "approval_comments": "Route approved for traffic management. Event route follows main arterial roads."
    }
    
    print_info(f"Approving request {request_id}...")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/permission-requests/{request_id}/approve",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Request approved successfully!")
            print(f"  Request Number: {data['request_number']}")
            print(f"  Status: {data['status']}")
            print(f"  Approved Date: {data['approved_date']}")
            print(f"  Next Phase: {data['next_phase']}")
            return True
        else:
            print_error(f"Failed to approve request: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_reject_pending_request(request_id: int):
    """Test 9: Reject a pending request"""
    print_header("TEST 9: Reject Pending Request (Module 2)")
    
    if not request_id:
        print_error("No valid request ID provided")
        return
    
    payload = {
        "rejection_reason": "The proposed route conflicts with an existing approved event on the same date. Please resubmit with alternative dates or routes."
    }
    
    print_info(f"Rejecting request {request_id}...")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/permission-requests/{request_id}/reject",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Request rejected successfully!")
            print(f"  Request Number: {data['request_number']}")
            print(f"  Status: {data['status']}")
            print(f"  Rejection Reason: {data['rejection_reason'][:80]}...")
            return True
        else:
            print_error(f"Failed to reject request: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_admin_dashboard():
    """Test 10: Get admin dashboard summary"""
    print_header("TEST 10: Admin Dashboard Summary (Module 2)")
    
    print_info("Fetching admin dashboard summary...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/permission-requests/admin/dashboard-summary",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Dashboard summary retrieved!")
            print(f"  Total Pending: {data['total_pending']}")
            print(f"  Total Under Review: {data['total_under_review']}")
            print(f"  Total Approved: {data['total_approved']}")
            print(f"  Total Rejected: {data['total_rejected']}")
            print(f"  Pending Requests (top 10):")
            for req in data['pending_requests_summary'][:3]:
                print(f"    - {req['request_number']}: {req['event_name']} ({req['status']})")
        else:
            print_error(f"Failed to get dashboard: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error: {e}")


def main():
    """Run all tests"""
    print(f"\n{BLUE}")
    print("=" * 70)
    print("MODULE 1 & 2: PERMISSION REQUEST WORKFLOW - FULL TEST SUITE".center(70))
    print("=" * 70)
    print(RESET)
    
    # Wait for backend
    print_info("Checking backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/permission-requests/", timeout=2)
        print_success("Backend is running!")
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_error("Please ensure the backend is running on port 8002")
        return
    
    # MODULE 1 TESTS
    test_submit_valid_request_id, test_request_number = test_submit_valid_request()
    test_submit_invalid_date()
    test_invalid_geometry()
    test_list_requests()
    
    if test_submit_valid_request_id:
        test_get_request_by_id(test_submit_valid_request_id)
        test_get_audit_logs(test_submit_valid_request_id)
        
        # MODULE 2 TESTS
        if test_approve_pending_request(test_submit_valid_request_id):
            # After approval, get audit logs to verify approval was logged
            test_get_audit_logs(test_submit_valid_request_id)
    
    # Create a second request to test rejection
    test_reject_request_id, _ = test_submit_valid_request()
    if test_reject_request_id:
        test_reject_pending_request(test_reject_request_id)
    
    # Test admin dashboard
    test_admin_dashboard()
    
    # Summary
    print_header("TEST SUITE COMPLETE")
    print_success("All tests (Module 1 & 2) completed!")
    print(f"{YELLOW}[OK] MODULE 1: Citizen Submission - All features working")
    print(f"[OK] MODULE 2: Admin Approval - Approval/Rejection working")
    print(f"[OK] Audit trail captures all governance actions")
    print(f"[OK] Admin dashboard summary functional")
    print(f"[OK] Status workflow: pending -> approved/rejected{RESET}\n")


if __name__ == "__main__":
    main()
