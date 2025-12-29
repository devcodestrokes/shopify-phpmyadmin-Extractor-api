# Shopify Data API - Complete Usage Guide

**Base URL:** `https://shopify-phpmyadmin-extractor-api.onrender.com`

**Authentication:** All endpoints (except `/health`) require an API key in the header.

```
X-API-Key: shopify_secure_key_2025
```

---

## Quick Start

### Get ALL Data (Recommended - Only 20-30MB Memory!)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?stream_all=true"
```

**Returns:** All 102,054 records in ONE response  
**Memory:** ~20-30MB on server  
**Time:** ~3-5 seconds

---

## API Endpoints

### 1. Get ALL Data (Streaming Mode) ⭐ RECOMMENDED

**Endpoint:** `GET /fetch-data?stream_all=true`

**Description:** Returns all 102,054 records in a single response using only 20-30MB memory.

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?stream_all=true"
```

**Response:**

```json
{
  "status": "success",
  "count": 102054,
  "last_updated": "Mon Dec 29 11:22:17 2025",
  "data": [
    {
      "id": 1,
      "user_id": 24,
      "shopify_order_id": 11821767491966,
      "name": "#1037",
      "opt_in": 1,
      "payment_status": "paid",
      "total_price": 13.93,
      "customer_id": 1,
      ...
    },
    // ... 102,053 more records
  ]
}
```

**Response Headers:**

```
Content-Type: application/json
X-Data-Mode: streaming-all
X-Memory-Usage: ~20-30MB
```

---

### 2. Get Paginated Data

**Endpoint:** `GET /fetch-data?limit={limit}&offset={offset}`

**Description:** Get a specific page of records (useful for infinite scroll).

**Parameters:**

- `limit` - Number of records (default: 100, max: 1000)
- `offset` - Starting position (default: 0)

**Examples:**

**First 100 records:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?limit=100&offset=0"
```

**1000 records from position 5000:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?limit=1000&offset=5000"
```

**Response:**

```json
{
  "status": "success",
  "count": 102054,
  "last_updated": "Mon Dec 29 11:22:17 2025",
  "page_info": {
    "limit": 100,
    "offset": 0,
    "returned": 100,
    "has_more": true
  },
  "data": [
    /* 100 records */
  ]
}
```

---

### 3. Get Metadata Only (Fast!)

**Endpoint:** `GET /fetch-data?metadata_only=true`

**Description:** Get count and stats without loading any records (< 1KB response).

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?metadata_only=true"
```

**Response:**

```json
{
  "status": "success",
  "count": 102054,
  "last_updated": "Mon Dec 29 11:22:17 2025",
  "file_mtime": 1766986717.184695,
  "file_size_mb": 78.29
}
```

---

### 4. Trigger Background Refresh

**Endpoint:** `GET /fetch-data?stream_all=true&refresh=true`

**Description:** Get all data AND trigger a background refresh for next time.

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?stream_all=true&refresh=true"
```

---

### 5. Manual Refresh

**Endpoint:** `POST /refresh`

**Description:** Manually trigger data refresh without fetching data.

**Example:**

```bash
curl -X POST \
  -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/refresh"
```

**Response:**

```json
{
  "status": "triggered",
  "message": "Data refresh triggered successfully"
}
```

---

### 6. Check API Status

**Endpoint:** `GET /status`

**Description:** Check cache age, size, and API health.

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/status"
```

**Response:**

```json
{
  "api_status": "online",
  "cache_exists": true,
  "cache_age_minutes": 15,
  "cache_size_mb": 78.29,
  "record_count": 102054,
  "update_in_progress": false,
  "timestamp": "Mon Dec 29 11:30:00 2025",
  "memory_note": "API uses pagination to handle large datasets efficiently"
}
```

---

### 7. Health Check

**Endpoint:** `GET /health`

**Description:** Simple health check (no authentication required).

**Example:**

```bash
curl "https://shopify-phpmyadmin-extractor-api.onrender.com/health"
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "Mon Dec 29 11:30:00 2025"
}
```

---

## Code Examples

### JavaScript / Node.js

#### Get All Data

```javascript
const API_URL = "https://shopify-phpmyadmin-extractor-api.onrender.com";
const API_KEY = "shopify_secure_key_2025";

