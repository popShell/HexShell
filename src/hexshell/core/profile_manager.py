#!/usr/bin/env python3
"""
Profile Manager for HexShell
Handles profile switching and profile-specific configurations
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class ProfileManager:    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_profile = None
        self.profile_history = []
        
    def get_available_profiles(self) -> List[str]:
        profiles = self.config_manager.get('profiles', {})
        return list(profiles.keys())
    
    def get_profile_info(self, profile_name: str) -> Optional[Dict[str, Any]]:
        return self.config_manager.get_profile(profile_name)
    
    def set_current_profile(self, profile_name: str) -> bool:
        if profile_name in self.get_available_profiles():
            self.current_profile = profile_name
            self.profile_history.append({
                'profile': profile_name,
                'timestamp': datetime.now()
            })
            
            storage_path = self.config_manager.get_storage_path(profile_name)
            storage_path.mkdir(parents=True, exist_ok=True)
            
            self._create_profile_structure(profile_name, storage_path)
            
            return True
        return False
    
    def _create_profile_structure(self, profile_name: str, base_path: Path):
        structures = {
            'gaming': ['ksp/missions', 'ksp/designs', 'ksp/science', 
                      'factorio/blueprints', 'factorio/ratios', 
                      'general/guides', 'general/notes'],
            'cybersec': ['reports', 'research/exploits', 'research/vulnerabilities',
                        'tools/scripts', 'tools/configs', 'networks/scans',
                        'networks/diagrams'],
            'embedded': ['arduino/projects', 'arduino/libraries', 
                        'circuits/schematics', 'circuits/pcb',
                        'datasheets', 'sensors/logs'],
            'general': ['projects', 'notes', 'research', 'archives']
        }
        
        subdirs = structures.get(profile_name, ['notes'])
        
        for subdir in subdirs:
            dir_path = base_path / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_profile_templates(self, profile_name: str) -> List[str]:
        profile_info = self.get_profile_info(profile_name)
        if profile_info:
            return profile_info.get('templates', [])
        return []
    
    def get_profile_color(self, profile_name: str) -> str:
        profile_info = self.get_profile_info(profile_name)
        if profile_info:
            return profile_info.get('color', 'green')
        return 'green'
    
    def get_profile_icon(self, profile_name: str) -> str:
        profile_info = self.get_profile_info(profile_name)
        if profile_info:
            return profile_info.get('icon', '📁')
        return '📁'
    
    def create_custom_profile(self, name: str, config: Dict[str, Any]) -> bool:
        profiles = self.config_manager.get('profiles', {})
        
        if name not in profiles:
            default_config = {
                'name': config.get('name', name.title()),
                'path': config.get('path', name.lower()),
                'icon': config.get('icon', '📂'),
                'color': config.get('color', 'cyan'),
                'templates': config.get('templates', [])
            }
            
            profiles[name] = default_config
            self.config_manager.set('profiles', profiles)
            self.config_manager.save_config()
            
            return True
        return False
    
    def get_recent_files(self, profile_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        # This would be implemented with a proper file history tracking system
        # For now, return empty list
        return []
    
    def get_profile_statistics(self, profile_name: str) -> Dict[str, Any]:
        storage_path = self.config_manager.get_storage_path(profile_name)
        
        total_files = 0
        total_size = 0
        file_types = {}
        
        if storage_path.exists():
            for file_path in storage_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
                    
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'file_types': file_types,
            'last_accessed': datetime.now()  # Would track this properly
        }