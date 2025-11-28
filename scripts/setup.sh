#!/bin/bash
# Setup script for Claude Skills + MCP Demo

set -e

echo "════════════════════════════════════════════════════════"
echo "  Claude Skills + MCP Setup"
echo "════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"
echo ""

# Use cenv if it exists, otherwise create it
echo "🔧 Setting up virtual environment..."
if [ -d "cenv" ]; then
    echo "✅ Using existing cenv"
elif [ -d "venv" ]; then
    echo "✅ Using existing venv"
else
    python3 -m venv cenv
    echo "✅ Created cenv"
fi
echo ""

# Activate
echo "🔌 Activating environment..."
if [ -d "cenv" ]; then
    source cenv/bin/activate
else
    source venv/bin/activate
fi
echo "✅ Activated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Check .env
echo "🔐 Checking .env file..."
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env with Bedrock defaults..."
    cat > .env << 'EOF'
# AWS Bedrock Configuration
AWS_DEFAULT_REGION=us-east-2
CLAUDE_CODE_USE_BEDROCK=1
EOF
    echo "✅ Created .env"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Configure AWS credentials in ~/.aws/credentials"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "✅ .env exists"
fi
echo ""

echo "════════════════════════════════════════════════════════"
echo "  ✅ Setup Complete!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start MCP servers:"
echo "     ./scripts/start-servers.sh"
echo ""
echo "  2. Run demo (in another terminal):"
echo "     ./scripts/run-demo.sh"
echo ""
echo "════════════════════════════════════════════════════════"