async function getAllData() {
  const response = await fetch(`${API_URL}/fetch-data?stream_all=true`, {
    headers: { "X-API-Key": API_KEY },
  });

  const data = await response.json();
  console.log(`Total records: ${data.count}`);
  console.log(`Records received: ${data.data.length}`);

  return data.data;
}

// Usage
getAllData().then((records) => {
  console.log(`Loaded ${records.length} records`);
  // Process your data here
});
```

#### Get Paginated Data

```javascript
async function getPage(limit = 100, offset = 0) {
  const response = await fetch(
    `${API_URL}/fetch-data?limit=${limit}&offset=${offset}`,
    {
      headers: { "X-API-Key": API_KEY },
    }
  );

  const data = await response.json();

  return {
    records: data.data,
    hasMore: data.page_info.has_more,
    total: data.count,
  };
}

// Usage
const page1 = await getPage(100, 0);
console.log(`Got ${page1.records.length} records`);
console.log(`Has more: ${page1.hasMore}`);
```

#### Get Metadata Only

```javascript
async function getMetadata() {
  const response = await fetch(`${API_URL}/fetch-data?metadata_only=true`, {
    headers: { "X-API-Key": API_KEY },
  });

  return await response.json();
}

// Usage
const meta = await getMetadata();
console.log(`Total records: ${meta.count}`);
console.log(`Last updated: ${meta.last_updated}`);
```

---

### Python

#### Get All Data

```python
import requests

API_URL = "https://shopify-phpmyadmin-extractor-api.onrender.com"
API_KEY = "shopify_secure_key_2025"

def get_all_data():
    response = requests.get(
        f"{API_URL}/fetch-data?stream_all=true",
        headers={'X-API-Key': API_KEY}
    )

    data = response.json()
    print(f"Total records: {data['count']}")
    print(f"Records received: {len(data['data'])}")

    return data['data']

# Usage
all_records = get_all_data()
print(f"Loaded {len(all_records)} records")
```

#### Get Paginated Data

```python
def get_page(limit=100, offset=0):
    response = requests.get(
        f"{API_URL}/fetch-data?limit={limit}&offset={offset}",
        headers={'X-API-Key': API_KEY}
    )

    data = response.json()

    return {
        'records': data['data'],
        'has_more': data['page_info']['has_more'],
        'total': data['count']
    }

# Usage
page1 = get_page(100, 0)
print(f"Got {len(page1['records'])} records")
print(f"Has more: {page1['has_more']}")
```

#### Load All Data with Pagination

```python
def load_all_paginated():
    all_records = []
    offset = 0
    limit = 1000

    while True:
        response = requests.get(
            f"{API_URL}/fetch-data?limit={limit}&offset={offset}",
            headers={'X-API-Key': API_KEY}
        )

        data = response.json()
        all_records.extend(data['data'])

        print(f"Loaded {len(all_records)} / {data['count']}")

        if not data['page_info']['has_more']:
            break

        offset += limit

    return all_records

# Usage
records = load_all_paginated()
print(f"Total loaded: {len(records)}")
```

---

### PHP

```php
<?php

$apiUrl = 'https://shopify-phpmyadmin-extractor-api.onrender.com';
$apiKey = 'shopify_secure_key_2025';

// Get all data
function getAllData() {
    global $apiUrl, $apiKey;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiUrl . '/fetch-data?stream_all=true');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'X-API-Key: ' . $apiKey
    ]);

    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    echo "Total records: " . $data['count'] . "\n";
    echo "Records received: " . count($data['data']) . "\n";

    return $data['data'];
}

// Usage
$records = getAllData();
echo "Loaded " . count($records) . " records\n";

?>
```

---

### cURL Examples

#### Download all data to file

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?stream_all=true" \
  -o shopify_data.json
```

#### Get just the record count

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?metadata_only=true" \
  | jq '.count'
```

#### Pretty print response

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?limit=5" \
  | jq '.'
```

