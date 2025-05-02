"""
Connection Handler Module

This module handles client connections to the chat server.
It manages the lifecycle of client connections including:
- Initial connection acceptance
- Message reception and processing
- Command handling
- Client disconnection

The module works with thread-based client handling where each client connection
is processed in its own thread. It also implements the shutdown event mechanism
to gracefully terminate all client connections when the server is shutting down.
"""
import socket
import threading
import time
from chat_app.config.server_config import RED, BLUE, GREEN, RESET
from chat_app.server.client_manager import clients, lock, handle_disconnect, send_to_client, broadcast, update_last_seen
from chat_app.server.auth_handler import authenticate
from chat_app.server.command_handler import process_command
from chat_app.utils.logger import log_message

# Keep track of all client threads
client_threads = []
# Event to signal server shutdown
shutdown_event = threading.Event()


def handle_client(client_socket):
    """Handle individual client connection with improved error handling."""
    # Add thread to global list
    global client_threads
    current_thread = threading.current_thread()
    with lock:
        client_threads.append(current_thread)

    # Keep track of whether authentication was successful
    authenticated = False
    username = None

    try:
        if not authenticate(client_socket):
            # Authentication failed, clean up silently
            try:
                client_socket.close()
            except:
                pass
            return

        authenticated = True
        username = clients[client_socket]
        update_last_seen(username)

        # Send initial status update
        try:
            broadcast(f"STATUS_UPDATE:{username}:online")
        except Exception as e:
            print(f"{RED}Error broadcasting status update: {e}{RESET}")
            log_message(f"Error in status broadcast: {e}")

        while not shutdown_event.is_set():
            try:
                # Use a timeout to allow checking for shutdown periodically
                client_socket.settimeout(1.0)
                message = client_socket.recv(1024).decode('utf-8')
                # Reset timeout after successful receive
                client_socket.settimeout(None)

                if not message:
                    print(f"{BLUE}Client {username} sent empty message, disconnecting...{RESET}")
                    break  # Client disconnected normally

                update_last_seen(username)

                # Check if it's a command
                if message.startswith('/'):
                    if process_command(client_socket, message.lower()):
                        continue

                # Regular message
                formatted_message = f"{username}: {message}"
                print(formatted_message)
                log_message(formatted_message)

                try:
                    broadcast(formatted_message, client_socket)
                except Exception as e:
                    print(f"{RED}Error broadcasting message: {e}{RESET}")
                    log_message(f"Error in message broadcast: {e}")
                    break

            except socket.timeout:
                # This is just the periodic timeout to check for shutdown
                continue
            except ConnectionResetError:
                print(f"{RED}Connection reset by {username}{RESET}")
                break
            except ConnectionAbortedError:
                print(f"{RED}Connection aborted by {username}{RESET}")
                break
            except Exception as e:
                if not shutdown_event.is_set():
                    try:
                        client_info = "unknown"
                        if hasattr(client_socket, 'getpeername'):
                            try:
                                client_info = client_socket.getpeername()
                            except:
                                pass
                        print(f"{RED}Error handling client {client_info}: {e}{RESET}")
                        log_message(f"Client error ({username}): {e}")
                    except:
                        print(f"{RED}Error handling client: {e}{RESET}")
                break
    finally:
        # Clean up client connection
        try:
            if authenticated and username:
                print(f"{BLUE}Cleaning up for disconnected user: {username}{RESET}")
                
                # Notify other clients about the disconnection BEFORE removing from clients dictionary
                try:
                    # Send a specially formatted message so clients can display it prominently
                    broadcast(f"USER_DISCONNECT:{username}", client_socket)
                    log_message(f"Broadcast disconnect notification for {username}")
                except Exception as e:
                    print(f"{RED}Error broadcasting disconnect: {e}{RESET}")
                    log_message(f"Error broadcasting disconnect: {e}")
                
                # Perform the disconnect - this will log the remaining users with correct count
                try:
                    handle_disconnect(client_socket)
                except Exception as e:
                    print(f"{RED}Error in handle_disconnect: {e}{RESET}")
                    log_message(f"Error in handle_disconnect: {e}")
            else:
                # Handle unauthenticated connection cleanup
                try:
                    handle_disconnect(client_socket)
                except Exception as e:
                    print(f"{RED}Error in handle_disconnect: {e}{RESET}")
                    log_message(f"Error in handle_disconnect: {e}")
        except Exception as e:
            print(f"{RED}Error in client cleanup: {e}{RESET}")
            log_message(f"Error in client cleanup: {e}")

        # Remove thread from global list
        with lock:
            if current_thread in client_threads:
                client_threads.remove(current_thread)
                
        # Log that the thread cleanup is complete
        if username:
            log_message(f"Thread cleanup complete for {username}")
            print(f"{GREEN}Thread cleanup successful for {username}{RESET}") 