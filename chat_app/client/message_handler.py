"""
Message Handler

Manages chat messages, formatting, and history.
Saves messages for later viewing and handles display formatting.
"""
import os
import json
from datetime import datetime
from colorama import Fore, Style
from chat_app.config.client_config import MESSAGE_HISTORY_FILE

# Message history
message_history = []


def load_message_history():
    """Load past messages from file."""
    global message_history
    if os.path.exists(MESSAGE_HISTORY_FILE):
        try:
            with open(MESSAGE_HISTORY_FILE, 'r') as f:
                message_history = json.load(f)
                return message_history
        except json.JSONDecodeError:
            message_history = []
            return []
    message_history = []
    return []


def save_message_history():
    """Save messages to file."""
    try:
        with open(MESSAGE_HISTORY_FILE, 'w') as f:
            json.dump(message_history, f, indent=4)
    except Exception as e:
        print(f"{Fore.RED}Error saving message history: {e}{Style.RESET_ALL}")


def clear_screen():
    """Clear the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_message(message, is_sent=False):
    """Add timestamp and colors to message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if is_sent:
        formatted = f"{Fore.CYAN}[{timestamp}] {Fore.GREEN}You: {Fore.WHITE}{message}{Style.RESET_ALL}"
    else:
        formatted = f"{Fore.CYAN}[{timestamp}] {Fore.YELLOW}{message}{Style.RESET_ALL}"

    # Save to history
    message_history.append({
        "timestamp": timestamp,
        "message": message,
        "is_sent": is_sent
    })
    save_message_history()

    return formatted


def display_history():
    """Show past messages."""
    clear_screen()
    print(f"{Fore.CYAN}=== Message History ==={Style.RESET_ALL}")
    for msg in message_history:
        timestamp = msg['timestamp']
        content = msg['message']
        if msg['is_sent']:
            print(f"{Fore.CYAN}[{timestamp}] {Fore.GREEN}You: {Fore.WHITE}{content}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[{timestamp}] {Fore.YELLOW}{content}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}====================={Style.RESET_ALL}\n") 