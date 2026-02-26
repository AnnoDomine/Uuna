#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   WoW Datamine Toolkit - Initialization Script  ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Helper function for yes/no prompts
ask_yes_no() {
    local prompt="$1"
    local default="$2"
    local reply
    
    if [ "$default" = "Y" ]; then
        prompt="$prompt [Y/n]"
    else
        prompt="$prompt [y/N]"
    fi
    
    echo -e -n "${YELLOW}$prompt ${NC}"
    read reply
    
    if [ -z "$reply" ]; then
        reply="$default"
    fi
    
    case "$reply" in
        Y*|y*) return 0 ;;
        *) return 1 ;;
    esac
}

# Helper function to check command existence
check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

# --- 1. Check/Install uv ---
echo -e "${GREEN}Checking Python Environment (uv)...${NC}"
if check_cmd uv; then
    echo "✅ uv is installed."
else
    echo -e "${YELLOW}⚠️  uv is missing.${NC}"
    if ask_yes_no "Do you want to install 'uv' (Python package manager)?" "Y"; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Source cargo env if needed or add to path for current session
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        echo -e "${RED}❌ uv is required. Aborting.${NC}"
        exit 1
    fi
fi

# --- 2. Check/Install Node.js & pnpm ---
echo -e "\n${GREEN}Checking Frontend Environment (Node.js & pnpm)...${NC}"

install_node() {
    echo "Select installation method for Node.js (Version 24+ recommended):"
    echo "1) Try via NVM (Node Version Manager)"
    echo "2) Try via System Package Manager (requires sudo)"
    echo "3) Skip (I will install it manually)"
    echo "4) Abort"
    
    echo -n "Choice [1-4]: "
    read choice
    case "$choice" in
        1)
            if [ -s "$NVM_DIR/nvm.sh" ]; then
                . "$NVM_DIR/nvm.sh"
                nvm install 24
                nvm use 24
                elif command -v nvm >/dev/null 2>&1; then
                nvm install 24
                nvm use 24
            else
                echo -e "${RED}NVM not found.${NC}"
                install_node # Retry
            fi
        ;;
        2)
            if check_cmd apt-get; then
                curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
                sudo apt-get install -y nodejs
                elif check_cmd brew; then
                brew install node
                elif check_cmd dnf; then
                sudo dnf install nodejs
                elif check_cmd pacman; then
                sudo pacman -S nodejs npm
            else
                echo -e "${RED}No supported package manager found.${NC}"
                install_node # Retry
            fi
        ;;
        3)
            echo "Skipping Node.js installation."
        ;;
        4)
            exit 1
        ;;
        *)
            echo "Invalid choice."
            install_node
        ;;
    esac
}

if ! check_cmd node; then
    echo -e "${YELLOW}⚠️  Node.js is missing.${NC}"
    install_node
else
    # Check version roughly
    NODE_VER=$(node -v | cut -d. -f1 | tr -d 'v')
    if [ "$NODE_VER" -lt 20 ]; then
        echo -e "${YELLOW}⚠️  Node.js version $NODE_VER is old (20+ recommended).${NC}"
        install_node
    else
        echo "✅ Node.js is installed ($NODE_VER)."
    fi
fi

if ! check_cmd pnpm; then
    echo -e "${YELLOW}⚠️  pnpm is missing.${NC}"
    if ask_yes_no "Install pnpm via corepack/npm?" "Y"; then
        if check_cmd corepack; then
            corepack enable
            corepack prepare pnpm@latest --activate
        else
            npm install -g pnpm
        fi
    else
        echo "Skipping pnpm. TUI installation might fail."
    fi
else
    echo "✅ pnpm is installed."
fi

# --- 3. Check/Install Ollama ---
echo -e "\n${GREEN}Checking AI Backend (Ollama)...${NC}"
if check_cmd ollama; then
    echo "✅ Ollama is installed."
else
    echo -e "${YELLOW}⚠️  Ollama is missing.${NC}"
    if ask_yes_no "Do you want to install Ollama (Local AI Runtime)?" "Y"; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Skipping Ollama. AI features will not work."
    fi
fi

# --- 4. Pull AI Model ---
DEFAULT_MODEL="qwen3:8b"
echo -e "\n${GREEN}Checking AI Model ($DEFAULT_MODEL)...${NC}"
if check_cmd ollama; then
    # Start ollama if not running? Usually it runs as daemon.
    # Check if model exists
    if ollama list | grep -q "$DEFAULT_MODEL"; then
        echo "✅ Model $DEFAULT_MODEL is present."
    else
        if ask_yes_no "Pull default model '$DEFAULT_MODEL'? (Required for agents)" "Y"; then
            echo "Pulling model (this may take a while)..."
            ollama pull "$DEFAULT_MODEL"
        fi
    fi
fi

# --- 5. Project Setup ---
echo -e "\n${BLUE}--- Project Setup ---${NC}"

echo -e "${GREEN}Syncing Python Environment...${NC}"
uv sync

echo -e "\n${GREEN}Installing Root Dependencies (Husky)...${NC}"
pnpm install

echo -e "\n${GREEN}Installing TUI Dependencies...${NC}"
cd Tools/web/tui-node && pnpm install && cd ../../..

echo -e "\n${GREEN}Initializing Database...${NC}"
if ask_yes_no "Initialize project database structure?" "Y"; then
    uv run manage.py init
else
    echo "Skipping database initialization."
fi

# --- 6. Hardware Optimization ---
echo -e "\n${GREEN}Running Hardware Auto-Optimization...${NC}"
if ask_yes_no "Run Hardware Auto-Optimization (Recommended)?" "Y"; then
    # Interactive optimization tool will handle its own confirmation or use -y if we wanted to force it
    # We let it run interactively so user sees what happens
    uv run manage.py optimize
else
    echo "Skipping hardware optimization."
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}✅ Initialization Complete!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo "You can now run:"
echo "  - TUI:    cd Tools/web/tui-node && pnpm start"
echo "  - Backend: uv run manage.py serve"
echo ""
