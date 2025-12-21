#!/usr/bin/env python3
"""
DroidForge Console - Main Entry Point
=====================================
A self-contained Android-native development, automation, and orchestration tool.
Operates as an independent execution environment with command-driven architecture.

Author: DroidForge Team
License: MIT
"""

import os
import sys

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
# Configure before other Kivy imports
Config.set('kivy', 'log_level', 'info')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp

from core.engine import DroidForgeEngine
from core.config_manager import ConfigManager
from core.event_bus import EventBus
from ui.main_screen import MainScreen
from utils.logger import setup_logger, get_logger

# Platform-specific setup
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.INTERNET,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
    ])


class DroidForgeApp(MDApp):
    """
    Main Application Class for DroidForge Console.
    
    This is the central controller that initializes all subsystems:
    - Core Engine: Command processing and execution
    - Config Manager: Live-configurable settings
    - Event Bus: Inter-component communication
    - UI Layer: KivyMD-based interface
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "DroidForge Console"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Lime"
        
        # Core subsystems
        self.logger = None
        self.config_manager = None
        self.event_bus = None
        self.engine = None
        
    def build(self):
        """Build and return the root widget."""
        # Initialize logging
        self.logger = setup_logger("DroidForge")
        self.logger.info("DroidForge Console starting...")
        
        # Initialize core subsystems
        self._init_subsystems()
        
        # Set window properties
        Window.clearcolor = (0.05, 0.05, 0.08, 1)
        
        # Build main screen
        return MainScreen(
            engine=self.engine,
            config_manager=self.config_manager,
            event_bus=self.event_bus
        )
    
    def _init_subsystems(self):
        """Initialize all core subsystems in proper order."""
        self.logger.info("Initializing subsystems...")
        
        # Event bus for decoupled communication
        self.event_bus = EventBus()
        self.logger.info("Event bus initialized")
        
        # Configuration manager for live settings
        self.config_manager = ConfigManager(self.event_bus)
        self.logger.info("Config manager initialized")
        
        # Core engine for command orchestration
        self.engine = DroidForgeEngine(
            config_manager=self.config_manager,
            event_bus=self.event_bus
        )
        self.logger.info("Core engine initialized")
        
        # Subscribe to critical events
        self.event_bus.subscribe("config_changed", self._on_config_changed)
        self.event_bus.subscribe("engine_error", self._on_engine_error)
        
        self.logger.info("All subsystems initialized successfully")
    
    def _on_config_changed(self, key, value):
        """Handle configuration changes at app level."""
        self.logger.info(f"Config changed: {key} = {value}")
        
        # Apply theme changes if applicable
        if key == "theme_style":
            self.theme_cls.theme_style = value
        elif key == "primary_color":
            self.theme_cls.primary_palette = value
    
    def _on_engine_error(self, error_type, message):
        """Handle engine errors at app level."""
        self.logger.error(f"Engine error [{error_type}]: {message}")
    
    def on_start(self):
        """Called when the application starts."""
        self.logger.info("DroidForge Console started")
        self.event_bus.emit("app_started")
    
    def on_stop(self):
        """Called when the application stops."""
        self.logger.info("DroidForge Console stopping...")
        
        # Cleanup
        if self.engine:
            self.engine.shutdown()
        if self.config_manager:
            self.config_manager.save()
        
        self.logger.info("DroidForge Console stopped")
        return True
    
    def on_pause(self):
        """Called when the application is paused (Android)."""
        self.logger.info("Application paused")
        if self.config_manager:
            self.config_manager.save()
        return True
    
    def on_resume(self):
        """Called when the application resumes (Android)."""
        self.logger.info("Application resumed")


def main():
    """Main entry point."""
    app = DroidForgeApp()
    app.run()


if __name__ == "__main__":
    main()
