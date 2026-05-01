#!/bin/bash
set -e

echo "🎓 Academic Slides Agent — Setup"
echo "================================="

# 1. Check Node.js
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo "❌ Node.js not found. Please install: https://nodejs.org/"
        exit 1
    fi
fi
echo "✅ Node.js $(node -v)"

# 2. Install Marp CLI
if ! command -v marp &> /dev/null; then
    echo "📦 Installing Marp CLI..."
    npm install -g @marp-team/marp-cli
fi
echo "✅ Marp CLI $(marp --version 2>/dev/null | head -1)"

# 3. Install Python package
echo "📦 Installing Python package..."
pip install -e ".[dev]"
echo "✅ Python package installed"

# 4. API Key setup
echo ""
echo "🔑 API Key Configuration"
echo "  The agent uses LLM APIs (OpenAI/Anthropic) for slide generation."
echo "  Keys are stored securely in your system's credential store."
echo ""
read -p "  Configure API keys now? [Y/n]: " setup_keys
if [ "$setup_keys" != "n" ] && [ "$setup_keys" != "N" ]; then
    slides setup-keys
fi

echo ""
echo "🎉 Setup complete! Try:"
echo "   slides validate examples/moe_paper/output/slides.md --config examples/moe_paper/paper_config.yaml"
echo "   slides --help"
