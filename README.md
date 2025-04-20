# Blockchain Implementation

A simple blockchain implementation with proof of work, transaction validation, and peer-to-peer networking.

## Features

- Proof of Work mining
- Transaction validation
- Merkle tree for transaction verification
- Peer-to-peer networking
- Chain synchronization
- Difficulty adjustment
- Block editing and verification

## Project Structure

```
.
├── src/
│   ├── blockchain/
│   │   ├── block.py      # Block implementation
│   │   ├── chain.py      # Blockchain implementation
│   │   └── transaction.py # Transaction implementation
│   ├── network/
│   │   ├── client.py     # Client node implementation
│   │   └── tracker.py    # Tracker server implementation
│   └── utils/
│       └── logger.py     # Logging utilities
├── run.py                # Main entry point
└── README.md
```

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Network

### Start Tracker Server
```bash
python run.py tracker --port 6000
```

### Start Client Nodes
```bash
# Start first client
python run.py client --port 5001

# Start second client
python run.py client --port 5002

# Start third client
python run.py client --port 5003
```

## API Endpoints

### Client Node Endpoints

- `POST /transaction`: Add a new transaction
- `POST /mine`: Mine pending transactions
- `GET /chain`: Get the current blockchain
- `POST /edit_block`: Edit a block's transaction (for testing)
- `GET /verify_block`: Verify block integrity and locate modified transactions

### Tracker Server Endpoints

- `POST /register`: Register a new client
- `POST /heartbeat`: Update client status
- `GET /peers`: Get list of active peers

## Testing Block Editing and Verification

1. Start the tracker and at least one client
2. Add some transactions and mine a block
3. Edit a block's transaction:
```bash
curl -X POST http://localhost:5001/edit_block \
  -H "Content-Type: application/json" \
  -d '{
    "block_index": 1,
    "transaction_index": 0,
    "field": "amount",
    "new_value": 1000
  }'
```

4. Verify the block:
```bash
curl http://localhost:5001/verify_block?block_index=1
```

The verification will show:
- Whether the block hash is valid
- Whether the Merkle root is valid
- The current and stored Merkle roots
- Indices of any modified transactions

## Logging

Logs are stored in the following directories:
- Client logs: `logs/client/client_{port}_{timestamp}.log`
- Tracker logs: `logs/tracker/tracker_{port}_{timestamp}.log`