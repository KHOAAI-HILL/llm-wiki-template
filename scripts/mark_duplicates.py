import json
import os
import hashlib
import re
from datetime import datetime

from pathlib import Path
ABSORB_LOG_PATH = Path.cwd() / 'wiki' / 'absorb-log.json'
RAW_DIR = Path.cwd() / 'raw' / 'misc'

def get_sha256(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def mark_dupes(dry_run=False):
    if not os.path.exists(ABSORB_LOG_PATH):
        raise FileNotFoundError(f"{ABSORB_LOG_PATH} not found.")
        
    with open(ABSORB_LOG_PATH, 'r', encoding='utf-8') as f:
        log = json.load(f)
    
    entries = log.get('entries', {})
    absorbed_keys = set(entries.keys())
    
    suffix_pattern = re.compile(r'^(.+?)(-\d+)?\.md$')
    
    count = 0
    today = datetime.now().strftime('%Y-%m-%d')
    marked_files = []
    
    for fn in os.listdir(RAW_DIR):
        if not fn.endswith('.md'):
            continue
            
        raw_key = f'raw/misc/{fn}'
        if raw_key in absorbed_keys:
            continue
            
        m = suffix_pattern.match(fn)
        if m:
            base_name = m.group(1)
            suffix = m.group(2)
            
            if suffix:
                base_key = f'raw/misc/{base_name}.md'
                if base_key in absorbed_keys:
                    file_path = os.path.join(RAW_DIR, fn)
                    file_hash = get_sha256(file_path)
                    
                    entries[raw_key] = {
                        "absorbed_at": today,
                        "wiki_articles": [],
                        "hash": file_hash
                    }
                    marked_files.append({"file": fn, "base": f"{base_name}.md"})
                    count += 1

    if count > 0 and not dry_run:
        log['entries'] = entries
        log['last_updated'] = today
        with open(ABSORB_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
            
    return {"marked": count, "files": marked_files}

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    print("--- Phase 1: Marking Suffix Duplicates ---")
    try:
        res = mark_dupes(dry_run)
    except Exception as e:
        print(f"Error: {e}")
        return
        
    for f in res['files']:
        print(f"  Marked: {f['file']} (Duplicate of {f['base']})")
        
    if res['marked'] > 0:
        if dry_run:
            print(f"\n[DRY-RUN] Found {res['marked']} duplicate files to mark.")
        else:
            print(f"\nSuccessfully marked {res['marked']} duplicate files in absorb-log.json.")
    else:
        print("\nNo duplicate suffix files found to mark.")

if __name__ == "__main__":
    main()
