import os
import json
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# --- CONFIGURATION ---
PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
API_KEY = "shopify_secure_key_2025" # Must match what you use in your headers

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    # 1. Security Check
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )

    # 2. Check if cache file exists
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                # Read the pre-built JSON file directly
                data = f.read()
                return Response(data, mimetype='application/json')
        except Exception as e:
            return Response(
                json.dumps({"status": "error", "message": f"Error reading cache: {str(e)}"}),
                status=500,
                mimetype='application/json'
            )
    
    # 3. If no data yet
    return Response(
        json.dumps({
            "status": "pending", 
            "message": "Data sync in progress. Please wait for the background worker."
        }), 
        status=503, 
        mimetype='application/json'
    )

if __name__ == '__main__':
    # This block is for testing locally. 
    # On PythonAnywhere, the WSGI file handles running the app.
    print(f"API Server running. Expecting cache file at: {CACHE_FILE}")
    app.run(host='0.0.0.0', port=5000, debug=True)