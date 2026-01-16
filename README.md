# 🚀 Shopify Data Scraper & API

A high-performance API that scrapes Shopify data, caches it, and serves it instantly with optional background refresh.

## ✨ Features

- ⚡ **Instant Response** - Returns cached data immediately (< 100ms)
- 🔄 **Background Refresh** - Scrapes fresh data without blocking
- 📊 **Row Ranges** - Get specific data chunks (start_row, end_row)
- 📡 **Real-time Updates** - Server-Sent Events (SSE) support
- 💾 **Fast Export** - Export all data to JSON/CSV in seconds
- 🔑 **API Key Auth** - Secure access control

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
python flask_app_enhanced.py
```

### 2. Open the Demo

```bash
start api_demo_enhanced.html
```

### 3. Export Data (Optional)

```bash
python export_data_fast.py
```

---

## 📚 API Endpoints

### Get Data

```http
# Get all data (instant cached response)
GET /api/data

# Get specific rows
GET /api/data?start_row=1&end_row=100

# Get cached data + trigger background refresh (RECOMMENDED)
GET /api/data?refresh=true&start_row=1&end_row=100

# Get metadata only (super fast)
GET /api/metadata
```

### Real-time Updates

```http
# Server-Sent Events - streams cached data then fresh data
GET /api/data/fresh?start_row=1&end_row=100
```

### Check Background Task

```http
# Check if background refresh is complete
GET /api/task/{task_id}
```

### Authentication

All endpoints require API key header:

```
X-API-Key: shopify_secure_key_2025
```

---

## 💻 Usage Examples

### JavaScript

```javascript
// Get cached data + trigger background refresh
const response = await fetch("/api/data?refresh=true&start_row=1&end_row=100", {
  headers: { "X-API-Key": "shopify_secure_key_2025" },
});

const data = await response.json();

// Show cached data immediately
console.log(`Showing ${data.returned_count} cached records`);
displayData(data.data);

// Poll for fresh data
if (data.task_id) {
  const checkTask = setInterval(async () => {
    const taskRes = await fetch(`/api/task/${data.task_id}`, {
      headers: { "X-API-Key": "shopify_secure_key_2025" },
    });

    const taskData = await taskRes.json();

    if (taskData.task_status === "completed") {
      console.log("Fresh data ready!");
      displayData(taskData.fresh_data.data);
      clearInterval(checkTask);
    }
  }, 2000);
}
```

### Python

```python
import requests
import time

API_URL = "http://localhost:5000"
headers = {"X-API-Key": "shopify_secure_key_2025"}

# Get cached data + trigger refresh
response = requests.get(
    f"{API_URL}/api/data",
    params={'start_row': 1, 'end_row': 100, 'refresh': 'true'},
    headers=headers
)

data = response.json()
print(f"Cached: {data['returned_count']} records")

# Poll for fresh data
if data.get('task_id'):
    while True:
        time.sleep(2)
        task_res = requests.get(f"{API_URL}/api/task/{data['task_id']}", headers=headers)
        task_data = task_res.json()

        if task_data['task_status'] == 'completed':
            print(f"Fresh: {task_data['fresh_data']['returned_count']} records")
            break
```

### cURL

```bash
# Get cached data + trigger refresh
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/api/data?refresh=true&start_row=1&end_row=100"

# Check task status
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/api/task/abc12345"

# Get metadata
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/api/metadata"
```

---

## 📊 How It Works

```
User Request (refresh=true)
    ↓
Step 1: Return cached data INSTANTLY (< 100ms)
    ↓
User sees data immediately! 😊
    ↓
Step 2: Background refresh starts (30-60s)
    ↓
Scrape fresh data → Update cache
    ↓
Step 3: User polls or gets notified
    ↓
Fresh data ready!
```

**Benefits:**

- Users never wait
- Always see data
- Auto-updates with fresh data
- One request gets both old & new data

---

## 📁 Project Structure

```
shopify-db-scrapping/
├── flask_app_enhanced.py     # Main API server
├── sync_worker.py             # Data scraper
├── export_data_fast.py        # Fast export tool
├── api_demo_enhanced.html     # Interactive demo
├── data_cache.json            # Cached data (auto-generated)
├── cookies.pkl                # Login cookies (auto-generated)
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker config
├── ENHANCED_API_DOCS.md       # Detailed API docs
└── README.md                  # This file
```

---

## 🔧 Configuration

Edit `flask_app_enhanced.py`:

```python
CACHE_FILE = "data_cache.json"  # Cache file path
API_KEY = "shopify_secure_key_2025"  # Your API key
```

---

## 📖 Documentation

- **Interactive Demo:** Open `api_demo_enhanced.html` in browser
- **Detailed API Docs:** See `ENHANCED_API_DOCS.md`
- **Code Examples:** Check usage examples above

---

## ⚡ Performance

For **107,296 records** (83 MB cache):

| Operation             | Time    |
| --------------------- | ------- |
| Get metadata          | ~0.001s |
| Get cached (100 rows) | ~0.01s  |
| Get cached (all)      | ~0.05s  |
| Background scrape     | 30-60s  |
| Export to JSON        | ~2s     |

---

## 🎯 Common Use Cases

### 1. Get All Data (Default)

```http
GET /api/data
```

### 2. Pagination

```http
# Page 1 (rows 1-100)
GET /api/data?start_row=1&end_row=100

# Page 2 (rows 101-200)
GET /api/data?start_row=101&end_row=200
```

### 3. Best UX (Cached + Refresh)

```http
GET /api/data?refresh=true&start_row=1&end_row=100
```

### 4. Export All Data

```bash
python export_data_fast.py
# Choose JSON or CSV format
```

---

## 🚢 Deployment

### Docker

```bash
docker build -t shopify-api .
docker run -p 5000:5000 shopify-api
```

### Local

```bash
python flask_app_enhanced.py
```

---

## 🔐 Security

- All endpoints require API key authentication
- Set your API key in `flask_app_enhanced.py`
- Use HTTPS in production
- Keep `cookies.pkl` secure

---

## 🐛 Troubleshooting

### API won't start

```bash
# Check if port 5000 is available
netstat -ano | findstr :5000

# Or use different port
# Edit flask_app_enhanced.py: app.run(port=5001)
```

### No cached data

```bash
# Run scraper first
python sync_worker.py
```

### Background refresh not working

- Check `update_in_progress` status
- Only one refresh runs at a time
- Check server logs for errors

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 🎉 Summary

**This API provides:**

- ✅ Instant cached responses (< 100ms)
- ✅ Background data refresh (30-60s)
- ✅ Row range support (chunking)
- ✅ Real-time updates (SSE)
- ✅ Fast data export
- ✅ Best user experience (no waiting!)

**Perfect for:**

- Dashboard applications
- Data analytics
- Real-time monitoring
- E-commerce reporting

---

**Questions? Check `ENHANCED_API_DOCS.md` or test with `api_demo_enhanced.html`!** 🚀
