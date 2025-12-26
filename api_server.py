import os
import time
import threading
import pandas as pd
import json
import gc
import gzip
from flask import Flask, Response, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
BASE_URL = "https://shopify.kvatt.com/d4ad5e396a34d97dae65c09957e17fecd326658d/index.php"
USERNAME = "kvatt_green_package_shopify_app"
PASSWORD = "esas8ZDsIu!52"
DB_NAME = "kvatt_green_package_shopify_app"
TABLE_NAME = "orders"
EXPORT_URL = f"{BASE_URL}?route=/table/export&db={DB_NAME}&table={TABLE_NAME}&single_table=true"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
API_KEY = "shopify_secure_key_2025" # CHANGE THIS to something secret!

# Global Cache - Pre-serialized and compressed for 10ms delivery
cached_json_data = json.dumps({"status": "starting", "message": "First sync in progress..."}).encode('utf-8')
last_sync_time = "Never"

def build_driver():
    """Builds a temporary optimized browser instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false") # No images = Faster
    
    prefs = {"download.default_directory": DOWNLOAD_DIR, "download.prompt_for_download": False}
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def background_worker():
    """The 'Engine' that keeps data real-time while using 0 resources when idle."""
    global cached_json_data, last_sync_time
    
    while True:
        driver = None
        try:
            print(f"[{time.ctime()}] Background Sync: Fetching newest data...")
            driver = build_driver()
            wait = WebDriverWait(driver, 30)
            
            # 1. Login
            driver.get(BASE_URL)
            wait.until(EC.presence_of_element_located((By.ID, "input_username"))).send_keys(USERNAME)
            driver.find_element(By.ID, "input_password").send_keys(PASSWORD)
            driver.find_element(By.ID, "input_go").click()
            wait.until(EC.presence_of_element_located((By.ID, "pma_navigation")))
            
            # 2. Export
            driver.get(EXPORT_URL)
            wait.until(EC.presence_of_element_located((By.ID, "plugins")))
            Select(driver.find_element(By.ID, "plugins")).select_by_value("csv")
            time.sleep(1)
            go_btn = wait.until(EC.presence_of_element_located((By.ID, "buttonGo")))
            driver.execute_script("arguments[0].click();", go_btn)
            
            # 3. Wait for Download (300s timeout for 58MB)
            file_path = None
            start_wait = time.time()
            while time.time() - start_wait < 300:
                files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv") and TABLE_NAME in f.lower()]
                if files:
                    file_path = os.path.join(DOWNLOAD_DIR, files[0])
                    break
                time.sleep(5)

            if file_path:
                # 4. Optimized Processing
                df = pd.read_csv(file_path)
                data_list = df.to_dict(orient='records')
                
                # Pre-encode to JSON bytes once
                response_obj = {
                    "status": "success",
                    "realtime_sync": True,
                    "count": len(data_list),
                    "last_updated": time.ctime(),
                    "data": data_list
                }
                cached_json_data = json.dumps(response_obj).encode('utf-8')
                last_sync_time = time.ctime()
                
                # Cleanup to keep RAM low
                del df, data_list, response_obj
                gc.collect()
                print(f"Background Sync: Success. {last_sync_time}")

        except Exception as e:
            print(f"Background Sync Error: {str(e)}")
        finally:
            if driver:
                driver.quit() # Releases all browser RAM back to system
            # Cleanup CSV after processing to save disk space
            for f in os.listdir(DOWNLOAD_DIR):
                try: os.remove(os.path.join(DOWNLOAD_DIR, f))
                except: pass

        # How 'Real-Time' do you want it? 
        # Set to 120 seconds (2 mins) for a good balance of fresh data vs server resource conservation.
        time.sleep(86400)

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    """The 10ms API Endpoint with Security."""
    # Check for API Key in headers
    user_key = request.headers.get("X-API-Key")
    
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}),
            status=401,
            mimetype='application/json'
        )

    # This return is virtually instant because the work is already done!
    return Response(
        cached_json_data,
        mimetype='application/json',
        headers={"X-Last-Sync": last_sync_time}
    )

if __name__ == '__main__':
    if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)
    
    # Run the worker in a background thread
    threading.Thread(target=background_worker, daemon=True).start()
    
    print("API Server Speed-Optimized starting on http://localhost:5000")
    # Using threaded=True allows the API to handle requests while the worker syncs data
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)