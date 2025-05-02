"""
Command Handler Module

This module processes and executes chat commands issued by clients.
It implements a command pattern where each command is registered with a handler function.

Features:
- Support for various chat commands like /help, /users, /time, etc.
- Private messaging functionality
- Broadcast messaging to all users
- User status management
- User information lookup

Commands are processed based on user input that starts with '/' and
the appropriate handler is called with the parsed command arguments.
"""
import time
from datetime import datetime
from chat_app.config.server_config import RED, RESET, AWAY_TIMEOUT, INACTIVE_TIMEOUT
from chat_app.server.client_manager import (
    clients, lock, broadcast, send_to_client, update_last_seen, 
    send_private_message, mark_messages_read, unread_messages, last_seen
)
from chat_app.utils.logger import log_message


def process_command(client_socket, command):
    """Process chat commands with improved error handling."""
    try:
        # First, check if the client is still in the clients dictionary
        with lock:
            if client_socket not in clients:
                print(f"{RED}Command received from disconnected client socket{RESET}")
                return True  # Prevent further processing for disconnected clients

        username = clients[client_socket]
        update_last_seen(username)

        if command == '/help':
            help_text = (
                "=== Chat Server Commands ===\n\n"
                "Basic Commands:\n"
                "  /help - Show this help message\n"
                "  /users - List all online users with their status\n"
                "  /time - Show current server time\n"
                "  /quit - Disconnect from the server\n"
                "  /clear - Clear the chat screen\n\n"
                "Messaging Commands:\n"
                "  /pm <username> <message> - Send private message\n"
                "  /broadcast <message> - Send message to all users\n"
                "  /me <action> - Send an action message (e.g., /me waves)\n\n"
                "Status Commands:\n"
                "  /status - Show your current status\n"
                "  /whois <username> - Show user's last seen time\n"
                "  /unread - Show unread messages\n\n"
                "Status Indicators:\n"
                "  away - User inactive for 1-5 minutes\n"
                "  inactive - User inactive for more than 5 minutes\n"
                "  online - User is currently active"
            )
            send_to_client(client_socket, help_text)
            return True

        elif command == '/users':
            try:
                user_list = []
                with lock:
                    online_users = list(clients.values())
                    for user in online_users:
                        last_active = last_seen.get(user, 0)
                        time_diff = time.time() - last_active

                        # Build status string
                        status_parts = []
                        if time_diff > INACTIVE_TIMEOUT:  # 5 minutes
                            status_parts.append("inactive")
                        elif time_diff > AWAY_TIMEOUT:  # 1 minute
                            status_parts.append("away")

                        status = f" ({', '.join(status_parts)})" if status_parts else " (online)"
                        user_list.append(f"{user}{status}")

                user_list_msg = f"Online users ({len(online_users)}):\n" + "\n".join(user_list)
                send_to_client(client_socket, user_list_msg)
                return True
            except Exception as e:
                print(f"{RED}Error processing /users command: {e}{RESET}")
                send_to_client(client_socket, "Error processing command. Please try again.")
                return True

        elif command == '/time':
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_to_client(client_socket, f"Current server time: {current_time}")
                return True
            except Exception as e:
                print(f"{RED}Error processing /time command: {e}{RESET}")
                return True

        elif command == '/quit':
            try:
                send_to_client(client_socket, "Goodbye!")
                from chat_app.server.client_manager import handle_disconnect
                handle_disconnect(client_socket)
                return True
            except Exception as e:
                print(f"{RED}Error processing /quit command: {e}{RESET}")
                return True

        elif command == '/clear':
            try:
                send_to_client(client_socket, "CLEAR_SCREEN")
                return True
            except Exception as e:
                print(f"{RED}Error processing /clear command: {e}{RESET}")
                return True

        elif command.startswith('/pm '):
            try:
                parts = command[4:].split(' ', 1)
                if len(parts) < 2:
                    send_to_client(client_socket, "Usage: /pm <username> <message>")
                    return True
                recipient, message = parts
                if send_private_message(client_socket, recipient, message):
                    send_to_client(client_socket, f"Message sent to {recipient}")
                else:
                    send_to_client(client_socket, f"Could not send message to {recipient}")
                return True
            except Exception as e:
                print(f"{RED}Error processing /pm command: {e}{RESET}")
                send_to_client(client_socket, "Error processing command. Please try again.")
                return True

        elif command == '/status':
            try:
                last_active = last_seen.get(username, 0)
                time_diff = time.time() - last_active
                status_parts = []

                if time_diff > INACTIVE_TIMEOUT:
                    status_parts.append("inactive")
                elif time_diff > AWAY_TIMEOUT:
                    status_parts.append("away")

                status = "active" if not status_parts else ", ".join(status_parts)
                send_to_client(client_socket, f"Your current status: {status}")
                return True
            except Exception as e:
                print(f"{RED}Error processing /status command: {e}{RESET}")
                return True

        elif command.startswith('/whois '):
            try:
                target_user = command[7:].strip()
                if target_user in last_seen:
                    last_active = last_seen[target_user]
                    time_diff = time.time() - last_active
                    if time_diff < AWAY_TIMEOUT:
                        status = "currently online"
                    elif time_diff < INACTIVE_TIMEOUT:
                        status = "away"
                    else:
                        status = "inactive"
                    last_seen_time = datetime.fromtimestamp(last_active).strftime("%Y-%m-%d %H:%M:%S")
                    send_to_client(client_socket, f"{target_user} was last seen {status} at {last_seen_time}")
                else:
                    send_to_client(client_socket, f"User {target_user} not found")
                return True
            except Exception as e:
                print(f"{RED}Error processing /whois command: {e}{RESET}")
                return True

        elif command.startswith('/broadcast '):
            try:
                message = command[10:].strip()
                if message:
                    broadcast(f"BROADCAST from {username}: {message}")
                    send_to_client(client_socket, "Broadcast message sent")
                else:
                    send_to_client(client_socket, "Usage: /broadcast <message>")
                return True
            except Exception as e:
                print(f"{RED}Error processing /broadcast command: {e}{RESET}")
                return True

        elif command.startswith('/me '):
            try:
                action = command[4:].strip()
                if action:
                    broadcast(f"* {username} {action}")
                else:
                    send_to_client(client_socket, "Usage: /me <action>")
                return True
            except Exception as e:
                print(f"{RED}Error processing /me command: {e}{RESET}")
                return True

        elif command == '/unread':
            try:
                if username in unread_messages and unread_messages[username]:
                    messages = unread_messages[username]
                    response = "Unread messages:\n"
                    for msg in messages:
                        timestamp = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                        response += f"[{timestamp}] From {msg['from']}: {msg['message']}\n"
                    send_to_client(client_socket, response)
                    mark_messages_read(username)
                else:
                    send_to_client(client_socket, "No unread messages")
                return True
            except Exception as e:
                print(f"{RED}Error processing /unread command: {e}{RESET}")
                return True

        return False
    except Exception as e:
        print(f"{RED}Error processing command '{command}': {e}{RESET}")
        log_message(f"Command error ({clients.get(client_socket, 'unknown')}): {e}")
        try:
            send_to_client(client_socket, "Error processing command. Please try again.")
        except:
            pass  # Client might be disconnected already
        return True  # Prevent falling through to regular message handling 