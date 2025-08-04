#!/usr/bin/env python3
"""
KSP Orbital Mechanics Display Panel
Interactive ASCII representation of orbits and orbital parameters
"""

import math
from typing import Dict, Tuple, List
from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from textual import events
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.align import Align


# KSP Celestial Bodies Database
BODIES = {
    "kerbin": {
        "name": "Kerbin",
        "radius": 600_000,  # meters
        "mu": 3.5316e12,    # gravitational parameter (m³/s²)
        "atmosphere": 70_000,
        "soi": 84_159_286,
        "color": "blue",
        "symbol": "🌍"
    },
    "mun": {
        "name": "Mun",
        "radius": 200_000,
        "mu": 6.5138e10,
        "atmosphere": 0,
        "soi": 2_430_559,
        "color": "gray",
        "symbol": "🌑"
    },
    "minmus": {
        "name": "Minmus",
        "radius": 60_000,
        "mu": 1.7658e9,
        "atmosphere": 0,
        "soi": 2_247_428,
        "color": "cyan",
        "symbol": "🌙"
    },
    "duna": {
        "name": "Duna",
        "radius": 320_000,
        "mu": 3.0136e11,
        "atmosphere": 50_000,
        "soi": 47_921_949,
        "color": "red",
        "symbol": "🔴"
    },
    "eve": {
        "name": "Eve",
        "radius": 700_000,
        "mu": 8.1717e12,
        "atmosphere": 90_000,
        "soi": 85_109_365,
        "color": "purple",
        "symbol": "🟣"
    },
    "jool": {
        "name": "Jool",
        "radius": 6_000_000,
        "mu": 2.8253e14,
        "atmosphere": 200_000,
        "soi": 2.4559e9,
        "color": "green",
        "symbol": "🟢"
    }
}


