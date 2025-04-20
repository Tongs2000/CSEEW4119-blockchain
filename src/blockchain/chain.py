from typing import List, Dict, Any
import time
from .block import Block

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = 2
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0" * 64,
            difficulty=self.difficulty
        )
        genesis_block.mine_block()
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self) -> Block:
        if not self.pending_transactions:
            raise ValueError("No pending transactions to mine")

        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            transactions=self.pending_transactions,
            timestamp=time.time(),
            previous_hash=latest_block.hash,
            difficulty=self.difficulty
        )
        new_block.mine_block()
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "difficulty": self.difficulty
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blockchain':
        blockchain = cls()
        blockchain.chain = [Block.from_dict(block_data) for block_data in data['chain']]
        blockchain.pending_transactions = data['pending_transactions']
        blockchain.difficulty = data['difficulty']
        return blockchain 