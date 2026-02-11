#!/usr/bin/env bash
# ABOUTME: Run Jarvis Chainlit UI in development mode

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Set default config directory if not already set
export DYNAGENT_CONFIG_ROOT_DIR="${DYNAGENT_CONFIG_ROOT_DIR:-configs/jarvis}"

# Default port
PORT="${PORT:-1337}"

echo "Starting Jarvis on http://localhost:$PORT"
echo "Config directory: $DYNAGENT_CONFIG_ROOT_DIR"

# Run Chainlit
chainlit run src/autobots_agents_jarvis/servers/jarvis_ui.py --port "$PORT" --host 0.0.0.0
