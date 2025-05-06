# Blockchain Implementation Testing

## 1. Network Testing

### 1.1 Peer-to-Peer Network Setup

* **Test Case**: Multiple client registration

  * **Steps**:

    1. On tracker VM, run: `python -m src.network.tracker --port 5001`
    2. On 3 separate client VMs, run: `python -m src.network.client --tracker-url http://<tracker-ip>:5001`
    3. Observe log outputs on tracker for registration confirmation
  * **Expected Result**: All clients successfully register with tracker
  * **Actual Result**: All clients registered successfully

* **Test Case**: Peer discovery

  * **Steps**:

    1. Start tracker and clients as above
    2. On each client, access `/peers` API or observe logs
  * **Expected Result**: Each client sees 2 other peers
  * **Actual Result**: All clients correctly discovered peers

* **Test Case**: Heartbeat monitoring

  * **Steps**:

    1. Start tracker and clients
    2. Wait 30 seconds, observe tracker logs
  * **Expected Result**: Heartbeat received regularly
  * **Actual Result**: Heartbeats received every 30 seconds

* **Test Case**: Inactive peer cleanup

  * **Steps**:

    1. Start tracker and clients
    2. Stop one client
    3. Wait \~60 seconds
  * **Expected Result**: Tracker removes inactive client
  * **Actual Result**: Client removed after timeout

## 2. Blockchain Testing

### 2.1 Block Creation and Validation

* **Test Case**: Block mining

  * **Steps**:

    1. Submit vote via frontend
    2. Click "Mine"
  * **Expected Result**: Valid block with correct hash
  * **Actual Result**: Block created with valid proof-of-work

* **Test Case**: Block broadcasting

  * **Steps**:

    1. Mine a block on one client
    2. Switch peers in frontend, observe dashboard
  * **Expected Result**: Block appears across all peers
  * **Actual Result**: Block successfully propagated

* **Test Case**: Chain synchronization

  * **Steps**:

    1. Introduce conflicting blocks on peers
    2. Wait for automatic resolution
  * **Expected Result**: Peers resolve to longest valid chain
  * **Actual Result**: Chains synchronized successfully

### 2.2 Block Editing and Verification

* **Test Case**: Transaction modification

  * **Steps**:

    1. Submit votes through the frontend and mine a block
    2. Call `/edit_transaction_only` API with the index and modified content
    3. Use `/verify_block` to check Merkle root
  * **Expected Result**: Modification detected via Merkle root
  * **Actual Result**: Modified transaction correctly identified

### 2.3 Fork Resolution

* **Test Case**: Simultaneous mining

  * **Steps**:

    1. Submit votes to two clients simultaneously
    2. Mine blocks at the same time
    3. Observe forked chains
    4. Continue mining to trigger resolution
  * **Expected Result**: System selects chain with greater cumulative work
  * **Actual Result**: Longest chain retained

### 2.4 Merkle Tree Tests

* **Test Case**: Odd number of transactions

  * **Steps**:

    1. Submit 3 votes from the frontend
    2. Mine a block
    3. View Merkle tree in backend logs or explorer
  * **Expected Result**: Last transaction duplicated to balance tree
  * **Actual Result**: Tree constructed correctly

### 2.5 Transaction Verification

* **Test Case**: Verification path construction

  * **Steps**:

    1. Submit several votes
    2. Mine block
    3. Use `/verify_transaction` on specific index
    4. Check proof path returned
  * **Expected Result**: Proof path correctly connects transaction to Merkle root
  * **Actual Result**: Constructed as expected

## 3. API Testing

### 3.1 Block Editing API

* **Test Case**: Modify block or tx field

  * **Steps**:

    1. Send POST to `/edit_block` or `/edit_transaction_only`
  * **Expected Result**: Field/transaction changed
  * **Actual Result**: As expected

### 3.2 Verification API

* **Test Case**: Block verification

  * **Steps**:

    1. Send GET to `/verify_block`
  * **Expected Result**: Valid or modified status shown
  * **Actual Result**: Accurate result

...\[section 4–9 remain unchanged]...



## 4. Performance Testing

### 4.1 Mining Performance

* **Test Case**: Auto difficulty adjustment

  * **Steps**:

    1. Open frontend "Settings"
    2. Set Difficulty = 1, Target Time = 1 sec, Adjustment Interval = 1
    3. Submit vote and mine block
    4. Return to "Settings" and observe difficulty change
  * **Expected Result**: Difficulty increases if mining too fast
  * **Actual Result**: Difficulty adjusted after each block

* **Test Case**: Multiple transactions

  * **Steps**:

    1. Submit several votes via the frontend Voting tab
    2. Check "Transactions" to ensure they appear in the pending pool
    3. Click "Mine" to mine block
    4. Go to "Dashboard" or "Explorer" to verify inclusion
  * **Expected Result**: All votes packed into new block
  * **Actual Result**: Confirmed in explorer

