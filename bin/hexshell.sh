#!/bin/bash
# HexShell - Cyberpunk Terminal Interface
# Main launcher script

# Color definitions
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
HEXSHELL_HOME="${HEXSHELL_HOME:-$HOME/.hexshell}"
CONFIG_FILE="$HEXSHELL_HOME/config.yaml"
VENV_PATH="$HEXSHELL_HOME/venv"
SRC_PATH="$PROJECT_ROOT/src"

mkdir -p "$HEXSHELL_HOME"

show_boot_sequence() {
    clear
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "    ██╗  ██╗███████╗██╗  ██╗███████╗██╗  ██╗███████╗██╗     ██╗"
    echo "    ██║  ██║██╔════╝╚██╗██╔╝██╔════╝██║  ██║██╔════╝██║     ██║"
    echo "    ███████║█████╗   ╚███╔╝ ███████╗███████║█████╗  ██║     ██║"
    echo "    ██╔══██║██╔══╝   ██╔██╗ ╚════██║██╔══██║██╔══╝  ██║     ██║"
    echo "    ██║  ██║███████╗██╔╝ ██╗███████║██║  ██║███████╗███████╗███████╗"
    echo "    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    
    boot_messages=(
        "Initializing quantum encryption matrix..."
        "Loading neural interface drivers..."
        "Establishing secure connection to mainframe..."
        "Calibrating holographic display parameters..."
        "Synchronizing with orbital mechanics database..."
        "Mounting virtual file systems..."
        "Starting tmux session manager..."
    )
    
    for msg in "${boot_messages[@]}"; do
        echo -e "${CYAN}[$(date +%H:%M:%S.%N | cut -b1-12)]${NC} ${msg}"
        sleep 0.1
    done
    
    echo -e "\n${GREEN}[SYSTEM READY]${NC}\n"
    sleep 0.5
}

check_dependencies() {
    local missing=()
    
    for cmd in tmux python3 pip3; do
        if ! command -v $cmd &> /dev/null; then
            missing+=($cmd)
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required dependencies:${NC}"
        printf '%s\n' "${missing[@]}"
        echo -e "\nPlease install missing dependencies:"
        echo "  sudo apt update"
        echo "  sudo apt install tmux python3 python3-pip python3-venv"
        exit 1
    fi
}

setup_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${YELLOW}First time setup detected. Creating virtual environment...${NC}"
        python3 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        
        pip install --upgrade pip
        
        # Install from requirements.txt if it exists
        if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
            pip install -r "$PROJECT_ROOT/requirements.txt"
        else
            # Fallback to manual installation
            pip install 'textual>=0.40.0' watchdog pyyaml rich numpy matplotlib libtmux click
        fi
        
        echo -e "${GREEN}Virtual environment setup complete!${NC}"
    else
        source "$VENV_PATH/bin/activate"
    fi
}

# Function to create default config if not exists
create_default_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << 'EOF'
# HexShell Configuration
storage_path: "~/Documents/HexShell"
default_editor: "nano"  # Will use internal editor by default
theme: "cyberpunk_green"
terminal_preference: "gnome-terminal"
boot_sequence: true

profiles:
  gaming:
    name: "Gaming & Simulation"
    path: "gaming"
    icon: "🎮"
    color: "green"
    templates:
      - "ksp_mission"
      - "factorio_production"
      - "game_guide"
    
  cybersec:
    name: "Cybersecurity Research"
    path: "cybersec"
    icon: "🔒"
    color: "red"
    templates:
      - "pentest_report"
      - "network_analysis"
      - "vulnerability_notes"
    
  embedded:
    name: "Embedded Programming"
    path: "embedded"
    icon: "🔧"
    color: "blue"
    templates:
      - "arduino_project"
      - "circuit_design"
      - "device_prototype"

  general:
    name: "General Technical Notes"
    path: "general"
    icon: "📝"
    color: "cyan"
    templates:
      - "technical_note"
      - "project_plan"
      - "research_notes"

ksp:
  bodies:
    - kerbin
    - mun
    - minmus
    - duna
    - eve
    - jool
  
  default_body: "kerbin"
EOF
        echo -e "${GREEN}Created default configuration at: $CONFIG_FILE${NC}"
    fi
}

check_tmux() {
    if [ -n "$TMUX" ]; then
        echo -e "${YELLOW}Warning: Already inside a tmux session.${NC}"
        echo "HexShell needs to create its own tmux session."
        echo -n "Detach from current session and continue? [y/N] "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 0
        fi
        tmux detach-client
        sleep 1
    fi
}

cleanup() {
    if [ -n "$HEXSHELL_SESSION" ]; then
        tmux kill-session -t "$HEXSHELL_SESSION" 2>/dev/null
    fi
}

trap cleanup EXIT

main() {
    case "$1" in
        --no-boot)
            SKIP_BOOT=1
            ;;
        --debug)
            DEBUG_MODE=1
            ;;
        --help|-h)
            echo "HexShell - Cyberpunk Terminal Interface"
            echo "Usage: hexshell [options]"
            echo ""
            echo "Options:"
            echo "  --no-boot    Skip boot sequence"
            echo "  --debug      Run in debug mode"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Configuration file: $CONFIG_FILE"
            exit 0
            ;;
    esac
    
    check_dependencies
    
    if [ -z "$SKIP_BOOT" ]; then
        show_boot_sequence
    fi
    
    create_default_config
    setup_venv
    check_tmux
    
    HEXSHELL_SESSION="hexshell-$$"
    export HEXSHELL_SESSION
    export HEXSHELL_HOME
    export PYTHONPATH="$SRC_PATH:$PYTHONPATH"
    
    echo -e "${CYAN}Launching HexShell interface...${NC}"
    
    # Create tmux session
    tmux new-session -d -s "$HEXSHELL_SESSION" -n "HexShell"
    
    # Set up the environment and run the app
    tmux send-keys -t "$HEXSHELL_SESSION" "cd '$PROJECT_ROOT'" C-m
    tmux send-keys -t "$HEXSHELL_SESSION" "source '$VENV_PATH/bin/activate'" C-m
    tmux send-keys -t "$HEXSHELL_SESSION" "export PYTHONPATH='$SRC_PATH:\$PYTHONPATH'" C-m
    tmux send-keys -t "$HEXSHELL_SESSION" "export HEXSHELL_HOME='$HEXSHELL_HOME'" C-m
    
    if [ -n "$DEBUG_MODE" ]; then
        tmux send-keys -t "$HEXSHELL_SESSION" "python -m hexshell.main --debug" C-m
    else
        tmux send-keys -t "$HEXSHELL_SESSION" "python -m hexshell.main" C-m
    fi
    
    # Give Python time to start
    sleep 0.5
    
    # Attach to the session
    tmux attach-session -t "$HEXSHELL_SESSION"
}

main "$@"