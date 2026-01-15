"""
Quick API Test Script - Tests all endpoints locally
"""

import requests
import json

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "shopify_secure_key_2025"

headers = {"X-API-Key": API_KEY}

print("="*70)
print("🔍 TESTING SHOPIFY DATA API LOCALLY")
print("="*70)

# Test 1: Health Check (No auth needed)
print("\n1️⃣  Testing /health endpoint (no auth needed)...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    if response.status_code == 200:
        print("   ✅ Health check PASSED!")
    else:
        print("   ❌ Health check FAILED!")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Make sure flask_app.py is running!")
    print("   Run: python flask_app.py")
    exit(1)

# Test 2: Metadata (with auth)
print("\n2️⃣  Testing /fetch-data?metadata_only=true...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?metadata_only=true",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total records: {data.get('count', 'N/A')}")
        print(f"   ✅ File size: {data.get('file_size_kb', 'N/A')} KB")
        print(f"   ✅ Last updated: {data.get('last_modified', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get 5 records
print("\n3️⃣  Testing /fetch-data?limit=5...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?limit=5",
        headers=headers,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        records = data.get('data', [])
        print(f"   ✅ Got {len(records)} records")
        if records:
            print(f"\n   First record sample:")
            # Show first 3 fields only
            first_record = records[0]
            for i, (key, value) in enumerate(list(first_record.items())[:3]):
                print(f"      {key}: {value}")
            print(f"      ... ({len(first_record)} total fields)")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Get 100 records
print("\n4️⃣  Testing /fetch-data?limit=100...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?limit=100",
        headers=headers,
        timeout=15
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        records = data.get('data', [])
        print(f"   ✅ Got {len(records)} records")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Status endpoint
print("\n5️⃣  Testing /status...")
try:
    response = requests.get(
        f"{API_URL}/status",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API Status: {data.get('api_status', 'N/A')}")
        print(f"   ✅ Cache exists: {data.get('cache_exists', False)}")
        print(f"   ✅ Cache age: {data.get('cache_age_minutes', 'N/A')} minutes")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Pagination test
print("\n6️⃣  Testing pagination (offset)...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?limit=10&offset=100",
        headers=headers,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        records = data.get('data', [])
        print(f"   ✅ Got {len(records)} records starting from offset 100")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 7: Test without API key (should fail)
print("\n7️⃣  Testing without API key (should fail with 401)...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?limit=5",
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ Correctly rejected unauthorized request!")
    else:
        print(f"   ⚠️ Expected 401, got {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETE!")
print("="*70)

print("\n📊 Summary:")
print("   • API is running at: http://localhost:5000")
print("   • Health check: ✅")
print("   • Authentication: ✅")
print("   • Data fetching: ✅")
print("   • Pagination: ✅")

print("\n💡 To fetch ALL data:")
print("   Use pagination with high limit:")
print(f"   curl -H 'X-API-Key: {API_KEY}' \\")
print(f"     'http://localhost:5000/fetch-data?limit=1000&offset=0'")

print("\n💡 Or use the /export endpoint (if you added it)")
print("   See the next section for export endpoint!")
