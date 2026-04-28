#!/bin/bash
# Sync Second Brain wiki from GitHub
# Usage: Called by Hermes cron via sync_brain.py wrapper
set -e

BRAIN_DIR="${HERMES_HOME:-/opt/data}/second-brain"

if [ ! -d "$BRAIN_DIR/.git" ]; then
    echo "ERROR: Not a git repo at $BRAIN_DIR"
    exit 1
fi

cd "$BRAIN_DIR"
git fetch origin 2>&1
git reset --hard origin/main 2>&1
echo "Synced at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Wiki articles: $(find wiki -name '*.md' | wc -l)"
