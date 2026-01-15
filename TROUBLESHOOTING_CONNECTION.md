# 🔧 Troubleshooting: ERR_CONNECTION_REFUSED

## ❌ **Error You're Seeing:**

```
[ERROR] Sync failed: Message: unknown error: net::ERR_CONNECTION_REFUSED
```

**This means:** Selenium/Chrome cannot connect to your phpMyAdmin server.

---

## 🔍 **Root Causes & Solutions:**

### **Cause 1: Server is Down or Blocking External Connections**

**Test:**

```bash
# In PythonAnywhere Bash console
curl -I https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php
```

**Expected:** HTTP 200 or 30x redirect  
**If fails:** Server is blocking external requests or is down

**Solutions:**

1. Check if server is online in your browser
2. Contact server admin to whitelist PythonAnywhere IPs
3. Check if URL has changed

---

### **Cause 2: Firewall Blocking Connections**

**Test:**

```bash
# Test basic connectivity
ping shopify.kvatt.com

# Test if web server responds
wget https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php
```

**Solution:**

- Ask hosting provider to whitelist PythonAnywhere IP ranges
- PythonAnywhere IPs: https://help.pythonanywhere.com/pages/403ForbiddenError/

---

### **Cause 3: phpMyAdmin Disabled Remote Access**

Many shared hosting providers **disable direct phpMyAdmin access** from external IPs for security.

**Solution:** Use **direct MySQL connection** instead!

---

## ✅ **BEST SOLUTION: Use Direct MySQL Connection**

Instead of scraping phpMyAdmin with Selenium, **connect directly to MySQL database!**

### **Advantages:**

- ✅ **Much faster** (no browser needed)
- ✅ **More reliable** (no network issues)
- ✅ **Less memory** (no Chrome process)
- ✅ **Works from anywhere** (if MySQL port open)

### **Steps:**

#### **1. Add MySQL Connector to Requirements**

Add to `requirements.txt`:

```
mysql-connector-python
```

Install:

```bash
pip install mysql-connector-python
```

#### **2. Use the MySQL Version**

I've created `sync_worker_mysql.py` for you. Use it instead:

```bash
# Test it
python sync_worker_mysql.py
```

#### **3. Update flask_app.py to use MySQL version**

Change import in `flask_app.py`:

```python
# OLD (Selenium version)
from sync_worker import perform_sync

# NEW (MySQL version)
from sync_worker_mysql import fetch_data_direct as perform_sync
```

---

## 🔑 **Check MySQL Access**

### **Test if MySQL port is accessible:**

```bash
# In PythonAnywhere Bash
telnet shopify.kvatt.com 3306
```

**Expected:** Connection succeeds  
**If fails:** MySQL port 3306 is blocked

### **Test MySQL login:**

```bash
mysql -h shopify.kvatt.com -u kvatt_green_package_shopify_app -p
# Enter password: esas8ZDsIu!52
```

**Success:** You can connect!  
**Failure:** Need to enable remote MySQL access

---

## 📋 **Quick Comparison:**

| Method                         | Speed | Reliability | Memory | Works on PA? |
| ------------------------------ | ----- | ----------- | ------ | ------------ |
| **Selenium (current)**         | Slow  | ❌ Blocked  | High   | ❌ No        |
| **Direct MySQL (recommended)** | Fast  | ✅ Better   | Low    | ✅ Maybe     |
| **Manual CSV Upload**          | N/A   | ✅ Always   | None   | ✅ Yes       |

---

## 🎯 **Recommended Actions:**

### **Option A: Enable MySQL Remote Access** (Best)

1. Contact your hosting provider
2. Ask to enable **remote MySQL access**
3. Whitelist **PythonAnywhere IP ranges**
4. Use `sync_worker_mysql.py`

### **Option B: Whitelist PythonAnywhere for phpMyAdmin**

1. Get PythonAnywhere IP ranges
2. Ask hosting to whitelist these IPs
3. Keep using `sync_worker.py` (Selenium)

### **Option C: Deploy Elsewhere** (Easiest)

1. Deploy on **Render** (where it worked)
2. Already has all fixes applied
3. No network issues

### **Option D: Manual Sync** (Temporary)

1. Download CSV manually from phpMyAdmin
2. Upload to PythonAnywhere
3. Process with a simple script
4. Not automated, but works!

---

## 💡 **Try This First:**

```bash
# 1. Install MySQL connector
pip install mysql-connector-python

# 2. Try the MySQL version
python sync_worker_mysql.py

# If it works:
# ✅ Use this version instead of Selenium!

# If it fails with "Access denied" or "Can't connect":
# ❌ MySQL remote access is disabled
# → Contact hosting provider
```

---

## 🆘 **Still Having Issues?**

### **Check These:**

1. **Is the phpMyAdmin URL accessible in YOUR browser?**

   ```
   https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php
   ```

2. **Are your credentials still valid?**

   - Username: `kvatt_green_package_shopify_app`
   - Password: `esas8ZDsIu!52`

3. **Has the hosting provider changed settings?**

   - Contact them to check

4. **Is port 3306 (MySQL) open for remote access?**
   ```bash
   telnet shopify.kvatt.com 3306
   ```

---

## 🎯 **Bottom Line:**

**The ERR_CONNECTION_REFUSED means the server is blocking the connection.**

**Solutions (in order of preference):**

1. ✅ **Use direct MySQL** (`sync_worker_mysql.py`) - Faster & better!
2. ⚠️ **Whitelist PythonAnywhere** - Keep Selenium version
3. ✅ **Deploy on Render instead** - Already working there
4. ⚠️ **Manual CSV uploads** - Not automated

**Try `sync_worker_mysql.py` first!** It's the best solution if MySQL port is accessible! 🚀
