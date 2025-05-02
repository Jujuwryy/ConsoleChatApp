"""
Server configuration settings.
"""
import os
from datetime import datetime

# Server connection settings
HOST = '127.0.0.1'  # Localhost for testing
PORT = 55556  # Port to listen on

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Logging settings
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"chat_log_{datetime.now().strftime('%Y%m%d')}.txt")

# User database settings
USER_DB_FILE = "users.json"

# Status timeouts (in seconds)
AWAY_TIMEOUT = 60  # 1 minute
INACTIVE_TIMEOUT = 300  # 5 minutes 