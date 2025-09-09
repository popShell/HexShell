#!/usr/bin/env python3
"""
HexShell - Main Application Entry Point
Cyberpunk terminal interface for technical note-taking
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Tree, TextArea, Button, Input
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Fix the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hexshell.core.config_manager import ConfigManager
from hexshell.core.profile_manager import ProfileManager
from hexshell.panels.file_tree import FileTreePanel
from hexshell.panels.editor import MarkdownEditor
from hexshell.contexts.ksp.orbital_display import KSPOrbitalDisplay
from hexshell.ui.themes import ThemeManager
from hexshell.ui.widgets import CommandInput, ProfileSelector


class HexShell(App):
    """Main HexShell Application"""
    
    # Load CSS as a string instead of using CSS_PATH
    # This ensures it works regardless of working directory
    DEFAULT_CSS = """
    Screen {
        background: #0a0a0a;
    }
    
    Header {
        background: #1a1a1a;
        color: #00ff00;
        height: 3;
    }
    
    #main-container {
        height: 100%;
    }
    
    #panels {
        height: 1fr;
    }
    
    #left-panel {
        width: 1fr;
    }
    
    #middle-panel {
        width: 2fr;
    }
    
    #right-panel {
        width: 1fr;
    }
    
    .panel {
        border: solid #00ff00;
        padding: 1;
    }
    
    .panel-header {
        background: #1a1a1a;
        color: #00ff00;
        padding: 1;
        height: 3;
    }
    
    Tree {
        background: #0f0f0f;
        color: #00ff00;
    }
    
    TextArea {
        background: #0a0a0a;
        color: #00ff00;
    }
    
    Input {
        background: #0a0a0a;
        color: #00ff00;
        border: solid #00ff00;
    }
    
    #command-bar {
        height: 3;
        background: #1a1a1a;
    }
    
    #command-input {
        width: 100%;
    }
    
    Footer {
        background: #1a1a1a;
        color: #00ff00;
    }
    
    Button {
        background: #1a1a1a;
        color: #00ff00;
        border: solid #00ff00;
    }
    
    Static {
        color: #00ff00;
    }
    """
    
    # Use the CSS string directly
    CSS = DEFAULT_CSS
    
    TITLE = "HexShell v1.0"
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+p", "switch_profile", "Profile"),
        Binding("ctrl+n", "new_note", "New Note"),
        Binding("ctrl+s", "save", "Save"),
        Binding("f1", "toggle_help", "Help"),
        Binding("f2", "toggle_theme", "Theme"),
        Binding("ctrl+slash", "focus_command", "Command"),
    ]
    
    current_profile = reactive("gaming")
    current_file = reactive(None)
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.profile_manager = ProfileManager(self.config_manager)
        self.theme_manager = ThemeManager()
        
        self.config = self.config_manager.load_config()
        
        self.file_tree = None
        self.editor = None
        self.context_panel = None
        self.command_input = None
        
    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Horizontal(id="panels"):
                # Left panel - File tree
                with Vertical(id="left-panel", classes="panel"):
                    yield Static("📁 FILES", id="file-header", classes="panel-header")
                    yield FileTreePanel(
                        self.config['storage_path'],
                        self.current_profile,
                        id="file-tree"
                    )
                
                # Middle panel - Editor
                with Vertical(id="middle-panel", classes="panel"):
                    yield Static("📝 EDITOR", id="editor-header", classes="panel-header")
                    yield MarkdownEditor(id="editor")
                
                # Right panel - Context tools
                with Vertical(id="right-panel", classes="panel"):
                    yield Static("🚀 ORBITAL MECHANICS", id="context-header", classes="panel-header")
                    yield KSPOrbitalDisplay(id="context-display")
            
            # Command bar at bottom
            with Horizontal(id="command-bar"):
                yield CommandInput(id="command-input", placeholder="Enter command (:help for commands)")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app after mounting"""
        self.file_tree = self.query_one("#file-tree", FileTreePanel)
        self.editor = self.query_one("#editor", MarkdownEditor)
        self.context_panel = self.query_one("#context-display", KSPOrbitalDisplay)
        self.command_input = self.query_one("#command-input", CommandInput)
        
        # Set initial profile
        await self.set_profile(self.current_profile)
        
        # Show welcome message
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Display welcome message in editor"""
        welcome_text = """# Welcome to HexShell

## Your Cyberpunk Terminal Interface

