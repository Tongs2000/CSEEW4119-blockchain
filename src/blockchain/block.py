import hashlib
import json
import time
from typing import List, Dict, Any, Tuple

def hash_pair(a: str, b: str) -> str:
    """
    Calculate combined hash of two hash values.
    
    Args:
        a: First hash string
        b: Second hash string
    
    Returns:
        Combined hash string
    """
    return hashlib.sha256((a + b).encode()).hexdigest()

def compute_merkle_root(tx_hashes: List[str]) -> str:
    """
    Calculate Merkle root hash from transaction hashes.
    
    Args:
        tx_hashes: List of transaction hash strings
    
    Returns:
        Merkle root hash string
    """
    if not tx_hashes:
        return '0' * 64
    if len(tx_hashes) == 1:
        return tx_hashes[0]
    
    new_level = []
    for i in range(0, len(tx_hashes), 2):
        left = tx_hashes[i]
        right = tx_hashes[i+1] if i+1 < len(tx_hashes) else left
        new_level.append(hash_pair(left, right))
    return compute_merkle_root(new_level)

class Block:
    """
    Block class representing a block in the blockchain.
    Contains transactions, timestamp, and cryptographic hashes.
    """
    
    def __init__(self, index: int, transactions: List[Dict[str, Any]], 
                 previous_hash: str, timestamp: float = None, difficulty: int = 2):
        """
        Initialize a new block.
        
        Args:
            index: Block index in the chain
            transactions: List of transaction dictionaries
            previous_hash: Hash of the previous block
            timestamp: Block creation timestamp
            difficulty: Mining difficulty level
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.calculate_hash()

    def compute_merkle_root(self) -> str:
        """Compute Merkle root from transaction hashes"""
        if not self.transactions:
            return "0" * 64  # Empty block hash
            
        tx_hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
            for tx in self.transactions
        ]
        return compute_merkle_root(tx_hashes)

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self) -> None:
        """
        Mine block by finding nonce that satisfies difficulty requirement.
        Updates block hash and nonce.
        """
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def edit_transaction(self, tx_index: int, field: str = None, new_value: Any = None, new_transaction: Dict[str, Any] = None) -> tuple:
        """
        Edit a transaction in the block.
        
        Args:
            tx_index: Index of transaction to edit
            field: Field to modify (optional)
            new_value: New value for the field (optional)
            new_transaction: New transaction to replace (optional)
            
        Returns:
            tuple: (original_transaction, original_merkle_root)
        """
        if tx_index >= len(self.transactions):
            raise IndexError("Transaction index out of range")
            
        # Store original values
        original_tx = self.transactions[tx_index].copy()
        original_merkle = self.merkle_root
        
        # Modify transaction
        if field is not None and new_value is not None:
            self.transactions[tx_index][field] = new_value
        elif new_transaction is not None:
            self.transactions[tx_index] = new_transaction
            
        # Update block hash and merkle root
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.calculate_hash()
        
        return original_tx, original_merkle

    def verify_self(self) -> Dict[str, Any]:
        """
        Verify the internal integrity of this block:
        - Check that merkle_root matches the hash of transactions
        - Check that hash matches the block header (including merkle_root)
        Returns a dict containing:
        - merkle_ok: whether the stored merkle_root is correct
        - hash_ok: whether the stored hash is correct
        - expected_merkle_root: the merkle root recomputed from transactions
        - expected_hash: the hash recomputed from block header
        """
        expected_merkle = self.compute_merkle_root()
        expected_hash   = self.calculate_hash()
        return {
            'merkle_ok': self.merkle_root == expected_merkle,
            'hash_ok':   self.hash == expected_hash,
            'expected_merkle_root': expected_merkle,
            'expected_hash': expected_hash
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary format.
        
        Returns:
            Dictionary containing block data
        """
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "merkle_root": self.merkle_root
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create block instance from dictionary.
        
        Args:
            data: Dictionary containing block data
            
        Returns:
            Block instance
        """
        block = cls(
            index=data["index"],
            transactions=data["transactions"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            difficulty=data.get("difficulty", 2)
        )
        block.hash = data["hash"]
        block.nonce = data["nonce"]
        block.merkle_root = data.get("merkle_root", '0' * 64)
        return block 

    def verify_transaction(self, tx_index: int) -> Dict[str, Any]:
        """
        Verify if a specific transaction has been modified using Merkle Proof
        
        Args:
            tx_index: Index of the transaction to verify
            
        Returns:
            Dict containing:
            - is_valid: Whether the transaction is valid
            - tx_hash: Current hash of the transaction
            - proof: Merkle proof for verification
            - merkle_root: Current Merkle root
        """
        if tx_index >= len(self.transactions):
            raise IndexError("Transaction index out of range")
            
        # Calculate current transaction hash
        current_tx_hash = hashlib.sha256(
            json.dumps(self.transactions[tx_index], sort_keys=True).encode()
        ).hexdigest()
        
        # Get Merkle proof for this transaction
        proof = self._get_merkle_proof(tx_index)
        
        # Verify using Merkle proof
        computed_root = current_tx_hash
        for sibling_hash, is_right in proof:
            if is_right:
                computed_root = hashlib.sha256((computed_root + sibling_hash).encode()).hexdigest()
            else:
                computed_root = hashlib.sha256((sibling_hash + computed_root).encode()).hexdigest()
        
        return {
            'is_valid': computed_root == self.merkle_root,
            'tx_hash': current_tx_hash,
            'proof': proof,
            'merkle_root': self.merkle_root,
            'computed_root': computed_root,
            'transaction': self.transactions[tx_index]
        }

    def _get_merkle_proof(self, tx_index: int) -> List[Tuple[str, bool]]:
        """
        Get Merkle proof for a specific transaction
        
        Args:
            tx_index: Index of the transaction
            
        Returns:
            List of (hash, is_right) tuples representing the Merkle proof
        """
        # Calculate all transaction hashes
        tx_hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
            for tx in self.transactions
        ]
        
        # Generate Merkle proof
        proof = []
        current_index = tx_index
        
        while len(tx_hashes) > 1:
            if current_index % 2 == 0:
                # Current node is left child
                if current_index + 1 < len(tx_hashes):
                    proof.append((tx_hashes[current_index + 1], True))
            else:
                # Current node is right child
                proof.append((tx_hashes[current_index - 1], False))
            
            # Move up one level
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                left = tx_hashes[i]
                right = tx_hashes[i+1] if i+1 < len(tx_hashes) else left
                new_hashes.append(hash_pair(left, right))
            tx_hashes = new_hashes
            current_index = current_index // 2
        
        return proof 