#!/usr/bin/env python3
"""
Configuration Manager for HexShell
Handles loading and saving configuration files
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    
    DEFAULT_CONFIG = {
        "storage_path": "~/Documents/HexShell",
        "default_editor": "internal",  # Use internal editor
        "theme": "cyberpunk_green",
        "terminal_preference": "gnome-terminal",
        "boot_sequence": True,
        "autosave_interval": 30,  # seconds
        
        "profiles": {
            "gaming": {
                "name": "Gaming & Simulation",
                "path": "gaming",
                "icon": "🎮",
                "color": "green",
                "templates": ["ksp_mission", "vessel_design", "factorio_blueprint", "game_guide"]
            },
            "cybersec": {
                "name": "Cybersecurity Research",
                "path": "cybersec",
                "icon": "🔒",
                "color": "red",
                "templates": ["pentest_report", "network_analysis", "vulnerability_notes", "exploit_poc"]
            },
            "embedded": {
                "name": "Embedded Programming",
                "path": "embedded",
                "icon": "🔧",
                "color": "blue",
                "templates": ["arduino_project", "circuit_design", "device_prototype", "sensor_log"]
            },
            "general": {
                "name": "General Technical Notes",
                "path": "general",
                "icon": "📝",
                "color": "cyan",
                "templates": ["technical_note", "project_plan", "research_notes"]
            }
        },
        
        "ksp": {
            "bodies": ["kerbin", "mun", "minmus", "duna", "eve", "jool", "laythe", "tylo", "vall"],
            "default_body": "kerbin",
            "default_orbit": {
                "apoapsis": 100000,  # 100km
                "periapsis": 80000   # 80km
            }
        },
        
        "keybindings": {
            "save": "ctrl+s",
            "new": "ctrl+n",
            "quit": "ctrl+q",
            "profile": "ctrl+p",
            "command": "ctrl+/",
            "theme": "f2"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            self.config_dir = Path(xdg_config) / 'hexshell'
            self.config_path = self.config_dir / 'config.yaml'
        
        self.config_dir = self.config_path.parent
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                
                self.config = self._merge_with_defaults(self.config)
                
            except Exception as e:
                print(f"Error loading config: {e}")
                print("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        
        self.config['storage_path'] = os.path.expanduser(self.config['storage_path'])
        
        return self.config
    
    def save_config(self) -> bool:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        def merge_dicts(default: Dict, override: Dict) -> Dict:
            result = default.copy()
            
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            
            return result
        
        return merge_dicts(self.DEFAULT_CONFIG, config)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        return self.config.get('profiles', {}).get(profile_name)
    
    def get_storage_path(self, profile: Optional[str] = None) -> Path:
        base_path = Path(self.config['storage_path'])
        
        if profile:
            profile_config = self.get_profile(profile)
            if profile_config:
                return base_path / profile_config['path']
        
        return base_path