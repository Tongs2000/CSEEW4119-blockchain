from flask import Flask, request, jsonify
from src.blockchain.chain import Blockchain
from src.blockchain.block import Block
import threading, requests, json

app = Flask(__name__)
blockchain = Blockchain()
peers = []  # List of peer addresses, populated from tracker
HOST = 'localhost'
PORT = 5001  # Port this client listens on

@app.route('/new_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()

    try:
        new_block = Block.from_dict(block_data)
    except Exception as e:
        return jsonify({'status': 'rejected', 'reason': f'invalid_format: {e}'}), 400

    latest_block = blockchain.get_latest_block()
    if new_block.previous_hash != latest_block.hash:
        return jsonify({'status': 'rejected', 'reason': 'previous_hash_mismatch'}), 400

    required_prefix = '0' * blockchain.difficulty
    if not new_block.hash.startswith(required_prefix):
        return jsonify({'status': 'rejected', 'reason': 'invalid_proof_of_work'}), 400

    if new_block.hash != new_block.calculate_hash():
        return jsonify({'status': 'rejected', 'reason': 'hash_mismatch'}), 400

    blockchain.chain.append(new_block)
    return jsonify({'status': 'accepted'}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.to_dict())

def broadcast_block(block):
    block_payload = block.to_dict() if hasattr(block, 'to_dict') else block

    for peer in peers:
        if peer == f"http://{HOST}:{PORT}":
            continue
        url = f"{peer}/new_block"
        try:
            response = requests.post(url, json=block_payload, timeout=3)
            if response.status_code == 200:
                print(f"Broadcast succeeded to {peer}")
            else:
                reason = response.json().get('reason')
                print(f"Broadcast rejected by {peer}: {reason}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to broadcast to {peer}: {e}")

def run_server():
    app.run(host='0.0.0.0', port=PORT)

def main():
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_server)
    http_thread.daemon = True
    http_thread.start()

    # Register with tracker and retrieve peer list
    try:
        reg_resp = requests.post(
            "http://localhost:5000/register",
            json={"address": f"http://{HOST}:{PORT}"},
            timeout=5
        )
        reg_data = reg_resp.json()
        if reg_resp.status_code == 200 and 'peers' in reg_data:
            peers.clear()
            peers.extend(reg_data['peers'])
            print("Registered with tracker. Peers:", peers)
        else:
            print("Registration failed or invalid response from tracker.")
    except Exception as e:
        print(f"Error registering with tracker: {e}")

    # Command-line interface loop
    while True:
        print("\nAvailable commands: add_tx | mine | list_peers | exit")
        command = input("Enter command: ").strip().lower()

        if command == 'add_tx':
            try:
                tx_input = input("Enter transaction JSON: ")
                transaction = json.loads(tx_input)
                blockchain.add_transaction(transaction)
                print("Transaction added to pending list.")
            except json.JSONDecodeError:
                print("Invalid JSON format. Please try again.")

        elif command == 'mine':
            try:
                new_block = blockchain.mine_pending_transactions()
                print(f"Mined new block #{new_block.index}, hash: {new_block.hash}")
                broadcast_block(new_block)
            except ValueError as ve:
                print(ve)

        elif command == 'list_peers':
            print("Current peers:")
            for p in peers:
                print(f" - {p}")

        elif command == 'exit':
            print("Shutting down client.")
            break

        else:
            print("Unknown command. Please choose from add_tx, mine, list_peers, exit.")

if __name__ == '__main__':
    main()
