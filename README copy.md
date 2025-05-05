# Blockchain-based Voting System

A decentralized voting system built on blockchain technology, ensuring transparency, immutability, and security in the voting process.

## Features

- Decentralized architecture
- Secure blockchain-based vote storage
- Real-time vote verification
- Tamper-evident vote records
- Distributed consensus mechanism
- Automatic difficulty adjustment
- Fork resolution
- Peer synchronization

## Prerequisites

- Python 3.8+
- Flask
- requests

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd blockchain-voting-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the System

1. Start the tracker server:
```bash
python -m src.network.tracker --port 6000
```

2. Start client nodes (in separate terminals):
```bash
# First client
python -m src.network.client --port 5001

# Second client
python -m src.network.client --port 5002

# Third client
python -m src.network.client --port 5003
```

## API Endpoints

### Tracker Server (Port 6000)

- `POST /register`: Register a new client node
- `POST /unregister`: Unregister a client node
- `POST /heartbeat`: Update client node status
- `GET /peers`: Get list of all peers

### Client Nodes

- `POST /vote`: Submit a new vote
- `GET /votes`: Get all votes
- `GET /chain`: Get the blockchain
- `POST /mine`: Mine pending transactions
- `GET /verify_block`: Verify block integrity
- `POST /edit_block`: Edit block content (for testing)
- `GET /mining_params`: Get current mining parameters
- `POST /mining_params`: Update mining parameters


## Project Structure

```
blockchain-voting/
├── src/
│   ├── blockchain/
│   │   ├── block.py
│   │   └── chain.py
│   ├── network/
│   │   ├── client.py
│   │   ├── tracker.py
│   │   └── voting.py
│   └── utils/
│       └── logger.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
