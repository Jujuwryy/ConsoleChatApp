"""
User Login Manager

Handles user accounts, registration, and login.
Manages saving and loading user data from file.
"""
import json
import bcrypt
import os
import threading
from chat_app.config.server_config import USER_DB_FILE, GREEN, RED, RESET
from chat_app.utils.logger import log_message

# Thread lock for shared resources
lock = threading.Lock()
# User database
users = {}


def load_users():
    """Load users from file with error handling."""
    global users
    if not os.path.exists(USER_DB_FILE):
        # Create default users if file missing
        default_users = {
            "User1": bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User2": bcrypt.hashpw("pass456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User3": bcrypt.hashpw("pass789".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        try:
            with open(USER_DB_FILE, 'w') as f:
                json.dump(default_users, f, indent=4)
            users = default_users
            return default_users
        except Exception as e:
            print(f"{RED}Error creating default users file: {e}{RESET}")
            users = default_users
            return default_users

    try:
        with open(USER_DB_FILE, 'r') as f:
            data = json.load(f)

            if not isinstance(data, dict):
                print("Invalid user database format. Using default users.")
                default_users = {
                    "User1": bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    "User2": bcrypt.hashpw("pass456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    "User3": bcrypt.hashpw("pass789".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                }
                users = default_users
                return default_users
            users = data
            return data
    except json.JSONDecodeError:
        print("Error reading user database: Invalid JSON format. Using default users.")
        default_users = {
            "User1": bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User2": bcrypt.hashpw("pass456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User3": bcrypt.hashpw("pass789".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        users = default_users
        return default_users
    except Exception as e:
        print(f"{RED}Error reading user database: {e}. Using default users.{RESET}")
        default_users = {
            "User1": bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User2": bcrypt.hashpw("pass456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "User3": bcrypt.hashpw("pass789".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        users = default_users
        return default_users


def save_users():
    """Save users to file with backup."""
    try:
        # Backup current file if it exists
        if os.path.exists(USER_DB_FILE):
            backup_file = f"{USER_DB_FILE}.bak"
            try:
                with open(USER_DB_FILE, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            except:
                pass  # Continue if backup fails

        # Save new data
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"{RED}Error saving user database: {e}{RESET}")
        # Try to restore from backup
        if os.path.exists(f"{USER_DB_FILE}.bak"):
            try:
                with open(f"{USER_DB_FILE}.bak", 'r') as src, open(USER_DB_FILE, 'w') as dst:
                    dst.write(src.read())
            except:
                pass


def validate_username(username):
    # Rules:
    # - 3-20 characters
    # - Letters, numbers, underscores only
    # - No spaces
    if not username:
        return False, "Username cannot be empty"
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username cannot be longer than 20 characters"
    if not username.isalnum() and '_' not in username:
        return False, "Username can only contain letters, numbers, and underscores"
    if ' ' in username:
        return False, "Username cannot contain spaces"
    return True, ""


def validate_password(password):
    # Rules:
    # - 6-30 characters
    # - At least one number
    # - At least one letter
    # - No spaces
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 30:
        return False, "Password cannot be longer than 30 characters"
    if ' ' in password:
        return False, "Password cannot contain spaces"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    return True, ""


# Load users when module starts
load_users() 