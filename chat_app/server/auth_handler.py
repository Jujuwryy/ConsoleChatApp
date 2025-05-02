"""
Login Handler

Handles user login and registration for the chat server.
Manages login validation, registration, and login security.
"""
import bcrypt
from chat_app.config.server_config import GREEN, RED, RESET
from chat_app.server.auth_manager import validate_username, validate_password, users, save_users
from chat_app.server.client_manager import clients, lock, send_to_client, broadcast
from chat_app.utils.logger import log_message


def register_user(client_socket):
    try:
        if not send_to_client(client_socket, "Enter new username: "):
            return False

        try:
            client_socket.settimeout(30.0)  # Longer timeout for input
            username = client_socket.recv(1024).decode('utf-8').strip()
            client_socket.settimeout(None)
        except Exception as e:
            print(f"{RED}Error receiving username: {e}{RESET}")
            return False

        # Check username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            send_to_client(client_socket, f"Invalid username: {error_msg}")
            return False

        # Check if username exists
        with lock:
            if username in users:
                send_to_client(client_socket, "Username already exists. Try again.")
                return False

        if not send_to_client(client_socket, "Enter password: "):
            return False

        try:
            client_socket.settimeout(30.0)  # Longer timeout for input
            password = client_socket.recv(1024).decode('utf-8').strip()
            client_socket.settimeout(None)
        except Exception as e:
            print(f"{RED}Error receiving password: {e}{RESET}")
            return False

        # Check password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            send_to_client(client_socket, f"Invalid password: {error_msg}")
            return False


        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Add new user
        with lock:
            # Check again (someone might have taken username)
            if username in users:
                send_to_client(client_socket, "Username was just taken. Please try another username.")
                return False
            users[username] = hashed_pass.decode('utf-8')
            save_users()

        send_to_client(client_socket, f"Registration successful! Welcome {username}.")
        with lock:
            # Check if already logged in
            for sock, name in clients.items():
                if name == username:
                    send_to_client(client_socket, "This account is already logged in elsewhere.")
                    return False
            clients[client_socket] = username

        print(f"{GREEN}New user registered: {username}{RESET}")
        log_message(f"New user registered: {username}")
        broadcast(f"{username} has joined the chat.")
        return True
    except Exception as e:
        print(f"{RED}Registration error: {e}{RESET}")
        send_to_client(client_socket, "An error occurred during registration. Please try again.")
        return False


def authenticate(client_socket):
    """Handle user login or registration."""
    try:
        if not send_to_client(client_socket, "Enter 'login' or 'register': "):
            return False

        try:
            client_socket.settimeout(30.0)  # Longer timeout for input
            choice = client_socket.recv(1024).decode('utf-8').strip().lower()
            client_socket.settimeout(None)
        except Exception as e:
            print(f"{RED}Error receiving authentication choice: {e}{RESET}")
            return False

        if choice == 'register':
            return register_user(client_socket)

        # Login path
        if not send_to_client(client_socket, "Enter username: "):
            return False

        try:
            client_socket.settimeout(30.0)  # Longer timeout for input
            username = client_socket.recv(1024).decode('utf-8').strip()
            client_socket.settimeout(None)
        except Exception as e:
            print(f"{RED}Error receiving username: {e}{RESET}")
            return False

        # Check username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            send_to_client(client_socket, f"Invalid username: {error_msg}")
            return False

        if not send_to_client(client_socket, "Enter password: "):
            return False

        try:
            client_socket.settimeout(30.0)  # Longer timeout for input
            password = client_socket.recv(1024).decode('utf-8').strip()
            client_socket.settimeout(None)
        except Exception as e:
            print(f"{RED}Error receiving password: {e}{RESET}")
            return False

        # Check password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            send_to_client(client_socket, f"Invalid password: {error_msg}")
            return False

        if username in users:
            # Verify password
            try:
                stored_hash = users[username].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    with lock:
                        # Check if already logged in
                        for sock, name in clients.items():
                            if name == username:
                                send_to_client(client_socket, "This account is already logged in elsewhere.")
                                return False

                        clients[client_socket] = username

                    send_to_client(client_socket,
                                  "Authentication successful! Welcome to the chat.\nType /help for available commands.")
                    print(f"{GREEN}New connection established: {username} ({client_socket.getpeername()[0]}){RESET}")
                    log_message(f"{username} connected.")
                    broadcast(f"{username} has joined the chat.")
                    return True
            except Exception as e:
                print(f"{RED}Password verification error: {e}{RESET}")
                send_to_client(client_socket, "Authentication failed. Disconnecting...")
                return False

        send_to_client(client_socket, "Authentication failed. Disconnecting...")
        return False
    except Exception as e:
        print(f"{RED}Authentication error: {e}{RESET}")
        return False 