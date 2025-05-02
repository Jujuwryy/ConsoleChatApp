"""
Logger Module

This module provides logging functionality for the chat application.
It handles logging of server and client actions to files for debugging purposes.
Features include:
- Timestamped log entries
- Log directory creation if not exists
- Log file management
- Thread-safe logging operations

The logger is designed to be simple while providing
essential logging capabilities for the application.
"""
import os
from datetime import datetime
from chat_app.config.server_config import LOG_DIR, LOG_FILE, RED, RESET


def ensure_log_directory():
    """Make sure the log directory exists."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def log_message(message):
    """Log messages to a file with timestamp."""
    ensure_log_directory()
    try:
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"{RED}Error writing to log file: {e}{RESET}") 