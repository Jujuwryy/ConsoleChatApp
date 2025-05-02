"""
Client Connection

Manages the connection to the chat server.
Handles connecting, login, and receiving messages.
"""
import socket
import threading
from colorama import Fore, Style
from chat_app.client.message_handler import format_message, clear_screen


def receive_messages(client_socket):
    """Get and display messages from server."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"{Fore.RED}Connection to server lost.{Style.RESET_ALL}")
                break

            if message == "CLEAR_SCREEN":
                clear_screen()
                continue

            if message.startswith("SERVER_SHUTDOWN:"):
                shutdown_msg = message.replace("SERVER_SHUTDOWN:", "")
                print(f"\n{Fore.RED}*** {shutdown_msg} ***{Style.RESET_ALL}")
                break
                
            if message.startswith("USER_DISCONNECT:"):
                username = message.replace("USER_DISCONNECT:", "")
                disconnect_msg = f"{username} has disconnected from the chat."
                print(f"\n{Fore.RED}!!! {disconnect_msg} !!!{Style.RESET_ALL}")
                # Add to history
                format_message(f"*** {disconnect_msg} ***")
                continue

            print(format_message(message))
        except (ConnectionResetError, BrokenPipeError):
            print(f"{Fore.RED}Connection to server lost.{Style.RESET_ALL}")
            break
        except OSError as e:
            if e.errno == 9:  # Bad file descriptor
                break
            else:
                print(f"{Fore.RED}Error receiving message: {e}{Style.RESET_ALL}")
                break
        except Exception as e:
            print(f"{Fore.RED}Error receiving message: {e}{Style.RESET_ALL}")
            break


    try:
        client_socket.close()
    except:
        pass
    print(f"{Fore.YELLOW}Connection closed. Press Ctrl+C to exit.{Style.RESET_ALL}")


def authenticate(client_socket):
    """Log in to the server."""
    try:
        # Get login prompt
        auth_prompt = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.CYAN}{auth_prompt}{Style.RESET_ALL}")
        choice = input().strip().lower()
        client_socket.send(choice.encode('utf-8'))

        # Enter username
        username_prompt = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.CYAN}{username_prompt}{Style.RESET_ALL}")
        username = input().strip()
        client_socket.send(username.encode('utf-8'))

        # Enter password
        password_prompt = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.CYAN}{password_prompt}{Style.RESET_ALL}")
        password = input().strip()
        client_socket.send(password.encode('utf-8'))

        # Get result
        result = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")

        # Check if successful
        if "successful" in result.lower():
            return True
        else:
            return False

    except Exception as e:
        print(f"{Fore.RED}Authentication error: {e}{Style.RESET_ALL}")
        return False


def connect_to_server(host, port):
    """Connect to the server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        print(f"{Fore.GREEN}Connected to server at {host}:{port}{Style.RESET_ALL}")
        return client
    except ConnectionRefusedError:
        print(f"{Fore.RED}Could not connect to server. Make sure the server is running.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Connection error: {e}{Style.RESET_ALL}")
        return None


def start_message_thread(client_socket):
    """Start thread to receive messages."""
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    return receive_thread 