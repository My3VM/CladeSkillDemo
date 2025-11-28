#!/bin/bash
# Start the Claude Agent Web UI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Claude Agent Web UI Launcher${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the project root
if [ ! -f "web_ui.py" ]; then
    echo -e "${YELLOW}⚠️  Error: web_ui.py not found. Run from project root.${NC}"
    exit 1
fi

# Activate virtual environment
if [ -d "cenv" ]; then
    echo -e "${GREEN}✓${NC} Activating cenv virtual environment..."
    source cenv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Activating venv virtual environment..."
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Warning: No virtual environment found. Using system Python.${NC}"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found.${NC}"
    echo -e "Creating .env with default AWS settings..."
    cat > .env << EOF
AWS_DEFAULT_REGION=us-east-2
CLAUDE_CODE_USE_BEDROCK=1
EOF
fi

# Install dependencies if needed
echo -e "${GREEN}✓${NC} Checking dependencies..."
pip install -q fastapi uvicorn websockets 2>/dev/null || true

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📋 Pre-flight Checklist:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}1.${NC} Make sure MCP servers are running:"
echo -e "   - Monitoring Analysis Server: http://127.0.0.1:9001/mcp"
echo -e "   - Workflow Orchestration Server: http://127.0.0.1:9002/mcp"
echo ""
echo -e "${YELLOW}2.${NC} Start MCP servers in separate terminals:"
echo -e "   ${BLUE}./scripts/start-servers.sh${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Give user a moment to read
sleep 2

# Run the web UI
echo -e "${GREEN}🌐 Starting Web UI on http://localhost:8000${NC}"
echo ""

python web_ui.py

