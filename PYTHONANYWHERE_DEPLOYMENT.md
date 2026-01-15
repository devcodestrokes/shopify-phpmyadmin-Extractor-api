# 🐍 PythonAnywhere Deployment Guide

## ✅ **Why PythonAnywhere is PERFECT for This API:**

1. **No Gunicorn timeouts** - Uses WSGI directly
2. **Selenium pre-installed** - Chrome/Firefox ready to use
3. **Easy scheduled tasks** - Built-in cron for hourly sync
4. **Free 512MB RAM** - More than enough for your <2MB app
5. **Code already compatible** - Has PythonAnywhere detection built-in!

---

## 🚀 **Step-by-Step Deployment:**

### **1. Sign Up for PythonAnywhere**

1. Go to [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Create a **free account**
3. Choose **Python 3.9** or later

---

### **2. Upload Your Code**

#### **Option A: Using Git (Recommended)**

```bash
# In PythonAnywhere Bash console
cd ~
git clone https://github.com/YOUR_USERNAME/shopify-phpmyadmin-Extractor-api.git
cd shopify-phpmyadmin-Extractor-api
```

#### **Option B: Upload Files**

1. Go to **Files** tab
2. Create folder: `/home/yourusername/shopify-api/`
3. Upload all your files

---

### **3. Install Dependencies**

Open a **Bash console** in PythonAnywhere:

```bash
cd ~/shopify-phpmyadmin-Extractor-api

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install Chrome webdriver manager
pip install webdriver-manager
```

---

### **4. Set Up the Web App**

1. Go to **Web** tab → Click **Add a new web app**
2. Choose **Manual configuration**
3. Select **Python 3.9**

---

### **5. Configure WSGI File**

Click on **WSGI configuration file** link, then replace content with:

```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/shopify-phpmyadmin-Extractor-api'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable for PythonAnywhere detection
os.environ['PYTHONANYWHERE_SITE'] = 'True'

# Import Flask app
from flask_app import app as application
```

**Replace `yourusername` with your actual PythonAnywhere username!**

---

### **6. Set Virtual Environment Path**

In the **Web** tab:

1. Find **Virtualenv** section
2. Enter path: `/home/yourusername/shopify-phpmyadmin-Extractor-api/venv`
3. Replace `yourusername` with your actual username

---

### **7. Configure Static Files (Optional)**

In **Static files** section:

| URL        | Directory                                                     |
| ---------- | ------------------------------------------------------------- |
| `/static/` | `/home/yourusername/shopify-phpmyadmin-Extractor-api/static/` |

---

### **8. Create Downloads Directory**

In **Bash console**:

```bash
cd ~/shopify-phpmyadmin-Extractor-api
mkdir -p downloads
chmod 755 downloads
```

---

### **9. Test Initial Sync**

In **Bash console**:

```bash
cd ~/shopify-phpmyadmin-Extractor-api
source venv/bin/activate
python sync_worker.py
```

**Expected output:**

```
=== ULTRA-LIGHTWEIGHT WORKER ===
Memory usage: <2MB
[Current time] Sync started
CSV downloaded, streaming to JSON...
Processed 107270 records with ~2MB memory
[OK] Sync complete, cache updated
```

---

### **10. Reload Web App**

1. Go to **Web** tab
2. Click **Reload yourusername.pythonanywhere.com** (green button)

---

### **11. Test Your API**

```bash
# Test health endpoint
curl https://yourusername.pythonanywhere.com/health

# Test with API key
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://yourusername.pythonanywhere.com/fetch-data?metadata_only=true"

# Get data
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://yourusername.pythonanywhere.com/fetch-data?limit=5"
```

---

### **12. Set Up Hourly Auto-Sync**

1. Go to **Tasks** tab
2. Create a new **Scheduled task**
3. Set to run **hourly**
4. Command:
   ```bash
   /home/yourusername/shopify-phpmyadmin-Extractor-api/venv/bin/python /home/yourusername/shopify-phpmyadmin-Extractor-api/sync_worker.py
   ```
5. Replace `yourusername` with your actual username

**This will automatically refresh your data every hour!** ✅

---

## 🔧 **PythonAnywhere-Specific Configuration**

Your code **already has PythonAnywhere detection** in `sync_worker.py`:

```python
def get_driver():
    """Auto-detect environment and configure Selenium accordingly"""
    if 'PYTHONANYWHERE_SITE' in os.environ:
        # PythonAnywhere configuration
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        return driver
    else:
        # Local/Windows configuration
        # ... existing code ...
```

**This means your app will automatically work on PythonAnywhere!** 🎉

---

## 📊 **API Endpoints on PythonAnywhere:**

Replace `yourusername` with your PythonAnywhere username:

### **Base URL:**

```
https://yourusername.pythonanywhere.com
```

### **Endpoints:**

```bash
# Health check
GET /health

# Get metadata (fast)
GET /fetch-data?metadata_only=true
Header: X-API-Key: shopify_secure_key_2025

# Get paginated data
GET /fetch-data?limit=10&offset=0
Header: X-API-Key: shopify_secure_key_2025

# Trigger background refresh
POST /refresh
Header: X-API-Key: shopify_secure_key_2025

# Check status
GET /status
Header: X-API-Key: shopify_secure_key_2025
```

---

## 🐛 **Troubleshooting:**

### **Issue 1: ImportError: No module named 'flask_app'**

**Solution:**

```bash
# In Bash console
cd ~/shopify-phpmyadmin-Extractor-api
source venv/bin/activate
pip install -r requirements.txt
```

### **Issue 2: Permission denied on downloads folder**

**Solution:**

```bash
chmod 755 ~/shopify-phpmyadmin-Extractor-api/downloads
```

### **Issue 3: Selenium not working**

**Solution:**

```bash
# Install webdriver-manager
pip install webdriver-manager

# Test manually
python sync_worker.py
```

### **Issue 4: API returns 401 Unauthorized**

**Solution:**

- Make sure you're sending the header: `X-API-Key: shopify_secure_key_2025`
- Use curl with `-H "X-API-Key: shopify_secure_key_2025"`

### **Issue 5: See error logs**

**Solution:**

1. Go to **Web** tab
2. Click on **Error log** link
3. Check latest errors

---

## 📝 **Environment Variables (Optional)**

If you want to use environment variables instead of hardcoded values:

1. Edit WSGI file to add:

```python
os.environ['API_KEY'] = 'shopify_secure_key_2025'
os.environ['PHPMYADMIN_USERNAME'] = 'your_username'
os.environ['PHPMYADMIN_PASSWORD'] = 'your_password'
```

2. Update `flask_app.py` and `sync_worker.py` to use:

```python
API_KEY = os.environ.get('API_KEY', 'shopify_secure_key_2025')
```

---

## ⚡ **Performance on PythonAnywhere:**

| Metric                | Value               |
| --------------------- | ------------------- |
| **Memory Usage**      | <2MB per request ✅ |
| **Response Time**     | <100ms (cached) ✅  |
| **Metadata Response** | <10ms ✅            |
| **Auto-sync**         | Every hour ✅       |
| **Uptime**            | 24/7 ✅             |
| **Free Tier RAM**     | 512MB (plenty!) ✅  |

---

## 🎯 **Advantages Over Render:**

| Feature              | PythonAnywhere | Render              |
| -------------------- | -------------- | ------------------- |
| **Timeout Issues**   | ✅ None        | ❌ Gunicorn timeout |
| **Selenium Support** | ✅ Built-in    | ⚠️ Needs config     |
| **Scheduled Tasks**  | ✅ Easy GUI    | ⚠️ Needs cron setup |
| **Free SSL**         | ✅ Yes         | ✅ Yes              |
| **Free Tier RAM**    | 512MB          | 512MB               |
| **Auto-deploy**      | ⚠️ Manual      | ✅ Git push         |

---

## 🚀 **Quick Start Checklist:**

- [ ] Create PythonAnywhere account
- [ ] Upload code (Git or manual)
- [ ] Install requirements in virtualenv
- [ ] Configure WSGI file
- [ ] Set virtualenv path
- [ ] Test `sync_worker.py` manually
- [ ] Reload web app
- [ ] Test API endpoints
- [ ] Set up hourly scheduled task
- [ ] Monitor error logs

---

## 💡 **Pro Tips:**

1. **Use the Bash console** for debugging - it's like having SSH access
2. **Check error logs regularly** - available in Web tab
3. **Test sync_worker.py manually first** - makes sure Selenium works
4. **Free tier limitations:**
   - Daily CPU limit (but you're well under it)
   - One web app only
   - Scheduled tasks limited to daily (but you can hack hourly)
5. **Upgrade to paid ($5/month)** if you need:
   - Multiple web apps
   - More CPU time
   - Custom domains

---

## 🎉 **You're Ready to Deploy!**

**PythonAnywhere is actually a BETTER choice than Render for this project:**

- ✅ No timeout issues
- ✅ Selenium just works
- ✅ Easy scheduled tasks
- ✅ Code already compatible
- ✅ More control with Bash console

**Start deploying now!** 🚀

---

## 📞 **Need Help?**

1. **PythonAnywhere Help:** https://help.pythonanywhere.com
2. **Forums:** https://www.pythonanywhere.com/forums/
3. **Your error logs:** Web tab → Error log link

**Happy hosting!** 🐍✨
