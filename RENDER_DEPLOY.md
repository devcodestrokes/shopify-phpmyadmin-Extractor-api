# 🚀 Render Deployment Guide

## 📋 Pre-Deployment Checklist

- ✅ Code pushed to GitHub
- ✅ API key configured in `flask_app.py`
- ✅ `requirements.txt` includes all dependencies
- ✅ `.gitignore` excludes data files

---

## 🎯 Step-by-Step Deployment

### 1. Prepare Your Code

```bash
# Make sure you're in the project directory
cd "c:\DivySApp\shopify db scrapping"

# Check git status
git status

# Add all files
git add .

# Commit
git commit -m "Production ready for Render"

# Push to GitHub
git push origin main
```

### 2. Create Render Web Service

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Select the repository: `shopify-phpmyadmin-Extractor-api`

### 3. Configure Service Settings

```
Name: shopify-data-api
Environment: Python 3
Region: Choose closest to your users
Branch: main
Root Directory: (leave empty)
Build Command: pip install -r requirements.txt
Start Command: gunicorn flask_app:app --bind 0.0.0.0:$PORT
```

### 4. Set Environment Variables

Click **Add Environment Variable** and add:

```
Key: API_KEY
Value: shopify_secure_key_2025
```

(Change the value to your secure API key)

### 5. Choose Plan

- **Free Plan**: Good for testing (sleeps after 15 min of inactivity)
- **Starter Plan**: $7/month, always on, better performance

### 6. Deploy!

Click **Create Web Service**

Render will:

1. Clone your repository
2. Install dependencies
3. Start the application
4. Give you a URL like: `https://shopify-data-api.onrender.com`

---

## ⏱️ Deployment Timeline

- **Build**: 2-3 minutes
- **First Request**: May take 30-60 seconds (if cache needs to be created)
- **Subsequent Requests**: < 100ms

---

## 🔗 Your API URL

After deployment, your API will be available at:

```
https://your-app-name.onrender.com
```

### Test Endpoints:

```bash
# Health check (no auth needed)
curl https://your-app-name.onrender.com/health

# Get metadata
curl -H "X-API-Key: your_api_key" \
  https://your-app-name.onrender.com/api/metadata

# Get data
curl -H "X-API-Key: your_api_key" \
  https://your-app-name.onrender.com/api/data?start_row=1&end_row=10
```

---

## 📊 Monitoring

### View Logs

1. Go to your service in Render dashboard
2. Click **Logs** tab
3. Monitor real-time logs

### Check Status

```bash
curl https://your-app-name.onrender.com/health
```

Expected response:

```json
{
  "status": "ok",
  "cache_exists": true,
  "update_in_progress": false
}
```

---

## 🔄 Auto-Deployment

Render will automatically redeploy when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update API"
git push origin main

# Render will auto-deploy in 2-3 minutes
```

---

## ⚠️ Important Notes

### Free Tier Limitations:

- **Sleeps after 15 minutes** of inactivity
- **First request after sleep**: 30-60 seconds startup time
- **750 hours/month**: Free tier limit

### Data Persistence:

- **Cache file** (`data_cache.json`) is NOT persistent on free tier
- Cache will be recreated on each deployment
- For persistent cache, upgrade to paid plan + add persistent disk

### Environment Variables:

- Always set `API_KEY` in Render dashboard
- Never commit API keys to GitHub
- Update in Render dashboard, not in code

---

## 🐛 Troubleshooting

### Deployment Failed

**Check Build Logs:**

1. Go to Render dashboard
2. Click on your service
3. Click **Events** tab
4. Look for error messages

**Common Issues:**

- Missing dependencies in `requirements.txt`
- Python version mismatch
- Syntax errors in code

### App Won't Start

**Check Logs:**

```
# In Render dashboard → Logs tab
Look for startup errors
```

**Common Issues:**

- Port binding (use `$PORT` environment variable)
- Missing `gunicorn` in requirements.txt
- Import errors

### API Not Responding

**Test Health Endpoint:**

```bash
curl https://your-app-name.onrender.com/health
```

**If health check fails:**

- Check if app is sleeping (free tier)
- Check logs for errors
- Verify deployment completed successfully

### Authentication Errors

**Verify API Key:**

```bash
# Check environment variable in Render dashboard
# Make sure it matches what you're sending
```

---

## 🔐 Security Best Practices

1. **Use Strong API Keys**

   ```python
   # DON'T: API_KEY = "123456"
   # DO: API_KEY = "sk_live_hj32k4h23kj4h32k4j23h4k"
   ```

2. **Use Environment Variables**

   - Set API key in Render dashboard
   - Don't hardcode in `flask_app.py`

3. **Enable HTTPS**

   - Render provides free HTTPS
   - All traffic is encrypted

4. **Rate Limiting** (Optional)
   - Consider adding Flask-Limiter for production

---

## 📈 Scaling

### Upgrade Options:

**Starter Plan ($7/month):**

- Always on (no sleep)
- 512 MB RAM
- Better performance

**Standard Plan ($25/month):**

- 2 GB RAM
- Persistent disk available
- Higher traffic capacity

### Add Persistent Disk:

1. Go to service settings
2. Click **Disks**
3. Add disk mounted at `/data`
4. Update `flask_app.py` cache path

---

## 🎉 You're Live!

Your Shopify Data API is now:

- ✅ Deployed on Render
- ✅ Auto-deploying on git push
- ✅ Serving data instantly
- ✅ Production-ready

---

## 📞 Need Help?

- **Render Docs**: https://docs.render.com/
- **Render Support**: support@render.com
- **GitHub Issues**: Check your repository issues

---

**Your API is ready! Share the URL with your team and start building!** 🚀
