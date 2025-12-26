import os
# Disable webdriver-manager usage stats to prevent "Error sending stats to Plausible"
os.environ["WDM_DISABLE_USAGE"] = "1"

import time
import pandas as pd
import json
import gc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION (Match your account) ---
# --- CONFIGURATION (Match your account) ---
BASE_URL = "https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php"
USERNAME = "kvatt_green_package_shopify_app"
PASSWORD = "esas8ZDsIu!52"
DB_NAME = "kvatt_green_package_shopify_app"
TABLE_NAME = "orders"
EXPORT_URL = f"{BASE_URL}?route=/table/export&db={DB_NAME}&table={TABLE_NAME}&single_table=true"

# Docker / Local Path Handling
PROJECT_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, "downloads")
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--verbose")
    
    # PythonAnywhere specific FIX for ERR_TUNNEL_CONNECTION_FAILED:
    options.add_argument('--proxy-server=direct://')
    options.add_argument('--proxy-bypass-list=*')
    
    # Check for PythonAnywhere environment
    # (PythonAnywhere sets 'PYTHONANYWHERE_DOMAIN' or 'PYTHONANYWHERE_SITE' env vars)
    if 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/home/kvatt'):
        print("Detected PythonAnywhere Environment. Configuring driver...", flush=True)
        options.add_experimental_option("prefs", {"download.default_directory": DOWNLOAD_DIR})
        
        # 1. Try finding the chromium binary explicitly
        paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser"]
        found_bin = None
        for p in paths:
            if os.path.exists(p):
                found_bin = p
                break
        
        if found_bin:
            print(f"Found chromium binary at: {found_bin}", flush=True)
            options.binary_location = found_bin
        
        # 2. Try using the system chromedriver
        try:
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"Failed to use system /usr/bin/chromedriver: {e}", flush=True)
            # Fallback to default initialization if explicit service fails
            pass

    # Local Windows / General Fallback
    try:
        options.add_experimental_option("prefs", {"download.default_directory": DOWNLOAD_DIR})
        if os.name == 'nt': # LOCAL WINDOWS
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        else: # Standard Linux
            return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Fatal Driver Error: {e}", flush=True)
        raise e

def perform_sync():
    driver = None
    try:
        print(f"Sync started at {time.ctime()}")
        driver = get_driver()
        wait = WebDriverWait(driver, 30)
        
        # 1. Login
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "input_username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "input_password").send_keys(PASSWORD)
        driver.find_element(By.ID, "input_go").click()
        wait.until(EC.presence_of_element_located((By.ID, "pma_navigation")))
        
        # 2. Trigger Export
        driver.get(EXPORT_URL)
        wait.until(EC.presence_of_element_located((By.ID, "plugins")))
        Select(driver.find_element(By.ID, "plugins")).select_by_value("csv")
        time.sleep(1)
        driver.execute_script("document.getElementById('buttonGo').click();")
        
        # 3. Wait for download
        file_path = None
        for _ in range(60): # 5 minute timeout
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv")]
            if files:
                file_path = os.path.join(DOWNLOAD_DIR, files[0])
                break
            time.sleep(5)
            
        if file_path:
            # 4. Process and Cache
            df = pd.read_csv(file_path)
            data = {
                "status": "success",
                "count": len(df),
                "last_updated": time.ctime(),
                "data": df.to_dict(orient='records')
            }
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f)
            print("Sync complete. Data cached.")
            
            # Clean up
            os.remove(file_path)
            del df, data
            gc.collect()

    except Exception as e:
        print(f"Sync error: {str(e)}")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    print("Worker started...", flush=True) # flush=True forces output to appear immediately
    while True:
        try:
            perform_sync()
        except Exception as e:
            print(f"CRITICAL WORKER FAIL: {str(e)}", flush=True)
        
        print("Sleeping for 1 hour...", flush=True)
        time.sleep(3600) # Sync once per hour