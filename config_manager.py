"""
DroidForge Configuration Manager
================================
Live-configurable settings system that propagates changes without rebuilds.
Implements declarative configuration with instant propagation.
"""

import json
import os
from typing import Any, Dict, Optional, List, Callable
from pathlib import Path

from utils.logger import get_logger


class ConfigManager:
    """
    Configuration Manager for live system reconfiguration.
    
    Features:
    - Hierarchical configuration with dot-notation access
    - Live updates that propagate to all subscribers
    - Persistent storage with automatic save/load
    - Default values with override support
    - Configuration validation
    """
    
    # Default configuration values
    DEFAULTS = {
        # App settings
        "app.name": "DroidForge Console",
        "app.version": "1.0.0",
        "app.debug": False,
        
        # Theme settings
        "theme.style": "Dark",
        "theme.primary_color": "Green",
        "theme.accent_color": "Lime",
        
        # Engine settings
        "engine.max_queue_size": 100,
        "engine.worker_threads": 1,
        "engine.command_timeout": 300,
        
        # Build settings
        "build.target": "android",
        "build.debug": True,
        "build.auto_sign": False,
        "build.min_sdk": 21,
        "build.target_sdk": 33,
        
        # GitHub settings
        "github.enabled": True,
        "github.owner": "",
        "github.repo": "",
        "github.branch": "main",
        "github.workflow": "build.yml",
        
        # AI settings
        "ai.enabled": True,
        "ai.model": "local",
        "ai.temperature": 0.7,
        "ai.max_tokens": 2048,
        
        # Automation settings
        "automation.auto_build": False,
        "automation.auto_test": True,
        "automation.auto_deploy": False,
        
        # Logging settings
        "logging.level": "INFO",
        "logging.file_enabled": True,
        "logging.max_size_mb": 10,
        
        # Network settings
        "network.timeout": 30,
        "network.retry_count": 3,
        "network.proxy_enabled": False,
    }
    
    def __init__(self, event_bus, config_file: str = None):
        self.event_bus = event_bus
        self.logger = get_logger("ConfigManager")
        
        # Determine config file path
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Use app data directory
            self.config_file = self._get_config_path()
        
        # Configuration storage
        self._config: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # Load configuration
        self._load()
        
        self.logger.info(f"ConfigManager initialized with {len(self._config)} settings")
    
    def _get_config_path(self) -> Path:
        """Get platform-appropriate config file path."""
        try:
            from kivy.utils import platform
            if platform == 'android':
                from android.storage import app_storage_path
                base_path = Path(app_storage_path())
            else:
                base_path = Path.home() / ".droidforge"
        except ImportError:
            base_path = Path.home() / ".droidforge"
        
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path / "config.json"
    
    def _load(self):
        """Load configuration from file."""
        # Start with defaults
        self._config = dict(self.DEFAULTS)
        
        # Load saved config
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    self._config.update(saved)
                self.logger.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
    
    def save(self):
        """Save configuration to file."""
        try:
            # Only save non-default values
            to_save = {
                k: v for k, v in self._config.items()
                if k not in self.DEFAULTS or self.DEFAULTS.get(k) != v
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(to_save, f, indent=2)
            
            self.logger.info(f"Saved config to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Dot-notation key (e.g., "build.target")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any, notify: bool = True):
        """
        Set configuration value with live propagation.
        
        Args:
            key: Dot-notation key
            value: New value
            notify: Whether to notify subscribers
        """
        old_value = self._config.get(key)
        self._config[key] = value
        
        self.logger.debug(f"Config set: {key} = {value}")
        
        if notify and old_value != value:
            # Notify specific subscribers
            self._notify_subscribers(key, value)
            
            # Emit global event
            self.event_bus.emit("config_changed", key, value)
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """
        Get all config values under a prefix.
        
        Args:
            prefix: Key prefix (e.g., "build")
            
        Returns:
            Dictionary of matching keys and values
        """
        prefix_dot = prefix + "."
        return {
            k: v for k, v in self._config.items()
            if k.startswith(prefix_dot) or k == prefix
        }
    
    def set_section(self, prefix: str, values: Dict[str, Any]):
        """
        Set multiple config values under a prefix.
        
        Args:
            prefix: Key prefix
            values: Dictionary of relative keys and values
        """
        for key, value in values.items():
            full_key = f"{prefix}.{key}" if prefix else key
            self.set(full_key, value)
    
    def subscribe(self, key: str, callback: Callable):
        """
        Subscribe to changes for a specific key.
        
        Args:
            key: Configuration key to watch
            callback: Function to call on change (receives key, value)
        """
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)
    
    def unsubscribe(self, key: str, callback: Callable):
        """Unsubscribe from configuration changes."""
        if key in self._subscribers:
            try:
                self._subscribers[key].remove(callback)
            except ValueError:
                pass
    
    def _notify_subscribers(self, key: str, value: Any):
        """Notify subscribers of a configuration change."""
        # Exact key subscribers
        for callback in self._subscribers.get(key, []):
            try:
                callback(key, value)
            except Exception as e:
                self.logger.error(f"Subscriber error for {key}: {e}")
        
        # Prefix subscribers (e.g., "build.*" pattern)
        parts = key.split(".")
        for i in range(len(parts)):
            prefix = ".".join(parts[:i+1]) + ".*"
            for callback in self._subscribers.get(prefix, []):
                try:
                    callback(key, value)
                except Exception as e:
                    self.logger.error(f"Subscriber error for {prefix}: {e}")
    
    def reset(self, key: str = None):
        """
        Reset configuration to defaults.
        
        Args:
            key: Specific key to reset, or None for all
        """
        if key:
            if key in self.DEFAULTS:
                self.set(key, self.DEFAULTS[key])
        else:
            self._config = dict(self.DEFAULTS)
            self.event_bus.emit("config_reset")
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        return dict(self._config)
    
    def import_config(self, config: Dict[str, Any], merge: bool = True):
        """
        Import configuration.
        
        Args:
            config: Configuration dictionary
            merge: If True, merge with existing; if False, replace
        """
        if not merge:
            self._config = dict(self.DEFAULTS)
        
        for key, value in config.items():
            self.set(key, value, notify=False)
        
        self.event_bus.emit("config_imported")
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required string fields
        required_strings = ["app.name", "app.version"]
        for key in required_strings:
            if not self.get(key):
                errors.append(f"Missing required config: {key}")
        
        # Numeric bounds
        if self.get("engine.max_queue_size", 0) < 1:
            errors.append("engine.max_queue_size must be >= 1")
        
        if self.get("build.min_sdk", 0) < 21:
            errors.append("build.min_sdk must be >= 21")
        
        return errors
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style assignment."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._config