class OrbitalParameters:
    
    def __init__(self, body: str, apoapsis: float, periapsis: float):
        self.body = body
        self.body_data = BODIES[body]
        self.apoapsis = apoapsis + self.body_data["radius"]  # Convert to altitude from center
        self.periapsis = periapsis + self.body_data["radius"]
        
        self.semi_major_axis = (self.apoapsis + self.periapsis) / 2
        self.eccentricity = (self.apoapsis - self.periapsis) / (self.apoapsis + self.periapsis)
        
        self.period = 2 * math.pi * math.sqrt(self.semi_major_axis**3 / self.body_data["mu"])
        
        self.v_apoapsis = math.sqrt(self.body_data["mu"] * (2/self.apoapsis - 1/self.semi_major_axis))
        self.v_periapsis = math.sqrt(self.body_data["mu"] * (2/self.periapsis - 1/self.semi_major_axis))
    
    def get_display_values(self) -> Dict[str, str]:
        return {
            "apoapsis": f"{(self.apoapsis - self.body_data['radius']) / 1000:.1f} km",
            "periapsis": f"{(self.periapsis - self.body_data['radius']) / 1000:.1f} km",
            "eccentricity": f"{self.eccentricity:.3f}",
            "period": self._format_time(self.period),
            "v_apoapsis": f"{self.v_apoapsis:.0f} m/s",
            "v_periapsis": f"{self.v_periapsis:.0f} m/s",
            "semi_major": f"{self.semi_major_axis / 1000:.1f} km"
        }
    
    def _format_time(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m {seconds%60:.0f}s"
        elif seconds < 21600:  # 6 hours (1 Kerbin day)
            return f"{seconds/3600:.0f}h {(seconds%3600)/60:.0f}m"
        else:
            days = seconds / 21600
            hours = (seconds % 21600) / 3600
            return f"{days:.0f}d {hours:.0f}h"


class KSPOrbitalDisplay(Widget):    
    current_body = reactive("kerbin")
    apoapsis = reactive(100_000.0)  # 100km default
    periapsis = reactive(80_000.0)   # 80km default
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orbital_params = None
        self._update_orbital_params()
    
    def _update_orbital_params(self):
        self.orbital_params = OrbitalParameters(
            self.current_body,
            self.apoapsis,
            self.periapsis
        )
    
    def set_body(self, body_name: str):
        if body_name.lower() in BODIES:
            self.current_body = body_name.lower()
            self._update_orbital_params()
            self.refresh()
    
    def set_orbit(self, apoapsis: float, periapsis: float):
        self.apoapsis = apoapsis
        self.periapsis = periapsis
        self._update_orbital_params()
        self.refresh()
    
    def render(self) -> RenderResult:
        body = BODIES[self.current_body]
        params = self.orbital_params.get_display_values()
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="orbit_display", size=15),
            Layout(name="parameters", size=12),
            Layout(name="controls", size=3)
        )
        
        header_text = Text(f"{body['symbol']} {body['name'].upper()} ORBITAL MECHANICS", 
                          style="bold cyan")
        layout["header"].update(Align.center(header_text))
        
        orbit_ascii = self._generate_orbit_ascii()
        layout["orbit_display"].update(Panel(orbit_ascii, border_style="cyan"))
        
        params_table = Table(show_header=False, box=None, padding=(0, 1))
        params_table.add_column("Parameter", style="cyan")
        params_table.add_column("Value", style="green")
        
        params_table.add_row("Apoapsis:", params["apoapsis"])
        params_table.add_row("Periapsis:", params["periapsis"])
        params_table.add_row("Eccentricity:", params["eccentricity"])
        params_table.add_row("Orbital Period:", params["period"])
        params_table.add_row("Velocity @ Ap:", params["v_apoapsis"])
        params_table.add_row("Velocity @ Pe:", params["v_periapsis"])
        
        if body["atmosphere"] > 0:
            atmo_height = body["atmosphere"] / 1000
            if self.periapsis < body["atmosphere"]:
                params_table.add_row("", "[red]⚠ PERIAPSIS IN ATMOSPHERE![/red]")
            else:
                params_table.add_row("Atmosphere:", f"{atmo_height:.0f} km")
        
        layout["parameters"].update(Panel(params_table, title="Orbital Parameters", 
                                         border_style="green"))
        
        controls = Text("[F3] Bodies  [F4] Maneuvers  [↑↓] Adjust Orbit", 
                       style="dim", justify="center")
        layout["controls"].update(controls)
        
        return layout
    
    def _generate_orbit_ascii(self) -> str:
        width = 40
        height = 12
        center_x = width // 2
        center_y = height // 2
        
        a = int(width * 0.4)  # semi-major axis in characters
        b = int(height * 0.4 * (1 - self.orbital_params.eccentricity))  # semi-minor axis
        
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        body_radius = 3
        for y in range(height):
            for x in range(width):
                dx = x - center_x
                dy = y - center_y
                
                if b > 0:  # Prevent division by zero
                    ellipse_value = (dx/a)**2 + (dy/b)**2
                    
                    if 0.8 < ellipse_value < 1.2:
                        grid[y][x] = '·'
                    elif 0.9 < ellipse_value < 1.1:
                        grid[y][x] = '○'
                
                if abs(dx) <= body_radius and abs(dy) <= body_radius/2:
                    if dx == 0 and dy == 0:
                        grid[y][x] = '★'
                    else:
                        distance = math.sqrt(dx**2 + (dy*2)**2)
                        if distance <= body_radius:
                            grid[y][x] = '█'
        
        grid[center_y][center_x + a - 1] = 'A'  # Apoapsis
        grid[center_y][center_x - a + 1] = 'P'  # Periapsis
        
        return '\n'.join(''.join(row) for row in grid)
    
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            self.apoapsis = min(self.apoapsis + 10_000, 1_000_000)
            self._update_orbital_params()
            self.refresh()
        elif event.key == "down":
            self.apoapsis = max(self.apoapsis - 10_000, self.periapsis + 1000)
            self._update_orbital_params()
            self.refresh()
        elif event.key == "shift+up":
            self.periapsis = min(self.periapsis + 10_000, self.apoapsis - 1000)
            self._update_orbital_params()
            self.refresh()
        elif event.key == "shift+down":
            body = BODIES[self.current_body]
            min_periapsis = body["atmosphere"] + 5000 if body["atmosphere"] > 0 else 10_000
            self.periapsis = max(self.periapsis - 10_000, min_periapsis)
            self._update_orbital_params()
            self.refresh()


class DeltaVCalculator:
    
    @staticmethod
    def hohmann_transfer(body: str, r1: float, r2: float) -> Tuple[float, float]:
        mu = BODIES[body]["mu"]
        
        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)
        
        a_transfer = (r1 + r2) / 2
        
        v_transfer_peri = math.sqrt(mu * (2/r1 - 1/a_transfer))
        v_transfer_apo = math.sqrt(mu * (2/r2 - 1/a_transfer))
        
        dv1 = abs(v_transfer_peri - v1)
        dv2 = abs(v2 - v_transfer_apo)
        
        return dv1, dv2
    
    @staticmethod
    def phase_angle(r1: float, r2: float) -> float:
        return 180 * (1 - ((r1/r2)**(3/2))**0.5)
    
    @staticmethod
    def escape_velocity(body: str, altitude: float) -> float:
        mu = BODIES[body]["mu"]
        r = BODIES[body]["radius"] + altitude
        return math.sqrt(2 * mu / r)