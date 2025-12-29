# Shopify Data API - Usage Guide

## Overview

This API provides shopify database data with intelligent caching. It supports:

- **Instant cached responses** - Get data immediately from cache
- **Background refresh** - Trigger updates without waiting
- **Server-Sent Events (SSE)** - Stream both cached and updated data
- **Manual refresh** - Force data synchronization

## Authentication

All endpoints (except `/health`) require API key authentication:

**Header:**

```
X-API-Key: shopify_secure_key_2025
```

---

## Endpoints

### 1. GET `/fetch-data`

Returns cached data immediately.

**Basic Usage:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.render.com/fetch-data
```

**Response:**

```json
{
  "status": "success",
  "count": 1234,
  "last_updated": "Sun Dec 29 10:20:15 2025",
  "data": [...]
}
```

---

### 2. GET `/fetch-data?refresh=true`

Returns cached data immediately **AND** triggers background refresh.

**Usage:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://your-api.render.com/fetch-data?refresh=true"
```

**Response:**

```json
{
  "status": "success",
  "count": 1234,
  "last_updated": "Sun Dec 29 10:20:15 2025",
  "_info": "Background refresh triggered. Call again in a few minutes for updated data.",
  "data": [...]
}
```

**How it works:**

1. ✅ Returns cached data instantly
2. 🔄 Starts background update (takes 2-5 minutes)
3. 📦 Next call will have fresh data

---

### 3. GET `/fetch-data?stream=true&refresh=true`

Uses **Server-Sent Events** to send both cached and updated data.

**Usage (JavaScript):**

```javascript
const eventSource = new EventSource(
  "https://your-api.render.com/fetch-data?stream=true&refresh=true",
  {
    headers: {
      "X-API-Key": "shopify_secure_key_2025",
    },
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "cached") {
    console.log("📦 Cached data:", data.payload);
    // Use cached data immediately
  } else if (data.type === "updated") {
    console.log("✅ Updated data:", data.payload);
    // Replace with fresh data
  } else if (data.type === "done") {
    eventSource.close();
  }
};
```

**Usage (Python):**

```python
import requests
import json

headers = {'X-API-Key': 'shopify_secure_key_2025'}
url = 'https://your-api.render.com/fetch-data?stream=true&refresh=true'

with requests.get(url, headers=headers, stream=True) as response:
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])

                if data['type'] == 'cached':
                    print("📦 Cached data received")
                elif data['type'] == 'updated':
                    print("✅ Updated data received")
                elif data['type'] == 'done':
                    break
```

**Flow:**

1. 📦 Immediately sends cached data
2. ⏳ Waits for background refresh to complete
3. ✅ Sends updated data when ready
4. 🏁 Sends "done" signal

---

### 4. POST `/refresh`

