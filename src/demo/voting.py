import threading
import time
import requests
import os
from src.blockchain.chain import Blockchain

# Configuration
HOST = 'localhost'
PORT = int(os.getenv('PORT', 5001))  # 从环境变量读取端口，默认5001
BASE_URL = f'http://{HOST}:{PORT}'
TRACKER_URL = 'http://localhost:6000'
HEARTBEAT_INTERVAL = 30

# Utility functions

def register_and_start_heartbeat():
    """Register this demo with tracker and start sending heartbeats."""
    try:
        resp = requests.post(f"{TRACKER_URL}/register", json={'address': BASE_URL}, timeout=5)
        resp.raise_for_status()
        print("Registered with tracker.")
    except Exception as e:
        print(f"Failed to register: {e}")

    def heartbeat_loop():
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            try:
                hb = requests.post(f"{TRACKER_URL}/heartbeat", json={'address': BASE_URL}, timeout=5)
                hb.raise_for_status()
                print("Heartbeat sent.")
            except Exception as e:
                print(f"Heartbeat error: {e}")

    threading.Thread(target=heartbeat_loop, daemon=True).start()


def send_vote(voter: str, candidate: str):
    """Send a vote transaction to the client via HTTP POST."""
    tx = {'voter': voter, 'vote_for': candidate}
    try:
        r = requests.post(f"{BASE_URL}/transaction", json=tx, timeout=5)
        r.raise_for_status()
        print(f"Vote recorded: {voter} -> {candidate}")
    except Exception as e:
        print(f"Failed to send vote: {e}")


def trigger_mine():
    """Trigger mining via HTTP POST to the client."""
    try:
        r = requests.post(f"{BASE_URL}/mine", timeout=10)
        r.raise_for_status()
        print(f"Mining result: {r.json()}")
    except Exception as e:
        print(f"Mining failed: {e}")


def tally_votes():
    """Fetch the chain and tally votes."""
    try:
        r = requests.get(f"{BASE_URL}/chain", timeout=5)
        r.raise_for_status()
        data = r.json()
        chain = Blockchain.from_dict(data)
        counts = {}
        for block in chain.chain:
            for tx in block.transactions:
                if 'vote_for' in tx:
                    counts[tx['vote_for']] = counts.get(tx['vote_for'], 0) + 1
        print("Current vote tally:")
        for cand, num in counts.items():
            print(f" - {cand}: {num}")
    except Exception as e:
        print(f"Failed to tally votes: {e}")


def main():
    register_and_start_heartbeat()

    # Example votes
    votes = [
        ('Alice', 'Bob'),
        ('Eve', 'Bob'),
        ('Mallory', 'Alice'),
    ]

    for voter, candidate in votes:
        send_vote(voter, candidate)

    # Give the client some time to collect transactions
    time.sleep(2)

    # Trigger mining
    trigger_mine()

    # Allow time for block broadcast
    time.sleep(2)

    # Tally votes
    tally_votes()

if __name__ == '__main__':
    main()