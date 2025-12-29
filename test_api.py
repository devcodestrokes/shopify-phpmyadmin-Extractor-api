"""
Test script for Shopify Data API
Tests all endpoints to verify functionality
"""

import requests
import json
import time
import sys
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
API_URL = "http://localhost:5000"  # Change to your deployed URL
API_KEY = "shopify_secure_key_2025"

headers = {
    "X-API-Key": API_KEY
}

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health():
    """Test /health endpoint"""
    print_section("Testing /health endpoint (no auth required)")
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print("❌ Health check failed!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_status():
    """Test /status endpoint"""
    print_section("Testing /status endpoint")
    
    try:
        response = requests.get(f"{API_URL}/status", headers=headers)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Status check passed!")
            
            if data.get('cache_exists'):
                print(f"📦 Cache exists (age: {data.get('cache_age_minutes')} minutes)")
            else:
                print("⚠️ No cache available yet")
        else:
            print("❌ Status check failed!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_fetch_data_simple():
    """Test /fetch-data endpoint (simple mode)"""
    print_section("Testing /fetch-data (cached only)")
    
    try:
        response = requests.get(f"{API_URL}/fetch-data", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Record Count: {data.get('count')}")
            print(f"Last Updated: {data.get('last_updated')}")
            print("✅ Fetch data passed!")
            
            # Show first 2 records as sample
            if data.get('data'):
                print(f"\nSample data (first 2 records):")
                print(json.dumps(data['data'][:2], indent=2))
        elif response.status_code == 503:
            print("⚠️ No cached data available yet")
            print(f"Message: {response.json().get('message')}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_fetch_data_refresh():
    """Test /fetch-data with refresh parameter"""
    print_section("Testing /fetch-data?refresh=true")
    
    try:
        response = requests.get(
            f"{API_URL}/fetch-data?refresh=true", 
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Record Count: {data.get('count')}")
            
            if '_info' in data:
                print(f"Info: {data['_info']}")
            
            print("✅ Fetch with refresh passed!")
            print("📝 Note: Background refresh triggered. Wait 2-5 minutes for fresh data.")
        elif response.status_code == 503:
            print("⚠️ No cached data available yet")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_manual_refresh():
    """Test /refresh endpoint"""
    print_section("Testing POST /refresh")
    
    try:
        response = requests.post(f"{API_URL}/refresh", headers=headers)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 202:
            print("✅ Manual refresh triggered!")
        elif response.status_code == 202 and 'in_progress' in data.get('status', ''):
            print("⚠️ Refresh already in progress")
        else:
            print(f"❌ Unexpected response")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_unauthorized():
    """Test authentication failure"""
    print_section("Testing authentication (should fail)")
    
    try:
        bad_headers = {"X-API-Key": "wrong_key"}
        response = requests.get(f"{API_URL}/fetch-data", headers=bad_headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized request!")
        else:
            print(f"❌ Should have returned 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_stream_sse():
    """Test SSE streaming (basic connectivity test)"""
    print_section("Testing /fetch-data?stream=true (SSE)")
    
    print("⚠️ SSE streaming test requires special handling.")
    print("For full SSE testing, use the demo.html page or a specialized SSE client.")
    print("Basic connectivity test:")
    
    try:
        response = requests.get(
            f"{API_URL}/fetch-data?stream=true&refresh=true",
            headers=headers,
            stream=True,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.headers.get('Content-Type') == 'text/event-stream':
            print("✅ SSE endpoint is accessible!")
            print("Reading first few events...")
            
            count = 0
            for line in response.iter_lines():
                if line:
                    print(line.decode('utf-8'))
                    count += 1
                    if count >= 5:  # Read first 5 lines only
                        print("... (stopping after 5 lines)")
                        break
        else:
            print("❌ SSE not configured correctly")
            
        response.close()
    except requests.exceptions.Timeout:
        print("⏱️ Timeout (expected for SSE streams)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*60)
    print("#  Shopify Data API - Test Suite")
    print("#  Target: " + API_URL)
    print("#"*60)
    
    # Test 1: Health check
    test_health()
    time.sleep(1)
    
    # Test 2: Authentication failure
    test_unauthorized()
    time.sleep(1)
    
    # Test 3: Status check
    test_status()
    time.sleep(1)
    
    # Test 4: Simple fetch
    test_fetch_data_simple()
    time.sleep(1)
    
    # Test 5: Fetch with refresh
    test_fetch_data_refresh()
    time.sleep(1)
    
    # Test 6: Manual refresh
    test_manual_refresh()
    time.sleep(1)
    
    # Test 7: SSE streaming
    test_stream_sse()
    
    # Summary
    print("\n" + "#"*60)
    print("#  Test Suite Complete!")
    print("#"*60)
    print("\n📝 Next Steps:")
    print("1. Open demo.html in your browser for interactive testing")
    print("2. Test SSE streaming using the demo page")
    print("3. Monitor /status endpoint to see cache age")
    print("4. Deploy to Render and update API_URL in this script")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