Manually trigger data refresh (doesn't return data).

**Usage:**

```bash
curl -X POST \
  -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.render.com/refresh
```

**Response:**

```json
{
  "status": "triggered",
  "message": "Data refresh triggered successfully"
}
```

**Use Cases:**

- Scheduled cron jobs
- Admin panels
- Pre-warming cache before peak hours

---

### 5. GET `/status`

Check cache status and API health.

**Usage:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.render.com/status
```

**Response:**

```json
{
  "api_status": "online",
  "cache_exists": true,
  "cache_age_minutes": 45,
  "update_in_progress": false,
  "timestamp": "Sun Dec 29 10:25:00 2025"
}
```

---

### 6. GET `/health`

Simple health check (no authentication required).

**Usage:**

```bash
curl https://your-api.render.com/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "Sun Dec 29 10:25:00 2025"
}
```

---

## Recommended Workflows

### Scenario 1: Frontend App (Best UX)

**Goal**: Show data immediately, update in background

```javascript
// On page load
async function loadData() {
  const response = await fetch(
    "https://your-api.render.com/fetch-data?refresh=true",
    {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    }
  );

  const data = await response.json();
  displayData(data); // Show cached data instantly

  // Fresh data will be available in 2-5 minutes
  // User can refresh page or poll /status
}
```

### Scenario 2: Real-time Dashboard (SSE)

**Goal**: Update UI automatically when fresh data arrives

```javascript
const eventSource = new EventSource(
  "https://your-api.render.com/fetch-data?stream=true&refresh=true",
  {
    headers: { "X-API-Key": "shopify_secure_key_2025" },
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "cached") {
    displayData(data.payload); // Show immediately
  } else if (data.type === "updated") {
    displayData(data.payload); // Update UI with fresh data
    showNotification("Data updated!");
  }
};
```

### Scenario 3: Scheduled Sync (Cron Job)

**Goal**: Keep cache fresh for all users

```bash
# Run every hour via cron or Render cron jobs
0 * * * * curl -X POST -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.render.com/refresh
```

### Scenario 4: Mobile App (Battery Efficient)

**Goal**: Get data fast without waiting

```kotlin
// Android/Kotlin example
fun fetchData() {
    val request = Request.Builder()
        .url("https://your-api.render.com/fetch-data")
        .header("X-API-Key", "shopify_secure_key_2025")
        .build()

    client.newCall(request).enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            val data = response.body?.string()
            // Display cached data instantly
        }
    })
}
```

---

## Error Handling

### 401 Unauthorized

**Cause**: Invalid or missing API key

```json
{
  "status": "error",
  "message": "Unauthorized access"
}
```

### 503 Service Unavailable

**Cause**: No cached data available yet

```json
{
  "status": "pending",
  "message": "No cached data available. Please wait for initial sync..."
}
```

**Solution**: Wait for `sync_worker.py` to run first sync, or call `/refresh` endpoint.

### 202 Accepted

**Cause**: Refresh already in progress

```json
{
  "status": "in_progress",
  "message": "Data refresh already in progress"
}
```

---

## Performance Notes

- **Cache Response Time**: < 100ms (instant)
- **Background Refresh**: 2-5 minutes (Selenium scraping)
- **SSE Timeout**: 5 minutes max wait for updated data
- **Concurrent Refreshes**: Only 1 update runs at a time

---

## Deployment on Render

1. **Environment Variables**: None needed (API key is in code)
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `python flask_app.py`
4. **Background Worker**: Deploy `sync_worker.py` as separate service

### Optional: Add Cron Job

In Render dashboard, add a cron job:

```yaml
- type: cron
  schedule: "0 * * * *"  # Every hour
  command: curl -X POST -H "X-API-Key: shopify_secure_key_2025" https://your-api.onrender.com/refresh
```

---

## Testing Locally

1. **Start the API:**

```bash
python flask_app.py
```

2. **Test basic fetch:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" http://localhost:5000/fetch-data
```

3. **Test with refresh:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" "http://localhost:5000/fetch-data?refresh=true"
```

4. **Check status:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" http://localhost:5000/status
```

---

## Security Best Practices

1. **Change the API key** in `flask_app.py`:

```python
API_KEY = "your_super_secret_key_here"
```

2. **Use environment variables** (recommended):

```python
API_KEY = os.getenv("SHOPIFY_API_KEY", "default_key")
```

3. **Enable HTTPS** on Render (automatic)

4. **Rate limiting** (add if needed using Flask-Limiter)

---

## Troubleshooting

**Q: API returns 503 "No cached data"**

- Run `sync_worker.py` manually first to generate initial cache
- Check if `data_cache.json` exists

**Q: Background refresh not working**

- Check Render logs for errors
- Verify Selenium dependencies are installed
- Ensure ChromeDriver is available

**Q: SSE connection closes immediately**

- Some proxies/CDNs don't support SSE
- Use standard `refresh=true` instead

**Q: Old data keeps returning**

- Check `/status` to see cache age
- Manually trigger `/refresh`
- Check if `sync_worker.py` is running

---

## Contact & Support

For issues or questions, check:

- Application logs on Render dashboard
- `sync_worker.py` logs for scraping errors
- Network tab for API response details
