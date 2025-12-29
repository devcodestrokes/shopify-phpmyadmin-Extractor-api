import os
import json
import threading
import time
from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
TEMP_CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache_temp.json")
API_KEY = "shopify_secure_key_2025"

# Global lock for thread-safe cache updates
cache_lock = threading.Lock()
update_in_progress = False

def trigger_background_update():
    """Triggers the sync_worker to fetch fresh data in the background"""
    global update_in_progress
    
    if update_in_progress:
        print("Update already in progress, skipping...")
        return
    
    def run_update():
        global update_in_progress
        try:
            update_in_progress = True
            print(f"[{time.ctime()}] Background update triggered...")
            
            # Import here to avoid circular dependencies
            from sync_worker import perform_sync
            perform_sync()
            
            print(f"[{time.ctime()}] Background update completed.")
        except Exception as e:
            print(f"[{time.ctime()}] Background update failed: {str(e)}")
        finally:
            update_in_progress = False
    
    # Start update in a separate thread
    update_thread = threading.Thread(target=run_update, daemon=True)
    update_thread.start()

def read_cache_data():
    """Reads and returns cached data"""
    with cache_lock:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading cache: {str(e)}")
                return None
        return None

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    """
    Main endpoint that returns cached data immediately and optionally triggers refresh.
    Query parameters:
    - refresh=true: Triggers a background data refresh
    - stream=true: Uses Server-Sent Events to send updated data when ready
    """
    # 1. Security Check
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )
    
    # 2. Check for refresh parameter
    should_refresh = request.args.get('refresh', 'false').lower() == 'true'
    use_stream = request.args.get('stream', 'false').lower() == 'true'
    
    # 3. Read cached data
    cached_data = read_cache_data()
    
    if cached_data is None:
        return Response(
            json.dumps({
                "status": "pending", 
                "message": "No cached data available. Please wait for initial sync or trigger manual refresh at /refresh endpoint."
            }), 
            status=503, 
            mimetype='application/json'
        )
    
    # 4. If streaming is requested
    if use_stream:
        def generate():
            # First, send cached data
            yield f"data: {json.dumps({'type': 'cached', 'payload': cached_data})}\n\n"
            
            # Trigger update if requested
            if should_refresh:
                trigger_background_update()
                
                # Wait for update to complete (with timeout)
                max_wait = 300  # 5 minutes max
                start_time = time.time()
                
                while update_in_progress and (time.time() - start_time) < max_wait:
                    time.sleep(2)
                
                # Send updated data
                updated_data = read_cache_data()
                if updated_data:
                    yield f"data: {json.dumps({'type': 'updated', 'payload': updated_data})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Update failed'})}\n\n"
            
            yield "data: {\"type\": \"done\"}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # 5. Standard response: return cached data immediately
    # Optionally trigger background refresh
    if should_refresh:
        trigger_background_update()
        cached_data['_info'] = "Background refresh triggered. Call again in a few minutes for updated data."
    
    return Response(
        json.dumps(cached_data),
        mimetype='application/json',
        headers={'Cache-Control': 'no-cache'}
    )

@app.route('/refresh', methods=['POST'])
def manual_refresh():
    """Manual endpoint to trigger data refresh"""
    # Security Check
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )
    
    if update_in_progress:
        return Response(
            json.dumps({
                "status": "in_progress",
                "message": "Data refresh already in progress"
            }),
            status=202,
            mimetype='application/json'
        )
    
    trigger_background_update()
    
    return Response(
        json.dumps({
            "status": "triggered",
            "message": "Data refresh triggered successfully"
        }),
        status=202,
        mimetype='application/json'
    )

@app.route('/status', methods=['GET'])
def status():
    """Check API and cache status"""
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )
    
    cache_exists = os.path.exists(CACHE_FILE)
    cache_age = None
    
    if cache_exists:
        cache_age = time.time() - os.path.getmtime(CACHE_FILE)
        cache_age_minutes = int(cache_age / 60)
    
    status_data = {
        "api_status": "online",
        "cache_exists": cache_exists,
        "cache_age_minutes": cache_age_minutes if cache_exists else None,
        "update_in_progress": update_in_progress,
        "timestamp": time.ctime()
    }
    
    return Response(
        json.dumps(status_data),
        mimetype='application/json'
    )

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint (no auth required)"""
    return Response(
        json.dumps({"status": "healthy", "timestamp": time.ctime()}),
        mimetype='application/json'
    )

if __name__ == '__main__':
    print(f"API Server running. Cache file location: {CACHE_FILE}")
    print(f"Endpoints available:")
    print(f"  - GET  /fetch-data (returns cached data)")
    print(f"  - GET  /fetch-data?refresh=true (returns cached + triggers update)")
    print(f"  - GET  /fetch-data?stream=true&refresh=true (SSE stream)")
    print(f"  - POST /refresh (manually triggers data refresh)")
    print(f"  - GET  /status (check cache and API status)")
    print(f"  - GET  /health (health check)")
    app.run(host='0.0.0.0', port=5000, debug=True)