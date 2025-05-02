"""
Main starting point for the chat app.
"""
import sys
import argparse


def parse_arguments():
    """Get command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Application')
    parser.add_argument('mode', choices=['client', 'server'], help='Run as client or server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to use (server only)')
    parser.add_argument('--port', type=int, default=55556, help='Port to use (server only)')
    return parser.parse_args()


def main():
    """Main function to start client or server."""
    args = parse_arguments()

    if args.mode == 'client':
        from chat_app.client.client import start_client
        start_client(args.host, args.port)
    elif args.mode == 'server':
        from chat_app.server.server import start_server
        start_server(args.host, args.port)
    else:
        print(f"Invalid mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main() 