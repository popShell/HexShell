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
from textual.widgets import Header, Footer, Static, Tree, TextArea, Button
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hexshell.core.config_manager import ConfigManager
from hexshell.core.profile_manager import ProfileManager
from hexshell.panels.file_tree import FileTreePanel
from hexshell.panels.editor import MarkdownEditor
from hexshell.contexts.ksp.orbital_display import KSPOrbitalDisplay
from hexshell.ui.themes import ThemeManager
from hexshell.ui.widgets import CommandInput, ProfileSelector


class HexShell(App):
    
    CSS_PATH = "hexshell.css"
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
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Horizontal(id="panels"):
                with Vertical(id="left-panel", classes="panel"):
                    yield Static("📁 FILES", id="file-header", classes="panel-header")
                    yield FileTreePanel(
                        self.config['storage_path'],
                        self.current_profile,
                        id="file-tree"
                    )
                
                with Vertical(id="middle-panel", classes="panel"):
                    yield Static("📝 EDITOR", id="editor-header", classes="panel-header")
                    yield MarkdownEditor(id="editor")
                
                with Vertical(id="right-panel", classes="panel"):
                    yield Static("🚀 ORBITAL MECHANICS", id="context-header", classes="panel-header")
                    yield KSPOrbitalDisplay(id="context-display")
            
            with Horizontal(id="command-bar"):
                yield CommandInput(id="command-input", placeholder="Enter command (:help for commands)")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        self.file_tree = self.query_one("#file-tree", FileTreePanel)
        self.editor = self.query_one("#editor", MarkdownEditor)
        self.context_panel = self.query_one("#context-display", KSPOrbitalDisplay)
        self.command_input = self.query_one("#command-input", CommandInput)
        
        self.theme_manager.apply_theme(self, self.config.get('theme', 'cyberpunk_green'))
        
        await self.set_profile(self.current_profile)
        
        self.show_welcome_message()
    
    def show_welcome_message(self):
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
        self.current_profile = profile_name
        profile = self.config['profiles'].get(profile_name)
        
        if profile:
            self.file_tree.set_profile(profile_name)
            
            context_header = self.query_one("#context-header", Static)
            
            if profile_name == "gaming":
                context_header.update("🚀 ORBITAL MECHANICS")
                # Context panel is already KSP
            elif profile_name == "cybersec":
                context_header.update("🔒 SECURITY TOOLS")
                # TODO: Switch to security context panel
            elif profile_name == "embedded":
                context_header.update("🔧 HARDWARE TOOLS")
                # TODO: Switch to hardware context panel
            else:
                context_header.update("📊 GENERAL TOOLS")
                # TODO: Switch to general context panel
            
            # Update status
            self.notify(f"Switched to {profile['name']} profile")
    
    async def action_switch_profile(self) -> None:
        # TODO: Implement profile selection dialog
        profiles = ["gaming", "cybersec", "embedded", "general"]
        current_idx = profiles.index(self.current_profile)
        next_idx = (current_idx + 1) % len(profiles)
        await self.set_profile(profiles[next_idx])
    
    async def action_new_note(self) -> None:
        self.command_input.value = ":new "
        self.set_focus(self.command_input)
    
    async def action_save(self) -> None:
        if self.current_file and self.editor.content:
            # TODO: Implement file saving
            self.notify("File saved!")
    
    async def action_focus_command(self) -> None:
        self.set_focus(self.command_input)
    
    async def action_toggle_theme(self) -> None:
        themes = ["cyberpunk_green", "cyberpunk_amber", "cyberpunk_cyan", "cyberpunk_red"]
        current = self.config.get('theme', 'cyberpunk_green')
        
        try:
            current_idx = themes.index(current)
            next_theme = themes[(current_idx + 1) % len(themes)]
        except ValueError:
            next_theme = themes[0]
        
        self.theme_manager.apply_theme(self, next_theme)
        self.config['theme'] = next_theme
        self.notify(f"Theme changed to {next_theme}")
    
    async def on_command_input_submitted(self, event) -> None:
        command = event.value.strip()
        
        if command.startswith(':'):
            await self.execute_command(command[1:])
        
        self.command_input.value = ""
    
    async def execute_command(self, command: str) -> None:
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
        elif cmd == "deltav":
            if len(args) >= 2 and self.current_profile == "gaming":
                # TODO: Calculate and display delta-v
                self.notify(f"Delta-v from {args[0]} to {args[1]}: Calculating...")
        elif cmd == "theme":
            if args:
                self.theme_manager.apply_theme(self, args[0])
                self.config['theme'] = args[0]
        elif cmd == "help":
            self.show_help()
        else:
            self.notify(f"Unknown command: {cmd}", severity="warning")
    
    async def create_new_note(self, template: Optional[str] = None) -> None:
        # TODO: Implement note creation with templates
        self.notify("Creating new note...")
    
    def show_help(self) -> None:
        help_text = """# HexShell Commands

## Global Commands
- `:quit` or `:q` - Exit HexShell
- `:new [template]` - Create new note with optional template
- `:profile <name>` - Switch to different profile (gaming, cybersec, embedded, general)
- `:theme <name>` - Change color theme
- `:help` - Show this help

## Gaming Profile Commands
- `:orbit <body>` - Change orbital display (kerbin, mun, minmus, etc.)
- `:deltav <from> <to>` - Calculate delta-v requirements
- `:stage` - Open stage planner
- `:transfer` - Calculate transfer windows

## Keyboard Shortcuts
- `Ctrl+N` - New note
- `Ctrl+S` - Save current file
- `Ctrl+P` - Switch profile
- `Ctrl+/` - Focus command bar
- `Ctrl+Q` - Quit
- `F1` - Toggle help
- `F2` - Cycle themes

## Navigation
- Use arrow keys or vim keys (hjkl) in file tree
- Tab to switch between panels
- Enter to open files
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
    app = HexShell()
    app.run()


if __name__ == "__main__":
    main()