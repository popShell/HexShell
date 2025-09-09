#!/usr/bin/env python3
"""
Theme Manager for HexShell
Handles color schemes and visual theming
"""

from typing import Dict, Any
from textual.app import App
from textual.css.query import NoMatches


class ThemeManager:
    
    THEMES = {
        "cyberpunk_green": {
            "name": "Cyberpunk Green",
            "primary": "#00ff00",
            "primary_dark": "#00aa00",
            "secondary": "#00ffff",
            "background": "#0a0a0a",
            "background_light": "#1a1a1a",
            "text": "#00ff00",
            "text_dim": "#006600",
            "border": "#00ff00",
            "error": "#ff0066",
            "warning": "#ffaa00",
            "info": "#00ffff",
            "success": "#00ff00"
        },
        "cyberpunk_amber": {
            "name": "Cyberpunk Amber",
            "primary": "#ffaa00",
            "primary_dark": "#aa6600",
            "secondary": "#ff6600",
            "background": "#0a0a0a",
            "background_light": "#1a1a1a",
            "text": "#ffaa00",
            "text_dim": "#aa6600",
            "border": "#ffaa00",
            "error": "#ff0066",
            "warning": "#ffff00",
            "info": "#00ffff",
            "success": "#00ff00"
        },
        "cyberpunk_cyan": {
            "name": "Cyberpunk Cyan",
            "primary": "#00ffff",
            "primary_dark": "#006666",
            "secondary": "#0099ff",
            "background": "#0a0a0a",
            "background_light": "#1a1a1a",
            "text": "#00ffff",
            "text_dim": "#006666",
            "border": "#00ffff",
            "error": "#ff0066",
            "warning": "#ffaa00",
            "info": "#0099ff",
            "success": "#00ff99"
        },
        "cyberpunk_red": {
            "name": "Cyberpunk Red",
            "primary": "#ff0066",
            "primary_dark": "#990033",
            "secondary": "#ff3366",
            "background": "#0a0a0a",
            "background_light": "#1a1a1a",
            "text": "#ff0066",
            "text_dim": "#990033",
            "border": "#ff0066",
            "error": "#ff0000",
            "warning": "#ffaa00",
            "info": "#ff99cc",
            "success": "#00ff00"
        },
        "matrix": {
            "name": "Matrix",
            "primary": "#00ff00",
            "primary_dark": "#008800",
            "secondary": "#00ff00",
            "background": "#000000",
            "background_light": "#001100",
            "text": "#00ff00",
            "text_dim": "#008800",
            "border": "#00ff00",
            "error": "#ff0000",
            "warning": "#ffff00",
            "info": "#00ff00",
            "success": "#00ff00"
        }
    }
    
    def __init__(self):
        self.current_theme = "cyberpunk_green"
        
    def get_available_themes(self) -> list:
        return list(self.THEMES.keys())
    
    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        return self.THEMES.get(theme_name, self.THEMES["cyberpunk_green"])
    
    def apply_theme(self, app: App, theme_name: str) -> bool:
        if theme_name not in self.THEMES:
            return False
        
        theme = self.THEMES[theme_name]
        self.current_theme = theme_name
        
        css_vars = f"""
        :root {{
            --primary: {theme['primary']};
            --primary-dark: {theme['primary_dark']};
            --secondary: {theme['secondary']};
            --background: {theme['background']};
            --background-light: {theme['background_light']};
            --text: {theme['text']};
            --text-dim: {theme['text_dim']};
            --border: {theme['border']};
            --error: {theme['error']};
            --warning: {theme['warning']};
            --info: {theme['info']};
            --success: {theme['success']};
        }}
        """
        
        self._apply_dynamic_styles(app, theme)
        
        return True
    
    def _apply_dynamic_styles(self, app: App, theme: Dict[str, str]):
        style_updates = {
            "Header": {
                "background": theme['background_light'],
                "color": theme['primary']
            },
            "Footer": {
                "background": theme['background_light'],
                "color": theme['primary']
            },
            ".panel": {
                "border": f"heavy {theme['border']}",
                "background": theme['background']
            },
            ".panel-header": {
                "background": theme['background_light'],
                "color": theme['primary'],
                "border-bottom": f"heavy {theme['border']}"
            },
            "Tree": {
                "background": theme['background'],
                "color": theme['text']
            },
            "TextArea": {
                "background": theme['background'],
                "color": theme['text']
            },
            "Input": {
                "background": theme['background'],
                "color": theme['text'],
                "border": f"solid {theme['border']}"
            },
            "#command-bar": {
                "background": theme['background_light'],
                "border-top": f"heavy {theme['border']}"
            }
        }
        
        for selector, styles in style_updates.items():
            try:
                widgets = app.query(selector)
                for widget in widgets:
                    for style_name, style_value in styles.items():
                        if style_name == "background":
                            widget.styles.background = style_value
                        elif style_name == "color":
                            widget.styles.color = style_value
                        elif style_name == "border":
                            widget.styles.border = style_value
                        elif style_name == "border-bottom":
                            widget.styles.border_bottom = style_value
                        elif style_name == "border-top":
                            widget.styles.border_top = style_value
            except NoMatches:
                pass
    
    def get_ascii_art_for_theme(self, theme_name: str) -> str:
        ascii_arts = {
            "cyberpunk_green": """
    ░█▀▀░█░█░█▀▄░█▀▀░█▀▄░█▀█░█░█░█▀█░█░█
    ░█░░░░█░░█▀▄░█▀▀░█▀▄░█▀▀░█░█░█░█░█▀▄
    ░▀▀▀░░▀░░▀▀░░▀▀▀░▀░▀░▀░░░▀▀▀░▀░▀░▀░▀
    """,
            "cyberpunk_amber": """
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    ██░▄▄▄░█░▄▀▄░██░▄▄▀██░▄▄▄██░▄▄▀████
    ██░▄▄▄░█░█▄█░██░▄▄▀██░▄▄▄██░▀▀▄████
    ██░▀▀▀░█▄███▄██░▀▀░██░▀▀▀██░██░████
    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
    """,
            "cyberpunk_cyan": """
    ╔═╗╦ ╦╔╗ ╔═╗╦═╗  ╔═╗╦ ╦╔═╗╔╗╔
    ║  ╚╦╝╠╩╗║╣ ╠╦╝  ║  ╚╦╝╠═╣║║║
    ╚═╝ ╩ ╚═╝╚═╝╩╚═  ╚═╝ ╩ ╩ ╩╝╚╝
    """,
            "cyberpunk_red": """
    ██████╗ ███████╗██████╗ 
    ██╔══██╗██╔════╝██╔══██╗
    ██████╔╝█████╗  ██║  ██║
    ██╔══██╗██╔══╝  ██║  ██║
    ██║  ██║███████╗██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═════╝ 
    """,
            "matrix": """
    01001000 01000101 01011000
    ░░░▒▒▒▓▓▓███▓▓▓▒▒▒░░░
    ▓▓▓▒▒▒░░░███░░░▒▒▒▓▓▓
    ░░░▒▒▒▓▓▓███▓▓▓▒▒▒░░░
    01010011 01001000 01001100
    """
        }
        
        return ascii_arts.get(theme_name, ascii_arts["cyberpunk_green"])