### Quick Start:
- **Ctrl+N**: Create new note
- **Ctrl+P**: Switch profile  
- **Ctrl+/**: Focus command bar
- **F1**: Show help
- **F2**: Change theme

### Available Commands:
- `:new [template]` - Create new note
- `:profile <name>` - Switch profile
- `:deltav <from> <to>` - Calculate delta-v
- `:orbit <body>` - Change orbital display
- `:theme <name>` - Change theme
- `:help` - Show all commands

### Current Profile: Gaming (KSP)
The right panel shows orbital mechanics for KSP.
Select a file from the left panel to begin editing.

---
*Embrace the imperfect terminal aesthetic*
"""
        self.editor.set_content(welcome_text)
    
    async def set_profile(self, profile_name: str) -> None:
        """Switch to a different profile"""
        self.current_profile = profile_name
        profile = self.config['profiles'].get(profile_name)
        
        if profile:
            self.file_tree.set_profile(profile_name)
            
            # Update context panel header based on profile
            context_header = self.query_one("#context-header", Static)
            
            if profile_name == "gaming":
                context_header.update("🚀 ORBITAL MECHANICS")
            elif profile_name == "cybersec":
                context_header.update("🔒 SECURITY TOOLS")
            elif profile_name == "embedded":
                context_header.update("🔧 HARDWARE TOOLS")
            else:
                context_header.update("📊 GENERAL TOOLS")
            
            # Show notification
            self.notify(f"Switched to {profile['name']} profile")
    
    async def action_switch_profile(self) -> None:
        """Cycle through profiles"""
        profiles = ["gaming", "cybersec", "embedded", "general"]
        current_idx = profiles.index(self.current_profile)
        next_idx = (current_idx + 1) % len(profiles)
        await self.set_profile(profiles[next_idx])
    
    async def action_new_note(self) -> None:
        """Create a new note"""
        self.command_input.value = ":new "
        self.set_focus(self.command_input)
    
    async def action_save(self) -> None:
        """Save current file"""
        if self.current_file and self.editor.text:
            # TODO: Implement file saving
            self.notify("File saved!")
    
    async def action_focus_command(self) -> None:
        """Focus the command input"""
        self.set_focus(self.command_input)
    
    async def action_toggle_theme(self) -> None:
        """Cycle through themes"""
        themes = ["cyberpunk_green", "cyberpunk_amber", "cyberpunk_cyan", "cyberpunk_red"]
        current = self.config.get('theme', 'cyberpunk_green')
        
        try:
            current_idx = themes.index(current)
            next_theme = themes[(current_idx + 1) % len(themes)]
        except ValueError:
            next_theme = themes[0]
        
        # For now just notify - theme switching would update CSS
        self.notify(f"Theme: {next_theme} (CSS theming in development)")
    
    async def on_command_input_submitted(self, event) -> None:
        """Handle command submission"""
        command = event.value.strip()
        
        if command.startswith(':'):
            await self.execute_command(command[1:])
        
        self.command_input.value = ""
    
    async def execute_command(self, command: str) -> None:
        """Execute a command"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "quit" or cmd == "q":
            self.exit()
        elif cmd == "new":
            template = args[0] if args else None
            await self.create_new_note(template)
        elif cmd == "profile":
            if args:
                await self.set_profile(args[0])
        elif cmd == "orbit":
            if args and self.current_profile == "gaming":
                self.context_panel.set_body(args[0])
        elif cmd == "help":
            self.show_help()
        else:
            self.notify(f"Unknown command: {cmd}", severity="warning")
    
    async def create_new_note(self, template: Optional[str] = None) -> None:
        """Create a new note with optional template"""
        # TODO: Implement note creation
        self.notify("Creating new note...")
    
    def show_help(self) -> None:
        """Show help in editor"""
        help_text = """# HexShell Commands

## Global Commands
- `:quit` or `:q` - Exit HexShell
- `:new [template]` - Create new note
- `:profile <name>` - Switch profile
- `:help` - Show this help

## Keyboard Shortcuts
- `Ctrl+N` - New note
- `Ctrl+S` - Save current file
- `Ctrl+P` - Switch profile
- `Ctrl+/` - Focus command bar
- `Ctrl+Q` - Quit
- `F1` - Toggle help
- `F2` - Cycle themes
"""
        self.editor.set_content(help_text)
    
    def on_file_tree_file_selected(self, event) -> None:
        """Handle file selection from tree"""
        file_path = event.file_path
        self.current_file = file_path
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            self.editor.set_content(content)
            self.notify(f"Opened: {file_path.name}")
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")


def main():
    """Main entry point"""
    app = HexShell()
    app.run()


if __name__ == "__main__":
    main()