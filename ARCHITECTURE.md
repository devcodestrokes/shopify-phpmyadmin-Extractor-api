# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │ Browser  │    │  Mobile  │    │  Python  │    │  Node.js │    │
│   │   App    │    │   App    │    │  Script  │    │   App    │    │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    │
└────────┼──────────────┼───────────────┼───────────────┼────────────┘
         │              │               │               │
         └──────────────┴───────────────┴───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   HTTPS Request   │
                    │  X-API-Key Header │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
┌────────▼──────────────────────────────────────────────────────────┐
│                      FLASK API SERVER                              │
│                      (flask_app.py)                                │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  ENDPOINTS:                                              │    │
│  │  • GET  /health        → Health check (no auth)    [1]   │    │
│  │  • GET  /status        → Cache status              [2]   │    │
│  │  • GET  /fetch-data    → Cached data (< 100ms)     [3]   │    │
│  │  • GET  /fetch-data?refresh=true  → Cache + Update [4]  │    │
│  │  • GET  /fetch-data?stream=true   → SSE Stream     [5]  │    │
│  │  • POST /refresh       → Manual trigger            [6]   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  CACHING LOGIC:                                          │    │
│  │  1. Authenticate (API Key)                               │    │
│  │  2. Read cache → Return instantly                        │    │
│  │  3. (Optional) Trigger background refresh                │    │
│  └──────────────────────────────────────────────────────────┘    │
└────────┬───────────────────────────┬─────────────────────────────┘
         │                           │
         │ [INSTANT]                 │ [ASYNC]
         │ < 100ms                   │ Trigger if needed
         │                           │
         ▼                           ▼
┌────────────────────┐    ┌──────────────────────────────┐
│   CACHE STORAGE    │    │   BACKGROUND THREAD          │
│                    │    │                              │
│  data_cache.json   │◄───┤  async update worker         │
│                    │    │                              │
│  📦 102,052 records│    │  Calls sync_worker.py        │
│  💾 81 MB          │    │  perform_sync()              │
│  ⏰ Updated: Now   │    └────────┬─────────────────────┘
└────────────────────┘             │
                                   │ [BACKGROUND]
                                   │ 2-5 minutes
                                   ▼
                    ┌──────────────────────────────┐
                    │   SYNC WORKER                │
                    │   (sync_worker.py)           │
                    │                              │
                    │  🔄 Runs every hour          │
                    │  OR on-demand trigger        │
                    │                              │
                    │  Process:                    │
                    │  1. Launch Selenium          │
                    │  2. Login to phpMyAdmin      │
                    │  3. Export data (CSV)        │
                    │  4. Convert to JSON          │
                    │  5. Update cache file        │
                    └────────┬─────────────────────┘
                             │
                             │ [WEB SCRAPING]
                             │ Selenium + ChromeDriver
                             │
                             ▼
                  ┌──────────────────────────┐
                  │   DATA SOURCE            │
                  │                          │
                  │   phpMyAdmin             │
                  │   Shopify Database       │
                  │                          │
                  │   🗄️ Orders Table        │
                  └──────────────────────────┘
```

## Data Flow Scenarios

### Scenario 1: Simple Fetch (Instant Response)

```
User Request
    │
    ▼
GET /fetch-data
    │
    ├─ 1. Validate API Key ✓
    │
    ├─ 2. Read data_cache.json
    │     (< 100ms)
    │
    └─ 3. Return JSON Response ✅
         {"status": "success", "count": 102052, ...}
```

### Scenario 2: Fetch with Background Refresh

```
User Request
    │
    ▼
GET /fetch-data?refresh=true
    │
    ├─ 1. Validate API Key ✓
    │
    ├─ 2. Read data_cache.json
    │     (< 100ms)
    │
    ├─ 3. Return JSON Response ✅
    │     {"status": "success", "count": 102052,
    │      "_info": "Background refresh triggered"}
    │
    └─ 4. Spawn Background Thread 🔄
              │
              ├─ Wait for completion
              │  (2-5 minutes)
              │
              ├─ Scrape new data
              │
              └─ Update cache ✨

Next request gets fresh data!
```

### Scenario 3: SSE Streaming

```
User Request
    │
    ▼
GET /fetch-data?stream=true&refresh=true
    │
    ├─ 1. Validate API Key ✓
    │
    ├─ 2. Open SSE Connection 📡
    │
    ├─ 3. Send cached data
    │     event: {"type": "cached", "payload": {...}}
    │     ⚡ INSTANT
    │
    ├─ 4. Trigger background refresh
    │     (2-5 minutes)
    │
    ├─ 5. Wait for refresh completion ⏳
    │
    ├─ 6. Send updated data
    │     event: {"type": "updated", "payload": {...}}
    │     ✅ FRESH
    │
    └─ 7. Close connection
          event: {"type": "done"}
          🏁 COMPLETE
```

### Scenario 4: Manual Refresh

```
Admin Request
    │
    ▼
POST /refresh
    │
    ├─ 1. Validate API Key ✓
    │
    ├─ 2. Check if update in progress
    │     │
    │     ├─ Yes → Return 202 "already in progress"
    │     │
    │     └─ No  → Trigger background refresh
    │
    └─ 3. Return 202 Accepted
         {"status": "triggered"}

