import os
import json
import threading
import time
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
PROJECT_DIR = os.getcwd()
CACHE_FILE = os.path.join(PROJECT_DIR, "data_cache.json")
API_KEY = "shopify_secure_key_2025"
CACHE_LOCK = threading.Lock()
update_in_progress = False
update_tasks = {}  # Track background tasks

def parse_destination_field(record):
    """Parse the destination field from string to JSON object"""
    if 'destination' in record and record['destination']:
        try:
            # The destination is double-encoded JSON string
            # First decode: removes outer quotes
            # Second decode: parses the actual JSON
            destination_str = record['destination']
            
            # Remove outer quotes if present
            if destination_str.startswith('"') and destination_str.endswith('"'):
                destination_str = destination_str[1:-1]
            
            # Unescape the JSON string
            destination_str = destination_str.replace('\\\"', '"').replace('\\\\', '\\')
            
            # Parse to JSON object
            record['destination'] = json.loads(destination_str)
        except Exception as e:
            # If parsing fails, keep original string
            print(f"Warning: Could not parse destination field: {e}")
            pass
    
    return record

def get_cached_data(start_row=None, end_row=None, parse_json=True):
    """Get data from cache file with optional row range"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('data', [])
        total_count = data.get('count', len(records))
        
        # Apply row range if specified
        if start_row is not None or end_row is not None:
            start_idx = (start_row - 1) if start_row else 0
            end_idx = end_row if end_row else len(records)
            records = records[start_idx:end_idx]
        
        # Parse destination field for each record
        if parse_json:
            records = [parse_destination_field(record.copy()) for record in records]
        
        return {
            'total_count': total_count,
            'returned_count': len(records),
            'start_row': (start_row or 1),
            'end_row': (start_row or 1) + len(records) - 1 if records else 0,
            'data': records,
            'cached_at': time.ctime(os.path.getmtime(CACHE_FILE))
        }
    except Exception as e:
        print(f"Error reading cache: {e}")
        return None

def trigger_background_scrape(task_id):
    """Scrape fresh data in background"""
    global update_in_progress
    
    try:
        update_in_progress = True
        update_tasks[task_id] = {
            'status': 'running',
            'started_at': time.time(),
            'message': 'Scraping fresh data...'
        }
        
        print(f"[{time.ctime()}] Background scrape started (task: {task_id})")
        
        # Import and run scraper
        from sync_worker import perform_sync
        perform_sync()
        
        # Update task status
        update_tasks[task_id] = {
            'status': 'completed',
            'completed_at': time.time(),
            'message': 'Fresh data ready!'
        }
        
        print(f"[{time.ctime()}] Background scrape completed (task: {task_id})")
        
    except Exception as e:
        update_tasks[task_id] = {
            'status': 'failed',
            'error': str(e),
            'completed_at': time.time()
        }
        print(f"Background scrape error: {e}")
    finally:
        update_in_progress = False

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Enhanced API endpoint:
    - Returns cached data immediately
    - Optionally triggers background refresh
    - Supports row ranges
    - Automatically parses destination field to JSON
    
    Query Parameters:
        - start_row: Starting row number (1-indexed)
        - end_row: Ending row number (inclusive)
        - refresh: If 'true', triggers background refresh
        - parse_json: If 'false', keeps destination as string (default: true)
    
    Examples:
        /api/data                           -> All cached data (destination parsed)
        /api/data?start_row=1&end_row=100   -> Rows 1-100
        /api/data?refresh=true              -> Return cached + trigger refresh
        /api/data?parse_json=false          -> Keep destination as string
    """
    # Auth check
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Parse parameters
    start_row = request.args.get('start_row', type=int)
    end_row = request.args.get('end_row', type=int)
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    parse_json = request.args.get('parse_json', 'true').lower() == 'true'
    
    # Get cached data immediately
    cached_data = get_cached_data(start_row, end_row, parse_json)
    
    if cached_data is None:
        return jsonify({
            "error": "No cached data available",
            "message": "Run sync_worker.py first to create cache"
        }), 503
    
    # Prepare response
    response_data = {
        "status": "success",
        "source": "cache",
        "total_count": cached_data['total_count'],
        "returned_count": cached_data['returned_count'],
        "start_row": cached_data['start_row'],
        "end_row": cached_data['end_row'],
        "cached_at": cached_data['cached_at'],
        "data": cached_data['data']
    }
    
    # Trigger background refresh if requested
    if refresh and not update_in_progress:
        task_id = str(uuid.uuid4())[:8]
        response_data['refresh_triggered'] = True
        response_data['task_id'] = task_id
        response_data['message'] = 'Returning cached data. Fresh data being fetched in background.'
        response_data['check_status_url'] = f'/api/task/{task_id}'
        
        # Start background task
        thread = threading.Thread(target=trigger_background_scrape, args=(task_id,), daemon=True)
        thread.start()
        
    elif refresh and update_in_progress:
        response_data['message'] = 'Refresh already in progress. Returning cached data.'
    
    return jsonify(response_data)

