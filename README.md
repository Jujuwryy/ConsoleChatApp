# Console Chat App

A secure, multi-user chat application that runs in the terminal.

## Features

- User registration and authentication with secure password hashing
- Real-time messaging between multiple clients
- Command system for user interactions
- Message history tracking
- Colorful terminal interface
- Logging system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jujuwryy/ConsoleChatApp.git
cd ConsoleChatApp
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
python -m chat_app.server
```

### Running the Client

```bash
python -m chat_app.client
```

### Commands

Use the `/help` command in the chat to see all available commands.

## Project Structure

- `chat_app/` - Main package
  - `client/` - Client-side code
  - `server/` - Server-side code
  - `config/` - Configuration settings
  - `utils/` - Utility functions
  - `docs/` - Technical documentation

## License

This project is available as open source under the terms of the MIT License. 