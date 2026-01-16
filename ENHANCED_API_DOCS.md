# 🚀 Enhanced API Documentation

## Overview

The **Enhanced Shopify Data API** provides **instant responses** by returning cached data immediately, while optionally refreshing data in the background. Users don't have to wait!

---

## ✨ Key Features

1. **⚡ Instant Response** - Return cached data immediately (no waiting!)
2. **🔄 Background Refresh** - Scrape fresh data while user views old data
3. **📊 Row Ranges** - Get specific chunks (e.g., rows 1-100, 101-200)
4. **📡 Real-time Updates** - Server-Sent Events (SSE) for live progress
5. **🎯 No Duplicate Requests** - One request gets both old and new data

---

## 🎯 API Endpoints

### 1️⃣ `/api/data` - Get Data (Recommended)

**Returns cached data instantly** + optionally triggers background refresh

#### Parameters:

- `start_row` (optional): Starting row number (1-indexed)
- `end_row` (optional): Ending row number (inclusive)
- `refresh` (optional): If `true`, triggers background scrape

#### Examples:

**Get all cached data:**

```bash
GET /api/data
```

**Get rows 1-100:**

```bash
GET /api/data?start_row=1&end_row=100
```

**Get cached data + trigger background refresh (BEST FOR UX):**

```bash
GET /api/data?refresh=true
```

**Get rows 500-1000 + refresh:**

```bash
GET /api/data?start_row=500&end_row=1000&refresh=true
```

#### Response Example:

**Immediate Response (Cached):**

```json
{
  "status": "success",
  "source": "cache",
  "total_count": 107296,
  "returned_count": 100,
  "start_row": 1,
  "end_row": 100,
  "cached_at": "Thu Jan 16 14:00:00 2026",
  "data": [
    /* array of records */
  ],
  "refresh_triggered": true,
  "task_id": "abc12345",
  "message": "Returning cached data. Fresh data being fetched in background.",
  "check_status_url": "/api/task/abc12345"
}
```

---

### 2️⃣ `/api/task/{task_id}` - Check Background Task Status

**Poll this endpoint** to check if background refresh is complete.

#### Example:

```bash
GET /api/task/abc12345
```

#### Response While Running:

```json
{
  "task_status": "running",
  "message": "Scraping fresh data..."
}
```

#### Response When Complete:

```json
{
  "task_status": "completed",
  "message": "Fresh data ready!",
  "fresh_data": {
    "total_count": 107296,
    "returned_count": 100,
    "start_row": 1,
    "end_row": 100,
    "data": [
      /* fresh records */
    ]
  }
}
```

---

### 3️⃣ `/api/data/fresh` - Real-time Updates (SSE)

**Server-Sent Events** - Streams updates in real-time

#### Parameters:

- `start_row` (optional)
- `end_row` (optional)

#### Example:

```bash
GET /api/data/fresh?start_row=1&end_row=100
```

#### Stream Events:

```
data: {"type":"cached","data":{...}}

data: {"type":"status","message":"Fetching fresh data..."}

data: {"type":"fresh","data":{...}}

data: {"type":"complete","message":"Fresh data ready"}
```

---

### 4️⃣ `/api/metadata` - Get Metadata Only

**Super fast** - Returns count and file info without loading data

#### Example:

```bash
GET /api/metadata
```

#### Response:

```json
{
  "total_count": 107296,
  "file_size_kb": 85548.4,
  "file_size_mb": 83.54,
  "last_modified": "Thu Jan 16 14:00:00 2026"
}
```

---

### 5️⃣ `/health` - Health Check

```bash
GET /health
```

#### Response:

```json
{
  "status": "ok",
  "cache_exists": true,
  "update_in_progress": false
}
```

---

## 🎨 Usage Patterns

### Pattern 1: Instant UX (Recommended)

**Best for user experience** - User sees data immediately!

