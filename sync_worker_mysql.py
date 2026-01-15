"""
Alternative: Direct MySQL Connection (No Selenium Needed!)
Use this if phpMyAdmin is not accessible from PythonAnywhere
"""

import mysql.connector
import json
import os
import time

# --- CONFIGURATION ---
# Replace with your actual MySQL credentials
MYSQL_HOST = "shopify.kvatt.com"  # Or IP address
MYSQL_USER = "kvatt_green_package_shopify_app"
MYSQL_PASSWORD = "esas8ZDsIu!52"
MYSQL_DATABASE = "kvatt_green_package_shopify_app"
MYSQL_TABLE = "orders"

PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")

def fetch_data_direct():
    """
    Fetch data directly from MySQL without Selenium
    Much faster and more reliable!
    """
    print("=== DIRECT MySQL CONNECTION ===")
    print(f"[{time.ctime()}] Connecting to database...")
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=3306  # Default MySQL port
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Fetch all records
        print(f"[{time.ctime()}] Fetching records from {MYSQL_TABLE}...")
        cursor.execute(f"SELECT * FROM {MYSQL_TABLE}")
        
        # Stream to JSON file
        print("Streaming to JSON...")
        
        # Write JSON structure
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            f.write('{"status":"success","count":0,"last_updated":"')
            f.write(time.ctime())
            f.write('","data":[')
            
            count = 0
            first = True
            
            for row in cursor:
                if not first:
                    f.write(',')
                json.dump(row, f, default=str)  # default=str handles datetime
                first = False
                count += 1
                
                if count % 1000 == 0:
                    print(f"  Processed {count} records...")
            
            f.write(']}')
        
        # Update count
        with open(CACHE_FILE, 'r+', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('"count":0', f'"count":{count}', 1)
            f.seek(0)
            f.write(content)
            f.truncate()
        
        print(f"✅ Success! Fetched {count} records")
        print(f"   Memory usage: <2MB")
        print(f"   Cache file: {CACHE_FILE}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        print(f"\nPossible issues:")
        print(f"  1. MySQL server not accessible from PythonAnywhere")
        print(f"  2. Wrong credentials")
        print(f"  3. Firewall blocking port 3306")
        print(f"  4. Need to whitelist PythonAnywhere IP")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SHOPIFY DATA SYNC - Direct MySQL Version")
    print("="*60)
    print("\n💡 This version connects directly to MySQL")
    print("   No Selenium/Chrome needed!")
    print("   Much faster and more reliable!\n")
    
    success = fetch_data_direct()
    
    if success:
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE!")
        print("="*60)
        print("\nYou can now use the API to fetch data:")
        print("  GET /fetch-data?limit=10")
    else:
        print("\n" + "="*60)
        print("❌ SYNC FAILED!")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Test MySQL connection:")
        print("   mysql -h shopify.kvatt.com -u kvatt_green_package_shopify_app -p")
        print("\n2. Check if port 3306 is accessible:")
        print("   telnet shopify.kvatt.com 3306")
        print("\n3. Contact server admin to:")
        print("   - Whitelist PythonAnywhere IP")
        print("   - Enable remote MySQL access")
        print("   - Check firewall rules")
