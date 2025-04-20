from flask import Flask, jsonify, request
import threading
import time
from typing import Set, Dict, Any

app = Flask(__name__)
peers: Set[str] = set()  # Store peer addresses
lock = threading.Lock()

@app.route('/register', methods=['POST'])
def register_peer():
    data = request.get_json()
    peer_address = data.get('address')
    
    with lock:
        peers.add(peer_address)
    
    return jsonify({
        'status': 'success',
        'message': f'Peer {peer_address} registered successfully'
    })

@app.route('/unregister', methods=['POST'])
def unregister_peer():
    data = request.get_json()
    peer_address = data.get('address')
    
    with lock:
        peers.discard(peer_address)
    
    return jsonify({
        'status': 'success',
        'message': f'Peer {peer_address} unregistered successfully'
    })

@app.route('/peers', methods=['GET'])
def get_peers():
    with lock:
        return jsonify({
            'peers': list(peers)
        })

def cleanup_inactive_peers():
    """Periodically check and remove inactive peers"""
    while True:
        time.sleep(60)  # Check every minute
        # Implementation of peer activity check would go here
        pass

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_inactive_peers, daemon=True)
    cleanup_thread.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000) 