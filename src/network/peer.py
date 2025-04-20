import requests
import threading
import time
from typing import List, Dict, Any
from ..blockchain.chain import Blockchain
from ..blockchain.block import Block

class Peer:
    def __init__(self, tracker_url: str, port: int):
        self.tracker_url = tracker_url
        self.port = port
        self.address = f"http://localhost:{port}"
        self.blockchain = Blockchain()
        self.peers: List[str] = []
        self.running = True

    def register_with_tracker(self) -> None:
        try:
            response = requests.post(
                f"{self.tracker_url}/register",
                json={"address": self.address}
            )
            if response.status_code == 200:
                print("Successfully registered with tracker")
            else:
                print("Failed to register with tracker")
        except Exception as e:
            print(f"Error registering with tracker: {e}")

    def unregister_with_tracker(self) -> None:
        try:
            response = requests.post(
                f"{self.tracker_url}/unregister",
                json={"address": self.address}
            )
            if response.status_code == 200:
                print("Successfully unregistered with tracker")
            else:
                print("Failed to unregister with tracker")
        except Exception as e:
            print(f"Error unregistering with tracker: {e}")

    def update_peer_list(self) -> None:
        try:
            response = requests.get(f"{self.tracker_url}/peers")
            if response.status_code == 200:
                data = response.json()
                self.peers = [peer for peer in data['peers'] if peer != self.address]
        except Exception as e:
            print(f"Error updating peer list: {e}")

    def broadcast_block(self, block: Block) -> None:
        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/new_block",
                    json=block.to_dict()
                )
            except Exception as e:
                print(f"Error broadcasting block to {peer}: {e}")

    def handle_new_block(self, block_data: Dict[str, Any]) -> None:
        new_block = Block.from_dict(block_data)
        latest_block = self.blockchain.get_latest_block()

        if new_block.index > latest_block.index:
            if new_block.previous_hash == latest_block.hash:
                self.blockchain.chain.append(new_block)
            else:
                # Handle fork
                self.resolve_conflicts()
        elif new_block.index == latest_block.index:
            # Another block was mined at the same time
            if new_block.timestamp < latest_block.timestamp:
                self.blockchain.chain[-1] = new_block

    def resolve_conflicts(self) -> None:
        max_length = len(self.blockchain.chain)
        new_chain = None

        for peer in self.peers:
            try:
                response = requests.get(f"{peer}/chain")
                if response.status_code == 200:
                    peer_chain = response.json()
                    if len(peer_chain) > max_length and self.blockchain.is_chain_valid():
                        max_length = len(peer_chain)
                        new_chain = peer_chain
            except Exception as e:
                print(f"Error resolving conflicts with {peer}: {e}")

        if new_chain:
            self.blockchain = Blockchain.from_dict(new_chain)

    def start(self) -> None:
        self.register_with_tracker()
        
        # Start peer list update thread
        threading.Thread(target=self._update_peer_list_loop, daemon=True).start()
        
        # Start mining thread
        threading.Thread(target=self._mining_loop, daemon=True).start()

    def _update_peer_list_loop(self) -> None:
        while self.running:
            self.update_peer_list()
            time.sleep(30)  # Update every 30 seconds

    def _mining_loop(self) -> None:
        while self.running:
            if self.blockchain.pending_transactions:
                try:
                    new_block = self.blockchain.mine_pending_transactions()
                    self.broadcast_block(new_block)
                except Exception as e:
                    print(f"Error mining block: {e}")
            time.sleep(1)

    def stop(self) -> None:
        self.running = False
        self.unregister_with_tracker() 