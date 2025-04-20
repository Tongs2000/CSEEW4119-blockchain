from flask import Flask, jsonify, request
import threading
import time
from typing import Dict

app = Flask(__name__)
lock = threading.Lock()
# Store peer address -> last heartbeat timestamp
peers_heartbeat: Dict[str, float] = {}
# Heartbeat timeout in seconds (e.g., 120s)
HEARTBEAT_TIMEOUT = 120
CLEANUP_INTERVAL = 60  # seconds

@app.route('/register', methods=['POST'])
def register_peer():
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        peers_heartbeat[address] = time.time()
        peers = list(peers_heartbeat.keys())

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/unregister', methods=['POST'])
def unregister_peer():
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        peers_heartbeat.pop(address, None)
        peers = list(peers_heartbeat.keys())

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({'status': 'error', 'message': 'address is required'}), 400

    with lock:
        if address in peers_heartbeat:
            peers_heartbeat[address] = time.time()
        else:
            return jsonify({'status': 'error', 'message': 'address not registered'}), 400
        peers = list(peers_heartbeat.keys())

    return jsonify({'status': 'success', 'peers': peers}), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    with lock:
        peers = list(peers_heartbeat.keys())
    return jsonify({'status': 'success', 'peers': peers}), 200


def cleanup_inactive_peers():
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
            print(f"Cleaned up inactive peers: {removed}")

if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_inactive_peers, daemon=True)
    cleanup_thread.start()
    app.run(host='0.0.0.0', port=6000)
