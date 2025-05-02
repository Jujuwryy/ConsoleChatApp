"""
Main Chat Server.
"""
import socket
import threading
import signal
import os
import argparse
import time
from chat_app.config.server_config import HOST, PORT, GREEN, RED, BLUE, RESET
from chat_app.server.connection_handler import handle_client, client_threads, shutdown_event
from chat_app.utils.logger import log_message

# Global server socket
server_socket = None


def shutdown_server():
    """Clean up and shut down the server."""
    print(f"{BLUE}\n=== Shutting down server... ==={RESET}")
    log_message("Server shutdown initiated")
    
    # Set shutdown flag
    shutdown_event.set()
    
    # Close server socket first
    if server_socket:
        try:
            server_socket.close()
        except Exception as e:
            print(f"{RED}Error closing server socket: {e}{RESET}")
    
    # Close all client connections
    from chat_app.server.client_manager import clients, lock, send_to_client, handle_disconnect
    
    # Count connected clients
    with lock:
        client_count = len(clients)
        clients_copy = list(clients.keys())
    
    if client_count > 0:
        print(f"{RED}Disconnecting {client_count} remaining client(s){RESET}")
        log_message(f"Disconnecting {client_count} remaining client(s) during shutdown")
    
    for client_socket in clients_copy:
        try:
            username = clients.get(client_socket, "Unknown")
            print(f"{RED}Disconnecting user: {username}{RESET}")
            log_message(f"Disconnecting user: {username} during server shutdown")
            send_to_client(client_socket, "SERVER_SHUTDOWN:Server is shutting down. Goodbye!")
        except:
            pass
        try:
            handle_disconnect(client_socket)
        except Exception as e:
            print(f"{RED}Error disconnecting client during shutdown: {e}{RESET}")
    
    # Wait for threads to clean up
    time.sleep(1)
    
    print(f"{GREEN}=== Server shutdown complete ==={RESET}")
    log_message("Server shutdown complete")
    os._exit(0)


def signal_handler(sig, frame):
    """Handle signals like Ctrl+C."""
    if not shutdown_event.is_set():
        shutdown_event.set()
        # Start shutdown in separate thread
        threading.Thread(target=shutdown_server, daemon=True).start()


def parse_arguments():
    """Get command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Server')
    parser.add_argument('--host', default=HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=PORT, help='Port to listen on')
    return parser.parse_args()


def start_server(host=HOST, port=PORT):
    """Launch the chat server and wait for connections."""
    global server_socket
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"{GREEN}=== Server started on {host}:{port} ==={RESET}")
        log_message(f"Server started on {host}:{port}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        while not shutdown_event.is_set():
            try:
                client_socket, address = server_socket.accept()
                print(f"{GREEN}New connection from {address[0]}:{address[1]}{RESET}")
                log_message(f"New connection from {address[0]}:{address[1]}")
                
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except OSError:
                # Socket closed
                break
            except Exception as e:
                print(f"{RED}Error accepting connection: {e}{RESET}")
                log_message(f"Error accepting connection: {e}")
                continue
    except Exception as e:
        print(f"{RED}Server error: {e}{RESET}")
        log_message(f"Server error: {e}")
    finally:
        if server_socket:
            server_socket.close()


if __name__ == "__main__":
    args = parse_arguments()
    start_server(args.host, args.port) 