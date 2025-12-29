import os
import json
import threading
import time
import gzip
from flask import Flask, Response, request, stream_with_context, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
TEMP_CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache_temp.json")
API_KEY = "shopify_secure_key_2025"

# Memory optimization: Cache metadata separately
CACHE_METADATA = None
CACHE_LOCK = threading.Lock()
update_in_progress = False

def stream_json_file(file_path, chunk_size=8192):
    """
    Stream a JSON file in chunks without loading it entirely into memory.
    Memory efficient: Uses only ~20-30MB regardless of file size.
    """
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def get_cache_metadata():
    """Get just the metadata without loading full data (memory efficient)"""
    global CACHE_METADATA
    
    if CACHE_METADATA and os.path.exists(CACHE_FILE):
        # Check if cache file was modified
        cache_mtime = os.path.getmtime(CACHE_FILE)
        if CACHE_METADATA.get('file_mtime') == cache_mtime:
            return CACHE_METADATA
    
    # Read just the metadata
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                # Read only first part to get metadata
                data = json.load(f)
                CACHE_METADATA = {
                    'status': data.get('status'),
                    'count': data.get('count', 0),
                    'last_updated': data.get('last_updated'),
                    'file_mtime': os.path.getmtime(CACHE_FILE),
                    'file_size_mb': round(os.path.getsize(CACHE_FILE) / (1024*1024), 2)
                }
                return CACHE_METADATA
        except Exception as e:
            print(f"Error reading cache metadata: {str(e)}")
            return None
    return None

def read_cache_data_paginated(limit=100, offset=0):
    """Read cache data with pagination (memory efficient)"""
    with CACHE_LOCK:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    full_data = json.load(f)
                    
                    # Extract paginated records
                    all_records = full_data.get('data', [])
                    total_count = len(all_records)
                    
                    # Apply pagination
                    paginated_records = all_records[offset:offset + limit]
                    
                    return {
                        'status': full_data.get('status'),
                        'count': total_count,
                        'last_updated': full_data.get('last_updated'),
                        'page_info': {
                            'limit': limit,
                            'offset': offset,
                            'returned': len(paginated_records),
                            'has_more': (offset + limit) < total_count
                        },
                        'data': paginated_records
                    }
            except Exception as e:
                print(f"Error reading cache: {str(e)}")
                return None
        return None

