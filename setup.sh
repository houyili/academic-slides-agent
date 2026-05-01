#!/bin/bash
set -e

echo "🎓 Academic Slides Agent — Setup"
echo "================================="
echo ""

# Detect OS
OS="$(uname -s)"
echo "📍 Detected OS: $OS"

# 1. Check/Install Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python >= 3.9"
    echo "   macOS:  brew install python3"
    echo "   Ubuntu: sudo apt install python3 python3-pip"
    echo "   Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi
PY_VERSION=$(python3 --version 2>&1)
echo "✅ $PY_VERSION"

# 2. Check/Install Node.js
if ! command -v node &> /dev/null; then
    echo "📦 Node.js not found. Installing..."
    case "$OS" in
        Darwin)
            if command -v brew &> /dev/null; then
                brew install node
            else
                echo "❌ Homebrew not found. Install Node.js manually: https://nodejs.org/"
                exit 1
            fi
            ;;
        Linux)
            if command -v apt &> /dev/null; then
                echo "  Using apt..."
                sudo apt update && sudo apt install -y nodejs npm
            elif command -v dnf &> /dev/null; then
                echo "  Using dnf..."
                sudo dnf install -y nodejs npm
            elif command -v pacman &> /dev/null; then
                echo "  Using pacman..."
                sudo pacman -S --noconfirm nodejs npm
            else
                echo "❌ No supported package manager found. Install Node.js manually: https://nodejs.org/"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unsupported OS: $OS. Install Node.js manually: https://nodejs.org/"
            exit 1
            ;;
    esac
fi
echo "✅ Node.js $(node -v)"

# 3. Install Marp CLI
if ! command -v marp &> /dev/null; then
    echo "📦 Installing Marp CLI..."
    npm install -g @marp-team/marp-cli
fi
echo "✅ Marp CLI $(marp --version 2>/dev/null | head -1)"

# 4. Install Python package
echo ""
echo "📦 Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt 2>/dev/null || python3 -m pip install --user click pyyaml keyring python-dotenv
echo "✅ Python dependencies installed"

# 5. Install the package itself
echo "📦 Installing academic-slides-agent..."
python3 -m pip install --user . 2>/dev/null || python3 -m pip install --user -e . 2>/dev/null || echo "⚠️  Package install failed. Use: PYTHONPATH=src python3 -m academic_slides_agent.cli"

# 6. Check if 'slides' CLI is accessible
if command -v slides &> /dev/null; then
    echo "✅ CLI installed: $(which slides)"
else
    echo "⚠️  'slides' CLI not in PATH. You can use:"
    echo "   PYTHONPATH=src python3 -m academic_slides_agent.cli --help"
    echo "   Or add ~/.local/bin to your PATH:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# 7. API Key setup (optional)
echo ""
echo "🔑 API Key Configuration (optional)"
echo "  The agent can use LLM APIs (OpenAI/Anthropic) for automated generation."
echo "  Keys are stored in your system's secure credential store."
echo ""
read -p "  Configure API keys now? [y/N]: " setup_keys
if [ "$setup_keys" = "y" ] || [ "$setup_keys" = "Y" ]; then
    PYTHONPATH=src python3 -c "from academic_slides_agent.keychain import interactive_setup; interactive_setup()"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "  Quick start:"
echo "    slides validate <slides.md> --config <paper_config.yaml>"
echo "    slides compile --workspace . --theme themes/academic-emerald-4k.css"
echo "    slides run --workspace . --config paper_config.yaml"
echo "    slides --help"
