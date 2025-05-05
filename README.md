# Blockchain-based Voting System

A decentralized voting system built on blockchain technology, ensuring transparency, immutability, and security in the voting process. This course project **fulfills all required and bonus features**, including full peer-to-peer functionality, demo application, and advanced blockchain capabilities.

## ✅ Completed Requirements

* Full peer-to-peer network with **1 tracker** and **3+ client nodes** on **Google Cloud VMs**
* Tracker maintains and broadcasts peer list updates
* Each peer:

  * Maintains its own copy of the blockchain
  * Mines blocks and broadcasts them to others
  * Verifies incoming blocks and resolves forks
* Demo application: **Decentralized Voting System**
* Tamper detection using hash validation and Merkle proof
* ✅ Bonus Features:

  * Frontend web UI
  * Dynamic mining difficulty based on performance
  * Multiple transactions per block
  * Merkle tree for transaction-level verification

## 🏗️ Project Structure

```
blockchain-voting/
├── block-backend/                  # Backend implementation
│   ├── src/
│   │   ├── blockchain/
│   │   │   ├── block.py
│   │   │   └── chain.py
│   │   ├── network/
│   │   │   ├── client.py
│   │   │   ├── tracker.py
│   │   │   └── voting.py
│   │   └── utils/
│   │       └── logger.py
│   ├── requirements.txt
│   └── README.md
├── blockchain-frontend/           # Frontend web UI
├── DESIGN.md                      # System architecture and diagrams
├── TESTING.md                     # Deployment and validation records
└── README.md                      # This file
```

## 🚀 Running on Google Cloud VMs

### 1. Tracker (run on one VM)

```bash
cd block-backend
pip install -r requirements.txt
python -m src.network.tracker --port 6000
```

### 2. Clients (run on other VMs)

```bash
cd block-backend
pip install -r requirements.txt
python -m src.network.client --tracker-url http://<TRACKER_VM_EXTERNAL_IP>:6000
```

Each client runs on a separate VM and automatically joins the network using the tracker URL.

## 📡 API Overview

### Tracker (`:6000`)

* `POST /register` — Add a new peer
* `POST /unregister` — Remove a peer
* `POST /heartbeat` — Keep-alive ping
* `GET /peers` — Fetch current peer list

### Client

* `POST /vote` — Submit a vote
* `GET /votes` — View all votes
* `GET /chain` — Retrieve blockchain
* `POST /mine` — Mine new block
* `GET /verify_block` — Check block integrity
* `POST /edit_block` — Modify block (for testing)
* `GET /mining_params` / `POST /mining_params` — View or update mining settings
* `GET /verify_transaction` — Verify specific transaction integrity
* `GET /verify_transaction_internal` — Internal endpoint for transaction verification
* `POST /edit_transaction_only` — Edit transaction without hash recalculation (for testing)
* `GET /peers` — Get list of connected peers
* `POST /transaction` — Add new transaction to pending pool