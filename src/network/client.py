from flask import Flask, request, jsonify
from src.blockchain.chain import Blockchain
from src.blockchain.block import Block
import threading, requests, json, time, os
from src.utils.logger import setup_logger

app = Flask(__name__)
blockchain = Blockchain()
peers = set()
HOST = 'localhost'

def get_port():
    """Get port from environment variable or default to 5001"""
    return int(os.getenv('PORT', 5001))

def get_base_url():
    """Get base URL using current port"""
    return f'http://{HOST}:{get_port()}'

# seconds between heartbeats to tracker
HEARTBEAT_INTERVAL = 30
TRACKER_URL = 'http://localhost:6000'
mining_params = {
    "difficulty": 1,
    "target_block_time": 60,
    "adjustment_interval": 10,
    "time_tolerance": 0.1
}

# Create logger with port information
client_logger = None

@app.route('/new_block', methods=['POST'])
def receive_block():
    """
    Receive and validate new block from peers.
    Handles chain synchronization and fork resolution.
    
    Returns:
        JSON response with status and reason if rejected
    """
    block_data = request.get_json()
    client_logger.info(f"Received new block from peer")

    try:
        new_block = Block.from_dict(block_data)
    except Exception as e:
        client_logger.error(f"Invalid block format: {e}")
        return jsonify({'status': 'rejected', 'reason': f'invalid_format: {e}'}), 400

    latest_block = blockchain.get_latest_block()
    if new_block.previous_hash != latest_block.hash:
        client_logger.warning(f"Previous hash mismatch. Expected: {latest_block.hash}, Got: {new_block.previous_hash}")
        # Handle forks by fetching chains from peers
        for peer in peers:
            if peer == get_base_url():
                continue
            try:
                resp = requests.get(f"{peer}/chain", timeout=5)
                data = resp.json()
                other_chain = Blockchain.from_dict(data)
                
                temp_block = new_block
                
                if other_chain.is_chain_valid() and len(other_chain.chain) > len(blockchain.chain):
                    blockchain.chain = other_chain.chain
                    client_logger.info(f"Replaced local chain with longer one from {peer}")
                    if temp_block.previous_hash == blockchain.get_latest_block().hash:
                        blockchain.chain.append(temp_block)
                        client_logger.info(f"New block added: {temp_block.hash}")
                        return jsonify({'status': 'accepted'}), 200
                
                elif other_chain.is_chain_valid() and len(other_chain.chain) == len(blockchain.chain):
                    current_work = sum(int(block.hash, 16) for block in blockchain.chain)
                    other_work = sum(int(block.hash, 16) for block in other_chain.chain)
                    
                    if other_work < current_work:
                        blockchain.chain = other_chain.chain
                        client_logger.info(f"Replaced local chain with one of equal length but greater work from {peer}")
                        if temp_block.previous_hash == blockchain.get_latest_block().hash:
                            blockchain.chain.append(temp_block)
                            client_logger.info(f"New block added: {temp_block.hash}")
                            return jsonify({'status': 'accepted'}), 200
                            
            except Exception as e:
                client_logger.warning(f"Failed to sync with {peer}: {e}")
                continue
        return jsonify({'status': 'rejected', 'reason': 'previous_hash_mismatch'}), 400

    # Validate proof of work
    prefix = '0' * blockchain.difficulty
    if not new_block.hash.startswith(prefix):
        client_logger.warning(f"Invalid proof of work. Hash: {new_block.hash}, Required prefix: {prefix}")
        return jsonify({'status': 'rejected', 'reason': 'invalid_proof_of_work'}), 400

    # Validate hash integrity
    if new_block.hash != new_block.calculate_hash():
        client_logger.warning(f"Hash mismatch. Calculated: {new_block.calculate_hash()}, Received: {new_block.hash}")
        return jsonify({'status': 'rejected', 'reason': 'hash_mismatch'}), 400

    blockchain.chain.append(new_block)
    client_logger.info(f"New block added: {new_block.hash}")
    return jsonify({'status': 'accepted'}), 200

@app.route('/transaction', methods=['POST'])
def new_transaction():
    """
    Add new transaction to pending transactions.
    
    Returns:
        JSON response with status
    """
    data = request.get_json()
    if not data:
        client_logger.error("No transaction data provided")
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    blockchain.add_transaction(data)
    client_logger.info(f"Added transaction: {data}")
    return jsonify({'status': 'success', 'message': 'Transaction added'}), 200

