"""
Main Chat Client

Handles connecting to server, sending/receiving messages,
processing commands, and displaying the chat interface.
"""
import signal
import time
from colorama import init, Fore, Style
from chat_app.config.client_config import HOST, PORT
from chat_app.client.connection_handler import (
    connect_to_server, authenticate, start_message_thread
)
from chat_app.client.message_handler import (
    load_message_history, clear_screen, format_message, display_history
)

# Start colorama
init()


def signal_handler(sig, frame):
    #Handle disconnects using the keyboard, control + c
    print(f"\n{Fore.YELLOW}Disconnecting from chat server...{Style.RESET_ALL}")
    raise KeyboardInterrupt


def start_client(host=HOST, port=PORT):
    """Start the chat client."""

    load_message_history()

    # Connect to server
    client_socket = connect_to_server(host, port)
    if not client_socket:
        return

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Login
    if not authenticate(client_socket):
        print(f"{Fore.RED}Authentication failed. Disconnecting...{Style.RESET_ALL}")
        client_socket.close()
        return

    # Show welcome message
    clear_screen()
    print(f"{Fore.CYAN}=== Welcome to the Chat! ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type your messages (press Ctrl+C to exit){Style.RESET_ALL}")
    print(f"{Fore.CYAN}Type /help to see available commands{Style.RESET_ALL}\n")

    # Start message receiver
    receive_thread = start_message_thread(client_socket)

    # Track connection status
    connected = True

    # Main message loop
    while connected:
        try:
            message = input(f"{Fore.GREEN}You > {Style.RESET_ALL}")

            if message.lower() == '/quit':
                print(f"{Fore.YELLOW}Disconnecting from chat server...{Style.RESET_ALL}")
                break
            elif message.lower() == '/clear':
                clear_screen()
                continue
            elif message.lower() == '/help':
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"{Fore.RED}Error sending command: Connection may be closed. ({e}){Style.RESET_ALL}")
                    connected = False
                continue
            elif message.lower() == '/history':
                display_history()
                continue
            elif message.strip() == '':
                # Skip empty messages
                continue

            # Send the message
            try:
                client_socket.send(message.encode('utf-8'))
                print(format_message(message, is_sent=True))
            except BrokenPipeError:
                print(f"{Fore.RED}Server connection lost. Cannot send message.{Style.RESET_ALL}")
                connected = False
                break
            except ConnectionResetError:
                print(f"{Fore.RED}Server connection reset. Cannot send message.{Style.RESET_ALL}")
                connected = False
                break
            except Exception as e:
                print(f"{Fore.RED}Error sending message: {e}{Style.RESET_ALL}")
                connected = False
                break

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Disconnecting from chat server...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
            time.sleep(1)  # Prevent CPU spikes
    
    # Send quit message
    if connected:
        try:
            client_socket.send("/quit".encode('utf-8'))
        except:
            pass  # Already disconnected
    
    # Close socket
    try:
        client_socket.close()
        print(f"{Fore.YELLOW}Connection closed.{Style.RESET_ALL}")
    except:
        pass
    
    # Wait for receive thread
    try:
        receive_thread.join(timeout=2.0)
    except:
        pass
    
    print(f"{Fore.YELLOW}Chat session ended. Goodbye!{Style.RESET_ALL}")


if __name__ == "__main__":
    start_client() 