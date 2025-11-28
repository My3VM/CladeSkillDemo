#!/bin/bash
# Start MCP Servers

set -e

echo "════════════════════════════════════════════════════════"
echo "  Starting MCP Servers"
echo "════════════════════════════════════════════════════════"
echo ""

# Activate environment
if [ -d "cenv" ]; then
    source cenv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping MCP servers..."
    pkill -f "monitoring-analysis-server.py" || true
    pkill -f "workflow-orchestration-server.py" || true
    pkill -f "log-analytics-server.py" || true
    sleep 1
}

# Trap to cleanup on exit
trap cleanup EXIT INT TERM

# Cleanup any existing servers
cleanup

echo "🚀 Starting Monitoring & Analysis Server on port 9001..."
python mcp-servers/monitoring-analysis-server.py &
MONITORING_PID=$!
echo "   PID: $MONITORING_PID"

sleep 1

echo "🚀 Starting Workflow Orchestration Server on port 9002..."
python mcp-servers/workflow-orchestration-server.py &
WORKFLOW_PID=$!
echo "   PID: $WORKFLOW_PID"

sleep 1

echo "🚀 Starting Log Analytics Server on port 9003..."
python mcp-servers/log-analytics-server.py &
ANALYTICS_PID=$!
echo "   PID: $ANALYTICS_PID"

sleep 2

echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅ MCP Servers Running"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Monitoring & Analysis:  http://127.0.0.1:9001/mcp"
echo "Workflow Orchestration: http://127.0.0.1:9002/mcp"
echo "Log Analytics:          http://127.0.0.1:9003/mcp"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait
