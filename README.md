# Simplified P2P Blockchain Implementation

This project implements a simplified peer-to-peer blockchain network with a demo application.

## Project Structure

```
.
├── src/
│   ├── blockchain/         # Blockchain core implementation
│   │   ├── block.py       # Block structure and mining
│   │   ├── chain.py       # Blockchain management
│   │   └── transaction.py # Transaction handling
│   ├── network/           # P2P network implementation
│   │   ├── tracker.py     # Tracker server
│   │   ├── peer.py        # Peer node implementation
│   │   └── protocol.py    # Network protocols
│   └── demo/              # Demo application
│       └── voting.py      # Example voting application
├── tests/                 # Test cases
├── docs/                  # Documentation
│   ├── DESIGN.md         # Design documentation
│   └── TESTING.md        # Testing documentation
└── requirements.txt       # Python dependencies
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the tracker:
```bash
python src/network/tracker.py
```

3. Start peer nodes:
```bash
python src/network/peer.py --tracker <tracker-ip> --port <peer-port>
```

4. Run the demo application:
```bash
python src/demo/voting.py
```

## Requirements

- Python 3.8+
- Google Cloud VM instances (1 tracker + 3 peers)
- Network connectivity between VMs