from flask import Flask, request, jsonify
from src.blockchain.chain import Blockchain
from src.blockchain.block import Block
import threading, requests, json, time, os

app = Flask(__name__)
# Blockchain now uses a deterministic genesis block
blockchain = Blockchain()
peers = []  # List of peer addresses, populated from tracker
HOST = 'localhost'
PORT = int(os.getenv('PORT', 5001))  # 从环境变量读取端口，默认5001
BASE_URL = f'http://{HOST}:{PORT}'
HEARTBEAT_INTERVAL = 30  # seconds between heartbeats to tracker
TRACKER_URL = 'http://localhost:6000'

@app.route('/new_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()

    try:
        new_block = Block.from_dict(block_data)
    except Exception as e:
        print(f"Invalid block format: {e}")
        return jsonify({'status': 'rejected', 'reason': f'invalid_format: {e}'}), 400

    latest_block = blockchain.get_latest_block()
    if new_block.previous_hash != latest_block.hash:
        print(f"Previous hash mismatch. Expected: {latest_block.hash}, Got: {new_block.previous_hash}")
        # Handle forks by fetching chains from peers
        for peer in peers:
            if peer == BASE_URL:
                continue
            try:
                resp = requests.get(f"{peer}/chain", timeout=5)
                data = resp.json()
                other_chain = Blockchain.from_dict(data)
                
                # 保存新区块
                temp_block = new_block
                
                # 如果找到更长的链，直接接受
                if other_chain.is_chain_valid() and len(other_chain.chain) > len(blockchain.chain):
                    blockchain.chain = other_chain.chain
                    print(f"Replaced local chain with longer one from {peer}")
                    # 尝试将新区块链接到新链
                    if temp_block.previous_hash == blockchain.get_latest_block().hash:
                        blockchain.chain.append(temp_block)
                        return jsonify({'status': 'accepted'}), 200
                
                # 如果链长度相同，比较工作量
                elif other_chain.is_chain_valid() and len(other_chain.chain) == len(blockchain.chain):
                    # 计算两条链的总工作量（哈希值之和）
                    current_work = sum(int(block.hash, 16) for block in blockchain.chain)
                    other_work = sum(int(block.hash, 16) for block in other_chain.chain)
                    
                    # 如果其他链的工作量更大（哈希值之和更小），接受它
                    if other_work < current_work:
                        blockchain.chain = other_chain.chain
                        print(f"Replaced local chain with one of equal length but greater work from {peer}")
                        # 尝试将新区块链接到新链
                        if temp_block.previous_hash == blockchain.get_latest_block().hash:
                            blockchain.chain.append(temp_block)
                            return jsonify({'status': 'accepted'}), 200
                            
            except Exception as e:
                print(f"Failed to sync with {peer}: {e}")
                continue
        return jsonify({'status': 'rejected', 'reason': 'previous_hash_mismatch'}), 400

    # Validate proof of work
    prefix = '0' * blockchain.difficulty
    if not new_block.hash.startswith(prefix):
        print(f"Invalid proof of work. Hash: {new_block.hash}, Required prefix: {prefix}")
        return jsonify({'status': 'rejected', 'reason': 'invalid_proof_of_work'}), 400

    # Validate hash integrity
    if new_block.hash != new_block.calculate_hash():
        print(f"Hash mismatch. Calculated: {new_block.calculate_hash()}, Received: {new_block.hash}")
        return jsonify({'status': 'rejected', 'reason': 'hash_mismatch'}), 400

    blockchain.chain.append(new_block)
    return jsonify({'status': 'accepted'}), 200

@app.route('/transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    blockchain.add_transaction(data)
    return jsonify({'status': 'success', 'message': 'Transaction added'}), 200

@app.route('/mine', methods=['POST'])
def mine():
    try:
        new_block = blockchain.mine_pending_transactions()
        # After mining locally, broadcast to peers
        threading.Thread(target=broadcast_block, args=(new_block,)).start()
        return jsonify({'status': 'success', 'block': new_block.to_dict()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.to_dict()), 200

@app.route('/mining_params', methods=['GET', 'POST'])
def mining_params():
    if request.method == 'GET':
        return jsonify({
            'difficulty': blockchain.difficulty,
            'target_block_time': blockchain.target_block_time,
            'adjustment_interval': blockchain.adjustment_interval,
            'time_tolerance': blockchain.time_tolerance,
            'min_difficulty': 1,
            'max_difficulty': 10,
            'min_tolerance': 0.01,
            'max_tolerance': 0.5
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            # 验证并设置参数
            if 'difficulty' in data:
                difficulty = int(data['difficulty'])
                if 1 <= difficulty <= 10:
                    blockchain.difficulty = difficulty
                else:
                    return jsonify({'status': 'error', 'message': 'Difficulty must be between 1 and 10'}), 400
            
            if 'target_block_time' in data:
                target_time = float(data['target_block_time'])
                if target_time > 0:
                    blockchain.target_block_time = target_time
                else:
                    return jsonify({'status': 'error', 'message': 'Target block time must be positive'}), 400
            
            if 'adjustment_interval' in data:
                interval = int(data['adjustment_interval'])
                if interval > 0:
                    blockchain.adjustment_interval = interval
                else:
                    return jsonify({'status': 'error', 'message': 'Adjustment interval must be positive'}), 400
            
            if 'time_tolerance' in data:
                tolerance = float(data['time_tolerance'])
                if 0.01 <= tolerance <= 0.5:
                    blockchain.time_tolerance = tolerance
                else:
                    return jsonify({'status': 'error', 'message': 'Time tolerance must be between 0.01 and 0.5'}), 400
            
            return jsonify({
                'status': 'success',
                'message': 'Mining parameters updated',
                'current_params': {
                    'difficulty': blockchain.difficulty,
                    'target_block_time': blockchain.target_block_time,
                    'adjustment_interval': blockchain.adjustment_interval,
                    'time_tolerance': blockchain.time_tolerance
                }
            }), 200
            
        except (ValueError, TypeError) as e:
            return jsonify({'status': 'error', 'message': f'Invalid parameter value: {str(e)}'}), 400

def broadcast_block(block):
    payload = block.to_dict()
    for peer in peers:
        if peer == BASE_URL:
            continue
        try:
            resp = requests.post(f"{peer}/new_block", json=payload, timeout=3)
            status = resp.json().get('status')
            print(f"Broadcast to {peer}: {status}")
        except Exception as e:
            print(f"Failed to broadcast to {peer}: {e}")

def run_server():
    app.run(host='0.0.0.0', port=PORT)

def register_with_tracker():
    try:
        resp = requests.post(
            f"{TRACKER_URL}/register",
            json={'address': BASE_URL},
            timeout=5
        )
        data = resp.json()
        if resp.status_code == 200 and 'peers' in data:
            peers.clear()
            peers.extend(data['peers'])
            print("Registered with tracker. Peers:", peers)
            
            # 注册后立即同步区块链
            if peers:  # 如果有其他节点
                print("Syncing blockchain with peers...")
                sync_chain()
        else:
            print("Registration failed or invalid response.")
    except Exception as e:
        print(f"Error registering with tracker: {e}")

def sync_chain():
    """同步区块链数据"""
    longest_chain = None
    max_length = len(blockchain.chain)
    
    for peer in peers:
        if peer == BASE_URL:
            continue
        try:
            resp = requests.get(f"{peer}/chain", timeout=5)
            data = resp.json()
            other_chain = Blockchain.from_dict(data)
            
            if other_chain.is_chain_valid():
                if len(other_chain.chain) > max_length:
                    max_length = len(other_chain.chain)
                    longest_chain = other_chain
                elif len(other_chain.chain) == max_length:
                    # 如果长度相同，比较工作量
                    current_work = sum(int(block.hash, 16) for block in blockchain.chain)
                    other_work = sum(int(block.hash, 16) for block in other_chain.chain)
                    if other_work < current_work:
                        longest_chain = other_chain
                        
        except Exception as e:
            print(f"Failed to sync with {peer}: {e}")
            continue
    
    if longest_chain:
        blockchain.chain = longest_chain.chain
        print(f"Successfully synced blockchain. New length: {len(blockchain.chain)}")
    else:
        print("No valid longer chain found during sync")

def send_heartbeat():
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        try:
            resp = requests.post(
                f"{TRACKER_URL}/heartbeat",
                json={'address': BASE_URL},
                timeout=5
            )
            data = resp.json()
            if resp.status_code == 200 and 'peers' in data:
                peers.clear()
                peers.extend(data['peers'])
                print("Heartbeat OK. Peers updated:", peers)
            else:
                print("Heartbeat rejected.")
        except Exception as e:
            print(f"Heartbeat error: {e}")

def main():
    # Start HTTP server
    server = threading.Thread(target=run_server)
    server.daemon = True
    server.start()

    # Register and begin heartbeats
    register_with_tracker()
    hb = threading.Thread(target=send_heartbeat)
    hb.daemon = True
    hb.start()

    # CLI loop
    while True:
        cmd = input("\nCommands: add_tx | mine | list_peers | show_chain | set_params | exit\nEnter command: ").strip().lower()
        if cmd == 'add_tx':
            tx_str = input("Transaction JSON: ")
            try:
                tx = json.loads(tx_str)
                blockchain.add_transaction(tx)
                print("Transaction added.")
            except json.JSONDecodeError:
                print("Invalid JSON.")
        elif cmd == 'mine':
            try:
                resp = requests.post(f"{BASE_URL}/mine", timeout=10).json()
                print("Mined and broadcast block:", resp.get('block'))
            except Exception as e:
                print(f"Mining error: {e}")
        elif cmd == 'list_peers':
            print("Peers:", peers)
        elif cmd == 'show_chain':
            chain = blockchain.to_dict()['chain']
            print(f"Chain length: {len(chain)}")
            for b in chain:
                print(f"Block #{b['index']} hash={b['hash']}")
        elif cmd == 'set_params':
            try:
                # 获取当前参数
                resp = requests.get(f"{BASE_URL}/mining_params")
                current_params = resp.json()
                print("\nCurrent mining parameters:")
                print(f"Difficulty: {current_params['difficulty']} (1-10)")
                print(f"Target block time: {current_params['target_block_time']} seconds")
                print(f"Adjustment interval: {current_params['adjustment_interval']} blocks")
                print(f"Time tolerance: {current_params['time_tolerance']} (0.01-0.5)")
                
                # 获取新参数
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
                
                # 发送更新请求
                if new_params:
                    resp = requests.post(f"{BASE_URL}/mining_params", json=new_params)
                    print("\nUpdate result:", resp.json())
                else:
                    print("No parameters changed.")
                    
            except Exception as e:
                print(f"Error setting parameters: {e}")
        elif cmd == 'exit':
            try:
                requests.post(f"{TRACKER_URL}/unregister", json={'address': BASE_URL}, timeout=5)
            except:
                pass
            break
        else:
            print("Unknown command.")

if __name__ == '__main__':
    main()
