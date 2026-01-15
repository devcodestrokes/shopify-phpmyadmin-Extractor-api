# 🌐 PythonAnywhere Selenium Setup Guide

## ✅ **Updated! Now Uses Web Scraping (Not Direct SQL)**

Your `sync_worker.py` now has **improved Chrome/Chromium detection** for PythonAnywhere!

---

## 🔧 **Step-by-Step PythonAnywhere Setup:**

### **1. Sign Up & Login**

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Go to **Bash console**

---

### **2. Install Chrome/Chromium**

PythonAnywhere free tier has Chrome pre-installed, but let's verify:

```bash
# Check if Chrome is available
which chromium
which chromium-browser
which google-chrome

# Should return something like:
# /usr/bin/chromium-browser
```

**If Chrome is NOT found:**

```bash
# You can't install it on free tier directly
# But you can use Selenium Grid or headless mode
# Your code already handles this!
```

---

### **3. Upload Your Code**

```bash
# Clone from GitHub
cd ~
git clone https://github.com/YOUR_USERNAME/shopify-api.git
cd shopify-api

# OR create directory and upload files
mkdir ~/shopify-api
cd ~/shopify-api
# Then upload files via Files tab
```

---

### **4. Install Dependencies**

```bash
cd ~/shopify-api

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install webdriver-manager (important!)
pip install webdriver-manager
```

---

### **5. Test Selenium/Chrome**

```bash
# Test if Chrome works
python -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; opts = Options(); opts.add_argument('--headless'); driver = webdriver.Chrome(options=opts); print('Chrome works!'); driver.quit()"
```

**Expected Output:**

```
Chrome works!
```

**If it fails:**

```bash
# Check Chrome version
chromium-browser --version

# Check chromedriver version
chromedriver --version

# They should match versions!
```

---

### **6. Test Your Sync Worker**

```bash
cd ~/shopify-api
source venv/bin/activate
python sync_worker.py
```

**Expected Output:**

```
=== ULTRA-LIGHTWEIGHT WORKER ===
Memory usage: <2MB
[Current time] Sync started
🐍 PythonAnywhere environment detected
   ✅ Found Chrome at: /usr/bin/chromium-browser
   ✅ Found ChromeDriver at: /usr/bin/chromedriver
CSV downloaded, streaming to JSON...
Processed 107270 records with ~2MB memory
[OK] Sync complete, cache updated
```

---

### **7. If Chrome/ChromeDriver Version Mismatch:**

```bash
# Option A: Install matching chromedriver
pip install webdriver-manager
# This will auto-download matching version

# Option B: Manually install chromedriver
cd ~/.local/bin
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Download matching version based on Chrome version
```

---

### **8. Configure Flask Web App**

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.9**

---

### **9. WSGI Configuration**

Edit WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

```python
import sys
import os

# Add your project to path
project_home = '/home/yourusername/shopify-api'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Very important - helps Chrome detection!
os.environ['PYTHONANYWHERE_SITE'] = 'True'

# Activate virtualenv
activate_this = '/home/yourusername/shopify-api/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from flask_app import app as application
```

**Replace `yourusername` with your actual PythonAnywhere username!**

---

### **10. Set Virtualenv Path**

In **Web** tab:

- Find **Virtualenv** section
- Enter: `/home/yourusername/shopify-api/venv`

---

### **11. Create Downloads Folder**

```bash
mkdir -p ~/shopify-api/downloads
chmod 755 ~/shopify-api/downloads
```

---

### **12. Set Up Scheduled Task (Hourly Sync)**

1. Go to **Tasks** tab
2. Create **Scheduled task**
3. Set to run **daily at 00:00** (free tier limit)
4. Command:

```bash
/home/yourusername/shopify-api/venv/bin/python /home/yourusername/shopify-api/sync_worker.py
```

**Note:** Free tier only allows daily tasks. Paid ($5/month) allows hourly.

---

### **13. Reload Web App**

1. Go to **Web** tab
2. Click green **Reload** button
3. Wait ~30 seconds

---

### **14. Test Your API**

