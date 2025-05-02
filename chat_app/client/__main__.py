"""
Client entry point module.
"""
import argparse
from chat_app.client.client import start_client

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')
    parser.add_argument('--host', default='127.0.0.1', help='Host to connect to')
    parser.add_argument('--port', type=int, default=55556, help='Port to connect to')
    return parser.parse_args()

def main():
    args = parse_arguments()
    start_client(args.host, args.port)

if __name__ == "__main__":
    main() 