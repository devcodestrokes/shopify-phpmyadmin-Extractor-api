# 🚀 Shopify Data Scraper & API

A high-performance API that scrapes Shopify order data, caches it, and serves it instantly with optional background refresh.

## ✨ Features

- ⚡ **Instant Response** - Returns cached data in < 100ms
- 🔄 **Background Refresh** - Scrapes fresh data without blocking users
- 📊 **Row Ranges** - Pagination support via start_row/end_row
- 📡 **Server-Sent Events** - Real-time updates via SSE
- 🔑 **API Key Authentication** - Secure access control
- ✨ **Auto JSON Parsing** - Destination field automatically parsed to JSON object

---

## � Render Deployment

### Quick Deploy

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create Web Service on Render:**

   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Use these settings:

   ```
   Name: shopify-data-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn flask_app:app
   ```

3. **Set Environment Variables:**

   ```
   API_KEY=your_secure_api_key_here
   ```

4. **Deploy!** 🚀

### Important Notes

- Render will auto-deploy on every git push
- First deployment may take 2-3 minutes
- Cache file (`data_cache.json`) will be created on first scrape
- Use Render's persistent disk for cache persistence (optional)

---

## 📦 Local Installation

```bash
# Clone repository
git clone <your-repo-url>
cd shopify-db-scrapping

# Install dependencies
pip install -r requirements.txt

# Run locally
python flask_app.py
```

---

## 🎯 How to Use This API

### Step 1: Get Your API URL

**After Render deployment:**

```
https://your-app-name.onrender.com
```

**Local development:**

```
http://localhost:5000
```

### Step 2: Get Your API Key

Set in Render environment variables or `flask_app.py`:

```
API_KEY: shopify_secure_key_2025
```

### Step 3: Make Requests

All requests need the API key in headers:

```http
X-API-Key: shopify_secure_key_2025
```

---

## � Common Use Cases

### 1️⃣ Get All Data (Simple)

**Request:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-app.onrender.com/api/data
```

**JavaScript:**

```javascript
const response = await fetch("https://your-app.onrender.com/api/data", {
  headers: { "X-API-Key": "shopify_secure_key_2025" },
});

const data = await response.json();
console.log(`Total: ${data.total_count} records`);
console.log(`Returned: ${data.returned_count} records`);

// Access destination fields directly
data.data.forEach((order) => {
  console.log(`Order: ${order.name}`);
  console.log(`Customer: ${order.destination.name}`);
  console.log(`City: ${order.destination.city}`);
});
```

---

### 2️⃣ Get Specific Rows (Pagination)

**Get first 100 records:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://your-app.onrender.com/api/data?start_row=1&end_row=100"
```

**Get next 100 records:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://your-app.onrender.com/api/data?start_row=101&end_row=200"
```

**JavaScript example:**

```javascript
// Page 1
const page1 = await fetch(
  "https://your-app.onrender.com/api/data?start_row=1&end_row=100",
  {
    headers: { "X-API-Key": "shopify_secure_key_2025" },
  }
);

// Page 2
const page2 = await fetch(
  "https://your-app.onrender.com/api/data?start_row=101&end_row=200",
  {
    headers: { "X-API-Key": "shopify_secure_key_2025" },
  }
);
```

---

### 3️⃣ Get Fresh Data (Background Refresh)

**Best for UX** - Returns cached data instantly, then fetches fresh data in background

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://your-app.onrender.com/api/data?refresh=true&start_row=1&end_row=100"
```

**Full JavaScript Example:**

```javascript
async function getDataWithRefresh() {
  const API_URL = "https://your-app.onrender.com";
  const API_KEY = "shopify_secure_key_2025";

  // Step 1: Get cached data + trigger refresh
  const response = await fetch(
    `${API_URL}/api/data?refresh=true&start_row=1&end_row=100`,
    {
      headers: { "X-API-Key": API_KEY },
    }
  );

  const data = await response.json();

  // Step 2: Show cached data immediately
  console.log("Showing cached data...");
  displayData(data.data);

  // Step 3: Poll for fresh data
  if (data.task_id) {
    console.log("Refreshing in background...");

    const checkTask = setInterval(async () => {
      const taskRes = await fetch(`${API_URL}/api/task/${data.task_id}`, {
        headers: { "X-API-Key": API_KEY },
      });

      const taskData = await taskRes.json();

      if (taskData.task_status === "completed") {
        console.log("Fresh data ready!");
        displayData(taskData.fresh_data.data);
        clearInterval(checkTask);
      }
    }, 2000); // Check every 2 seconds
  }
}

function displayData(orders) {
  orders.forEach((order) => {
    console.log(`
      Order: ${order.name}
      Customer: ${order.destination.name}
      City: ${order.destination.city}
      Total: $${order.total_price}
    `);
  });
}
```

