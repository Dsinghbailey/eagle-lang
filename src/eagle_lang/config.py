"""Configuration management for Eagle."""

import os
import json
from typing import Dict, Any


# Configuration constants
CONFIG_FILENAME = "eagle_config.json"
PROJECT_EAGLE_DIR = os.path.join(os.getcwd(), ".eagle")
USER_EAGLE_DIR = os.path.expanduser("~/.eagle")
PROJECT_CONFIG_PATH = os.path.join(PROJECT_EAGLE_DIR, CONFIG_FILENAME)
USER_CONFIG_PATH = os.path.join(USER_EAGLE_DIR, CONFIG_FILENAME)


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration values from default-config folder."""
    # Path to default config file in the package
    default_config_dir = os.path.join(os.path.dirname(__file__), "default-config")
    default_config_path = os.path.join(default_config_dir, CONFIG_FILENAME)
    
    # Load from default-config folder (should always exist)
    with open(default_config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> Dict[str, Any]:
    """Load config from .eagle folder in project directory, user home directory, or defaults."""
    # Check project config first, then user config, then use defaults
    if os.path.exists(PROJECT_CONFIG_PATH):
        with open(PROJECT_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"Loaded Eagle config from project: {PROJECT_CONFIG_PATH}")
        return config
    elif os.path.exists(USER_CONFIG_PATH):
        with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"Loaded Eagle config from user home: {USER_CONFIG_PATH}")
        return config
    else:
        # Use default configuration
        config = get_default_config()
        print("Using default Eagle configuration (no .eagle folder found)")
        return config


def save_config(config: Dict[str, Any], to_project: bool = True) -> None:
    """Save config to .eagle folder in project or user directory."""
    if to_project:
        config_dir = PROJECT_EAGLE_DIR
        config_path = PROJECT_CONFIG_PATH
    else:
        config_dir = USER_EAGLE_DIR
        config_path = USER_CONFIG_PATH
    
    # Create .eagle directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"Eagle config saved to: {config_path}")