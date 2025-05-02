"""
Client Manager Module

This module manages client connections, messaging, and status tracking in the chat server.
It provides functionality for:
- Maintaining active client connections and their associated usernames
- Sending messages between clients (both public and private)
- Managing user statuses (online, away, inactive)
- Handling client disconnections
- Tracking message history and unread messages

The module uses thread-safe operations with a lock mechanism to ensure
concurrent access to shared resources is properly managed.
"""
import socket
import threading
import time
from chat_app.config.server_config import RED, BLUE, GREEN, RESET
from chat_app.utils.logger import log_message

# Dictionary to store client sockets and usernames
clients = {}
# Thread lock for safe access to shared resources
lock = threading.Lock()
# Track when users were last active
last_seen = {}
# Track unread messages
unread_messages = {}
# Track socket states to prevent double-close operations
socket_states = {}  # key: socket object, value: "open", "closing", "closed"


def update_last_seen(username):
    """Update the last seen timestamp for a user."""
    try:
        last_seen[username] = time.time()
    except Exception as e:
        print(f"{RED}Error updating last seen for {username}: {e}{RESET}")


def mark_messages_read(username):
    """Mark all unread messages as read for a user."""
    try:
        with lock:
            if username in unread_messages:
                del unread_messages[username]
    except Exception as e:
        print(f"{RED}Error marking messages read for {username}: {e}{RESET}")


def broadcast(message, sender_socket=None):
    """Broadcast message to all connected clients except the sender with improved error handling."""
    # Create a copy of the clients dictionary to avoid modifying during iteration
    clients_copy = {}
    with lock:
        clients_copy = clients.copy()

    disconnected_clients = []
    for client_socket in clients_copy:
        if client_socket != sender_socket:
            # Skip sockets that are already being closed
            with lock:
                if socket_states.get(client_socket) in ["closing", "closed"]:
                    continue
                    
            try:
                # Set a timeout for sending
                client_socket.settimeout(1.0)
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"{RED}Error sending broadcast to a client: {e}{RESET}")
                disconnected_clients.append(client_socket)
            finally:
                # Reset timeout
                try:
                    client_socket.settimeout(None)
                except:
                    pass  # Socket might be closed already

    # Handle disconnected clients outside the iteration
    for client in disconnected_clients:
        with lock:
            if socket_states.get(client) not in ["closing", "closed"]:
                socket_states[client] = "closing"
                try:
                    handle_disconnect(client)
                except Exception as e:
                    print(f"{RED}Error handling disconnected client during broadcast: {e}{RESET}")
                    log_message(f"Error handling disconnected client during broadcast: {e}")


def handle_disconnect(client_socket):
    """Handle client disconnection with improved error handling."""
    username = None
    
    # Skip if socket is already being closed or closed
    with lock:
        if socket_states.get(client_socket) == "closed":
            return None
        # Mark as closing to prevent double-close
        socket_states[client_socket] = "closing"
    
    # Critical section - get username and remove from dictionaries
    with lock:
        if client_socket in clients:
            try:
                username = clients[client_socket]
                
                # Get current user count BEFORE removing this user
                current_count = len(clients)
                
                # Delete from clients dictionary
                del clients[client_socket]
                
                # Calculate remaining count AFTER removing this user
                remaining_count = len(clients)
                
                # Log the disconnection details
                disconnect_msg = f"{username} has disconnected."
                print(f"\n{RED}!!! {disconnect_msg} !!!{RESET}")
                log_message(disconnect_msg)
                
                # Log user counts
                log_message(f"User count before disconnect: {current_count}, after disconnect: {remaining_count}")
                
                # Check if this was the last user
                if remaining_count == 0:
                    last_user_msg = f"Last user ({username}) has disconnected. Server is now empty."
                    print(f"{RED}{last_user_msg}{RESET}")
                    log_message(last_user_msg)
                else:
                    user_text = "user" if remaining_count == 1 else "users"
                    print(f"{GREEN}Server has {remaining_count} active {user_text} remaining{RESET}")
                    log_message(f"Server has {remaining_count} active {user_text} remaining")
            except Exception as e:
                print(f"{RED}Error removing client from dictionaries: {e}{RESET}")
                log_message(f"Error removing client from dictionaries: {e}")
    
    # Close socket - outside the lock to avoid deadlocks
    if client_socket:
        try:
            # Try to shutdown the socket properly
            try:
                if socket_states.get(client_socket) != "closed":
                    client_socket.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                # Don't report common shutdown errors
                if not isinstance(e, (socket.error, OSError)) or e.errno != 9:  # Not a "Bad file descriptor"
                    print(f"{RED}Socket shutdown error (expected): {e}{RESET}")
            
            # Try to close the socket
            try:
                client_socket.close()
                with lock:
                    socket_states[client_socket] = "closed"
            except Exception as e:
                # Don't report common close errors
                if not isinstance(e, (socket.error, OSError)) or e.errno != 9:  # Not a "Bad file descriptor"
                    print(f"{RED}Socket close error (expected): {e}{RESET}")
                with lock:
                    socket_states[client_socket] = "closed"  # Mark as closed even if close failed
            
            print(f"{GREEN}Socket for {username or 'unknown'} closed successfully{RESET}")
            log_message(f"Socket for {username or 'unknown'} closed successfully")
        except Exception as e:
            print(f"{RED}Unexpected error closing client socket: {e}{RESET}")
            log_message(f"Unexpected error closing client socket: {e}")
            with lock:
                socket_states[client_socket] = "closed"  # Mark as closed for safety
    
    return username