@app.route('/api/data/fresh', methods=['GET'])
def get_fresh_data():
    """
    Get fresh data with Server-Sent Events (SSE)
    - Streams old data immediately
    - Scrapes fresh data
    - Streams updated data when ready
    
    Query Parameters:
        - start_row: Starting row number
        - end_row: Ending row number
    """
    # Auth check
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    start_row = request.args.get('start_row', type=int)
    end_row = request.args.get('end_row', type=int)
    
    def generate():
        # Step 1: Send cached data immediately
        cached = get_cached_data(start_row, end_row)
        
        if cached:
            yield f"data: {json.dumps({'type': 'cached', 'data': cached})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'No cache available'})}\n\n"
            return
        
        # Step 2: Notify starting refresh
        yield f"data: {json.dumps({'type': 'status', 'message': 'Fetching fresh data...'})}\n\n"
        
        # Step 3: Scrape fresh data
        try:
            from sync_worker import perform_sync
            perform_sync()
            
            # Step 4: Send fresh data
            fresh = get_cached_data(start_row, end_row)
            if fresh:
                yield f"data: {json.dumps({'type': 'fresh', 'data': fresh})}\n\n"
            
            # Step 5: Send completion
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Fresh data ready'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/task/<task_id>', methods=['GET'])
def check_task_status(task_id):
    """Check status of background task"""
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    if task_id not in update_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task_info = update_tasks[task_id]
    
    # If task is completed, return fresh data
    if task_info['status'] == 'completed':
        start_row = request.args.get('start_row', type=int)
        end_row = request.args.get('end_row', type=int)
        fresh_data = get_cached_data(start_row, end_row)
        
        return jsonify({
            "task_status": task_info['status'],
            "message": task_info['message'],
            "fresh_data": fresh_data
        })
    
    return jsonify({
        "task_status": task_info['status'],
        "message": task_info.get('message', ''),
        "error": task_info.get('error')
    })

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Get metadata without loading full data"""
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    if not os.path.exists(CACHE_FILE):
        return jsonify({"error": "No cache available"}), 503
    
    try:
        # Read only first few bytes for count
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            partial = f.read(500)
        
        if '"count":' in partial:
            start = partial.index('"count":') + 8
            end = partial.index(',', start)
            count = int(partial[start:end].strip())
        else:
            count = 0
        
        return jsonify({
            'total_count': count,
            'file_size_kb': round(os.path.getsize(CACHE_FILE) / 1024, 2),
            'file_size_mb': round(os.path.getsize(CACHE_FILE) / (1024 * 1024), 2),
            'last_modified': time.ctime(os.path.getmtime(CACHE_FILE))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "cache_exists": os.path.exists(CACHE_FILE),
        "update_in_progress": update_in_progress
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 ENHANCED SHOPIFY DATA API")
    print("="*80)
    print("\n📚 API Endpoints:")
    print("\n1️⃣ Get Data (Immediate + Optional Background Refresh):")
    print("   GET /api/data")
    print("   GET /api/data?start_row=1&end_row=100")
    print("   GET /api/data?refresh=true  (returns cached, refreshes in background)")
    print("   GET /api/data?start_row=1&end_row=100&refresh=true")
    
    print("\n2️⃣ Get Fresh Data (Server-Sent Events - Real-time Updates):")
    print("   GET /api/data/fresh")
    print("   GET /api/data/fresh?start_row=1&end_row=100")
    
    print("\n3️⃣ Check Background Task Status:")
    print("   GET /api/task/{task_id}")
    
    print("\n4️⃣ Get Metadata:")
    print("   GET /api/metadata")
    
    print("\n5️⃣ Health Check:")
    print("   GET /health")
    
    print("\n" + "="*80)
    print("💡 USAGE TIPS:")
    print("="*80)
    print("\n📌 For Best User Experience:")
    print("   1. Use /api/data with refresh=true")
    print("   2. Show cached data to user immediately")
    print("   3. Poll /api/task/{task_id} or use /api/data/fresh for updates")
    
    print("\n📌 Row Ranges:")
    print("   - start_row is 1-indexed (starts at 1, not 0)")
    print("   - end_row is inclusive")
    print("   - Example: start_row=1&end_row=100 returns rows 1 to 100")
    
    print("\n📌 All requests require X-API-Key header")
    print(f"   X-API-Key: {API_KEY}")
    
    print("\n" + "="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
