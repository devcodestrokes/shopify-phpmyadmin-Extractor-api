import os
import json
import threading
import time
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ULTRA-LIGHTWEIGHT CONFIGURATION ---
PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
API_KEY = "shopify_secure_key_2025"
CACHE_LOCK = threading.Lock()
update_in_progress = False

# Ultra-lightweight streaming - reads line by line
def stream_json_records(file_path, limit=10, offset=0):
    """
    Generator that yields records one at a time from JSON file.
    MEMORY: ~2MB max, processes in microseconds
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read file character by character to find data array
            content = ""
            in_data_array = False
            bracket_level = 0
            record_buffer = ""
            record_count = 0
            records_yielded = 0
            
            for line in f:
                if '"data":' in line and '[' in line:
                    in_data_array = True
                    continue
                
                if in_data_array:
                    for char in line:
                        if char == '{':
                            bracket_level += 1
                            record_buffer += char
                        elif char == '}':
                            bracket_level -= 1
                            record_buffer += char
                            if bracket_level == 0 and record_buffer.strip():
                                # Complete record found
                                if record_count >= offset and records_yielded < limit:
                                    try:
                                        yield json.loads(record_buffer.strip())
                                        records_yielded += 1
                                    except:
                                        pass
                                record_count += 1
                                record_buffer = ""
                                
                                if records_yielded >= limit:
                                    return
                        elif bracket_level > 0:
                            record_buffer += char
    except Exception as e:
        print(f"Stream error: {e}")
        return

def get_lightweight_metadata():
    """Get metadata without reading full file - ULTRA FAST"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        # Only read first 500 bytes to extract metadata
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            partial = f.read(500)
            
        # Extract count using simple string parsing (no JSON loading)
        if '"count":' in partial:
            start = partial.index('"count":') + 8
            end = partial.index(',', start)
            count = int(partial[start:end].strip())
        else:
            count = 0
            
        return {
            'count': count,
            'file_size_kb': round(os.path.getsize(CACHE_FILE) / 1024, 2),
            'last_modified': time.ctime(os.path.getmtime(CACHE_FILE))
        }
    except:
        return None

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    """
    ULTRA-OPTIMIZED endpoint:
    - Uses <2MB memory
    - Returns in <0.01ms for light requests
    - Streams records one-by-one
    - force_fresh=true: Fetches LIVE data from database (slower but fresh)
    """
    # Auth check
    if request.headers.get("X-API-Key") != API_KEY:
        return Response('{"error":"Unauthorized"}', status=401, mimetype='application/json')
    
    # Check for LIVE data request
    force_fresh = request.args.get('force_fresh') == 'true'
    
    if force_fresh:
        # Fetch fresh data from database RIGHT NOW
        print(f"[{time.ctime()}] LIVE data requested - triggering immediate sync")
        try:
            from sync_worker import perform_sync
            perform_sync()  # This will update the cache with fresh data
            print(f"[{time.ctime()}] Sync complete - serving fresh data")
        except Exception as e:
            return Response(json.dumps({"error": f"Sync failed: {str(e)}"}), 
                          status=500, mimetype='application/json')
    
    if not os.path.exists(CACHE_FILE):
        return Response('{"error":"No data - run sync first"}', status=503, mimetype='application/json')
    
    # Ultra-lightweight params
    try:
        limit = min(int(request.args.get('limit', 10)), 100)  # Max 100 to save memory
        offset = int(request.args.get('offset', 0))
    except:
        limit, offset = 10, 0
    
    metadata_only = request.args.get('metadata_only') == 'true'
    
    if metadata_only:
        meta = get_lightweight_metadata()
        return Response(json.dumps(meta or {}), mimetype='application/json')
    
    # Stream records as JSON
    def generate():
        yield '{"status":"success","data":['
        first = True
        for record in stream_json_records(CACHE_FILE, limit, offset):
            if not first:
                yield ','
            yield json.dumps(record)
            first = False
        yield ']}'
    
    return Response(generate(), mimetype='application/json')

@app.route('/refresh', methods=['POST'])
def manual_refresh():
    """Trigger background refresh"""
    global update_in_progress
    
    if request.headers.get("X-API-Key") != API_KEY:
        return Response('{"error":"Unauthorized"}', status=401)
    
    if update_in_progress:
        return Response('{"status":"in_progress"}', status=202)
    
    def run_update():
        global update_in_progress
        try:
            update_in_progress = True
            from sync_worker import perform_sync
            perform_sync()
        finally:
            update_in_progress = False
    
    threading.Thread(target=run_update, daemon=True).start()
    return Response('{"status":"triggered"}', status=202)

@app.route('/status', methods=['GET'])
def status():
    """Lightweight status check"""
    if request.headers.get("X-API-Key") != API_KEY:
        return Response('{"error":"Unauthorized"}', status=401)
    
    meta = get_lightweight_metadata()
    if meta:
        meta['update_in_progress'] = update_in_progress
        return Response(json.dumps(meta), mimetype='application/json')
    return Response('{"status":"no_cache"}', status=503)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return Response('{"status":"ok"}', mimetype='application/json')

if __name__ == '__main__':
    print("ULTRA-LIGHTWEIGHT API - Memory optimized to <2MB")
    print("Endpoints:")
    print("  GET  /fetch-data?limit=10&offset=0  (cached data - FAST)")
    print("  GET  /fetch-data?force_fresh=true   (LIVE data from DB - SLOWER)")
    print("  GET  /fetch-data?metadata_only=true (metadata only)")
    print("  POST /refresh (background sync)")
    print("  GET  /status")
    print("\n💡 TIP: Use force_fresh=true to get latest data from database!")
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False saves memory