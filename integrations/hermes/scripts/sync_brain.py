#!/usr/bin/env python3
"""
Python wrapper for sync-brain script.
Allows Hermes cron scheduling to easily execute the correct platform-specific script.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    
    if sys.platform == "win32":
        script_path = script_dir / "sync-brain.ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
    else:
        script_path = script_dir / "sync-brain.sh"
        # Make sure it's executable
        if not os.access(script_path, os.X_OK):
            os.chmod(script_path, 0o755)
        cmd = ["bash", str(script_path)]
        
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing sync script: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
