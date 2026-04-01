#!/usr/bin/env python3
"""
Backend API Testing for WhatCEM Sandbox
Testing endpoints at: https://whatcem-modernize.preview.emergentagent.com
"""

import requests
import json
import sys
from datetime import datetime

# Base URL for the backend API
BASE_URL = "https://whatcem-modernize.preview.emergentagent.com/api"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint and return result"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            print(f"❌ FAIL - Unsupported method: {method}")
            return False
            
        print(f"Status Code: {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text[:500]}...")
        
        # Consider 2xx status codes as success
        if 200 <= response.status_code < 300:
            print(f"✅ PASS - {method} {endpoint}")
            return True
        else:
            print(f"❌ FAIL - {method} {endpoint} (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL - {method} {endpoint} (Error: {str(e)})")
        return False

def main():
    """Run all backend API tests"""
    print("WhatCEM Sandbox Backend API Testing")
    print("=" * 60)
    
    results = {}
    
    # Test 1: GET /api/lead-assignment/rules
    results["GET /api/lead-assignment/rules"] = test_endpoint(
        "GET", 
        "/lead-assignment/rules",
        description="Get lead assignment rules configuration"
    )
    
    # Test 2: POST /api/lead-assignment/notifications/test (with phone)
    test_phone_data = {
        "phone": "+1234567890",
        "message": "Test notification from WhatCEM sandbox"
    }
    results["POST /api/lead-assignment/notifications/test"] = test_endpoint(
        "POST", 
        "/lead-assignment/notifications/test",
        data=test_phone_data,
        description="Test lead assignment notification with phone number"
    )
    
    # Test 3: POST /api/campaigns/ai-optimize-content
    optimize_content_data = {
        "content": "Test campaign content for optimization",
        "target_audience": "business professionals",
        "campaign_type": "whatsapp"
    }
    results["POST /api/campaigns/ai-optimize-content"] = test_endpoint(
        "POST", 
        "/campaigns/ai-optimize-content",
        data=optimize_content_data,
        description="AI optimize campaign content"
    )
    
    # Test 4a: POST /api/campaigns
    campaign_data = {
        "name": "Test Campaign",
        "content": "Test campaign message",
        "target_audience": "test users",
        "schedule_time": "2024-12-20T10:00:00Z"
    }
    results["POST /api/campaigns"] = test_endpoint(
        "POST", 
        "/campaigns",
        data=campaign_data,
        description="Create new campaign"
    )
    
    # Test 4b: POST /api/campaigns/{id}/start (using test ID)
    test_campaign_id = "test-campaign-123"
    results["POST /api/campaigns/{id}/start"] = test_endpoint(
        "POST", 
        f"/campaigns/{test_campaign_id}/start",
        data={},
        description="Start existing campaign"
    )
    
    # Test 5a: POST /api/voice-campaigns
    voice_campaign_data = {
        "name": "Test Voice Campaign",
        "script": "Hello, this is a test voice campaign message",
        "target_audience": "test users",
        "schedule_time": "2024-12-20T11:00:00Z"
    }
    results["POST /api/voice-campaigns"] = test_endpoint(
        "POST", 
        "/voice-campaigns",
        data=voice_campaign_data,
        description="Create new voice campaign"
    )
    
    # Test 5b: POST /api/voice-campaigns/{id}/start (using test ID)
    test_voice_campaign_id = "test-voice-campaign-123"
    results["POST /api/voice-campaigns/{id}/start"] = test_endpoint(
        "POST", 
        f"/voice-campaigns/{test_voice_campaign_id}/start",
        data={},
        description="Start existing voice campaign"
    )
    
    # Test 6a: GET /api/campaigns/stats
    results["GET /api/campaigns/stats"] = test_endpoint(
        "GET", 
        "/campaigns/stats",
        description="Get campaign statistics"
    )
    
    # Test 6b: GET /api/voice-campaigns/stats
    results["GET /api/voice-campaigns/stats"] = test_endpoint(
        "GET", 
        "/voice-campaigns/stats",
        description="Get voice campaign statistics"
    )
    
    # Test 6c: GET /api/analytics/overview
    results["GET /api/analytics/overview"] = test_endpoint(
        "GET", 
        "/analytics/overview",
        description="Get analytics overview"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for endpoint, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {endpoint}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)