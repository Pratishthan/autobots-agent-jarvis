#!/usr/bin/env bash
# ABOUTME: Run all domain Chainlit UIs simultaneously (Concierge, Customer Support, Sales)

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Array to store background process PIDs
PIDS=()

# Cleanup function to kill all background processes
cleanup() {
    echo ""
    echo "Shutting down all domains..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait
    echo "All domains stopped."
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

echo "=========================================="
echo "Starting All Domains"
echo "=========================================="
echo ""

# Start Concierge (port 2337)
echo "🤖 Starting Concierge..."
DYNAGENT_CONFIG_ROOT_DIR="agent_configs/concierge" \
    chainlit run src/autobots_agents_jarvis/domains/concierge/server.py \
    --port 2337 --host 127.0.0.1 > /dev/null 2>&1 &
PIDS+=($!)
echo "   ✅ Concierge running at http://localhost:2337"

# Start Customer Support (port 2338)
echo "🎧 Starting Customer Support..."
DYNAGENT_CONFIG_ROOT_DIR="agent_configs/customer-support" \
    chainlit run src/autobots_agents_jarvis/domains/customer_support/server.py \
    --port 2338 --host 127.0.0.1 > /dev/null 2>&1 &
PIDS+=($!)
echo "   ✅ Customer Support running at http://localhost:2338"

# Start Sales (port 2339)
echo "💼 Starting Sales..."
DYNAGENT_CONFIG_ROOT_DIR="agent_configs/sales" \
    chainlit run src/autobots_agents_jarvis/domains/sales/server.py \
    --port 2339 --host 127.0.0.1 > /dev/null 2>&1 &
PIDS+=($!)
echo "   ✅ Sales running at http://localhost:2339"

echo ""
echo "=========================================="
echo "All domains are running!"
echo "=========================================="
echo ""
echo "Access your domains at:"
echo "  🤖 Concierge:        http://localhost:2337"
echo "  🎧 Customer Support: http://localhost:2338"
echo "  💼 Sales:            http://localhost:2339"
echo ""
echo "Press Ctrl+C to stop all domains..."
echo ""

# Wait for all background processes
wait