(Background refresh runs independently)
```

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│                   MAIN THREAD                           │
│                   (Flask App)                           │
│                                                         │
│  • Handles HTTP Requests                               │
│  • Reads cache (thread-safe with lock)                 │
│  • Returns responses                                   │
│  • Spawns worker threads when needed                   │
└─────────────┬───────────────────────────────────────────┘
              │
              │ Spawns (when refresh=true)
              ▼
┌─────────────────────────────────────────────────────────┐
│              BACKGROUND WORKER THREAD                   │
│              (daemon thread)                            │
│                                                         │
│  • Runs independently                                  │
│  • Calls sync_worker.perform_sync()                    │
│  • Updates cache (thread-safe with lock)               │
│  • Sets update_in_progress flag                        │
│  • Auto-terminates when done                           │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architectures

### Architecture A: Web Service + Background Worker (Recommended)

```
┌──────────────┐         ┌──────────────┐
│   Render     │         │   Render     │
│ Web Service  │         │   Worker     │
│              │         │              │
│ flask_app.py │         │sync_worker.py│
│              │         │              │
│ Serves API   │◄────────┤ Updates      │
│ requests     │  shares │ cache every  │
│              │  volume │ hour         │
└──────────────┘         └──────────────┘
        │                        │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Shared Volume  │
        │data_cache.json │
        └────────────────┘
```

### Architecture B: Web Service + Cron Job

```
┌──────────────┐         ┌──────────────┐
│   Render     │         │   Render     │
│ Web Service  │         │   Cron Job   │
│              │         │              │
│ flask_app.py │◄────────┤ Calls /refresh│
│              │  HTTP   │ every hour   │
│ Serves API + │         │              │
│ Background   │         │              │
│ refresh      │         │              │
└──────────────┘         └──────────────┘
```

### Architecture C: Single Web Service (On-Demand)

```
┌──────────────────────┐
│      Render          │
│    Web Service       │
│                      │
│   flask_app.py       │
│                      │
│ • Serves API         │
│ • Caches data        │
│ • Refreshes only     │
│   when requested     │
│   (refresh=true)     │
└──────────────────────┘
```

## Performance Characteristics

```
┌──────────────────────┬─────────────┬──────────────┐
│ Operation            │ Latency     │ Notes        │
├──────────────────────┼─────────────┼──────────────┤
│ GET /health          │ < 10ms      │ No auth      │
│ GET /status          │ < 50ms      │ File stat    │
│ GET /fetch-data      │ < 100ms     │ Read cache   │
│ Background refresh   │ 2-5 min     │ Selenium     │
│ SSE: First response  │ < 100ms     │ Cached data  │
│ SSE: Second response │ 2-5 min     │ Wait for sync│
└──────────────────────┴─────────────┴──────────────┘
```

## Cache Behavior Timeline

```
Time: 0:00         Request 1 arrives
      │
      ├─ Cache: Empty
      └─ Response: 503 "No cached data"

Time: 0:05         Initial sync runs (manual or worker)
      │
      ├─ Scrapes data (5 min)
      └─ Cache: Updated ✓

Time: 0:10         Request 2 arrives
      │
      ├─ Cache: Fresh (5 min old)
      └─ Response: 200 OK ✅

Time: 1:00         Worker auto-refresh (if deployed)
      │
      ├─ Scrapes data (5 min)
      └─ Cache: Updated ✓

Time: 1:05         Request 3 arrives
      │
      ├─ Cache: Fresh (5 min old)
      └─ Response: 200 OK ✅

... continues every hour
```

## Security Model

```
┌────────────────────┐
│  Incoming Request  │
└─────────┬──────────┘
          │
          ▼
    ┌─────────────┐     NO      ┌──────────────┐
    │ Has API Key?├─────────────►│ Return 401   │
    └─────┬───────┘              │ Unauthorized │
          │ YES                  └──────────────┘
          ▼
    ┌─────────────┐     NO      ┌──────────────┐
    │ Key Matches?├─────────────►│ Return 401   │
    └─────┬───────┘              │ Unauthorized │
          │ YES                  └──────────────┘
          ▼
    ┌─────────────┐
    │ Process     │
    │ Request ✅  │
    └─────────────┘
```

## Error Handling Flow

```
┌────────────────┐
│ API Request    │
└───────┬────────┘
        │
        ▼
   ┌──────────────┐
   │ Try Block:   │
   │ • Validate   │
   │ • Read cache │
   │ • Return     │
   └───┬──────────┘
       │
       ├─ Success ──────► Return 200 OK
       │
       ├─ No cache ─────► Return 503 "No data"
       │
       ├─ Bad auth ─────► Return 401 "Unauthorized"
       │
       ├─ Read error ───► Return 500 "Error reading cache"
       │
       └─ Exception ────► Return 500 "Internal error"
```

---

## Legend

```
Symbols:
  │  ├  └  ─   Flow lines
  ▼  ►        Direction arrows
  ✓  ✅       Success/Complete
  ❌          Error/Failure
  🔄          Refresh/Update
  ⏰  ⏳       Time/Wait
  📦  💾       Storage/Cache
  🗄️          Database
  📡          Streaming
  ⚡          Fast operation
  ✨          Fresh data
  🏁          Complete

Colors (conceptual):
  Green  = Fast path (< 100ms)
  Blue   = Background/Async (2-5 min)
  Red    = Error path
  Orange = Data update
```
