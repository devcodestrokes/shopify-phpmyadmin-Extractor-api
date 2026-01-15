"""
Fetch ALL data from API using pagination
This script fetches the entire dataset by making multiple requests
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "shopify_secure_key_2025"
headers = {"X-API-Key": API_KEY}

print("="*70)
print("📥 FETCHING ALL DATA FROM API")
print("="*70)

# Step 1: Get total count
print("\n1️⃣  Getting total record count...")
try:
    response = requests.get(
        f"{API_URL}/fetch-data?metadata_only=true",
        headers=headers,
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ Error getting metadata: {response.text}")
        exit(1)
    
    metadata = response.json()
    total_count = metadata.get('count', 0)
    file_size_kb = metadata.get('file_size_kb', 0)
    
    print(f"   ✅ Total records: {total_count:,}")
    print(f"   ✅ Cache file size: {file_size_kb:,.2f} KB")
    
    if total_count == 0:
        print("   ⚠️ No data available. Run sync_worker.py first!")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Make sure flask_app.py is running!")
    exit(1)

# Step 2: Fetch all data in batches
print(f"\n2️⃣  Fetching {total_count:,} records in batches...")

all_data = []
limit = 100  # Max records per request
offset = 0
batch_number = 1

start_time = time.time()

while offset < total_count:
    try:
        print(f"   Batch {batch_number}: Fetching records {offset:,} to {min(offset + limit, total_count):,}...", end=" ")
        
        response = requests.get(
            f"{API_URL}/fetch-data?limit={limit}&offset={offset}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"\n   ❌ Error: {response.text}")
            break
        
        batch_data = response.json().get('data', [])
        
        if not batch_data:
            print("(no more data)")
            break
        
        all_data.extend(batch_data)
        print(f"✅ Got {len(batch_data)} records")
        
        offset += limit
        batch_number += 1
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        break

elapsed_time = time.time() - start_time

print(f"\n3️⃣  Saving to file...")

# Save to JSON file
output_file = "all_shopify_data.json"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_count": len(all_data),
            "fetched_at": time.ctime(),
            "data": all_data
        }, f, indent=2)
    
    print(f"   ✅ Saved {len(all_data):,} records to: {output_file}")
    
    # Show file size
    import os
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"   ✅ File size: {file_size_mb:.2f} MB")
    
except Exception as e:
    print(f"   ❌ Error saving file: {e}")

print("\n" + "="*70)
print("✅ EXPORT COMPLETE!")
print("="*70)

print(f"\n📊 Summary:")
print(f"   • Total records fetched: {len(all_data):,}")
print(f"   • Time taken: {elapsed_time:.2f} seconds")
print(f"   • Average speed: {len(all_data)/elapsed_time:.0f} records/second")
print(f"   • Output file: {output_file}")

print(f"\n💡 You can now use '{output_file}' with any tool!")
print(f"💡 Or import it in Python:")
print(f"""
import json

with open('{output_file}', 'r') as f:
    data = json.load(f)

all_records = data['data']
print(f"Loaded {{len(all_records):,}} records")
""")
