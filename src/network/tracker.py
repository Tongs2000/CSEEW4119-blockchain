from flask import Flask, jsonify, request
import threading
import time
from typing import Dict
import os
import argparse
from src.utils.logger import setup_logger

app = Flask(__name__)

from flask_cors import CORS
CORS(app, supports_credentials=False)

lock = threading.Lock()
# Store peer address -> last heartbeat timestamp
peers_heartbeat: Dict[str, float] = {}
# Heartbeat timeout in seconds
HEARTBEAT_TIMEOUT = 120
# Cleanup interval in seconds
CLEANUP_INTERVAL = 60
HOST = 'localhost'

# Parse command line arguments
parser = argparse.ArgumentParser(description='Start blockchain tracker server')
parser.add_argument('--port', type=int, help='Port to run the tracker on')
args = parser.parse_args()

def get_port():
    """Get port from command line argument, environment variable, or default to 6000"""
    if args.port:
        return args.port
    return int(os.getenv('PORT', 6000))

def get_base_url():
    """Get base URL using current port"""
    return f'http://{HOST}:{get_port()}'

# Create logger with port information
tracker_logger = None

@app.route('/register', methods=['POST'])
def register_peer():
    """
    Register new peer with tracker.
    
    Returns:
        JSON response with peer list
    """
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        tracker_logger.error("Invalid registration data: address is required")
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        peers_heartbeat[address] = time.time()
        peers = list(peers_heartbeat.keys())
        tracker_logger.info(f"New peer registered: {address}")

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/unregister', methods=['POST'])
def unregister_peer():
    """
    Unregister peer from tracker.
    
    Returns:
        JSON response with status
    """
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        tracker_logger.error("Invalid unregistration data: address is required")
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        peers_heartbeat.pop(address, None)
        peers = list(peers_heartbeat.keys())
        tracker_logger.info(f"Peer unregistered: {address}")

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Update peer's last seen timestamp.
    
    Returns:
        JSON response with peer list
    """
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        tracker_logger.error("Invalid heartbeat data: address is required")
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        if address in peers_heartbeat:
            peers_heartbeat[address] = time.time()
            tracker_logger.debug(f"Heartbeat received from {address}")
        else:
            tracker_logger.warning(f"Unknown peer attempted heartbeat: {address}")
            return jsonify({'status': 'error', 'message': 'address not registered'}), 400
        peers = list(peers_heartbeat.keys())

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    with lock:
        peers = list(peers_heartbeat.keys())
        tracker_logger.debug(f"Returning {len(peers)} active peers")
    return jsonify({'status': 'success', 'peers': peers}), 200

def cleanup_inactive_peers():
    """
    Periodically remove inactive peers.
    """
    while True:
        time.sleep(CLEANUP_INTERVAL)
        now = time.time()
        removed = []
        with lock:
            for address, ts in list(peers_heartbeat.items()):
                if now - ts > HEARTBEAT_TIMEOUT:
                    peers_heartbeat.pop(address, None)
                    removed.append(address)
        if removed:
            tracker_logger.info(f"Cleaned up inactive peers: {removed}")
            print(f"Cleaned up inactive peers: {removed}")

def run_server():
    """
    Start tracker server.
    """
    tracker_logger.info(f"Starting tracker server on {HOST}:{get_port()}")
    app.run(host='0.0.0.0', port=get_port())

def main():
    """
    Main function to start tracker.
    """
    global tracker_logger
    tracker_logger = setup_logger('tracker', 'logs/tracker', port=get_port())
    
    cleanup_thread = threading.Thread(target=cleanup_inactive_peers, daemon=True)
    cleanup_thread.start()
    
    run_server()

if __name__ == '__main__':
    main()
