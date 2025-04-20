# Blockchain Voting System

A simplified peer-to-peer blockchain system with voting functionality.

## Features

- **Blockchain Core**
  - Proof of Work consensus
  - Merkle tree for transaction verification
  - Dynamic difficulty adjustment
  - P2P network synchronization

- **Voting System**
  - Secure vote submission
  - Real-time vote counting
  - Voter participation tracking
  - Vote statistics and analytics

- **Network**
  - Tracker-based peer discovery
  - Automatic chain synchronization
  - Heartbeat mechanism
  - Fork resolution

## Project Structure

```
.
├── src/
│   ├── blockchain/     # Core blockchain implementation
│   ├── network/        # Network and API implementation
│   └── utils/          # Utility functions
├── docs/              # Documentation
├── logs/              # Log files
└── tests/             # Test files
```

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
python src/network/tracker.py
```

2. Start client nodes (in separate terminals):
```bash
python src/network/client.py
```

## API Documentation

See [API.md](docs/API.md) for detailed API documentation.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Design

See [DESIGN.md](docs/DESIGN.md) for system design details.

## License

MIT License
