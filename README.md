# Shopify Data API with Smart Caching

A Flask API that scrapes Shopify phpMyAdmin data and serves it with intelligent caching. The API provides cached data instantly while optionally refreshing in the background.

## 🌟 Features

- ✅ **Instant Response**: Returns cached data immediately (< 100ms)
- 🔄 **Background Refresh**: Optionally updates data without blocking requests
- 📡 **Server-Sent Events (SSE)**: Stream both cached and updated data
- 🔒 **API Key Authentication**: Secure access control
- 📊 **Status Monitoring**: Check cache age and update progress
- 🎯 **Multiple Endpoints**: Flexible API for different use cases

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         API Request                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      flask_app.py                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  1. Authenticate (API Key)                            │  │
│  │  2. Read cache → Return instantly                     │  │
│  │  3. (Optional) Trigger background refresh             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼──────┐    ┌──────▼──────────┐
            │ data_cache.  │    │  Background     │
            │    json      │    │  Thread         │
            └──────────────┘    │                 │
                                │  sync_worker.   │
                                │  perform_sync() │
                                │                 │
                                │  1. Selenium    │
                                │  2. Login       │
                                │  3. Export CSV  │
                                │  4. Update cache│
                                └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (auto-installed on Windows)

## 🚀 Installation

### 1. Clone the repository

```bash
cd "c:\DivySApp\shopify db scrapping"
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your credentials

Edit `sync_worker.py` and update:

```python
BASE_URL = "https://your-phpmyadmin-url.com"
USERNAME = "your_username"
PASSWORD = "your_password"
DB_NAME = "your_database"
TABLE_NAME = "orders"
```

### 4. (Optional) Change API Key

Edit `flask_app.py`:

```python
API_KEY = "your_custom_secure_key"
```

## 🎯 Usage

### Running Locally

#### 1. Start the API Server

```bash
python flask_app.py
```

The server will start on `http://localhost:5000`

#### 2. (Optional) Run Background Worker

In a separate terminal:

```bash
python sync_worker.py
```

This will:

- Perform initial data sync
- Update cache every hour automatically

#### 3. Test the API

**Option A: Use the Demo Page**
Open `demo.html` in your browser and interact with the UI.

**Option B: Use curl**

```bash
# Get cached data
curl -H "X-API-Key: shopify_secure_key_2025" http://localhost:5000/fetch-data

# Get cached data + trigger refresh
curl -H "X-API-Key: shopify_secure_key_2025" "http://localhost:5000/fetch-data?refresh=true"

# Check status
curl -H "X-API-Key: shopify_secure_key_2025" http://localhost:5000/status
```

## 🌐 Deploying to Render

### Method 1: Web Service + Background Worker (Recommended)

#### Step 1: Deploy API Service

1. Create new **Web Service** on Render
2. Connect your repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python flask_app.py`
   - **Environment**: Python 3

#### Step 2: Deploy Background Worker

1. Create new **Background Worker** on Render
2. Connect same repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python sync_worker.py`

### Method 2: Single Service with Cron Jobs

Deploy only the API service and use Render's Cron Jobs:

1. Deploy as **Web Service** (see Step 1 above)
2. Add a **Cron Job**:
   - **Schedule**: `0 * * * *` (every hour)
   - **Command**:
   ```bash
   curl -X POST -H "X-API-Key: shopify_secure_key_2025" https://your-api.onrender.com/refresh
   ```

### Method 3: API-Triggered Refresh (Most Flexible)

Deploy only the API service. Clients trigger refresh when needed:

```javascript
// Frontend code
async function loadData() {
  // Returns cached data instantly + triggers background refresh
  const response = await fetch(
    "https://your-api.onrender.com/fetch-data?refresh=true",
    {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    }
  );

  const data = await response.json();
  displayData(data); // Show instant cached data

  // Fresh data will be available in 2-5 minutes
}
```

## 📡 API Endpoints

### GET `/fetch-data`

Returns cached data immediately.

**Query Parameters:**

- `refresh=true` - Trigger background update
- `stream=true` - Use Server-Sent Events

**Examples:**

```bash
# Standard (cached only)
/fetch-data

# With background refresh
/fetch-data?refresh=true

# SSE stream (cached + updated)
/fetch-data?stream=true&refresh=true
```

### POST `/refresh`

Manually trigger data refresh.

```bash
curl -X POST \
  -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.onrender.com/refresh
```

### GET `/status`

Check API and cache status.

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.onrender.com/status
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

### GET `/health`

Simple health check (no authentication).

```bash
curl https://your-api.onrender.com/health
```

## 🎨 Example Implementations

### React/Next.js