---

### 4️⃣ Get Just the Count (Fast)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  https://your-app.onrender.com/api/metadata
```

**Response:**

```json
{
  "total_count": 107296,
  "file_size_kb": 85548.4,
  "file_size_mb": 83.54,
  "last_modified": "Thu Jan 16 14:00:00 2026"
}
```

---

### 5️⃣ Real-time Updates (SSE)

**For live dashboards** - Streams cached data, then fresh data when ready

```javascript
function streamData() {
  const eventSource = new EventSource(
    "https://your-app.onrender.com/api/data/fresh?start_row=1&end_row=100"
  );

  eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data);

    switch (update.type) {
      case "cached":
        console.log("Cached data:", update.data);
        displayData(update.data.data);
        break;

      case "status":
        console.log("Status:", update.message);
        break;

      case "fresh":
        console.log("Fresh data:", update.data);
        displayData(update.data.data);
        break;

      case "complete":
        console.log("Complete!");
        eventSource.close();
        break;
    }
  };
}
```

---

## �📚 API Endpoints Reference

### 🔹 Get Data

```http
GET /api/data
```

**Query Parameters:**

- `start_row` (optional): Starting row number (1-indexed)
- `end_row` (optional): Ending row number (inclusive)
- `refresh` (optional): Set to `true` to trigger background refresh
- `parse_json` (optional): Set to `false` to keep destination as string (default: `true`)

**Examples:**

```bash
# Get all data (destination auto-parsed to JSON)
curl -H "X-API-Key: your_api_key" https://your-app.onrender.com/api/data

# Get rows 1-100
curl -H "X-API-Key: your_api_key" https://your-app.onrender.com/api/data?start_row=1&end_row=100

# Get cached data + trigger background refresh
curl -H "X-API-Key: your_api_key" https://your-app.onrender.com/api/data?refresh=true&start_row=1&end_row=100
```

### 🔹 Get Metadata

```http
GET /api/metadata
```

Returns total count and cache info without loading full data.

**Example:**

```bash
curl -H "X-API-Key: your_api_key" https://your-app.onrender.com/api/metadata
```

### 🔹 Real-time Updates (SSE)

```http
GET /api/data/fresh
```

Streams cached data immediately, then fresh data when ready.

### 🔹 Check Background Task

```http
GET /api/task/{task_id}
```

Check status of background refresh task.

### 🔹 Health Check

```http
GET /health
```

No authentication required. Returns API status.

---

## 🔐 Authentication

All endpoints (except `/health`) require API key in headers:

```http
X-API-Key: your_api_key_here
```

**Set your API key in `flask_app.py`:**

```python
API_KEY = "your_secure_api_key_here"
```

---

## ✨ Destination Field Auto-Parsing

By default, the `destination` field is automatically parsed from escaped JSON string to JSON object:

**Before (Raw String):**

```json
{
  "destination": "\"{\\\"first_name\\\":\\\"John\\\",\\\"city\\\":\\\"NYC\\\"}\""
}
```

**After (Parsed JSON):**

```json
{
  "destination": {
    "first_name": "John",
    "last_name": "Doe",
    "address1": "123 Main St",
    "city": "NYC",
    "country": "United States",
    "latitude": 40.7128,
    "longitude": -74.006
  }
}
```

**Disable parsing:**

```http
GET /api/data?parse_json=false
```

---

## 💻 Usage Examples

### JavaScript

```javascript
const API_URL = "https://your-app.onrender.com";
const API_KEY = "your_api_key";

// Get data with background refresh
const response = await fetch(
  `${API_URL}/api/data?refresh=true&start_row=1&end_row=100`,
  {
    headers: { "X-API-Key": API_KEY },
  }
);

const data = await response.json();

