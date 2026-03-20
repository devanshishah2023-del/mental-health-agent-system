#!/bin/bash
# Mental Health Agent System — offline, no API key
# Usage: bash run.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   Mental Health Agent System      
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check Python 3
if ! command -v python3 &>/dev/null; then
  echo "  Python 3 not found."
  echo "    Install via Homebrew:  brew install python3"
  echo "    Or download from:      https://www.python.org/downloads/"
  exit 1
fi
echo "  Python $(python3 --version | cut -d' ' -f2) found"
echo "  No API key needed — fully offline"
echo ""
echo "  Starting on http://localhost:8000"
echo "    Opening browser in 2 seconds…"
echo "    Press Ctrl+C to stop."
echo ""

# Open browser after short delay (macOS)
(sleep 2 && open http://localhost:8000 2>/dev/null || true) &

python3 server.py