@app.route('/mine', methods=['POST'])
def mine():
    """
    Mine pending transactions into new block.
    
    Returns:
        JSON response with mined block or error
    """
    try:
        # Sync chain before mining
        sync_chain()
        new_block = blockchain.mine_pending_transactions()
        if not new_block:
            client_logger.warning("No transactions to mine")
            return jsonify({'status': 'error', 'message': 'No transactions to mine'}), 400
            
        client_logger.info(f"Starting to mine block #{new_block.index}")
        # After mining locally, broadcast to peers
        for peer in peers:
            if peer == get_base_url():
                continue
            try:
                requests.post(f"{peer}/new_block", json=new_block.to_dict())
                client_logger.debug(f"Block broadcasted to {peer}")
            except Exception as e:
                client_logger.warning(f"Failed to broadcast to {peer}: {str(e)}")
        client_logger.info(f"Mined new block: {new_block.hash}")
        return jsonify({'status': 'success', 'block': new_block.to_dict()}), 200
    except Exception as e:
        client_logger.error(f"Error mining block: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Get current blockchain.
    
    Returns:
        JSON response with blockchain data
    """
    client_logger.debug("Chain requested")
    return jsonify(blockchain.to_dict()), 200

@app.route('/mining_params', methods=['GET', 'POST'])
def mining_params_endpoint():
    """
    Get or update mining parameters.
    
    Returns:
        JSON response with current or updated parameters
    """
    if request.method == 'GET':
        client_logger.debug("Mining parameters requested")
        return jsonify(mining_params), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            if 'difficulty' in data:
                difficulty = int(data['difficulty'])
                if 1 <= difficulty <= 10:
                    mining_params['difficulty'] = difficulty
                else:
                    client_logger.warning(f"Invalid difficulty value: {difficulty}")
                    return jsonify({'status': 'error', 'message': 'Difficulty must be between 1 and 10'}), 400
            
            if 'target_block_time' in data:
                target_time = float(data['target_block_time'])
                if target_time > 0:
                    mining_params['target_block_time'] = target_time
                else:
                    client_logger.warning(f"Invalid target block time: {target_time}")
                    return jsonify({'status': 'error', 'message': 'Target block time must be positive'}), 400
            
            if 'adjustment_interval' in data:
                interval = int(data['adjustment_interval'])
                if interval > 0:
                    mining_params['adjustment_interval'] = interval
                else:
                    client_logger.warning(f"Invalid adjustment interval: {interval}")
                    return jsonify({'status': 'error', 'message': 'Adjustment interval must be positive'}), 400
            
            if 'time_tolerance' in data:
                tolerance = float(data['time_tolerance'])
                if 0.01 <= tolerance <= 0.5:
                    mining_params['time_tolerance'] = tolerance
                else:
                    client_logger.warning(f"Invalid time tolerance: {tolerance}")
                    return jsonify({'status': 'error', 'message': 'Time tolerance must be between 0.01 and 0.5'}), 400
            
            client_logger.info(f"Mining parameters updated: {mining_params}")
            return jsonify({
                'status': 'success',
                'message': 'Mining parameters updated',
                'current_params': mining_params
            }), 200
            
        except (ValueError, TypeError) as e:
            client_logger.error(f"Invalid parameter value: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Invalid parameter value: {str(e)}'}), 400

@app.route('/peers', methods=['GET'])
def get_peers():
    """
    Get list of all peers.
    
    Returns:
        JSON response with list of peers
    """
    client_logger.debug("Peers list requested")
    return jsonify({'peers': list(peers)}), 200

def broadcast_block(block):
    """
    Broadcast new block to all peers.
    
    Args:
        block: Block to broadcast
    """
    payload = block.to_dict()
    for peer in peers:
        if peer == get_base_url():
            continue
        try:
            requests.post(f"{peer}/new_block", json=payload, timeout=3)
            client_logger.debug(f"Block broadcasted to {peer}")
        except Exception as e:
            client_logger.warning(f"Failed to broadcast to {peer}: {e}")

def run_server():
    """
    Start Flask server.
    """
    if not register_with_tracker():
        client_logger.error("Failed to register with tracker, exiting")
        return

    # Start background threads
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=periodic_sync, daemon=True).start()

    client_logger.info("Starting client server...")
    app.run(host='0.0.0.0', port=get_port())

def register_with_tracker():
    """
    Register with tracker server and sync blockchain.
    """
    try:
        response = requests.post(
            f"{TRACKER_URL}/register",
            json={
                "address": get_base_url()
            }
        )
        if response.status_code == 200:
            client_logger.info("Successfully registered with tracker")
            peers.clear()
            peers.update(response.json()['peers'])
            print("Registered with tracker. Peers:", peers)
            
            if peers:
                client_logger.info("Syncing blockchain with peers...")
                sync_chain()
            return True
        else:
            client_logger.error(f"Failed to register with tracker: {response.text}")
            return False
    except Exception as e:
        client_logger.error(f"Error registering with tracker: {str(e)}")
        return False

def sync_chain():
    """
    Synchronize blockchain with peers.
    Updates to longest valid chain.
    
    Returns:
        bool: True if chain was updated, False otherwise
    """
    client_logger.info("Starting chain synchronization...")
    client_logger.info(f"Current peers: {peers}")
    client_logger.info(f"Current chain length: {len(blockchain.chain)}")
    
    longest_chain = None
    max_length = len(blockchain.chain)
    max_work = blockchain.calculate_work()
    
    for peer in peers:
        if peer == get_base_url():
            continue
        try:
            client_logger.info(f"Attempting to sync with peer: {peer}")
            resp = requests.get(f"{peer}/chain", timeout=5)
            data = resp.json()
            other_chain = Blockchain.from_dict(data)
            
            if other_chain.is_chain_valid():
                peer_length = len(other_chain.chain)
                peer_work = other_chain.calculate_work()
                client_logger.info(f"Peer {peer} chain length: {peer_length}, work: {peer_work}")
                
                if peer_length > max_length or (peer_length == max_length and peer_work > max_work):
                    longest_chain = other_chain
                    max_length = peer_length
                    max_work = peer_work
                    client_logger.info(f"Found longer valid chain from {peer}")
            else:
                client_logger.warning(f"Invalid chain received from {peer}")
                    
        except Exception as e:
            client_logger.warning(f"Failed to sync with {peer}: {e}")
            continue
    
    if longest_chain:
        blockchain.chain = longest_chain.chain
        client_logger.info(f"Successfully synced blockchain. New length: {len(blockchain.chain)}")
        return True
    else:
        client_logger.info("No valid longer chain found during sync")
        return False

def send_heartbeat():
    """
    Send periodic heartbeat to tracker.
    Updates peer list.
    """
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        try:
            response = requests.post(
                f"{TRACKER_URL}/heartbeat",
                json={
                    "address": get_base_url()
                },
                timeout=5
            )
            if response.status_code != 200:
                client_logger.warning("Heartbeat failed, attempting to re-register")
                register_with_tracker()
            else:
                peers.clear()
                peers.update(response.json()['peers'])
        except Exception as e:
            client_logger.error(f"Heartbeat error: {e}")

def periodic_sync():
    """
    Periodically sync blockchain with peers.
    """
    while True:
        time.sleep(10)
        sync_chain()

@app.route('/edit_block', methods=['POST'])
def edit_block():
    """
    Edit block content for testing purposes.
    
    Request body:
    {
        "block_index": int,  # Index of block to edit
        "transaction_index": int,  # Index of transaction to modify
        "field": str,  # Field to modify in transaction
        "new_value": any  # New value to set
    }
    
    Returns:
        JSON response with status and modified block
    """
    data = request.get_json()
    if not data or 'block_index' not in data or 'transaction_index' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
    block_index = data['block_index']
    tx_index = data['transaction_index']
    
    if block_index >= len(blockchain.chain):
        return jsonify({'status': 'error', 'message': 'Block index out of range'}), 400
        
    block = blockchain.chain[block_index]
    try:
        original_tx, original_merkle = block.edit_transaction(
            tx_index=tx_index,
            field=data.get('field'),
            new_value=data.get('new_value'),
            new_transaction=data.get('new_transaction')
        )
        
        client_logger.info(f"Block {block_index} transaction {tx_index} edited")
        return jsonify({
            'status': 'success',
            'message': 'Block edited successfully',
            'block': block.to_dict(),
            'original_transaction': original_tx,
            'original_merkle_root': original_merkle
        }), 200
    except IndexError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/verify_block', methods=['GET'])
def verify_block():
    """
    Verify block integrity using Merkle tree and locate modified transactions.
    
    Query parameters:
    - block_index: int (optional, defaults to latest block)
    
    Returns:
        JSON response with verification results and modified transaction indices
    """
    block_index = request.args.get('block_index', type=int)
    if block_index is None:
        block_index = len(blockchain.chain) - 1
        
    if block_index >= len(blockchain.chain):
        return jsonify({'status': 'error', 'message': 'Block index out of range'}), 400
        
    block = blockchain.chain[block_index]
    
    verification = block.verify_integrity()
    
    return jsonify({
        'status': 'success',
        'block_index': block_index,
        'is_hash_valid': verification['is_hash_valid'],
        'is_merkle_valid': verification['is_merkle_valid'],
        'current_merkle_root': verification['current_merkle_root'],
        'stored_merkle_root': block.merkle_root,
        'modified_transaction_indices': verification['modified_indices'],
        'block': block.to_dict()
    }), 200

def main():
    """
    Main function to start client node.
    Handles server startup, registration, and CLI interface.
    """
    global client_logger
    client_logger = setup_logger('client', 'logs/client', port=get_port())
    
    # Start HTTP server
    run_server()
    
    # Start periodic sync thread
    sync_thread = threading.Thread(target=periodic_sync, daemon=True)
    sync_thread.start()
    
    # Start heartbeat thread
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    # CLI loop
    while True:
        cmd = input("\nCommands: add_tx | mine | list_peers | show_chain | set_params | exit\nEnter command: ").strip().lower()
        if cmd == 'add_tx':
            tx_str = input("Transaction JSON: ")
            try:
                tx = json.loads(tx_str)
                blockchain.add_transaction(tx)
                client_logger.info("Transaction added via CLI")
                print("Transaction added.")
            except json.JSONDecodeError:
                client_logger.error("Invalid JSON in transaction input")
                print("Invalid JSON.")
        elif cmd == 'mine':
            try:
                resp = requests.post(f"{get_base_url()}/mine", timeout=10).json()
                client_logger.info("Block mined via CLI")
                print("Mined and broadcast block:", resp.get('block'))
            except Exception as e:
                client_logger.error(f"Mining error: {e}")
                print(f"Mining error: {e}")
        elif cmd == 'list_peers':
            client_logger.debug("Peers list requested via CLI")
            print("Peers:", peers)
        elif cmd == 'show_chain':
            chain = blockchain.to_dict()['chain']
            client_logger.debug("Chain displayed via CLI")
            print(f"Chain length: {len(chain)}")
            for b in chain:
                print(f"Block #{b['index']} hash={b['hash']}")
        elif cmd == 'set_params':
            try:
                resp = requests.get(f"{get_base_url()}/mining_params")
                current_params = resp.json()
                client_logger.debug("Mining parameters displayed via CLI")
                print("\nCurrent mining parameters:")
                print(f"Difficulty: {current_params['difficulty']} (1-10)")
                print(f"Target block time: {current_params['target_block_time']} seconds")
                print(f"Adjustment interval: {current_params['adjustment_interval']} blocks")
                print(f"Time tolerance: {current_params['time_tolerance']} (0.01-0.5)")
                
                new_params = {}
                difficulty = input("New difficulty (press Enter to keep current): ")
                if difficulty:
                    new_params['difficulty'] = int(difficulty)
                
                target_time = input("New target block time (press Enter to keep current): ")
                if target_time:
                    new_params['target_block_time'] = float(target_time)
                
                interval = input("New adjustment interval (press Enter to keep current): ")
                if interval:
                    new_params['adjustment_interval'] = int(interval)
                
                tolerance = input("New time tolerance (press Enter to keep current): ")
                if tolerance:
                    new_params['time_tolerance'] = float(tolerance)
                
                if new_params:
                    resp = requests.post(f"{get_base_url()}/mining_params", json=new_params)
                    client_logger.info(f"Mining parameters updated via CLI: {new_params}")
                    print("\nUpdate result:", resp.json())
                else:
                    client_logger.debug("No mining parameters changed via CLI")
                    print("No parameters changed.")
                    
            except Exception as e:
                client_logger.error(f"Error setting parameters: {e}")
                print(f"Error setting parameters: {e}")
        elif cmd == 'exit':
            try:
                requests.post(f"{TRACKER_URL}/unregister", json={'address': get_base_url()}, timeout=5)
                client_logger.info("Client unregistered from tracker")
            except:
                client_logger.error("Failed to unregister from tracker")
                pass
            break
        else:
            client_logger.warning(f"Unknown command: {cmd}")
            print("Unknown command.")

if __name__ == '__main__':
    main()
