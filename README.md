# Blockchain-based Voting System

A decentralized voting system built on blockchain technology, ensuring transparency, immutability, and security in the voting process. This course project **fulfills all required and bonus features**, including full peer-to-peer functionality, demo application, and advanced blockchain capabilities.

## ✅ Completed Requirements

- Peer-to-peer network with **1 tracker** and **3+ client nodes**, all running on **Google Cloud VMs**
- Tracker maintains and synchronizes a live peer list
- Each peer node:
  - Maintains an up-to-date local blockchain
  - Mines new blocks and broadcasts them
  - Verifies and accepts blocks from others
  - Resolves forks when multiple valid branches exist
- Demo application: **Blockchain-based Voting System**
- Protection against tampering using **hash verification** and **Merkle tree proofs**

### 🔒 Bonus Features Implemented

- Interactive **frontend UI** for voting, exploration, and management
- **Dynamic mining difficulty** based on block times
- **Merkle Tree** verification for individual transactions
- Support for **multiple transactions per block**

## 🏗️ Project Structure

```

blockchain-voting/
├── block-backend/                  # Backend system (tracker, peers, blockchain logic)
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
├── TESTING.md                     # GCP deployment setup and testing process
└── README.md                      # This file

````

## 🚀 Running on Google Cloud VMs

### 1. Tracker (run on one GCP VM)

```bash
cd block-backend
pip install -r requirements.txt
python -m src.network.tracker --port 6000
````

### 2. Client Nodes (run on other GCP VMs)

```bash
cd block-backend
pip install -r requirements.txt
python -m src.network.client --tracker-url http://<TRACKER_VM_EXTERNAL_IP>:6000
```

Each peer runs on a separate VM and communicates via the tracker.

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

---

## 🌐 Frontend UI Setup and Usage

The frontend interface is located in the `blockchain-frontend/` folder. It provides a user-friendly web interface to interact with the blockchain system and supports all major functionalities including voting, exploring blocks, managing transactions, and node configuration.

### Prerequisites

* Node.js (via `nvm`)

```bash
nvm install 18
nvm use 18
```

* Ensure you have `npm` installed (comes with Node.js)

### Configuration (Important)

Before running the frontend, update the tracker proxy destination in:

```bash
blockchain-frontend/next.config.mjs
```

Locate the `rewrites()` configuration and modify the following entry:

```js
{
  source: "/tracker/:path*",
  destination: "http://127.0.0.1:6000/:path*",
}
```

⬇️ Change `127.0.0.1` to the **external IP of your tracker VM**, for example:

```js
{
  source: "/tracker/:path*",
  destination: "http://34.123.45.67:6000/:path*",
}
```

This ensures the frontend can route requests to the tracker server deployed on GCP.

### Running the Frontend

You can run the frontend from **any of the client VMs** (or locally if needed):

```bash
cd blockchain-frontend
npm install
npm run dev
```

This will start the web interface at `http://localhost:3000/` by default. Use external IP instead when using external browser.

---

### UI Overview

* **Dashboard**
  ![Dashboard Overview](./images/1-dashboard.png)
  * Displays system parameters and blockchain status
  * Shows real-time blockchain height, mining difficulty, and node status

* **Voting**
  ![Voting Interface](./images/2-voting.png)
  * Enter voter name and select candidate to cast vote
  * Vote records are stored in pending transactions
  * Click mine button to connect block to chain when pending transactions reach threshold
  * Automatically updates and tallies voting results

* **Blockchain Explorer - Overview**
  ![Blockchain Overview](./images/3-explorers.png)
  * Shows overall blockchain status
  * Displays basic information of all blocks
  * Click any block to view detailed information

* **Blockchain Explorer - Block Details**
  ![Block Details](./images/4-block_details.png)
  * Shows detailed content of selected block
  * Provides verify block and verify transaction functionality
  * Validates individual transaction records and entire block integrity
  * Detects any block tampering

* **Blockchain Explorer - Verification**
  ![Block Verification](./images/5-verification.png)
  * Provides block and transaction verification features
  * Supports Merkle tree verification
  * Ensures data integrity and immutability

* **Transaction Management**
  ![Transaction Interface](./images/6-transactions.png)
  * Manually add new transaction records
  * Displays all pending transactions
  * Manages transaction pool

* **System Settings**
  ![System Settings](./images/7-settings.png)
  * Switch between different backend nodes
  * Adjust mining difficulty and other parameters
  * Configure system runtime parameters