---

## Response Format

### Success Response

```json
{
  "status": "success",
  "count": 102054,
  "last_updated": "Mon Dec 29 11:22:17 2025",
  "data": [
    /* array of records */
  ]
}
```

### Paginated Response

```json
{
  "status": "success",
  "count": 102054,
  "last_updated": "Mon Dec 29 11:22:17 2025",
  "page_info": {
    "limit": 100,
    "offset": 0,
    "returned": 100,
    "has_more": true
  },
  "data": [
    /* array of records */
  ]
}
```

### Error Responses

**401 Unauthorized:**

```json
{
  "status": "error",
  "message": "Unauthorized access"
}
```

**503 Service Unavailable:**

```json
{
  "status": "pending",
  "message": "No cached data available. Please wait for initial sync..."
}
```

**400 Bad Request:**

```json
{
  "status": "error",
  "message": "Invalid limit or offset parameter"
}
```

---

## Performance Guide

### Best Performance (Recommended)

**Use stream_all for complete dataset:**

```bash
GET /fetch-data?stream_all=true
```

- **Memory:** 20-30MB
- **Time:** 3-5 seconds
- **Data:** All 102,054 records

### For Quick Checks

**Use metadata_only:**

```bash
GET /fetch-data?metadata_only=true
```

- **Memory:** < 1MB
- **Time:** < 100ms
- **Data:** Count and stats only

### For Pagination

**Use limit/offset:**

```bash
GET /fetch-data?limit=1000&offset=0
```

- **Memory:** 50-60MB
- **Time:** ~1 second
- **Data:** Specified records

---

## Rate Limiting

Currently **no rate limiting** is enforced, but please be respectful:

- Don't make more than **1 request per second**
- Cache responses on your end when possible
- Use `metadata_only=true` for status checks

---

## CORS Support

CORS is **enabled** for all origins. You can call this API from:

- Browser JavaScript
- Mobile apps
- Any domain

---

## Security

- ✅ API Key required (except `/health`)
- ✅ HTTPS enforced
- ✅ No sensitive data in responses
- ⚠️ Keep your API key secret!

**If your key is compromised, contact support to rotate it.**

---

## Support & Issues

**Common Issues:**

**503 Error - No cached data:**

- Wait 5-10 minutes for initial sync
- Or manually trigger: `POST /refresh`

**Slow response:**

- Use `stream_all=true` for best performance
- Avoid requesting too frequently

**Authentication failed:**

- Check API key is correct
- Ensure `X-API-Key` header is set

---

## Changelog

**v2.0 (2025-12-29):**

- Added `stream_all=true` endpoint (ALL data with 20-30MB memory)
- Added gzip compression
- Added metadata-only mode
- Optimized for Render deployment

**v1.0 (2025-12-25):**

- Initial release
- Basic caching and pagination

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Base URL:                                                   │
│  https://shopify-phpmyadmin-extractor-api.onrender.com      │
│                                                              │
│  API Key Header:                                             │
│  X-API-Key: shopify_secure_key_2025                         │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  GET ALL DATA (Recommended):                                │
│  /fetch-data?stream_all=true                                │
│  → Returns all 102K records (20-30MB memory)                │
│                                                              │
│  GET PAGINATED:                                              │
│  /fetch-data?limit=100&offset=0                             │
│  → Returns 100 records from position 0                      │
│                                                              │
│  GET METADATA:                                               │
│  /fetch-data?metadata_only=true                             │
│  → Returns count and stats only (< 1KB)                     │
│                                                              │
│  TRIGGER REFRESH:                                            │
│  POST /refresh                                               │
│  → Manually update cached data                              │
│                                                              │
│  CHECK STATUS:                                               │
│  GET /status                                                 │
│  → Cache age, size, record count                            │
│                                                              │
│  HEALTH CHECK:                                               │
│  GET /health                                                 │
│  → Simple health check (no auth)                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

**Ready to use! 🚀**

Start with:

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://shopify-phpmyadmin-extractor-api.onrender.com/fetch-data?stream_all=true"
```
