# --- Add this to your Hermes entrypoint.sh ---
# Second Brain: clone or pull
BRAIN_DIR="$HERMES_HOME/second-brain"
BRAIN_REPO="${SECOND_BRAIN_REPO:-}"
BRAIN_TOKEN="${GITHUB_TOKEN:-}"

if [ -n "$BRAIN_REPO" ] && [ -n "$BRAIN_TOKEN" ]; then
    BRAIN_URL="https://${BRAIN_TOKEN}@github.com/${BRAIN_REPO}.git"
    if [ -d "$BRAIN_DIR/.git" ]; then
        echo "Pulling latest Second Brain..."
        cd "$BRAIN_DIR" && git pull --rebase 2>&1 || echo "Warning: pull failed"
        cd "$HERMES_HOME"
    else
        echo "Cloning Second Brain..."
        git clone "$BRAIN_URL" "$BRAIN_DIR" 2>&1 || echo "Warning: clone failed"
    fi
fi
