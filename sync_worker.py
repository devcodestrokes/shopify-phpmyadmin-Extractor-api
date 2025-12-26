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
BASE_URL = "https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php"
USERNAME = "kvatt_green_package_shopify_app"
PASSWORD = "esas8ZDsIu!52"
DB_NAME = "kvatt_green_package_shopify_app"
TABLE_NAME = "orders"
EXPORT_URL = f"{BASE_URL}?route=/table/export&db={DB_NAME}&table={TABLE_NAME}&single_table=true"

# Smart Path Handling (Works locally AND on PythonAnywhere)
if os.name == 'nt': # Windows (Local Machine)
    PROJECT_DIR = os.getcwd()
else: # Linux (PythonAnywhere)
    HOME = os.path.expanduser("~")
    PROJECT_DIR = os.path.join(HOME, "mysite")

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
    # PythonAnywhere specific FIX for ERR_TUNNEL_CONNECTION_FAILED:
    options.add_argument('--proxy-server=direct://')
    options.add_argument('--proxy-bypass-list=*')
    
    # PythonAnywhere works best with these specifically
    options.add_experimental_option("prefs", {"download.default_directory": DOWNLOAD_DIR})
    
    if os.name == 'nt': # LOCAL WINDOWS
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    else: # PYTHONANYWHERE (Linux)
        return webdriver.Chrome(options=options)

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
    while True:
        perform_sync()
        time.sleep(3600) # Sync once per hour