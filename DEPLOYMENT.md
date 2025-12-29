# Render Deployment Checklist

## Pre-Deployment

- [ ] **Update API Key** in `flask_app.py`

  ```python
  API_KEY = "your_production_secure_key_2025"
  ```

- [ ] **Test locally**

  ```bash
  python flask_app.py
  python test_api.py
  ```

- [ ] **Commit all changes to Git**
  ```bash
  git add .
  git commit -m "Added smart caching API"
  git push origin main
  ```

---

## Render Deployment - Option 1: API + Background Worker

### Step 1: Create Web Service (API)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect Repository**: Select your Git repository
4. **Configure Service**:

   - **Name**: `shopify-data-api`
   - **Region**: Select closest to your users
   - **Branch**: `main`
   - **Root Directory**: (leave blank or path to project)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python flask_app.py`
   - **Plan**: Free (or paid for production)

5. **Environment Variables** (Optional):

   - Click "Advanced" → "Add Environment Variable"
   - `SHOPIFY_API_KEY` = `your_secure_key` (if you modify code to use env vars)

6. **Click "Create Web Service"**

7. **Wait for deployment** (2-5 minutes)

8. **Note your API URL**: `https://shopify-data-api.onrender.com`

9. **Test the API**:
   ```bash
   curl -H "X-API-Key: your_secure_key" \
     https://shopify-data-api.onrender.com/health
   ```

### Step 2: Create Background Worker

1. **Click "New +"** → **"Background Worker"**
2. **Connect same repository**
3. **Configure Worker**:

   - **Name**: `shopify-data-worker`
   - **Region**: Same as API service
   - **Branch**: `main`
   - **Root Directory**: (same as API)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python sync_worker.py`
   - **Plan**: Free

4. **Click "Create Background Worker"**

5. **Monitor logs** to verify worker is running

✅ **Done! Your API is live with automatic hourly data refresh!**

---

## Render Deployment - Option 2: API Only + Cron Job

### Step 1: Create Web Service

Follow **Step 1** from Option 1 above.

### Step 2: Add Cron Job

1. **In Render Dashboard**, find your newly created service
2. **Click on the service** → **"Cron Jobs"** tab
3. **Click "Add Cron Job"**
4. **Configure**:

   - **Schedule**: `0 * * * *` (every hour)
   - **Command**:
     ```bash
     curl -X POST -H "X-API-Key: your_secure_key" https://shopify-data-api.onrender.com/refresh
     ```

5. **Save**

✅ **Done! Your API will refresh data every hour via cron job!**

---

## Post-Deployment

### 1. Test Your Deployed API

Update `test_api.py` with your Render URL:

```python
API_URL = "https://shopify-data-api.onrender.com"
API_KEY = "your_secure_key"
```

Run tests:

```bash
python test_api.py
```

### 2. Initial Data Sync

**Option A: Let worker run** (if you deployed worker)

- Wait for sync_worker.py to complete first run (~5 minutes)

**Option B: Manual trigger** (if API only)

```bash
curl -X POST \
  -H "X-API-Key: your_secure_key" \
  https://shopify-data-api.onrender.com/refresh
```

### 3. Verify Data

Check status:

```bash
curl -H "X-API-Key: your_secure_key" \
  https://shopify-data-api.onrender.com/status
```

Expected response:

```json
{
  "api_status": "online",
  "cache_exists": true,
  "cache_age_minutes": 5,
  "update_in_progress": false
}
```

Fetch data:

```bash
curl -H "X-API-Key: your_secure_key" \
  https://shopify-data-api.onrender.com/fetch-data
```

### 4. Update Frontend/Client Apps

Update your client code with the new API URL:

**JavaScript:**

```javascript
const API_URL = "https://shopify-data-api.onrender.com";
const API_KEY = "your_secure_key";

async function getData() {
  const response = await fetch(`${API_URL}/fetch-data?refresh=true`, {
    headers: { "X-API-Key": API_KEY },
  });
  return await response.json();
}
```

**Python:**

```python
API_URL = "https://shopify-data-api.onrender.com"
API_KEY = "your_secure_key"

response = requests.get(
    f"{API_URL}/fetch-data?refresh=true",
    headers={'X-API-Key': API_KEY}
)
```

### 5. Set Up Monitoring (Optional)

**Uptime Monitoring** (Free services):

- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- Monitor endpoint: `https://your-api.onrender.com/health`

