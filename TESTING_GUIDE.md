# 🧪 Quick Local Testing Guide

## ✅ **How to Test Your API Locally**

### **Step 1: Start the API Server**

Open a terminal and run:

```bash
cd "c:\DivySApp\shopify db scrapping"
python flask_app.py
```

**Expected Output:**

```
ULTRA-LIGHTWEIGHT API - Memory optimized to <2MB
Endpoints:
  GET  /fetch-data?limit=10&offset=0
  GET  /fetch-data?metadata_only=true
  POST /refresh
  GET  /status
 * Running on http://0.0.0.0:5000
```

---

### **Step 2: Run the Test Script**

**Open a NEW terminal** (keep the first one running!) and run:

```bash
cd "c:\DivySApp\shopify db scrapping"
python test_local.py
```

**This will test all endpoints automatically!** ✅

---

## 🌐 **Manual Testing (Using Browser or curl)**

### **Test 1: Health Check** (No auth needed)

```bash
# Browser: Open this URL
http://localhost:5000/health

# Or use curl
curl http://localhost:5000/health
```

**Expected:** `{"status":"ok"}`

---

### **Test 2: Get Metadata** (Fast - shows total count)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?metadata_only=true"
```

**Returns:**

```json
{
  "count": 107270,
  "file_size_kb": 80173.73,
  "last_modified": "Thu Jan 15 12:13:45 2026"
}
```

---

### **Test 3: Get First 10 Records**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=10&offset=0"
```

**Returns:** First 10 records

---

### **Test 4: Get 100 Records**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=100&offset=0"
```

**Returns:** First 100 records (max allowed per request)

---

## 📥 **How to Fetch ALL Data (Entire Dataset)**

### **Method 1: Using Pagination Loop** (Recommended)

Create a Python script:

```python
import requests
import json

API_URL = "http://localhost:5000"
API_KEY = "shopify_secure_key_2025"
headers = {"X-API-Key": API_KEY}

# Get total count first
response = requests.get(
    f"{API_URL}/fetch-data?metadata_only=true",
    headers=headers
)
total_count = response.json()['count']
print(f"Total records: {total_count}")

# Fetch all data in batches
all_data = []
limit = 100  # Max per request
offset = 0

while offset < total_count:
    print(f"Fetching records {offset} to {offset + limit}...")

    response = requests.get(
        f"{API_URL}/fetch-data?limit={limit}&offset={offset}",
        headers=headers
    )

    records = response.json()['data']
    all_data.extend(records)
    offset += limit

print(f"✅ Fetched all {len(all_data)} records!")

# Save to file
with open('all_data.json', 'w') as f:
    json.dump(all_data, f, indent=2)

print("✅ Saved to all_data.json")
```

**Save as `fetch_all.py` and run:**

```bash
python fetch_all.py
```

---

### **Method 2: Direct Access to Cache File** (Fastest!)

The cache file already contains ALL data:

```python
import json

# Read the entire cache
with open('data_cache.json', 'r') as f:
    data = json.load(f)

all_records = data['data']
print(f"Total records: {len(all_records)}")

# Now you have all records in all_records variable!
```

---

### **Method 3: Using curl with High Limit** (Quick Test)

```bash
# Get first 1000 records (but max is 100, so you'll get 100)
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=100&offset=0" > data.json
```

---

## 🔍 **Available Endpoints:**

| Endpoint                             | Auth?  | Description             | Max Records     |
| ------------------------------------ | ------ | ----------------------- | --------------- |
| `GET /health`                        | ❌ No  | Health check            | -               |
| `GET /status`                        | ✅ Yes | API status + cache info | -               |
| `GET /fetch-data?metadata_only=true` | ✅ Yes | Get count & metadata    | -               |
| `GET /fetch-data?limit=10&offset=0`  | ✅ Yes | Paginated data          | 100 per request |
| `POST /refresh`                      | ✅ Yes | Trigger background sync | -               |

---

## 💡 **Examples:**

### **Get Total Count:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?metadata_only=true"
```

### **Get Records 0-99:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=100&offset=0"
```

### **Get Records 100-199:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=100&offset=100"
```

### **Get Records 1000-1099:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=100&offset=1000"
```

---

## 🎯 **Quick Testing Checklist:**

- [ ] Start Flask app: `python flask_app.py`
- [ ] Run test script: `python test_local.py`
- [ ] Check health: `http://localhost:5000/health`
- [ ] Get metadata: Test shows total count
- [ ] Get sample data: Test shows 5 records
- [ ] Test pagination: Different offsets work
- [ ] Test authentication: Fails without API key

---

## 📊 **Complete Example Session:**

```bash
# Terminal 1: Start API
python flask_app.py

# Terminal 2: Test it
python test_local.py

# Expected output:
# ✅ Health check PASSED!
# ✅ Total records: 107270
# ✅ Got 5 records
# ✅ Got 100 records
# ✅ ALL TESTS COMPLETE!
```

---

## 🚀 **Your API is Working If:**

1. ✅ `test_local.py` runs without errors
2. ✅ You can access `http://localhost:5000/health`
3. ✅ Metadata shows total count (e.g., 107270 records)
4. ✅ `/fetch-data?limit=10` returns 10 records
5. ✅ Without API key, you get 401 Unauthorized

---

## 💾 **To Export All Data:**

**Just copy the cache file!**

```bash
# The cache file IS your complete dataset
copy "data_cache.json" "backup_all_data.json"
```

Or use the Python script above (`fetch_all.py`) to export via API! 🎉
