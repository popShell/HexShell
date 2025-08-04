#!/usr/bin/env python3
"""
File Tree Panel for HexShell
Displays project files with auto-updating capability
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from textual.widget import Widget
from textual.widgets import Tree
from textual.widgets._tree import TreeNode
from textual.reactive import reactive
from textual.message import Message
from textual import events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileTreeHandler(FileSystemEventHandler):    
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget
        
    def on_any_event(self, event: FileSystemEvent):
        if not event.is_directory or event.event_type in ['created', 'deleted', 'moved']:
            # Schedule a refresh of the tree
            # Note: In production, this should be debounced and run in the main thread
            pass


class FileTreePanel(Tree):    
    class FileSelected(Message):
        def __init__(self, file_path: Path):
            self.file_path = file_path
            super().__init__()
    
    def __init__(self, base_path: str, profile: str, **kwargs):
        super().__init__("📁 Files", **kwargs)
        self.base_path = Path(base_path).expanduser()
        self.current_profile = profile
        self.profile_path = self.base_path / profile
        
        self.observer = Observer()
        self.file_handler = FileTreeHandler(self)
        
        # Icon mappings
        self.file_icons = {
            '.md': '📝',
            '.txt': '📄',
            '.ksp': '🚀',
            '.py': '🐍',
            '.sh': '📜',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.json': '📊',
            '.ino': '🔧',
            '.c': '💾',
            '.cpp': '💾',
            '.h': '📋',
        }
        
        self.folder_icons = {
            'gaming': '🎮',
            'cybersec': '🔒',
            'embedded': '🔧',
            'general': '📁',
            'ksp': '🚀',
            'factorio': '⚙️',
            'missions': '🎯',
            'designs': '📐',
            'research': '🔬',
            'exploits': '💀',
            'reports': '📊',
            'arduino': '🔌',
            'circuits': '⚡',
        }
        
        self.recent_files: List[Path] = []
        self.max_recent = 5
        
    def on_mount(self):
        self.profile_path.mkdir(parents=True, exist_ok=True)
        self.build_tree()
        self.start_watching()
        self.root.expand()
        
    def build_tree(self):
        self.clear()
        
        if self.recent_files:
            recent_node = self.root.add("⏰ Recent Files", expand=False)
            for file_path in self.recent_files[:self.max_recent]:
                icon = self.get_file_icon(file_path)
                recent_node.add_leaf(f"{icon} {file_path.name}").data = file_path
        
        profile_icon = self.folder_icons.get(self.current_profile, '📁')
        profile_node = self.root.add(f"{profile_icon} {self.current_profile}", expand=True)
        
        self._add_directory_contents(profile_node, self.profile_path)
        
        templates_node = self.root.add("📋 Templates", expand=False)
        self._add_templates(templates_node)
        
    def _add_directory_contents(self, node, path: Path):
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.'):  # Skip hidden files
                    continue
                    
                if item.is_dir():
                    icon = self.folder_icons.get(item.name.lower(), '📁')
                    dir_node = node.add(f"{icon} {item.name}", expand=False)
                    self._add_directory_contents(dir_node, item)
                else:
                    icon = self.get_file_icon(item)
                    leaf = node.add_leaf(f"{icon} {item.name}")
                    leaf.data = item
                    
        except PermissionError:
            node.add_leaf("⚠️ Permission Denied")
            
    def _add_templates(self, templates_node):
        templates = {
            "gaming": [
                ("ksp_mission", "🚀 KSP Mission Plan"),
                ("vessel_design", "🛸 Vessel Design"),
                ("orbital_transfer", "🌍 Orbital Transfer"),
                ("factorio_blueprint", "⚙️ Factorio Blueprint"),
            ],
            "cybersec": [
                ("pentest_report", "📊 Pentest Report"),
                ("vulnerability", "🐛 Vulnerability Note"),
                ("network_scan", "🌐 Network Scan"),
                ("exploit_poc", "💀 Exploit PoC"),
            ],
            "embedded": [
                ("arduino_project", "🔌 Arduino Project"),
                ("circuit_design", "⚡ Circuit Design"),
                ("sensor_log", "📊 Sensor Data Log"),
                ("device_spec", "📋 Device Spec"),
            ],
        }
        
        profile_templates = templates.get(self.current_profile, [])
        for template_id, template_name in profile_templates:
            leaf = templates_node.add_leaf(template_name)
            leaf.data = f"template:{template_id}"
    
    def get_file_icon(self, file_path: Path) -> str:
        return self.file_icons.get(file_path.suffix.lower(), '📄')
    
    def set_profile(self, profile: str):
        self.current_profile = profile
        self.profile_path = self.base_path / profile
        self.profile_path.mkdir(parents=True, exist_ok=True)
        
        self.stop_watching()
        self.build_tree()
        self.start_watching()
    
    def start_watching(self):
        try:
            self.observer.schedule(
                self.file_handler,
                str(self.profile_path),
                recursive=True
            )
            if not self.observer.is_alive():
                self.observer.start()
        except Exception as e:
            # Log error but don't crash
            pass
    
    def stop_watching(self):
        if self.observer.is_alive():
            self.observer.stop()
            # Don't wait too long for observer to stop
            self.observer.join(timeout=0.5)
    
    def refresh_tree(self):
        """Refresh the file tree"""
        self.build_tree()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        node_data = getattr(node, 'data', None)
        
        if node_data and isinstance(node_data, Path):
            if node_data.is_file():
                if node_data in self.recent_files:
                    self.recent_files.remove(node_data)
                self.recent_files.insert(0, node_data)
                self.recent_files = self.recent_files[:self.max_recent]
                
                self.post_message(self.FileSelected(node_data))
        elif node_data and isinstance(node_data, str) and node_data.startswith("template:"):
            template_id = node_data.split(":", 1)[1]
            # For now, just notify - template handling will be implemented later
            from textual.app import App
            app = App.get_running_app()
            if app:
                app.notify(f"Template selected: {template_id}")
    
    def on_unmount(self):
        self.stop_watching()
    
    def action_create_file(self):
        # TODO: Implement file creation dialog
        pass
    
    def action_create_folder(self):
        # TODO: Implement folder creation dialog
        pass
    
    def action_delete(self):
        # TODO: Implement deletion with confirmation
        pass
    
    def action_rename(self):
        # TODO: Implement rename dialog
        pass