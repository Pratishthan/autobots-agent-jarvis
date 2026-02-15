#!/usr/bin/env bash
# ABOUTME: Run Sales Chainlit UI in development mode

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Set default config directory if not already set
export DYNAGENT_CONFIG_ROOT_DIR="${DYNAGENT_CONFIG_ROOT_DIR:-agent_configs/sales}"

# Default port
PORT="${PORT:-2339}"

echo "Starting Sales on http://localhost:$PORT"
echo "Config directory: $DYNAGENT_CONFIG_ROOT_DIR"

# Run Chainlit
chainlit run src/autobots_agents_jarvis/domains/sales/server.py --port "$PORT" --host 127.0.0.1
