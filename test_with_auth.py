"""
Simple API Tester - Shows how to use the API correctly
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "shopify_secure_key_2025"

# Headers (REQUIRED for authentication)
headers = {
    "X-API-Key": API_KEY
}

print("=" * 60)
print("Shopify Data API - Quick Tester")
print("=" * 60)

# Test 1: Get cached data (fast)
print("\n1️⃣  Testing CACHED data (fast)...")
try:
    start = time.time()
    response = requests.get(
        f"{API_URL}/fetch-data?limit=5&offset=0",
        headers=headers
    )
    elapsed = time.time() - start
    
    print(f"   Status: {response.status_code}")
    print(f"   Time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Got {len(data.get('data', []))} records")
        print(f"   First record: {json.dumps(data['data'][0], indent=2)[:200]}...")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Get metadata (super fast)
print("\n2️⃣  Testing METADATA (super fast)...")
try:
    start = time.time()
    response = requests.get(
        f"{API_URL}/fetch-data?metadata_only=true",
        headers=headers
    )
    elapsed = time.time() - start
    
    print(f"   Status: {response.status_code}")
    print(f"   Time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"   Total records: {data.get('count')}")
        print(f"   File size: {data.get('file_size_kb')} KB")
        print(f"   Last updated: {data.get('last_modified')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get LIVE data (slow but fresh)
print("\n3️⃣  Testing LIVE DATA (takes 30-60 seconds)...")
print("   ⏳ Scraping database... please wait...")
try:
    start = time.time()
    response = requests.get(
        f"{API_URL}/fetch-data?force_fresh=true&limit=5",
        headers=headers,
        timeout=120  # 2 minute timeout
    )
    elapsed = time.time() - start
    
    print(f"   Status: {response.status_code}")
    print(f"   Time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Got {len(data.get('data', []))} FRESH records")
        print(f"   This data is LIVE from database!")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check status
print("\n4️⃣  Testing STATUS endpoint...")
try:
    response = requests.get(
        f"{API_URL}/status",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API is online!")
        print(f"   Cache exists: {data.get('cache_exists', False)}")
        if data.get('cache_exists'):
            print(f"   Cache age: {data.get('cache_age_minutes')} minutes")
            print(f"   Record count: {data.get('count')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")
print("=" * 60)
print("\n💡 To use in your code:")
print("""
import requests

headers = {"X-API-Key": "shopify_secure_key_2025"}

# Fast cached data
response = requests.get(
    "http://localhost:5000/fetch-data?limit=10",
    headers=headers
)

# LIVE fresh data (slower)
response = requests.get(
    "http://localhost:5000/fetch-data?force_fresh=true&limit=10",
    headers=headers
)
""")
