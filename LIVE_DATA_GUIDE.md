# 🔴 LIVE DATA vs CACHED DATA - Quick Guide

## Problem Solved ✅

**Issue:** API was returning old/cached data instead of live data from database  
**Solution:** Added `force_fresh=true` parameter for live data on demand

---

## 📊 Two Modes Available

### 🟢 Mode 1: CACHED Data (Fast - Recommended for most use)

```bash
GET /fetch-data?limit=10&offset=0
```

**Features:**

- ⚡ **Super fast** (<50ms response)
- 💾 **Low memory** (<2MB)
- 📦 **Returns cached data** (updates every hour automatically)
- ✅ **Best for:** Regular queries, dashboards, frequent requests

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=10"
```

---

### 🔴 Mode 2: LIVE Data (Slower - Use when you need fresh data)

```bash
GET /fetch-data?force_fresh=true&limit=10
```

**Features:**

- 🔄 **Fetches from database RIGHT NOW** (scrapes phpMyAdmin)
- ⏱️ **Slower** (30-60 seconds wait while scraping)
- ✅ **Always fresh** (includes orders added in last minute)
- 💾 **Still optimized** (<2MB memory)
- ✅ **Best for:** When you MUST have the latest data

**Example:**

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?force_fresh=true&limit=10"
```

**What happens:**

1. API receives request with `force_fresh=true`
2. Immediately logs into phpMyAdmin
3. Downloads CSV from database (includes ALL latest orders)
4. Processes CSV and updates cache
5. Returns fresh data to you
6. Future requests (without `force_fresh`) use this new cache

---

## 🎯 When to Use Each Mode

### Use CACHED (default):

- ✅ Building a dashboard
- ✅ Regular monitoring
- ✅ Frequent API calls
- ✅ Don't need second-by-second updates
- ✅ Want fast responses

### Use LIVE (`force_fresh=true`):

- ✅ Just added a new order manually and want to see it NOW
- ✅ Critical operation requiring latest data
- ✅ Initial data pull
- ✅ Troubleshooting/debugging
- ✅ Don't mind waiting 30-60 seconds

---

## 📝 Complete API Examples

### 1. Get Cached Metadata (Fastest - <10ms)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?metadata_only=true"

# Response: {"count": 102845, "file_size_kb": 80174, "last_modified": "..."}
```

### 2. Get Cached Data (Fast - <100ms)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?limit=50&offset=0"

# Response: {"status":"success", "data": [{...}, {...}, ...]}
```

### 3. Get LIVE Fresh Data (Slow - 30-60s)

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?force_fresh=true&limit=50"

# Server logs:
# [Current time] LIVE data requested - triggering immediate sync
# [Current time] Sync started
# CSV downloaded, streaming to JSON...
# Processed 102850 records with ~2MB memory  ← NEW ORDER INCLUDED!
# [Current time] Sync complete - serving fresh data
#
# Response: {"status":"success", "data": [{NEW ORDER}, {...}, ...]}
```

### 4. Trigger Background Refresh (Returns Immediately)

```bash
curl -X POST -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/refresh"

# Response: {"status":"triggered"}
# Sync happens in background, doesn't block request
```

---

## 🔬 Testing It Works

### Test 1: Verify Cache Age

```bash
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/status"

# Shows when cache was last updated
```

### Test 2: Force Fresh Data

```bash
# This will take 30-60 seconds but gives you LIVE data
curl -w "\nTime: %{time_total}s\n" \
  -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?force_fresh=true&limit=5"

# Expected: 30-60s wait, then fresh data
```

### Test 3: Compare Cached vs Live

```bash
# Get cached count
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?metadata_only=true"
# Shows count: 102845

# Add a new order to database manually...

# Get LIVE count (will be higher if new order exists)
curl -H "X-API-Key: shopify_secure_key_2025" \
  "http://localhost:5000/fetch-data?force_fresh=true&metadata_only=true"
# Shows count: 102846 ← NEW ORDER DETECTED!
```

---

## ⚡ Performance Comparison

| Metric             | Cached Mode      | Live Mode (`force_fresh=true`) |
| ------------------ | ---------------- | ------------------------------ |
| **Response Time**  | <100ms           | 30-60 seconds                  |
| **Memory Usage**   | <2MB             | <2MB ✅                        |
| **Data Freshness** | Up to 1 hour old | Real-time fresh                |
| **Database Load**  | None             | Full scrape                    |
| **Use Case**       | Regular queries  | Critical/fresh data            |

---

## 🚀 Deployment Notes

### For Production:

```python
# Option 1: Use cached for speed (recommended)
response = requests.get(
    f"{API_URL}/fetch-data?limit=100&offset=0",
    headers={"X-API-Key": API_KEY}
)

# Option 2: Force fresh when critical
response = requests.get(
    f"{API_URL}/fetch-data?force_fresh=true&limit=100",
    headers={"X-API-Key": API_KEY}
)
```

### Auto-Refresh Strategy:

1. **Use cached data** for 99% of requests (fast)
2. **Run background sync** every hour (via cron or `sync_worker.py`)
3. **Use `force_fresh=true`** only when user explicitly needs latest data

---

## ✅ Summary

**Problem:** Old cached data  
**Solution:** Added `force_fresh=true` parameter

**Usage:**

- **Default (no params):** Fast cached data ⚡
- **`force_fresh=true`:** Live database scrape 🔴
- **Both modes:** Still <2MB memory ✅

**Now you have the best of both worlds:** Fast caching + Live data on demand! 🎉
