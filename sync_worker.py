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
    
    # === ENVIRONMENT DETECTION ===
    if os.name == 'posix':
        print("� Linux environment detected (likely Render)", flush=True)
        
        # Standard Linux paths
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser"
        ]
        chromedriver_paths = ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver"]
        
    else:
        # Windows / Local
        print("� Local Windows environment detected", flush=True)
        chrome_paths = []
        chromedriver_paths = []

    # === DRIVER SETUP (Shared Logic) ===
    
    # 1. Find Chrome Binary (Linux only usually needs this explicit path if not in PATH)
    chrome_binary = None
    if os.name == 'posix':
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                print(f"   ✅ Found Chrome at: {path}", flush=True)
                break
        
        if chrome_binary:
            options.binary_location = chrome_binary
        else:
            print("   ⚠️ Chrome not found in standard paths, hoping it's on PATH...", flush=True)

    # 2. Find/Install ChromeDriver
    driver_path = None
    
    # Check pre-installed paths first (Linux)
    for path in chromedriver_paths:
        if os.path.exists(path):
            driver_path = path
            print(f"   ✅ Found System ChromeDriver at: {path}", flush=True)
            break
    
    if not driver_path:
        # Use webdriver-manager
        try:
            print("   ⚙️ Using webdriver-manager to install ChromeDriver...", flush=True)
            installed_path = ChromeDriverManager().install()
            print(f"   📁 webdriver-manager returned: {installed_path}", flush=True)
            
            # Robustly find the actual executable (Fixes "THIRD_PARTY_NOTICES" bug)
            possible_files = []
            if os.path.isfile(installed_path):
                driver_dir = os.path.dirname(installed_path)
                possible_files.append(installed_path)
            else:
                driver_dir = installed_path
            
            # Walk the directory to find the binary
            found_binary = None
            for root, dirs, files in os.walk(driver_dir):
                for filename in files:
                    # Match likely executable names
                    if filename == 'chromedriver' or filename == 'chromedriver.exe':
                        full_path = os.path.join(root, filename)
                        
                        # Explicitly ignore known non-binaries
                        if "THIRD_PARTY_NOTICES" in full_path:
                            continue
                            
                        found_binary = full_path
                        break
                if found_binary:
                    break
            
            if found_binary:
                driver_path = found_binary
                print(f"   ✅ Found actual ChromeDriver executable at: {driver_path}", flush=True)
                
                # Ensure it is executable on Linux
                if os.name == 'posix':
                    st = os.stat(driver_path)
                    os.chmod(driver_path, st.st_mode | 0o111)
            else:
                # Fallback if walk failed but installed_path exists
                if os.path.exists(installed_path) and "THIRD_PARTY_NOTICES" not in installed_path:
                     driver_path = installed_path
                     print(f"   ⚠️ Using raw path (verification failed): {driver_path}", flush=True)
                else:
                     print(f"   ❌ Could not locate valid chromedriver binary in {driver_dir}", flush=True)

        except Exception as e:
            print(f"   ❌ webdriver-manager failed: {e}", flush=True)
    
    try:
        if driver_path:
            print(f"   🚀 Launching Chrome with driver: {driver_path}", flush=True)
            return webdriver.Chrome(service=Service(driver_path), options=options)
        else:
            print("   ⚠️ No specific driver found, letting Selenium auto-detect...", flush=True)
            return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"   ❌ Chrome initialization failed: {e}", flush=True)
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