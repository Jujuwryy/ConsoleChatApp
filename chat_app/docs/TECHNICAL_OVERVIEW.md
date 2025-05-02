# Technical Overview - Chat App

This document explains how the chat app works behind the scenes.

## How Messages Work

The app uses simple text messages over TCP connections. All messages use UTF-8 encoding.

### Login Process

1. **Connect**:
   - User connects to server
   - Server creates a new thread for the user

2. **Login Steps**:
   ```
   Server: "Do you want to (l)ogin or (r)egister?"
   User: "l" or "r"
   Server: "Enter username:"
   User: [username]
   Server: "Enter password:"
   User: [password]
   Server: "Login successful" or "Login failed"
   ```

3. **After Login**:
   - Server tells everyone a new user joined
   - Server sends welcome message to new user
   - User can now chat

### Message Types

Messages are just text. Special message types have prefixes:

- **System Messages**:
  - `USER_DISCONNECT:{username}` - Someone left
  - `SERVER_SHUTDOWN:{message}` - Server is closing
  - `CLEAR_SCREEN` - Clears the screen

- **Commands**:
  All commands start with `/`:
  - `/help` - Shows available commands
  - `/pm {username} {message}` - Private message
  - etc.

### How Commands Work

1. User types a command starting with `/`
2. Server sees it's a command and sends it to command handler
3. Command handler processes it and sends back a response
4. Response goes to the user or everyone as needed

## Data Storage

### User Data (`users.json`)

```json
{
  "username1": {
    "password": "password_hash",
    "last_seen": "timestamp"
  },
  "username2": {
    "password": "password_hash",
    "last_seen": "timestamp"
  }
}
```

### Memory Storage

- **Connected Users**:
  ```python
  clients = {
      client_socket: username,
      # ...
  }
  ```

- **User Status**:
  ```python
  user_status = {
      username: status,  # "online", "away", "inactive"
      # ...
  }
  ```

- **Unread Messages**:
  ```python
  unread_messages = {
      username: [message1, message2, ...],
      # ...
  }
  ```

## How Threading Works

The app uses Python's threading module:

1. **Main Server Thread**:
   - Listens for new connections
   - Creates new threads for clients

2. **Client Threads**:
   - One thread per connected user
   - Handles login, messages, and commands

3. **Shutdown Thread**:
   - Starts when server is closing
   - Handles clean shutdown

## Thread Safety

Thread safety uses:

- **Locks**:
  ```python
  lock = threading.Lock()
  with lock:
      # Protected code
  ```

- **Events**:
  ```python
  shutdown_event = threading.Event()
  if shutdown_event.is_set():
      # Server is shutting down
  ```

## Error Handling

- **Connection Problems**:
  - `ConnectionResetError`, `BrokenPipeError` → Connection lost
  - `ConnectionRefusedError` → Server not running
  
- **Login Problems**:
  - Wrong username/password → Login fails
  
- **Command Problems**:
  - Wrong command format → Error message to user

## Example: Private Message

1. **User A sends message to User B**:
   - User A types: `/pm UserB Hello there!`
   - Server gets command and sees it's a PM
   - Server formats as: `[Private from UserA] Hello there!`
   - Server sends to User B
   - Server confirms to User A: `[Private to UserB] Hello there!`

2. **Server tells users when someone leaves**:
   - User A disconnects
   - Server notices the closed connection
   - Server removes User A from connected list
   - Server sends to everyone: `USER_DISCONNECT:UserA`
   - Everyone's screen shows: `UserA has disconnected from the chat.`



