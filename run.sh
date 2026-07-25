#!/usr/bin/env bash
set -euo pipefail

# run_all.sh: starts the backend server in the background and the Textual
# UI in the foreground (or a new terminal window with --popup).
#
# Usage:
#   ./run_all.sh            # UI in this terminal
#   ./run_all.sh --popup    # UI in a new terminal window; backend stays
#                            # running in THIS terminal until you Ctrl+C it

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONSOLE_UI_DIR="$REPO_ROOT/console_ui"
SERVER_SCRIPT="$REPO_ROOT/battlefieldengine/battlefieldengine/server.py"
UI_SCRIPT="$CONSOLE_UI_DIR/battlefield_ui.py"

POPUP=false
[[ "${1:-}" == "--popup" ]] && POPUP=true

echo "Starting backend server..."
python3 "$SERVER_SCRIPT" &
SERVER_PID=$!

cleanup() {
  echo ""
  echo "Stopping backend (pid $SERVER_PID)..."
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Give the backend a moment to connect before the UI starts talking to it
sleep 1

cd "$CONSOLE_UI_DIR"

if [[ "$POPUP" == true ]]; then
  echo "Launching UI in a new terminal window..."
  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- python3 "$UI_SCRIPT"
  elif command -v konsole >/dev/null 2>&1; then
    konsole -e python3 "$UI_SCRIPT" &
  elif command -v xterm >/dev/null 2>&1; then
    xterm -e python3 "$UI_SCRIPT" &
  else
    echo "No known terminal emulator found (gnome-terminal/konsole/xterm)."
    echo "Falling back to running the UI in this terminal."
    python3 "$UI_SCRIPT"
    exit 0
  fi
  echo ""
  echo "Backend is running in this window. Press Ctrl+C here to stop it when you're done."
  wait "$SERVER_PID"
else
  python3 "$UI_SCRIPT"
fi