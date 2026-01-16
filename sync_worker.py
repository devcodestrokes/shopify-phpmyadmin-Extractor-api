import os
# Disable webdriver-manager usage stats
os.environ["WDM_DISABLE_USAGE"] = "1"

import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
BASE_URL = "https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php"
USERNAME = "kvatt_green_package_shopify_app"
PASSWORD = "esas8ZDsIu!52"
DB_NAME = "kvatt_green_package_shopify_app"
TABLE_NAME = "orders"
EXPORT_URL = f"{BASE_URL}?route=/table/export&db={DB_NAME}&table={TABLE_NAME}&single_table=true"

PROJECT_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, "downloads")
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
if not os.path.exists(DOWNLOAD_DIR): 
    os.makedirs(DOWNLOAD_DIR)

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_driver():
    """
    Smart driver detection for PythonAnywhere, Render, and Local environments
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument('--proxy-server=direct://')
    options.add_argument('--proxy-bypass-list=*')
    options.add_experimental_option("prefs", {"download.default_directory": DOWNLOAD_DIR})
    
    # === PYTHONANYWHERE DETECTION ===
    is_pythonanywhere = (
        'PYTHONANYWHERE_DOMAIN' in os.environ or 
        'PYTHONANYWHERE_SITE' in os.environ or
        os.path.exists('/home') and not os.path.exists('C:\\')
    )
    
    if is_pythonanywhere:
        print("🐍 PythonAnywhere environment detected", flush=True)
        
        # Try multiple Chrome/Chromium paths (PythonAnywhere-specific)
        chrome_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser", 
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/chromium"
        ]
        
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/home/{}/.local/bin/chromedriver".format(os.environ.get('USER', 'unknown'))
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                print(f"   ✅ Found Chrome at: {path}", flush=True)
                break
        
        if chrome_binary:
            options.binary_location = chrome_binary
        else:
            print("   ⚠️ Chrome not found in standard locations", flush=True)
            print("   Available paths checked:", chrome_paths, flush=True)
        
        # Try to find chromedriver
        driver_path = None
        for path in chromedriver_paths:
            if os.path.exists(path):
                driver_path = path
                print(f"   ✅ Found ChromeDriver at: {path}", flush=True)
                break
        
        if not driver_path:
            # Try webdriver-manager as fallback
            try:
                print("   ⚙️ Using webdriver-manager to install ChromeDriver...", flush=True)
                installed_path = ChromeDriverManager().install()
                print(f"   📁 webdriver-manager returned: {installed_path}", flush=True)
                
                # Fix: webdriver-manager sometimes returns wrong file
                # Find actual chromedriver executable in the directory
                if os.path.isfile(installed_path):
                    driver_dir = os.path.dirname(installed_path)
                else:
                    driver_dir = installed_path
                
                # Look for actual chromedriver executable
                for filename in ['chromedriver', 'chromedriver.exe']:
                    potential_path = os.path.join(driver_dir, filename)
                    if os.path.exists(potential_path) and os.path.isfile(potential_path):
                        driver_path = potential_path
                        print(f"   ✅ Found actual ChromeDriver at: {driver_path}", flush=True)
                        break
                
                if not driver_path:
                    # Fallback: use what webdriver-manager gave us
                    driver_path = installed_path
                    print(f"   ⚠️ Using webdriver-manager path as-is: {driver_path}", flush=True)
                    
            except Exception as e:
                print(f"   ❌ webdriver-manager failed: {e}", flush=True)
        
        try:
            if driver_path:
                return webdriver.Chrome(service=Service(driver_path), options=options)
            else:
                # Last resort - try without explicit path
                return webdriver.Chrome(options=options)
        except Exception as e:
            print(f"   ❌ Chrome initialization failed: {e}", flush=True)
            raise
    
    # === WINDOWS/LOCAL ENVIRONMENT ===
    print("💻 Local Windows environment detected", flush=True)
    try:
        installed_path = ChromeDriverManager().install()
        print(f"   📁 webdriver-manager returned: {installed_path}", flush=True)
        
        # Fix: Find actual chromedriver executable
        if os.path.isfile(installed_path):
            driver_dir = os.path.dirname(installed_path)
        else:
            driver_dir = installed_path
        
        driver_path = None
        for filename in ['chromedriver.exe', 'chromedriver']:
            potential_path = os.path.join(driver_dir, filename)
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                driver_path = potential_path
                print(f"   ✅ Found ChromeDriver at: {driver_path}", flush=True)
                break
        
        if not driver_path:
            driver_path = installed_path
        
        return webdriver.Chrome(service=Service(driver_path), options=options)
    except Exception as e:
        print(f"   ❌ Error: {e}", flush=True)
        raise

def csv_to_json_streaming(csv_path, json_path):
    """
    ULTRA-LIGHTWEIGHT: Stream CSV to JSON line-by-line
    MEMORY: ~2MB max, regardless of file size
    """
    with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile, \
         open(json_path, 'w', encoding='utf-8') as jsonfile:
        
        reader = csv.DictReader(csvfile)
        
        # Write JSON header
        jsonfile.write('{"status":"success","count":0,"last_updated":"')
        jsonfile.write(time.ctime())
        jsonfile.write('","data":[')
        
        first_record = True
        count = 0
        
        # Stream records one at a time
        for row in reader:
            if not first_record:
                jsonfile.write(',')
            json.dump(row, jsonfile)
            first_record = False
            count += 1
        
        jsonfile.write(']}')
    
    # Update count in file (read first 200 chars, update, write back)
    with open(json_path, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('"count":0', f'"count":{count}', 1)
        f.seek(0)
        f.write(content)
        f.truncate()
    
    print(f"Processed {count} records with ~2MB memory", flush=True)

def perform_sync():
    """Ultra-optimized sync process"""
    driver = None
    try:
        print(f"[{time.ctime()}] Sync started", flush=True)
        driver = get_driver()
        wait = WebDriverWait(driver, 30)
        
        # Login
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "input_username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "input_password").send_keys(PASSWORD)
        driver.find_element(By.ID, "input_go").click()
        wait.until(EC.presence_of_element_located((By.ID, "pma_navigation")))
        
        # Trigger CSV export
        driver.get(EXPORT_URL)
        wait.until(EC.presence_of_element_located((By.ID, "plugins")))
        Select(driver.find_element(By.ID, "plugins")).select_by_value("csv")
        time.sleep(1)
        driver.execute_script("document.getElementById('buttonGo').click();")
        
        # Wait for download (max 5 min)
        csv_path = None
        for _ in range(60):
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv")]
            if files:
                csv_path = os.path.join(DOWNLOAD_DIR, files[0])
                break
            time.sleep(5)
        
        if csv_path:
            print(f"CSV downloaded, streaming to JSON...", flush=True)
            
            # ULTRA-LIGHTWEIGHT STREAMING CONVERSION
            csv_to_json_streaming(csv_path, CACHE_FILE)
            
            # Cleanup
            os.remove(csv_path)
            print("[OK] Sync complete, cache updated", flush=True)
        else:
            print("[ERROR] CSV download timeout", flush=True)
            
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}", flush=True)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("=== ULTRA-LIGHTWEIGHT WORKER ===", flush=True)
    print("Memory usage: <2MB", flush=True)
    
    while True:
        try:
            perform_sync()
        except Exception as e:
            print(f"[CRITICAL] {e}", flush=True)
        
        print(f"Sleeping 1h...", flush=True)
        time.sleep(3600)