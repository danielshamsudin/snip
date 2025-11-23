#!/usr/bin/env python3
"""Configuration management for Snip"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "screenshot": {
            "save_directory": str(Path.home() / "Pictures" / "Snip"),
            "filename_format": "snip_%Y%m%d_%H%M%S.png",
            "copy_to_clipboard": True,
            "auto_save": False,
        },
        "shortcuts": {
            "capture_region": "Super+Shift+A",
            "capture_fullscreen": "Super+Shift+S",
            "capture_window": "Super+Shift+W",
        },
        "annotation": {
            "default_color": "#FF0000",
            "default_line_width": 3,
            "font_size": 14,
            "font_family": "Sans",
        },
        "pin": {
            "border_width": 2,
            "border_color": "#00FF00",
            "always_on_top": True,
        }
    }

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "snip"
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, *keys, default=None):
        """Get configuration value by nested keys"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default

    def set(self, *keys, value):
        """Set configuration value by nested keys"""
        config = self.config
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        config[keys[-1]] = value
        self.save_config()
