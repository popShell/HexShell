#!/usr/bin/env python3
"""
Markdown Editor Panel for HexShell
Provides syntax highlighting and vim-like keybindings
"""

from typing import Optional
from pathlib import Path

from textual.widgets import TextArea
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from rich.syntax import Syntax
from rich.console import Console


class MarkdownEditor(TextArea):
    """Enhanced markdown editor with syntax highlighting"""
    
    BINDINGS = [
        Binding("ctrl+s", "save", "Save", show=False),
        Binding("escape", "normal_mode", "Normal Mode", show=False),
        Binding("i", "insert_mode", "Insert Mode", show=False),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+y", "redo", "Redo", show=False),
    ]
    
    # Markdown syntax patterns for basic highlighting
    MARKDOWN_PATTERNS = {
        'heading': r'^#{1,6}\s.*$',
        'bold': r'\*\*[^*]+\*\*|__[^_]+__',
        'italic': r'\*[^*]+\*|_[^_]+_',
        'code': r'`[^`]+`',
        'code_block': r'^```[\s\S]*?^```',
        'link': r'\[([^\]]+)\]\(([^)]+)\)',
        'list': r'^[\s]*[-*+]\s',
        'numbered_list': r'^[\s]*\d+\.\s',
        'blockquote': r'^>\s.*$',
        'horizontal_rule': r'^---+$|^\*\*\*+$',
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path: Optional[Path] = None
        self.modified = False
        self.vim_mode = "insert"  # Start in insert mode for ease of use
        
        self.show_line_numbers = True
        self.language = "markdown"
        self.theme = "monokai"
        
    def set_content(self, content: str, file_path: Optional[Path] = None):
        self.clear()
        self.insert(content)
        self.file_path = file_path
        self.modified = False
        
        self.cursor_location = (0, 0)
        
    def get_content(self) -> str:
        return self.text
    
    def on_text_changed(self, event):
        self.modified = True
        
        if self.file_path:
            header = self.parent.query_one("#editor-header")
            if header:
                file_name = self.file_path.name
                header.update(f"📝 EDITOR - {file_name} {'*' if self.modified else ''}")
    
    def action_save(self):
        if self.file_path and self.modified:
            try:
                self.file_path.write_text(self.text)
                self.modified = False
                self.notify("File saved!", severity="information")
                
                header = self.parent.query_one("#editor-header")
                if header:
                    header.update(f"📝 EDITOR - {self.file_path.name}")
                    
            except Exception as e:
                self.notify(f"Error saving file: {e}", severity="error")
        elif not self.file_path:
            self.notify("No file open to save", severity="warning")
    
    def action_normal_mode(self):
        self.vim_mode = "normal"
        self.read_only = True
        self.notify("-- NORMAL --", severity="information")
    
    def action_insert_mode(self):
        self.vim_mode = "insert"
        self.read_only = False
        self.notify("-- INSERT --", severity="information")
    
    def insert_template(self, template_name: str):
        templates = {
            "ksp_mission": """# KSP Mission: [Mission Name]

## Mission Objectives
- Primary: 
- Secondary: 
- Optional: 

## Vehicle Design
- Launch Vehicle: 
- Payload: 
- Total Delta-V: 
- Total Mass: 

## Mission Profile
1. Launch Window: 
2. Ascent Profile: 
3. Orbital Insertion: 
4. Transfer Burn: 
5. Arrival: 
6. Landing/Docking: 
7. Return: 

## Delta-V Budget
| Maneuver | Delta-V (m/s) | Notes |
|----------|---------------|-------|
| Launch   |               |       |
| Transfer |               |       |
| Capture  |               |       |
| Landing  |               |       |
| Return   |               |       |
| **Total**|               |       |

## Notes
""",
            "vessel_design": """# Vessel Design: [Vessel Name]

## Purpose
[Mission type and requirements]

## Specifications
- Total Mass: [X] tons
- Crew Capacity: [X]
- Delta-V (vacuum): [X] m/s
- TWR (launch): [X]

## Stage Breakdown
### Stage 1 (Booster)
- Engines: 
- Fuel: 
- Delta-V: 
- TWR: 

### Stage 2 (Core)
- Engines: 
- Fuel: 
- Delta-V: 
- TWR: 

### Stage 3 (Payload)
- Components: 
- Science Equipment: 
- Special Features: 

## Action Groups
1. [Action Group 1]
2. [Action Group 2]
3. [Action Group 3]

## Design Notes
""",
            "factorio_blueprint": """# Factorio Blueprint: [Name]

## Purpose
[What this blueprint accomplishes]

## Requirements
- Space: [X]x[Y] tiles
- Power: [X] MW
- Resources:
  - Iron Plates: [X]/min
  - Copper Plates: [X]/min
  - Other: 

## Production Rates
| Item | Rate/min | Machines |
|------|----------|----------|
|      |          |          |

## Blueprint String
```
[Paste blueprint string here]
```

## Setup Instructions
1. 
2. 
3. 

## Notes
""",
            "pentest_report": """# Penetration Test Report: [Target]

## Executive Summary
Date: [Date]
Tester: [Name]
Scope: [IP ranges/domains]

## Findings Summary
| Severity | Count |
|----------|-------|
| Critical | 0     |
| High     | 0     |
| Medium   | 0     |
| Low      | 0     |
| Info     | 0     |

## Detailed Findings

### Finding 1: [Title]
**Severity**: [Critical/High/Medium/Low]
**CVSS**: [Score]

**Description**:
[Detailed description]

**Impact**:
[Business impact]

**Proof of Concept**:
```bash
[Commands or code]
```

**Remediation**:
[Steps to fix]

## Methodology
- [ ] Reconnaissance
- [ ] Scanning
- [ ] Enumeration
- [ ] Exploitation
- [ ] Post-Exploitation
- [ ] Reporting

## Tools Used
- 
- 
- 

## Appendix
""",
        }
        
        template_content = templates.get(template_name, "# New Document\n\n")
        self.insert(template_content)
    
    def toggle_markdown_preview(self):
        # TODO: Implement markdown preview
        self.notify("Markdown preview not yet implemented", severity="warning")