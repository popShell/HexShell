#!/usr/bin/env python3
"""
Custom UI Widgets for HexShell
Provides specialized input and display widgets
"""

from typing import Optional, List, Callable
from textual.widgets import Input, Static, Button
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual import events
from rich.text import Text
from rich.panel import Panel


class CommandInput(Input):    
    class Submitted(Message):
        def __init__(self, value: str):
            self.value = value
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_history: List[str] = []
        self.history_index = -1
        self.max_history = 100
        
        self.commands = {
            ":new": "Create new note",
            ":profile": "Switch profile",
            ":orbit": "Change orbital body",
            ":deltav": "Calculate delta-v",
            ":theme": "Change theme",
            ":save": "Save current file",
            ":quit": "Exit HexShell",
            ":help": "Show help",
            ":template": "Use template",
            ":ascii": "Generate ASCII art",
            ":calc": "Calculator",
            ":stage": "Stage planner",
            ":transfer": "Transfer window"
        }
    
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.value = self.command_history[-(self.history_index + 1)]
                self.cursor_position = len(self.value)
        elif event.key == "down":
            if self.history_index > 0:
                self.history_index -= 1
                self.value = self.command_history[-(self.history_index + 1)]
                self.cursor_position = len(self.value)
            elif self.history_index == 0:
                self.history_index = -1
                self.value = ""
        elif event.key == "tab":
            self._autocomplete()
        else:
            super().on_key(event)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = self.value.strip()
        
        if command:
            if not self.command_history or self.command_history[-1] != command:
                self.command_history.append(command)
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
            
            self.history_index = -1
            
            self.post_message(self.Submitted(command))
    
    def _autocomplete(self):
        current = self.value.strip()
        
        if current.startswith(':'):
            matches = [cmd for cmd in self.commands.keys() if cmd.startswith(current)]
            
            if len(matches) == 1:
                self.value = matches[0] + " "
                self.cursor_position = len(self.value)
            elif len(matches) > 1:
                suggestions = ", ".join(matches)
                self.app.notify(f"Suggestions: {suggestions}", severity="information")


class ProfileSelector(Container):
    
    class ProfileSelected(Message):
        def __init__(self, profile: str):
            self.profile = profile
            super().__init__()
    
    def __init__(self, profiles: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.profiles = profiles
        
    def compose(self):
        with Vertical(id="profile-selector"):
            yield Static("Select Profile", id="profile-title")
            
            for i, profile in enumerate(self.profiles, 1):
                icon = profile.get('icon', '📁')
                name = profile.get('name', profile['id'])
                color = profile.get('color', 'green')
                
                button_text = f"{i}. {icon} {name}"
                yield ProfileButton(
                    button_text,
                    profile['id'],
                    id=f"profile-{profile['id']}",
                    classes=f"profile-button profile-{color}"
                )


class ProfileButton(Button):
   
    def __init__(self, label: str, profile_id: str, **kwargs):
        super().__init__(label, **kwargs)
        self.profile_id = profile_id
        
    def on_button_pressed(self):
        self.parent.post_message(ProfileSelector.ProfileSelected(self.profile_id))


class StatusBar(Static):
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.profile = "general"
        self.file_path = None
        self.modified = False
        self.mode = "INSERT"
        
    def update_status(self, profile: Optional[str] = None, 
                     file_path: Optional[str] = None,
                     modified: Optional[bool] = None,
                     mode: Optional[str] = None):
        if profile is not None:
            self.profile = profile
        if file_path is not None:
            self.file_path = file_path
        if modified is not None:
            self.modified = modified
        if mode is not None:
            self.mode = mode
            
        self._render_status()
    
    def _render_status(self):
        parts = []
        
        if self.mode:
            parts.append(f"[{self.mode}]")
        
        parts.append(f"Profile: {self.profile}")
        
        if self.file_path:
            file_name = self.file_path if isinstance(self.file_path, str) else self.file_path.name
            modified_indicator = " *" if self.modified else ""
            parts.append(f"File: {file_name}{modified_indicator}")
        else:
            parts.append("No file")
        
        status_text = " | ".join(parts)
        self.update(status_text)


class ASCIIArtDisplay(Static):    
    def __init__(self, art: str = "", **kwargs):
        super().__init__(art, **kwargs)
        
    def set_art(self, art: str, title: Optional[str] = None):
        if title:
            content = Panel(art, title=title, border_style="green")
        else:
            content = art
            
        self.update(content)


class CalculatorWidget(Container):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self.result = ""
        
    def compose(self):
        with Vertical():
            yield Static("Calculator", id="calc-title")
            yield Input(placeholder="Enter expression...", id="calc-input")
            yield Static("", id="calc-result")
    
    def on_input_submitted(self, event: Input.Submitted):
        try:
            import ast
            import operator as op
            
            operators = {
                ast.Add: op.add,
                ast.Sub: op.sub,
                ast.Mult: op.mul,
                ast.Div: op.truediv,
                ast.Pow: op.pow,
                ast.USub: op.neg,
            }
            
            def eval_expr(expr):
                def _eval(node):
                    if isinstance(node, ast.Num):
                        return node.n
                    elif isinstance(node, ast.BinOp):
                        return operators[type(node.op)](_eval(node.left), _eval(node.right))
                    elif isinstance(node, ast.UnaryOp):
                        return operators[type(node.op)](_eval(node.operand))
                    else:
                        raise TypeError(node)
                
                return _eval(ast.parse(expr, mode='eval').body)
            
            result = eval_expr(event.value)
            result_widget = self.query_one("#calc-result", Static)
            result_widget.update(f"= {result}")
            
        except Exception as e:
            result_widget = self.query_one("#calc-result", Static)
            result_widget.update(f"Error: {str(e)}")