# HexShell

A cyberpunk terminal interface for technical note-taking across gaming, cybersecurity, and embedded programming domains.

![HexShell](https://img.shields.io/badge/version-1.0.0-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

## Overview

HexShell is a terminal-based note-taking application designed for technical hobbyists who work across multiple domains. It features a three-panel tmux layout with context-aware tools and a cyberpunk aesthetic that makes note-taking engaging rather than perfect.

### Key Features

- **Three-Panel Layout**: File tree, editor, and context-aware tools
- **Multiple Profiles**: Gaming (KSP/Factorio), Cybersecurity, Embedded Programming
- **Context-Aware Tools**: Orbital mechanics calculator, network diagrams, pin layouts
- **Cyberpunk Aesthetic**: Multiple color themes with ASCII art integration
- **Standard Commands**: Uses familiar Linux commands (ls, cd, vim, nano)
- **Auto-Updating**: File tree updates automatically when files change
- **Template System**: Quick-start templates for different project types

## Installation

### Prerequisites

- Linux (Ubuntu/Debian-based preferred)
- Python 3.8+
- tmux
- pip3

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/hexshell.git
cd hexshell

# Install system dependencies
sudo apt update
sudo apt install tmux python3 python3-pip python3-venv

# Make the launcher executable
chmod +x bin/hexshell

# Add to PATH (optional)
echo 'export PATH="$PATH:'$(pwd)'/bin"' >> ~/.bashrc
source ~/.bashrc
```

### First Run

```bash
# Run HexShell
hexshell

# Or if not in PATH
./bin/hexshell
```

On first run, HexShell will:
1. Create a virtual environment
2. Install Python dependencies
3. Create default configuration
4. Show the boot sequence
5. Present profile selection

## Usage

### Profile Selection

On startup, select your working profile:
1. **Gaming** - KSP, Factorio, automation games
2. **CyberSec** - Security research & pentesting
3. **Embedded** - Arduino, IoT, device prototyping
4. **General** - Mixed technical notes

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New note |
| `Ctrl+S` | Save current file |
| `Ctrl+P` | Switch profile |
| `Ctrl+/` | Focus command bar |
| `Ctrl+Q` | Quit |
| `F1` | Show help |
| `F2` | Change theme |
| `Tab` | Switch between panels |

### Commands

All commands start with `:` in the command bar:

```bash
:new [template]         # Create new note
:profile <name>         # Switch profile
:orbit <body>          # Change orbital display (KSP)
:deltav <from> <to>    # Calculate delta-v
:theme <name>          # Change color theme
:template list         # Show available templates
:ascii "text"          # Generate ASCII art
:help                  # Show help
:quit                  # Exit HexShell
```

### KSP Orbital Mechanics

In Gaming profile, the right panel shows:
- Interactive orbital display
- Adjustable orbit parameters (↑↓ keys)
- Delta-v calculations
- Transfer window planning

Available bodies: Kerbin, Mun, Minmus, Duna, Eve, Jool

## Configuration

Configuration file: `~/.config/hexshell/config.yaml`

```yaml
storage_path: "~/Documents/HexShell"
theme: "cyberpunk_green"
boot_sequence: true

profiles:
  gaming:
    name: "Gaming & Simulation"
    templates: ["ksp_mission", "vessel_design", "factorio_blueprint"]
```

### Available Themes (WIP)

- `cyberpunk_green` - Classic green terminal
- `cyberpunk_amber` - Warm amber glow
- `cyberpunk_cyan` - Cool cyan aesthetic
- `cyberpunk_red` - Aggressive red theme
- `matrix` - Pure Matrix style

## File Organization

```
~/Documents/HexShell/
├── gaming/
│   ├── ksp/
│   │   ├── missions/
│   │   ├── designs/
│   │   └── science/
│   └── factorio/
│       ├── blueprints/
│       └── ratios/
├── cybersec/
│   ├── reports/
│   ├── research/
│   └── tools/
├── embedded/
│   ├── arduino/
│   ├── circuits/
│   └── datasheets/
└── general/
    └── notes/
```

## Templates

### Gaming Templates
- **KSP Mission Plan**: Mission objectives, vehicle design, delta-v budget
- **Vessel Design**: Specifications, staging, action groups
- **Factorio Blueprint**: Production rates, requirements, setup

### CyberSec Templates
- **Pentest Report**: Executive summary, findings, methodology
- **Vulnerability Note**: CVE details, PoC, remediation
- **Network Scan**: Topology, discovered services, analysis

### Embedded Templates
- **Arduino Project**: Pin connections, libraries, code structure
- **Circuit Design**: Components, schematics, calculations
- **Sensor Log**: Data format, calibration, analysis

## Development

### Project Structure

```
hexshell/
├── bin/hexshell           # Launcher script
├── src/hexshell/         # Python source
│   ├── core/            # Core functionality
│   ├── panels/          # UI panels
│   ├── contexts/        # Domain-specific tools
│   └── ui/              # Themes and widgets
├── templates/           # Note templates
└── config/             # Default configuration
```

### Adding New Features

1. **New Profile**: Add to `config_manager.py` and create context module
2. **New Theme**: Add to `theme_manager.py` THEMES dictionary
3. **New Template**: Add to templates directory and editor module
4. **New Calculator**: Add to appropriate context module

## Troubleshooting

### Common Issues

**tmux not found**
```bash
sudo apt install tmux
```

**Import errors**
```bash
# Reset virtual environment
rm -rf ~/.hexshell/venv
hexshell  # Will recreate venv
```

**Permission denied**
```bash
chmod +x bin/hexshell
```

### Debug Mode

```bash
hexshell --debug  # Show detailed logs
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file

## Acknowledgments

- ASCII art generation: patorjk.com
- Orbital mechanics: KSP community
- Terminal UI: Textual framework