```jsx
import { useState, useEffect } from "react";

function DataComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const response = await fetch(
        "https://your-api.onrender.com/fetch-data?refresh=true",
        {
          headers: { "X-API-Key": "shopify_secure_key_2025" },
        }
      );

      const result = await response.json();
      setData(result);
      setLoading(false);
    }

    fetchData();
  }, []);

  return <div>{loading ? "Loading..." : `${data.count} records loaded`}</div>;
}
```

### Python

```python
import requests

headers = {'X-API-Key': 'shopify_secure_key_2025'}
url = 'https://your-api.onrender.com/fetch-data?refresh=true'

response = requests.get(url, headers=headers)
data = response.json()

print(f"Status: {data['status']}")
print(f"Records: {data['count']}")
print(f"Last Updated: {data['last_updated']}")
```

### Node.js

```javascript
const fetch = require("node-fetch");

async function getData() {
  const response = await fetch(
    "https://your-api.onrender.com/fetch-data?refresh=true",
    {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    }
  );

  const data = await response.json();
  console.log(`Loaded ${data.count} records`);
  return data;
}

getData();
```

## 🔧 Configuration

### Cache Behavior

The caching system works as follows:

1. **First Request**: Returns 503 if no cache exists
2. **Subsequent Requests**: Returns cached data instantly
3. **With `refresh=true`**: Returns cache + triggers background update
4. **Background Worker**: Updates cache every hour

### Performance Tuning

**Adjust refresh interval** in `sync_worker.py`:

```python
# Default: 1 hour
time.sleep(3600)

# Example: 30 minutes
time.sleep(1800)
```

**Timeout settings** in `flask_app.py`:

```python
# SSE stream timeout (default: 5 minutes)
max_wait = 300

# Change to 10 minutes
max_wait = 600
```

## 📝 File Structure

```
shopify db scrapping/
├── flask_app.py          # Main API server
├── sync_worker.py        # Background data sync worker
├── demo.html             # Interactive test page
├── API_USAGE.md          # Detailed API documentation
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── data_cache.json       # Cached data (auto-generated)
└── downloads/            # Temporary CSV downloads
```

## 🐛 Troubleshooting

### Problem: API returns 503 "No cached data"

**Solution**: Run `sync_worker.py` to perform initial sync:

```bash
python sync_worker.py
```

### Problem: Background refresh not working

**Check:**

1. ChromeDriver is installed
2. Selenium can access the phpMyAdmin URL
3. Check logs for error messages

### Problem: SSE stream not working

**Cause**: Some proxies/CDNs don't support SSE

**Solution**: Use standard `refresh=true` instead:

```bash
/fetch-data?refresh=true
```

### Problem: Data is old/stale

**Solutions:**

1. Check if `sync_worker.py` is running
2. Manually trigger refresh:
   ```bash
   curl -X POST -H "X-API-Key: shopify_secure_key_2025" \
     https://your-api.onrender.com/refresh
   ```
3. Check `/status` to see cache age

### Problem: "Update already in progress"

**Cause**: Only one update can run at a time

**Solution**: Wait 2-5 minutes for current update to complete, then retry

## 🔒 Security Best Practices

1. **Change the default API key** before deployment
2. **Use environment variables** for sensitive data:
   ```python
   API_KEY = os.getenv("SHOPIFY_API_KEY", "default_key")
   ```
3. **Enable HTTPS** (automatic on Render)
4. **Implement rate limiting** for production (optional)

## 📊 Monitoring

### Check API Health

```bash
curl https://your-api.onrender.com/health
```

### Monitor Cache Status

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.onrender.com/status
```

### View Logs

On Render dashboard:

- **API Service**: View request logs
- **Background Worker**: View sync progress

## 📚 Additional Resources

- [API Usage Guide](API_USAGE.md) - Detailed endpoint documentation
- [Interactive Demo](demo.html) - Test all features in browser
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Render Deployment Guide](https://render.com/docs)

## 🤝 Contributing

This is a private project, but suggestions are welcome!

## 📄 License

Private project - All rights reserved

## 💡 Tips & Tricks

### Pre-warming Cache

Before peak traffic, trigger a manual refresh:

```bash
curl -X POST -H "X-API-Key: shopify_secure_key_2025" \
  https://your-api.onrender.com/refresh
```

### Periodic Health Checks

Set up a monitoring service (UptimeRobot, Pingdom) to ping:

```
https://your-api.onrender.com/health
```

### Optimize for Mobile

For mobile apps, use simple `/fetch-data` without streaming:

```kotlin
// Android example
val response = client.get("https://your-api.onrender.com/fetch-data") {
    header("X-API-Key", "shopify_secure_key_2025")
}
```

---

**Built with ❤️ for fast, reliable data access**