**Configure alerts**:

- Email/SMS when API goes down
- Check every 5 minutes

### 6. Test Interactive Demo

Update `demo.html` with your production URL:

```javascript
// In demo.html, update the default API URL
const API_URL = "https://shopify-data-api.onrender.com";
```

Then open `demo.html` and test all features.

---

## Troubleshooting

### ❌ API returns 503 "No cached data"

**Cause**: Initial sync not completed yet

**Solutions**:

1. Check if background worker is running (Render logs)
2. Manually trigger: `curl -X POST -H "X-API-Key: key" https://your-api.onrender.com/refresh`
3. Wait 5-10 minutes for first sync
4. Check status: `curl -H "X-API-Key: key" https://your-api.onrender.com/status`

### ❌ Build fails on Render

**Common causes**:

- Missing `requirements.txt`
- Wrong Python version
- Dependencies not compatible

**Solutions**:

1. Check build logs on Render
2. Verify `requirements.txt` is committed
3. Try locally: `pip install -r requirements.txt`

### ❌ Worker keeps crashing

**Common causes**:

- ChromeDriver not available on Render
- Selenium issues
- Memory limits

**Solutions**:

1. Check worker logs
2. Render might not support Selenium (check their docs)
3. Consider alternative: Use API-only with manual /refresh calls

### ❌ Data not updating

**Check**:

1. Worker logs (if using background worker)
2. Cron job execution (if using cron)
3. Call `/status` to see cache age
4. Manually trigger: `POST /refresh`

### ❌ CORS errors in browser

**Solution**: CORS is enabled in `flask_app.py`. If still having issues:

```python
# In flask_app.py, update CORS settings
CORS(app, origins=["https://your-frontend-domain.com"])
```

---

## Maintenance

### Regular Tasks

**Weekly**:

- [ ] Check API health: `/health`
- [ ] Verify cache age: `/status`
- [ ] Review Render logs for errors

**Monthly**:

- [ ] Rotate API key (if needed)
- [ ] Review data quality
- [ ] Check Render resource usage

### Updating Code

When you make changes:

1. **Test locally** first

   ```bash
   python flask_app.py
   python test_api.py
   ```

2. **Commit and push**

   ```bash
   git add .
   git commit -m "Updated feature X"
   git push origin main
   ```

3. **Render auto-deploys** (if enabled)

   - Or manually trigger deploy in Render dashboard

4. **Verify deployment**
   ```bash
   curl https://your-api.onrender.com/health
   ```

### Scaling

If you need better performance:

1. **Upgrade Render plan** (Free → Starter → Standard)
2. **Add Redis caching** for ultra-fast responses
3. **Use CDN** for global distribution
4. **Enable database** instead of JSON cache

---

## Security Reminder

Before going live:

- [ ] **Change API_KEY** to a strong, unique value
- [ ] **Don't commit** API keys to Git (use environment variables)
- [ ] **Enable HTTPS** (automatic on Render)
- [ ] **Add rate limiting** if expecting high traffic
- [ ] **Monitor logs** for suspicious activity
- [ ] **Rotate keys** periodically

---

## Quick Reference

### Your API Endpoints

```
Base URL: https://your-api.onrender.com

GET  /health                    - Health check (no auth)
GET  /status                    - Cache status
GET  /fetch-data                - Get cached data
GET  /fetch-data?refresh=true   - Get cached + trigger refresh
GET  /fetch-data?stream=true    - SSE stream
POST /refresh                   - Manual refresh
```

### API Key Header

```
X-API-Key: your_secure_key
```

### Testing Commands

```bash
# Health
curl https://your-api.onrender.com/health

# Status
curl -H "X-API-Key: key" https://your-api.onrender.com/status

# Fetch
curl -H "X-API-Key: key" https://your-api.onrender.com/fetch-data

# Refresh
curl -X POST -H "X-API-Key: key" https://your-api.onrender.com/refresh
```

---

## Need Help?

- 📖 Check **README.md** for comprehensive docs
- 📚 Review **API_USAGE.md** for endpoint details
- 🎨 Use **demo.html** for interactive testing
- 🧪 Run **test_api.py** for automated validation
- 📝 Read **IMPLEMENTATION_SUMMARY.md** for overview

---

Happy Deploying! 🚀
