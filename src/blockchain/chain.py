from typing import List, Dict, Any
from .block import Block
import time

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = 4  # 初始难度
        self.target_block_time = 10  # 目标区块生成时间（秒）
        self.block_times = []  # 记录最近区块的生成时间
        self.adjustment_interval = 10  # 每10个区块调整一次难度
        self.time_tolerance = 0.1  # 误差限幅（10%）
        
        # 创建创世块
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        # Use fixed timestamp for deterministic genesis across all nodes
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

    def adjust_difficulty(self):
        """动态调整挖矿难度"""
        if len(self.block_times) < self.adjustment_interval:
            return
            
        # 计算最近N个区块的平均生成时间
        avg_time = sum(self.block_times[-self.adjustment_interval:]) / self.adjustment_interval
        
        # 如果平均时间大于目标时间，降低难度
        if avg_time > self.target_block_time * (1 + self.time_tolerance):
            self.difficulty = max(1, self.difficulty - 1)
            print(f"Difficulty decreased to {self.difficulty}")
        # 如果平均时间小于目标时间，增加难度
        elif avg_time < self.target_block_time * (1 - self.time_tolerance):
            self.difficulty += 1
            print(f"Difficulty increased to {self.difficulty}")
            
        # 清空时间记录，开始新的调整周期
        self.block_times = []

    def mine_pending_transactions(self) -> Block:
        if not self.pending_transactions:
            raise ValueError("No pending transactions to mine")

        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            transactions=self.pending_transactions,
            timestamp=time.time(),  # use current time for new blocks
            previous_hash=latest_block.hash,
            difficulty=self.difficulty
        )

        # 记录挖矿开始时间
        start_time = time.time()
        
        # 挖矿
        new_block.mine_block()
        
        # 记录区块生成时间
        block_time = time.time() - start_time
        self.block_times.append(block_time)
        
        # 调整难度
        self.adjust_difficulty()

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

            # 验证工作量证明
            prefix = '0' * self.difficulty
            if not current_block.hash.startswith(prefix):
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "difficulty": self.difficulty,
            "target_block_time": self.target_block_time,
            "adjustment_interval": self.adjustment_interval,
            "time_tolerance": self.time_tolerance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blockchain':
        blockchain = cls()
        # Overwrite the auto-created genesis and subsequent blocks
        blockchain.chain = [Block.from_dict(block_data) for block_data in data['chain']]
        blockchain.pending_transactions = data['pending_transactions']
        blockchain.difficulty = data['difficulty']
        blockchain.target_block_time = data['target_block_time']
        blockchain.adjustment_interval = data['adjustment_interval']
        blockchain.time_tolerance = data['time_tolerance']
        return blockchain