"""
DroidForge Logger
=================
Centralized logging configuration with support for multiple outputs.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


# Global logger registry
_loggers = {}


class ColoredFormatter(logging.Formatter):
    """Formatter with color support for terminal output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        # Add color codes for terminal
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(name: str = "DroidForge", 
                 level: str = "INFO",
                 log_file: str = None,
                 console: bool = True) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Format string
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%H:%M:%S"
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(fmt, date_fmt))
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(fmt, date_fmt))
        logger.addHandler(file_handler)
    
    # Register logger
    _loggers[name] = logger
    
    return logger


def get_logger(name: str = "DroidForge") -> logging.Logger:
    """
    Get or create a logger with the specified name.
    
    Args:
        name: Logger name (will be prefixed with DroidForge.)
        
    Returns:
        Logger instance
    """
    full_name = f"DroidForge.{name}" if not name.startswith("DroidForge") else name
    
    if full_name in _loggers:
        return _loggers[full_name]
    
    # Create child logger
    parent = _loggers.get("DroidForge")
    if parent:
        logger = parent.getChild(name)
    else:
        logger = logging.getLogger(full_name)
        logger.setLevel(logging.INFO)
    
    _loggers[full_name] = logger
    return logger


class LogCapture:
    """Context manager to capture log messages."""
    
    def __init__(self, logger_name: str = "DroidForge"):
        self.logger = logging.getLogger(logger_name)
        self.records = []
        self._handler = None
    
    def __enter__(self):
        self._handler = CaptureHandler(self.records)
        self.logger.addHandler(self._handler)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handler:
            self.logger.removeHandler(self._handler)
    
    def get_messages(self, level: str = None) -> list:
        """Get captured messages, optionally filtered by level."""
        if level:
            return [r.getMessage() for r in self.records 
                    if r.levelname == level.upper()]
        return [r.getMessage() for r in self.records]


class CaptureHandler(logging.Handler):
    """Handler that captures log records to a list."""
    
    def __init__(self, records: list):
        super().__init__()
        self.records = records
    
    def emit(self, record):
        self.records.append(record)


def log_exception(logger: logging.Logger, message: str, exc: Exception):
    """Log an exception with full traceback."""
    logger.error(f"{message}: {exc}", exc_info=True)