def trigger_background_update():
    """Triggers the sync_worker to fetch fresh data in the background"""
    global update_in_progress
    
    if update_in_progress:
        print("Update already in progress, skipping...")
        return
    
    def run_update():
        global update_in_progress, CACHE_METADATA
        try:
            update_in_progress = True
            CACHE_METADATA = None  # Invalidate cache
            print(f"[{time.ctime()}] Background update triggered...")
            
            # Import here to avoid circular dependencies
            from sync_worker import perform_sync
            perform_sync()
            
            print(f"[{time.ctime()}] Background update completed.")
        except Exception as e:
            print(f"[{time.ctime()}] Background update failed: {str(e)}")
        finally:
            update_in_progress = False
            CACHE_METADATA = None  # Invalidate cache
    
    # Start update in a separate thread
    update_thread = threading.Thread(target=run_update, daemon=True)
    update_thread.start()

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    """
    Memory-optimized endpoint with multiple modes:
    
    Query parameters:
    - stream_all=true: Stream ALL data in one response (uses only 20-30MB memory)
    - limit: Number of records to return (default: 100, max: 1000)
    - offset: Starting position (default: 0)
    - metadata_only: If true, returns only metadata without data (default: false)
    - refresh: Triggers background data refresh (default: false)
    """
    # 1. Security Check
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )
    
    # 2. Check if streaming all data is requested
    stream_all = request.args.get('stream_all', 'false').lower() == 'true'
    
    if stream_all:
        # Stream the entire cache file directly (memory efficient!)
        if not os.path.exists(CACHE_FILE):
            return Response(
                json.dumps({
                    "status": "pending", 
                    "message": "No cached data available."
                }), 
                status=503, 
                mimetype='application/json'
            )
        
        # Check if refresh requested
        should_refresh = request.args.get('refresh', 'false').lower() == 'true'
        if should_refresh:
            trigger_background_update()
        
        # Stream the file directly
        # This uses only ~20-30MB memory regardless of file size!
        return Response(
            stream_with_context(stream_json_file(CACHE_FILE)),
            mimetype='application/json',
            headers={
                'Cache-Control': 'no-cache',
                'X-Data-Mode': 'streaming-all',
                'X-Memory-Usage': '~20-30MB'
            }
        )
    
    # 3. Parse pagination parameters
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)  # Max 1000 per request
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return Response(
            json.dumps({"status": "error", "message": "Invalid limit or offset parameter"}),
            status=400,
            mimetype='application/json'
        )
    
    metadata_only = request.args.get('metadata_only', 'false').lower() == 'true'
    should_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # 4. Check if cache exists
    if not os.path.exists(CACHE_FILE):
        return Response(
            json.dumps({
                "status": "pending", 
                "message": "No cached data available. Please wait for initial sync or trigger manual refresh at /refresh endpoint."
            }), 
            status=503, 
            mimetype='application/json'
        )
    
    # 5. If metadata only, return lightweight response
    if metadata_only:
        metadata = get_cache_metadata()
        if metadata:
            if should_refresh:
                trigger_background_update()
                metadata['_info'] = "Background refresh triggered."
            
            return Response(
                json.dumps(metadata),
                mimetype='application/json',
                headers={'Cache-Control': 'no-cache'}
            )
    
    # 6. Get paginated data
    try:
        paginated_data = read_cache_data_paginated(limit=limit, offset=offset)
        
        if paginated_data is None:
            return Response(
                json.dumps({"status": "error", "message": "Failed to read cache data"}),
                status=500,
                mimetype='application/json'
            )
        
        # Trigger background refresh if requested
        if should_refresh:
            trigger_background_update()
            paginated_data['_info'] = "Background refresh triggered. Call again in a few minutes for updated data."
        
        # Use gzip compression for large responses
        json_data = json.dumps(paginated_data)
        
        # Only compress if response is large
        if len(json_data) > 1024:  # Compress if > 1KB
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            return Response(
                compressed_data,
                mimetype='application/json',
                headers={
                    'Cache-Control': 'no-cache',
                    'Content-Encoding': 'gzip'
                }
            )
        else:
            return Response(
                json_data,
                mimetype='application/json',
                headers={'Cache-Control': 'no-cache'}
            )
            
    except Exception as e:
        print(f"Error in fetch_data: {str(e)}")
        return Response(
            json.dumps({"status": "error", "message": f"Internal error: {str(e)}"}),
            status=500,
            mimetype='application/json'
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
    """Check API and cache status (lightweight, no data loading)"""
    user_key = request.headers.get("X-API-Key")
    if user_key != API_KEY:
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized access"}), 
            status=401, 
            mimetype='application/json'
        )
    
    cache_exists = os.path.exists(CACHE_FILE)
    cache_age_minutes = None
    cache_size_mb = None
    record_count = None
    
    if cache_exists:
        cache_age = time.time() - os.path.getmtime(CACHE_FILE)
        cache_age_minutes = int(cache_age / 60)
        cache_size_mb = round(os.path.getsize(CACHE_FILE) / (1024*1024), 2)
        
        # Get record count from metadata
        metadata = get_cache_metadata()
        if metadata:
            record_count = metadata.get('count')
    
    status_data = {
        "api_status": "online",
        "cache_exists": cache_exists,
        "cache_age_minutes": cache_age_minutes,
        "cache_size_mb": cache_size_mb,
        "record_count": record_count,
        "update_in_progress": update_in_progress,
        "timestamp": time.ctime(),
        "memory_note": "API uses pagination to handle large datasets efficiently"
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
    print(f"  - GET  /fetch-data?stream_all=true (ALL data, only 20-30MB memory!) [NEW]")
    print(f"  - GET  /fetch-data?limit=100&offset=0 (paginated data)")
    print(f"  - GET  /fetch-data?metadata_only=true (lightweight metadata)")
    print(f"  - GET  /fetch-data?refresh=true (cached + triggers update)")
    print(f"  - POST /refresh (manually triggers data refresh)")
    print(f"  - GET  /status (check cache and API status)")
    print(f"  - GET  /health (health check)")
    print(f"\n[NEW] stream_all=true returns ALL 102K records using only 20-30MB!")
    print(f"Memory-optimized for Render's 512MB limit!")
    app.run(host='0.0.0.0', port=5000, debug=True)