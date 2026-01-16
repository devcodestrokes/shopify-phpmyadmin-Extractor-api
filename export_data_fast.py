"""
ULTRA-FAST Data Exporter - Reads directly from cache file
Perfect for large datasets (100k+ records)
"""

import json
import csv
import os
import time

# Configuration
CACHE_FILE = "data_cache.json"

def print_banner():
    print("\n" + "="*80)
    print("⚡ ULTRA-FAST DATA EXPORTER - Direct File Access")
    print("="*80 + "\n")

def read_cache_fast():
    """Read cache file directly - INSTANT for any size!"""
    if not os.path.exists(CACHE_FILE):
        print(f"❌ Error: {CACHE_FILE} not found!")
        print("\n💡 Run sync_worker.py first to create the cache")
        return None
    
    print("📊 Reading cache file...")
    
    file_size_mb = os.path.getsize(CACHE_FILE) / (1024 * 1024)
    print(f"   File size: {file_size_mb:.2f} MB")
    
    start_time = time.time()
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    elapsed = time.time() - start_time
    
    records = data.get('data', [])
    count = data.get('count', len(records))
    
    print(f"✅ Loaded {count:,} records in {elapsed:.2f} seconds!")
    print(f"   Speed: {count/elapsed:,.0f} records/second")
    
    return records

def save_as_json(data, filename="exported_data.json"):
    """Save as JSON with metadata"""
    print(f"\n💾 Saving as JSON: {filename}")
    start_time = time.time()
    
    output = {
        "total_count": len(data),
        "exported_at": time.ctime(),
        "source": "data_cache.json",
        "data": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    
    print(f"✅ Saved {len(data):,} records in {elapsed:.2f} seconds")
    print(f"   File size: {size_mb:.2f} MB")
    
    return filename

def save_as_csv(data, filename="exported_data.csv"):
    """Save as CSV"""
    if not data:
        print("❌ No data to save")
        return None
    
    print(f"\n💾 Saving as CSV: {filename}")
    start_time = time.time()
    
    # Get all unique keys
    all_keys = set()
    for record in data:
        if isinstance(record, dict):
            all_keys.update(record.keys())
    
    fieldnames = sorted(all_keys)
    
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Show progress for large files
        for i, record in enumerate(data, 1):
            writer.writerow(record)
            if i % 10000 == 0:
                print(f"   Progress: {i:,}/{len(data):,} ({i/len(data)*100:.1f}%)")
    
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    
    print(f"✅ Saved {len(data):,} records in {elapsed:.2f} seconds")
    print(f"   File size: {size_mb:.2f} MB")
    
    return filename

def show_sample_data(data, num_records=5):
    """Show sample records"""
    print(f"\n📋 Sample Data (first {num_records} records):")
    print("-" * 80)
    
    for i, record in enumerate(data[:num_records], 1):
        print(f"\n{i}. {json.dumps(record, indent=2, ensure_ascii=False)[:500]}...")
    
    print("-" * 80)

def main():
    print_banner()
    
    # Step 1: Read cache file (FAST!)
    records = read_cache_fast()
    
    if not records:
        return
    
    if len(records) == 0:
        print("\n⚠️ Cache file is empty!")
        return
    
    # Show sample
    show_sample_data(records, 3)
    
    # Step 2: Choose export format
    print("\n📦 Export Options:")
    print("   1. JSON (structured, easy to parse)")
    print("   2. CSV (for Excel/Google Sheets)")
    print("   3. Both formats")
    print("   4. Just show stats (no export)")
    
    choice = input("\nChoose option (1/2/3/4) [1]: ").strip() or "1"
    
    if choice == "4":
        print("\n✅ No export requested")
        return
    
    # Step 3: Export
    print("\n" + "="*80)
    print("💾 EXPORTING DATA")
    print("="*80)
    
    files_created = []
    total_start = time.time()
    
    if choice in ["1", "3"]:
        json_file = save_as_json(records, "all_shopify_data.json")
        files_created.append(json_file)
    
    if choice in ["2", "3"]:
        csv_file = save_as_csv(records, "all_shopify_data.csv")
        if csv_file:
            files_created.append(csv_file)
    
    total_elapsed = time.time() - total_start
    
    # Step 4: Summary
    print("\n" + "="*80)
    print("✅ EXPORT COMPLETE!")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   • Total records: {len(records):,}")
    print(f"   • Total time: {total_elapsed:.2f} seconds")
    print(f"   • Files created: {len(files_created)}")
    
    total_size = 0
    for filepath in files_created:
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_size += size_mb
        print(f"      - {filepath} ({size_mb:.2f} MB)")
    
    print(f"   • Total exported size: {total_size:.2f} MB")
    
    print("\n💡 What's next?")
    print("   ✅ Open JSON in any text editor or IDE")
    print("   ✅ Import CSV into Excel/Google Sheets")
    print("   ✅ Use in your applications")
    
    if files_created and files_created[0].endswith('.json'):
        print(f"\n📖 How to use in Python:")
        print(f"""
    import json
    
    with open('{files_created[0]}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_records = data['data']
    print(f"Loaded {{len(all_records):,}} records")
    
    # Example: Access first record
    if all_records:
        first_record = all_records[0]
        print("First record:", first_record)
    
    # Example: Filter data
    # filtered = [r for r in all_records if some_condition]
        """)
    
    print("\n🎉 Done! All your data is now exported.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Export cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