// Show cached data immediately
console.log(`${data.returned_count} records`);
data.data.forEach((order) => {
  // Access destination fields directly!
  console.log(`Order: ${order.name}`);
  console.log(`Customer: ${order.destination.name}`);
  console.log(`City: ${order.destination.city}`);
});

// Poll for fresh data
if (data.task_id) {
  const checkTask = setInterval(async () => {
    const taskRes = await fetch(`${API_URL}/api/task/${data.task_id}`, {
      headers: { "X-API-Key": API_KEY },
    });

    const taskData = await taskRes.json();
    if (taskData.task_status === "completed") {
      console.log("Fresh data ready!");
      clearInterval(checkTask);
    }
  }, 2000);
}
```

### Python

```python
import requests

API_URL = 'https://your-app.onrender.com'
API_KEY = 'your_api_key'
headers = {'X-API-Key': API_KEY}

# Get cached data + trigger refresh
response = requests.get(
    f'{API_URL}/api/data',
    params={'start_row': 1, 'end_row': 100, 'refresh': 'true'},
    headers=headers
)

data = response.json()
print(f"Cached: {data['returned_count']} records")

# Access destination fields
for order in data['data']:
    print(f"Order: {order['name']}")
    print(f"Customer: {order['destination']['name']}")
    print(f"City: {order['destination']['city']}")
```

---

## 📊 Response Format

### Success Response

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
    {
      "id": "1",
      "name": "#1037",
      "customer_id": "1",
      "total_price": "13.93",
      "payment_status": "paid",
      "destination": {
        "first_name": "Bhakti",
        "last_name": "Admin",
        "address1": "6-8 Great Marlborough Street",
        "city": "Manchester",
        "country": "United Kingdom"
      }
    }
  ],
  "refresh_triggered": true,
  "task_id": "abc12345",
  "message": "Returning cached data. Fresh data being fetched in background."
}
```

---

## 🎯 How It Works

```
User Request (with refresh=true)
    ↓
Step 1: Return cached data INSTANTLY (< 100ms)
    ↓
User sees data immediately! 😊
    ↓
Step 2: Background refresh starts (30-60s)
    ↓
Scrapes fresh Shopify data → Updates cache
    ↓
Step 3: User polls task status or receives SSE update
    ↓
Fresh data ready!
```

**Benefits:**

- Users never wait for scraping
- Always see data immediately
- Auto-updates with fresh data
- One request handles both cached and fresh data

---

## 📁 Project Structure

```
shopify-db-scrapping/
├── flask_app.py           # Main API server
├── sync_worker.py         # Shopify data scraper
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration (optional)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── data_cache.json       # Cached data (auto-generated)
└── cookies.pkl           # Session cookies (auto-generated)
```

---

## 🔧 Configuration

Edit `flask_app.py`:

```python
# Line 14-15
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
API_KEY = "your_secure_api_key_here"  # Change this!
```

---

## ⚡ Performance

For **107,296 records** (83 MB cache):

| Operation             | Time    |
| --------------------- | ------- |
| Get metadata          | ~0.001s |
| Get cached (100 rows) | ~0.01s  |
| Get cached (all)      | ~0.05s  |
| Background scrape     | 30-60s  |

---

## Troubleshooting

### API won't start locally

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use different port
# Edit flask_app.py line 341: app.run(port=5001)
```

### No cached data

```bash
# Run scraper manually to create cache
python sync_worker.py
```

### Authentication errors

- Verify API key matches in headers and `flask_app.py`
- Check header format: `X-API-Key: your_key`

---

## 📝 Environment Variables (Render)

Set these in Render dashboard:

```bash
API_KEY=your_secure_api_key_here
PYTHON_VERSION=3.11.0
```

---

## 🎉 Summary

**This API provides:**

- ✅ Instant cached responses (< 100ms)
- ✅ Background data refresh (no user waiting)
- ✅ Row range support for pagination
- ✅ Real-time updates via SSE
- ✅ Auto-parsed destination fields
- ✅ Production-ready for Render deployment

**Perfect for:**

- E-commerce dashboards
- Order management systems
- Data analytics platforms
- Real-time monitoring

---

## 📞 Support

For issues or questions:

1. Check this README
2. Review API responses for error messages
3. Check Render logs for deployment issues

---

**Ready to deploy? Push to GitHub and deploy on Render!** 🚀