### 4.2 Network Propagation

* **Test Case**: Block propagation

  * **Steps**:

    1. Mine a block on Peer A
    2. In frontend, use Settings to switch to Peer B
    3. Check dashboard or logs
  * **Expected Result**: New block visible on Peer B shortly
  * **Actual Result**: Appears within seconds, logs confirm propagation

## 5. Resilience Testing

### 5.1 Network Resilience

* **Test Case**: Peer disconnection

  * **Steps**:

    1. Manually close a peer VM
    2. Wait over 60 seconds
    3. Refresh frontend peers list
  * **Expected Result**: Disconnected peer removed automatically
  * **Actual Result**: Peer list updated after timeout

* **Test Case**: Tracker failure

  * **Steps**:

    1. Stop tracker process
    2. Refresh frontend — peers cannot be fetched
    3. Restart tracker
    4. Observe clients auto re-register via `/register`
  * **Expected Result**: Clients reappear after tracker restart
  * **Actual Result**: Verified through logs and UI

### 5.2 Data Resilience

* **Test Case**: Invalid block rejection

  * **Steps**:

    1. Modify `hash_pair()` in `src/blockchain/block.py` to always return "1"
    2. Mine a block
    3. Observe backend logs
  * **Expected Result**: Block is rejected due to hash format
  * **Actual Result**: Block discarded as expected

## 6. Voting System Testing

### 6.1 Voting Submission Test

* **Test Case**: Submit valid vote

  * **Steps**:

    1. Go to the Voting tab on the frontend
    2. Enter a valid voter ID and select a candidate
    3. Click "Submit Vote"
  * **Expected Result**: Vote accepted and added to pending transactions
  * **Actual Result**: Vote submitted successfully

* **Test Case**: Submit duplicate vote

  * **Steps**:

    1. Submit a vote as above
    2. Repeat submission using the same voter ID
  * **Expected Result**: Duplicate vote rejected
  * **Actual Result**: Duplicate vote correctly rejected

* **Test Case**: Submit invalid vote

  * **Steps**:

    1. Use an invalid or empty voter ID
    2. Attempt to submit
  * **Expected Result**: Invalid vote rejected
  * **Actual Result**: Invalid input correctly handled

### 6.2 Voting Statistics Test

* **Test Case**: Verify vote count

  * **Steps**:

    1. Submit multiple votes for different candidates
    2. Mine the block
    3. Go to Dashboard tab
  * **Expected Result**: Vote statistics displayed accurately
  * **Actual Result**: Stats match submissions

### 6.3 Voting Status Test

* **Test Case**: Track vote inclusion

  * **Steps**:

    1. Submit a vote
    2. Use the Explorer tab to locate the block
    3. Verify the vote appears in transaction list
  * **Expected Result**: Vote status correctly reflected
  * **Actual Result**: Confirmed via explorer

## 7. API Testing

### 7.1 Interface Availability Test

* **Test Case**: Endpoint reachability

  * **Steps**:

    1. Use Postman or curl to call all backend endpoints
    2. Confirm responses and error handling
  * **Expected Result**: All APIs respond with correct status
  * **Actual Result**: Verified successfully

### 7.2 Data Consistency Test

* **Test Case**: Sync after cross-node operations

  * **Steps**:

    1. Submit a vote to client A
    2. Wait for block to propagate
    3. Check blockchain state from client B
  * **Expected Result**: Chain data consistent across nodes
  * **Actual Result**: Confirmed

## 8. Performance Testing

### 8.1 Concurrent Voting Test

* **Test Case**: Simulate high concurrency

  * **Steps**:

    1. Submit votes rapidly from multiple tabs or scripts
    2. Monitor pending pool and mining behavior
  * **Expected Result**: System handles load without failure
  * **Actual Result**: Stable under concurrent requests

### 8.2 Large-scale Data Test

* **Test Case**: Stress test with bulk data

  * **Steps**:

    1. Pre-generate many fake votes using scripts
    2. Feed to system and mine over time
    3. Observe performance metrics (memory, CPU, delay)
  * **Expected Result**: No crashes or major delays
  * **Actual Result**: Passed under expected limits

## 9. Test Environment

### 9.1 Hardware Requirements

* CPU: 4 cores or more
* RAM: 8 GB or more
* Disk: 100 GB+

### 9.2 Software Requirements

* Python 3.8 or newer
* All packages listed in `requirements.txt`
* Node.js 18+ (for frontend)

### 9.3 Network Requirements

* Public IP access between tracker and peers
* Stable and low-latency connections
* Open ports for tracker and client HTTP communication