def send_to_client(client_socket, message):
    """Send a message to a specific client"""
    # Skip if socket is already being closed or closed
    with lock:
        if socket_states.get(client_socket) in ["closing", "closed"]:
            return False
    
    try:
        # Set a timeout for sending
        client_socket.settimeout(1.0)
        client_socket.send(message.encode('utf-8'))
        # Reset timeout
        client_socket.settimeout(None)
        return True
    except (ConnectionResetError, ConnectionAbortedError) as e:
        print(f"{RED}Connection error when sending to client: {e}{RESET}")
        log_message(f"Connection error when sending to client: {e}")
        try:
            with lock:
                if socket_states.get(client_socket) not in ["closing", "closed"]:
                    socket_states[client_socket] = "closing"
                    handle_disconnect(client_socket)
        except Exception as disconnect_error:
            print(f"{RED}Error in disconnect handling: {disconnect_error}{RESET}")
            log_message(f"Error in disconnect handling: {disconnect_error}")
        return False
    except Exception as e:
        print(f"{RED}Error sending to client: {e}{RESET}")
        log_message(f"Error sending to client: {e}")
        try:
            with lock:
                if socket_states.get(client_socket) not in ["closing", "closed"]:
                    socket_states[client_socket] = "closing"
                    handle_disconnect(client_socket)
        except Exception as disconnect_error:
            print(f"{RED}Error in disconnect handling: {disconnect_error}{RESET}")
            log_message(f"Error in disconnect handling: {disconnect_error}")
        return False


def send_private_message(sender_socket, recipient, message):
    """Send a private message to a specific user with improved error handling."""
    try:
        sender = clients[sender_socket]
        update_last_seen(sender)

        # Find recipient's socket
        recipient_socket = None
        with lock:
            for sock, username in clients.items():
                if username == recipient:
                    # Skip recipients that are being closed
                    if socket_states.get(sock) in ["closing", "closed"]:
                        continue
                    recipient_socket = sock
                    break

        if recipient_socket:
            # Format the private message
            formatted_msg = f"PRIVATE:{sender}:{message}"
            timestamp = time.time()

            # Send to recipient
            try:
                recipient_socket.send(formatted_msg.encode('utf-8'))
                # Add to unread messages if recipient is not active
                if time.time() - last_seen.get(recipient, 0) > 60:  # Consider inactive if not seen for 1 minute
                    with lock:
                        if recipient not in unread_messages:
                            unread_messages[recipient] = []
                        unread_messages[recipient].append({
                            'from': sender,
                            'message': message,
                            'timestamp': timestamp
                        })
                return True
            except Exception as e:
                print(f"{RED}Error sending private message: {e}{RESET}")
                log_message(f"Error sending private message: {e}")
                return False
        else:
            print(f"{RED}Recipient {recipient} not found or offline{RESET}")
            log_message(f"Recipient {recipient} not found or offline")
            return False
    except Exception as e:
        print(f"{RED}Private message error: {e}{RESET}")
        log_message(f"Private message error: {e}")
        return False 