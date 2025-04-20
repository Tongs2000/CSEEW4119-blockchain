# Blockchain Implementation Design

## 1. System Overview

### 1.1 Project Goals
- Implement a peer-to-peer blockchain network
- Demonstrate blockchain resilience to invalid transactions
- Implement advanced features like Merkle tree and dynamic difficulty adjustment
- Provide block editing and verification capabilities for testing

### 1.2 Network Structure
```
[Client 1] <----> [Tracker] <----> [Client 2] <----> [Client 3]
    |                                    |                |
    |                                    |                |
    v                                    v                v
[Blockchain]                        [Blockchain]     [Blockchain]
```

## 2. Core Components

### 2.1 Tracker Server
- **Registration**: New clients register with the tracker
- **Peer Discovery**: Maintains list of active peers
- **Heartbeat Monitoring**: Tracks client health status (30-second intervals)
- **Cleanup**: Removes inactive clients (60-second intervals)

### 2.2 Client Node
- **Blockchain Management**: Maintains local copy of blockchain
- **Transaction Processing**: Handles new transactions
- **Mining**: Creates new blocks through proof-of-work
- **Network Communication**: Broadcasts new blocks to peers
- **Synchronization**: Keeps blockchain in sync with peers (10-second intervals)
- **Block Editing**: Provides interface for testing block modifications
- **Integrity Verification**: Verifies block integrity using Merkle tree

### 2.3 Blockchain
- **Blocks**: Contain transactions, timestamps, and proof-of-work
- **Merkle Tree**: For transaction integrity verification
- **Consensus**: Longest valid chain rule with work consideration

## 3. Implementation Details

### 3.1 P2P Network Implementation
- **Tracker Protocol**:
  - `/register`: Register new client
  - `/unregister`: Remove client
  - `/heartbeat`: Client status update
  - `/peers`: Get list of active peers

- **Client Protocol**:
  - `/new_block`: Receive and validate new blocks
  - `/transaction`: Add new transaction
  - `/mine`: Create and broadcast new block
  - `/chain`: Get current blockchain
  - `/mining_params`: Configure mining parameters
  - `/edit_block`: Edit block content (for testing)
  - `/verify_block`: Verify block integrity

### 3.2 Blockchain Implementation
- **Block Structure**:
  ```python
  {
    "index": int,
    "previous_hash": str,
    "timestamp": int,
    "transactions": list,
    "merkle_root": str,
    "nonce": int,
    "hash": str
  }
  ```

- **Mining Process**:
  1. Sync with peers before mining
  2. Collect pending transactions
  3. Calculate Merkle root
  4. Find valid nonce through proof-of-work
  5. Create and broadcast new block

- **Difficulty Adjustment**:
  - Target block time: Configurable (default 60 seconds)
  - Adjustment interval: Configurable (default 10 blocks)
  - Time tolerance: Configurable (default 0.1)
  - Range: 1-10 difficulty levels

### 3.3 Block Editing and Verification
- **Block Editing**:
  - Modify specific transaction fields
  - Replace entire transactions
  - Update block hash and Merkle root
  - Preserve original values for verification

- **Integrity Verification**:
  - Block hash validation
  - Merkle root verification
  - Transaction integrity checks
  - Modified transaction detection

## 4. Security and Resilience

### 4.1 Block Validation
- **Hash Verification**: Ensure block hash matches content
- **Merkle Tree Verification**: Validate transaction integrity
- **Chain Validation**: Verify entire blockchain integrity
- **Fork Resolution**: Select longest valid chain

### 4.2 Network Security
- **Peer Authentication**: Validate peer connections
- **Block Broadcasting**: Secure block propagation
- **Chain Synchronization**: Safe chain updates
- **Heartbeat Monitoring**: Track peer health

### 4.3 Testing Capabilities
- **Block Editing**: Simulate malicious modifications
- **Integrity Checks**: Verify detection of modifications
- **Merkle Tree Verification**: Test transaction integrity
- **Chain Validation**: Test blockchain resilience

## 5. Testing and Verification

### 5.1 Network Tests
- Multiple client registration
- Peer discovery and updates
- Heartbeat monitoring
- Cleanup of inactive peers

### 5.2 Blockchain Tests
- Block creation and validation
- Fork resolution
- Chain synchronization
- Merkle tree verification

### 5.3 Application Tests
- Vote transaction processing
- Block mining and broadcasting
- Difficulty adjustment
- Invalid transaction rejection

## 6. CLI Commands

### 6.1 Client Commands
- `add_tx`: Add new transaction
- `mine`: Mine pending transactions
- `list_peers`: Show connected peers
- `show_chain`: Display blockchain
- `set_params`: Configure mining parameters
- `exit`: Shutdown client

### 6.2 Mining Parameters
- **Difficulty**: 1-10 (controls proof-of-work)
- **Target Block Time**: Desired time between blocks
- **Adjustment Interval**: Blocks between difficulty adjustments
- **Time Tolerance**: Allowed deviation from target time

## 7. Error Handling

### 7.1 Network Errors
- Connection timeouts
- Invalid responses
- Peer unavailability

### 7.2 Validation Errors
- Invalid block format
- Invalid proof-of-work
- Hash mismatches
- Invalid transactions