```javascript
async function loadData() {
  // 1. Get cached data + trigger refresh
  const response = await fetch(
    "/api/data?refresh=true&start_row=1&end_row=100",
    {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    }
  );

  const data = await response.json();

  // 2. Show cached data to user IMMEDIATELY
  displayData(data.data);
  showMessage("Showing cached data. Refreshing in background...");

  // 3. Poll for fresh data
  if (data.task_id) {
    const freshData = await pollForFreshData(data.task_id);

    // 4. Update UI with fresh data when ready
    displayData(freshData.data);
    showMessage("✅ Fresh data loaded!");
  }
}

async function pollForFreshData(taskId) {
  while (true) {
    const response = await fetch(`/api/task/${taskId}`, {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    });

    const taskData = await response.json();

    if (taskData.task_status === "completed") {
      return taskData.fresh_data;
    } else if (taskData.task_status === "failed") {
      throw new Error("Refresh failed");
    }

    // Wait 2 seconds before checking again
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
}
```

---

### Pattern 2: Real-time Stream (SSE)

**Best for showing progress** - User sees live updates

```javascript
function loadDataWithSSE() {
  const eventSource = new EventSource(
    "/api/data/fresh?start_row=1&end_row=100"
  );

  eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data);

    switch (update.type) {
      case "cached":
        // Show cached data immediately
        displayData(update.data);
        showStatus("📦 Showing cached data...");
        break;

      case "status":
        // Show progress
        showStatus("⏳ " + update.message);
        break;

      case "fresh":
        // Update with fresh data
        displayData(update.data);
        showStatus("✨ Fresh data loaded!");
        break;

      case "complete":
        // Done!
        eventSource.close();
        break;
    }
  };
}
```

---

### Pattern 3: Cached Only (Fast)

**Best when fresh data not needed** - Instant response

```javascript
async function loadCachedOnly() {
  const response = await fetch("/api/data?start_row=1&end_row=100", {
    headers: { "X-API-Key": "shopify_secure_key_2025" },
  });

  const data = await response.json();
  displayData(data.data);
}
```

---

## 📊 Row Range Examples

### Get first 100 rows:

```
/api/data?start_row=1&end_row=100
```

### Get rows 101-200:

```
/api/data?start_row=101&end_row=200
```

### Get last 100 rows (if total is 107,296):

```
/api/data?start_row=107197&end_row=107296
```

### Get all data (no range):

```
/api/data
```

---

## 🔑 Authentication

All endpoints (except `/health`) require API key:

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  http://localhost:5000/api/data
```

---

## ⚡ Performance Metrics

For **107,296 records** (83 MB cache):

| Operation                  | Time    |
| -------------------------- | ------- |
| Get metadata               | ~0.001s |
| Get cached data (all)      | ~0.05s  |
| Get cached data (100 rows) | ~0.01s  |
| Background scrape          | 30-60s  |
| SSE stream (cached)        | ~0.05s  |
| SSE stream (fresh)         | 30-60s  |

---

## 🎯 Benefits

### ✅ User Experience:

- **No waiting** - Users see data immediately
- **Progress feedback** - Users know something is happening
- **Fresh data** - Gets updated automatically

### ✅ Performance:

- **Instant first response** - \<100ms
- **No blocking** - Background refresh doesn't block
- **Efficient** - Single request for both old and new data

### ✅ Server:

- **No duplicate requests** - One request handles everything
- **Non-blocking** - Doesn't tie up server resources
- **Scalable** - Can handle multiple concurrent refreshes

---

## 🚀 Quick Start

### 1. Start the enhanced API:

```bash
python flask_app_enhanced.py
```

### 2. Open the demo in browser:

```bash
start api_demo_enhanced.html
```

### 3. Test with curl:

**Get cached data + trigger refresh:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/api/data?refresh=true&start_row=1&end_row=100"
```

**Check task status:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/api/task/abc12345"
```

---

## 🔧 Configuration

Edit `flask_app_enhanced.py`:

```python
CACHE_FILE = "data_cache.json"  # Cache file path
API_KEY = "shopify_secure_key_2025"  # Your API key
```

---

## 📝 Notes

- **Row numbers are 1-indexed** (start_row=1 is the first row)
- **end_row is inclusive** (start_row=1, end_row=100 returns 100 rows)
- **Background tasks are non-blocking** (API remains responsive)
- **Multiple refreshes** are prevented (only one runs at a time)
- **Task IDs** are auto-generated and track each refresh request

---

## 🎉 Summary

This API gives you the **best of both worlds**:

1. ⚡ **Instant response** → Users happy
2. 🔄 **Fresh data** → Data stays current
3. 📊 **Chunking** → Efficient data transfer
4. 📡 **Real-time** → Modern UX

No more choosing between **fast** or **fresh** - you get **BOTH**! 🚀
