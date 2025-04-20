import os
import sys
import argparse

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def main():
    parser = argparse.ArgumentParser(description='Run blockchain tracker or client service')
    parser.add_argument('service', choices=['tracker', 'client'], help='Service to run')
    parser.add_argument('--port', type=int, help='Port to run the service on')
    
    args = parser.parse_args()
    
    if args.service == 'tracker':
        from src.network.tracker import main as tracker_main
        if args.port:
            os.environ['PORT'] = str(args.port)
        tracker_main()
    elif args.service == 'client':
        from src.network.client import main as client_main
        if args.port:
            os.environ['PORT'] = str(args.port)
        client_main()

if __name__ == '__main__':
    main() 