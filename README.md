# Blockchain System Algorithm at the Junction of 6G and MANET Networks

## 1. System Architecture

The system is a hybrid network infrastructure that includes:
- Stationary 6G base station
- Dynamic MANET network with mobile nodes
- Distributed blockchain registry for registration, validation, and monitoring of nodes and routes

## 2. System Initialization

1. The 6G base station initializes the blockchain genesis block
2. Initial network parameters are defined:
   - Base station coverage radius
   - Threshold values for verification
   - Time intervals for activity checks
   - Consensus algorithm parameters
3. Primary trusted nodes within the base station radius are registered
4. An initial set of validators is formed from the trusted nodes

## 3. Registration of New Nodes

1. **Node entering the base station coverage area**:
   1. The new node sends a registration request to the network
   2. The base station verifies the digital signature and credentials of the node
   3. Upon successful verification, the station generates a node registration transaction
   4. The transaction is placed in the blockchain after consensus confirmation
   5. The node receives a unique identifier and cryptographic keys

2. **Node entering another MANET node's zone (outside base station coverage)**:
   1. The node sends a request to the nearest active MANET node
   2. The receiving node verifies the digital signature of the requester
   3. A registration transaction is created and propagated through the network
   4. Confirmation from several neighboring nodes (quorum) is required
   5. After consensus is reached, the node is added to the blockchain registry with an "unverified" marker
   6. The node receives limited rights until confirmed by the base station

## 4. Security Mechanisms

1. **Multi-level authentication**:
   1. Verification of digital certificates with each connection
   2. Periodic rotation of session keys
   3. Use of zero-knowledge proof scheme for identity verification

2. **Node rating system**:
   1. Each node has a dynamic trust rating
   2. Rating increases with successful data transmission
   3. Rating decreases with anomalous behavior or failures
   4. Nodes with low ratings are excluded from critical routes

3. **Protection against Sybil attacks**:
   1. Limitation of registration rate for new nodes
   2. Physical verification through response time measurement
   3. Analysis of spatial distribution of nodes
   4. Requirement for confirmation from geographically distributed nodes

## 5. Node Activity Monitoring

1. **Regular activity checks**:
   1. Each node sends "heartbeat" transactions at specified intervals
   2. Sending frequency is dynamically determined based on network load
   3. The transaction contains current node parameters (battery charge, GPS coordinates, load)
   4. Missing more than N consecutive heartbeat signals indicates node loss

2. **Monitoring of neighboring nodes**:
   1. Each node maintains a table of neighbors within direct visibility radius
   2. Periodically sends confirmation of neighboring nodes' activity
   3. When discrepancies are detected (node claims activity, but neighbors don't see it), verification is initiated

3. **Activity data processing**:
   1. Smart contract correlates data from different nodes
   2. Forms an up-to-date network map in the blockchain
   3. Marks suspicious nodes for additional verification
   4. Automatically excludes inactive nodes from routes

## 6. Route Construction and Verification

1. **Route initialization**:
   1. The sending node forms a route request to the receiving node
   2. The request includes route requirements (reliability, speed, priority)
   3. The request is signed with the sender's digital signature

2. **Route formation**:
   1. Smart contract analyzes the current network topology from the blockchain
   2. A modified Dijkstra's algorithm is applied, taking into account:
      - Node trust rating
      - Current node load
      - Battery charge level
      - Connection stability
   3. Several alternative routes are formed

3. **Route verification**:
   1. Each proposed route is verified by validator nodes
   2. The availability of all nodes in the route is checked
   3. Route security parameters are evaluated
   4. Verification result is recorded in the blockchain

4. **Route selection and use**:
   1. The sender receives a list of verified routes
   2. The optimal route is selected based on specified criteria
   3. Route nodes are notified of inclusion in the active route
   4. Each data transmission along the route is registered in the blockchain
   5. Smart contract tracks transmission success to update node ratings

## 7. Adaptation to Topology Changes

1. **Detection of changes**:
   1. Continuous monitoring of node status
   2. Detection of new node connections
   3. Identification of disconnections or failures of existing nodes
   4. Tracking changes in connection quality

2. **Real-time topology updates**:
   1. Changes are recorded in the blockchain with special transactions
   2. A procedure for reassessing affected routes is initiated
   3. Validators confirm the topology update
   4. Updated information is propagated through the network

3. **Route reconstruction**:
   1. Critical changes trigger a route reconstruction procedure
   2. Proactive creation of alternative routes for mission-critical connections
   3. Temporary routes are activated until full verification of new permanent routes

## 8. Consensus Mechanism

1. **Hybrid consensus**:
   1. In the direct 6G coverage area: lightweight Proof-of-Authority (PoA)
   2. Outside the coverage area: modified Practical Byzantine Fault Tolerance (PBFT)
   3. The base station has a special role in verifying critical transactions

2. **Hierarchical validation**:
   1. Nodes are divided into three categories: full validators, light validators, regular nodes
   2. The category is determined based on computational resources, connection stability, and trust rating
   3. Heavy operations are delegated to full validators
   4. Light operations can be performed by all nodes

3. **Consensus optimization**:
   1. Dynamic regulation of the number of validators depending on the load
   2. Blockchain sharding for parallel transaction processing
   3. Prioritization of mission-critical transactions (related to network security and integrity)

## 9. Recovery After Failures

1. **Failure detection**:
   1. Continuous checking of node synchronization
   2. Identification of inconsistencies in local blockchain copies
   3. Detection of temporary network partitioning

2. **Recovery procedure**:
   1. Segmented parts of the network continue to function autonomously
   2. When connection is restored, a blockchain merging procedure is initiated
   3. Conflict resolution based on strict priority rules
   4. Rollback of transactions that did not reach the necessary consensus

3. **Local reorganization**:
   1. When a key node fails, adjacent nodes automatically restructure connections
   2. Temporary enhanced verification mode for new connections
   3. Priority restoration of critical routes

## 10. Performance and Energy Consumption Optimization

1. **Adaptive resource management**:
   1. Nodes with low battery charge are switched to energy-saving mode
   2. Dynamic load distribution between nodes
   3. Automatic scaling of validation operations

2. **Compression and optimization of blockchain data**:
   1. Use of lightweight transaction format for mobile nodes
   2. Pruning of historical data for devices with limited memory
   3. Optimization of block size depending on network bandwidth

3. **Prediction of changes**:
   1. Analysis of node movement patterns to predict topology changes
   2. Advance preparation of alternative routes
   3. Proactive regulation of load based on forecasts

## 11. Security Policies and Updates

1. **Anomalous behavior detection**:
   1. Continuous analysis of node activity
   2. Identification of inconsistencies in data transmission patterns
   3. Detection of protocol modification attempts

2. **Attack response**:
   1. Automatic isolation of suspicious nodes
   2. Creation of a "quarantine zone" for node verification
   3. Notification of network administrators through secure channels

3. **System updates**:
   1. Secure distribution of updates through the blockchain
   2. Multi-stage verification of updates by key validators
   3. Gradual implementation with the possibility of rollback when problems are detected

## 12. Conclusion

This algorithm ensures reliable operation of a hybrid network that combines a stationary 6G infrastructure and a dynamic MANET network through blockchain technology. The system guarantees security, adaptability to changes, efficient resource utilization, and fault tolerance, providing transparency and trust between all network participants.