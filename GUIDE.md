# Developer Guide - Chat App

This guide helps developers who want to understand, change, or add to the chat app.

## App Structure

The chat app has a client-server design with separate parts:

### Server Side

- **Server Core (`server.py`)**: Main server code that handles connections
- **User System (`auth_manager.py`, `auth_handler.py`)**: Handles user accounts and login
- **User Management (`client_manager.py`)**: Tracks connected users
- **Command Processing (`command_handler.py`)**: Handles chat commands
- **Connection Handling (`connection_handler.py`)**: Manages user connections

### Client Side

- **Client Core (`client.py`)**: Main client code with the user interface
- **Connection Handling (`connection_handler.py`)**: Manages server connection
- **Message Handling (`message_handler.py`)**: Formats messages and saves history

### Shared Components

- **Settings (`config/`)**: App settings for client and server
- **Helpers (`utils/`)**: Helper functions like logging

## How Messages Work

The app uses a simple text protocol over TCP:

1. Client connects to server
2. Server asks for username and password
3. After login, messages are sent as UTF-8 text
4. System messages use special formats (like `"USER_DISCONNECT:"`)
5. Commands start with `/` and are handled specially

## Adding New Features

### Adding a New Command

To add a new command:

1. Add a function in `command_handler.py`
2. Add the command to the commands dictionary
3. Update the help text
4. Update client code if needed

Example:
```python
def weather_command(client_socket, args):
    """Get weather info."""
    # Your code here
    return "Weather: Sunny, 25°C"

# Add to commands
commands = {
    # ... existing commands ...
    'weather': weather_command,
}
```



#### Server Side

1. Choose the right file for your feature
2. Write thread-safe code
3. Update related parts
4. Add error handling and logging

#### Client Side

1. Add UI elements in `client.py`
2. Update message handling if needed
3. Add error handling


### Changing User Login

User data is in `users.json`:
```json
{
    "username": {
        "password": "password_hash",
        "last_seen": "timestamp"
    }
}
```

To change login:
1. Update functions in `auth_manager.py`
2. Consider adding password hashing if not already done

### Adding User Roles

To add roles:
1. Add role info to `users.json`
2. Update `auth_manager.py` to handle roles
3. Add role checks to commands

## Performance Tips

- The server uses threads which works for moderate numbers of users
- For larger numbers consider:
  - Using async code instead of threads
  - Adding connection pooling
  - Testing with more users

## Security Notes

Current limitations:
- Passwords might be stored as plain text
- Messages aren't encrypted
- Limited protection against login attacks
- No input validation against attacks

## Running in Production

For real-world use:
1. Update settings in `config/`
2. Set up proper logging
3. Consider using Docker
4. Add monitoring

## Troubleshooting

Common problems:
- Can't connect: Check if server is running
- Login failure: Check username/password in `users.json`
- Thread errors: Look for race conditions

Check logs in the `logs/` folder for detailed error information. 