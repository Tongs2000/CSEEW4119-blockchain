from flask import Flask, jsonify, request
from typing import Dict, Any
import json
from ..network.peer import Peer

app = Flask(__name__)
peer = None

@app.route('/vote', methods=['POST'])
def cast_vote():
    data = request.get_json()
    candidate = data.get('candidate')
    voter_id = data.get('voter_id')
    
    if not candidate or not voter_id:
        return jsonify({'error': 'Missing candidate or voter_id'}), 400
    
    # Create transaction
    transaction = {
        'type': 'vote',
        'candidate': candidate,
        'voter_id': voter_id,
        'timestamp': time.time()
    }
    
    # Add to pending transactions
    peer.blockchain.add_transaction(transaction)
    
    return jsonify({
        'status': 'success',
        'message': 'Vote cast successfully'
    })

@app.route('/results', methods=['GET'])
def get_results():
    votes = {}
    
    # Count votes from blockchain
    for block in peer.blockchain.chain:
        for transaction in block.transactions:
            if transaction['type'] == 'vote':
                candidate = transaction['candidate']
                votes[candidate] = votes.get(candidate, 0) + 1
    
    return jsonify({
        'results': votes,
        'total_blocks': len(peer.blockchain.chain)
    })

def start_voting_app(tracker_url: str, port: int):
    global peer
    peer = Peer(tracker_url, port)
    peer.start()
    
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tracker', required=True, help='Tracker URL')
    parser.add_argument('--port', type=int, required=True, help='Port number')
    args = parser.parse_args()
    
    start_voting_app(args.tracker, args.port) 