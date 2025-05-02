"""
Server entry point module.
"""
from chat_app.server.server import start_server, parse_arguments

def main():
    """Main entry point for the server."""
    args = parse_arguments()
    start_server(args.host, args.port)

if __name__ == "__main__":
    main() 