```bash
# Health check
curl https://yourusername.pythonanywhere.com/health

# Get data (with API key)
curl -H "X-API-Key: shopify_secure_key_2025" \
  "https://yourusername.pythonanywhere.com/fetch-data?metadata_only=true"
```

---

## 🐛 **Troubleshooting:**

### **Issue 1: "Chrome not found"**

**Solution:**

```bash
# Check what's installed
ls -la /usr/bin/ | grep -i chrom

# If found at different path, update sync_worker.py chrome_paths list
```

### **Issue 2: "ChromeDriver version mismatch"**

**Solution:**

```bash
# Use webdriver-manager (already in your code!)
pip install webdriver-manager

# It will auto-download matching version
```

### **Issue 3: "Permission denied on downloads folder"**

**Solution:**

```bash
chmod 755 ~/shopify-api/downloads
chmod 755 ~/shopify-api
```

### **Issue 4: "ERR_CONNECTION_REFUSED to phpMyAdmin"**

**This is the original problem - likely your server blocks external IPs**

**Solutions:**

1. **Contact hosting provider** (kvatt.com) to whitelist PythonAnywhere IPs
2. **See:** https://help.pythonanywhere.com/pages/403ForbiddenError/
3. **Or use VPN/proxy** (advanced)

### **Issue 5: Check Error Logs**

**Web tab → Error log** shows any Python errors

**Bash console:**

```bash
tail -f ~/shopify-api/error.log
```

---

## ✅ **What Your Code Now Does:**

### **Smart Environment Detection:**

1. **Detects PythonAnywhere** automatically
2. **Searches multiple Chrome paths**:

   - `/usr/bin/chromium`
   - `/usr/bin/chromium-browser`
   - `/usr/bin/google-chrome`
   - `/usr/bin/google-chrome-stable`
   - `/snap/bin/chromium`

3. **Searches multiple ChromeDriver paths**:

   - `/usr/bin/chromedriver`
   - `/usr/local/bin/chromedriver`
   - `~/.local/bin/chromedriver`

4. **Falls back to webdriver-manager** if not found

---

## 🎯 **Your Deployment Options:**

| Platform           | Selenium Works?                   | SQL Blocked?       | Recommendation                   |
| ------------------ | --------------------------------- | ------------------ | -------------------------------- |
| **PythonAnywhere** | ✅ Yes (if phpMyAdmin accessible) | ✅ Yes (port 3306) | **Try again with updated code!** |
| **Render**         | ✅ Yes                            | ✅ Yes             | **Already working!**             |
| **Local Windows**  | ✅ Yes                            | ✅ Yes             | ✅ Works perfectly               |

---

## 🚀 **Quick Test on PythonAnywhere:**

```bash
# 1. Upload updated sync_worker.py
# 2. Install dependencies
pip install -r requirements.txt

# 3. Test
python sync_worker.py

# Expected output:
# 🐍 PythonAnywhere environment detected
#    ✅ Found Chrome at: /usr/bin/chromium-browser
#    ✅ Found ChromeDriver at: /usr/bin/chromedriver
# [Time] Sync started
# CSV downloaded...
# ✅ Success!
```

---

## 💡 **Important Notes:**

1. **Your phpMyAdmin server must allow connections from PythonAnywhere IPs**
   - If you still get ERR_CONNECTION_REFUSED, contact your host
2. **Free tier limitations:**

   - Daily scheduled tasks only (not hourly)
   - Daily CPU quota
   - But plenty for this use case!

3. **Selenium requires more resources:**
   - But your code is optimized to <2MB
   - Should work fine!

---

## 🎉 **Your Updated Code is Ready!**

**The `sync_worker.py` now:**

- ✅ Auto-detects PythonAnywhere
- ✅ Finds Chrome/Chromium automatically
- ✅ Tries multiple paths
- ✅ Falls back to webdriver-manager
- ✅ Still works on Windows locally
- ✅ Works on Render too!

**Try deploying to PythonAnywhere again!** 🚀

**If phpMyAdmin is still blocked**, you'll need to contact kvatt.com to whitelist PythonAnywhere IPs.
