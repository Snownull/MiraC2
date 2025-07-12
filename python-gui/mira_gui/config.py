"""
Configuration management for MiraC2 GUI
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "server_host": "localhost",
    "server_port": 8080,
    "theme": "cyberpunk",
    "window": {
        "width": 1400,
        "height": 900,
        "resizable": True
    },
    "colors": {
        "primary": "#ff0040",      # Red
        "secondary": "#00ff41",    # Green  
        "background": "#000000",   # Black
        "surface": "#1a1a1a",     # Dark gray
        "text": "#ffffff",         # White
        "text_secondary": "#b0b0b0", # Light gray
        "accent": "#ff6b00",       # Orange
        "warning": "#ffaa00",      # Yellow
        "error": "#ff0040",        # Red
        "success": "#00ff41",      # Green
        "info": "#00aaff"          # Blue
    },
    "fonts": {
        "primary": "Consolas",
        "secondary": "Arial",
        "monospace": "Courier New",
        "size_small": 9,
        "size_normal": 11,
        "size_large": 13,
        "size_header": 16
    },
    "logging": {
        "level": "INFO",
        "max_entries": 1000,
        "auto_scroll": True
    },
    "map": {
        "default_zoom": 2,
        "center_lat": 20.0,
        "center_lng": 0.0
    }
}

def get_config_path() -> Path:
    """Get the path to the configuration file"""
    return Path.home() / ".mira_gui" / "config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults"""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
    
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file"""
    config_path = get_config_path()
    
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
        
    except IOError as e:
        print(f"Error saving config file: {e}")
        return False

def get_color(config: Dict[str, Any], color_name: str) -> str:
    """Get a color value from the configuration"""
    return config.get("colors", {}).get(color_name, "#ffffff")

def get_font(config: Dict[str, Any], font_type: str = "primary", size: str = "normal") -> tuple:
    """Get font configuration as (family, size) tuple"""
    fonts = config.get("fonts", {})
    family = fonts.get(font_type, "Arial")
    font_size = fonts.get(f"size_{size}", 11)
    return (family, font_size)