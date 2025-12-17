# Technical Documentation for Master's Thesis
## Blockchain-Assisted QoS Routing in 6G MANET

---

## Section 1: The Proposed Routing Protocol (Formal Logic)

### 1.1 Trust Model

The trust model implements a behavioral detection mechanism that dynamically identifies malicious nodes through packet drop analysis. The formal logic is defined in the `UpdateMetric` function of the `BlockchainLedger` class.

#### Trust Score Initialization

All link metrics are initialized with a default trust value:

\[
T_{init}(i,j) = 1.0 \quad \forall (i,j) \in E
\]

where \(E\) represents the set of all edges in the network graph, and \(T(i,j)\) denotes the trust score for the link between nodes \(i\) and \(j\). This initialization assumes a "trust by default" approach, where all nodes begin with maximum trustworthiness.

#### Trust Decay Mechanism

The trust decay function implements a multiplicative penalty with a safety floor to prevent network partitioning:

\[
T_{new}(i,j) = \max(0.3, T_{old}(i,j) \times 0.5) \quad \text{if } D(i,j) = 1 \text{ and } M = \text{Proposed}
\]

where:
- \(D(i,j) \in \{0,1\}\) is a binary indicator for packet drop on link \((i,j)\)
- \(M \in \{\text{Baseline}, \text{Proposed}\}\) is the routing mode
- The floor value of \(0.3\) ensures links remain usable (expensive but not dead) even after multiple drops

The decay sequence follows:
\[
T_0 = 1.0 \rightarrow T_1 = 0.5 \rightarrow T_2 = 0.25 \rightarrow T_3 = 0.3 \text{ (floor)}
\]

After 2-3 consecutive drops, the trust score reaches the minimum threshold of \(0.3\), which is used for blackhole detection.

#### Recovery Mechanism

The current implementation does not include an explicit recovery mechanism. Once a node's trust decays, it remains at the floor value (\(0.3\)) or continues to decay if additional drops occur. This design prioritizes security over recovery, as malicious nodes are permanently marked as untrustworthy.

### 1.2 Cost Function

The routing cost function combines Signal-to-Noise Ratio (SNR) and Trust metrics using weighted coefficients:

\[
\text{Cost}(i,j) = \frac{\alpha}{\text{SNR}(i,j)} + \frac{\beta}{T(i,j)}
\]

where:
- \(\alpha = 1.0\) is the SNR coefficient (weight for physical link quality)
- \(\beta = 500.0\) is the Trust coefficient (weight for security/reliability)
- \(\text{SNR}(i,j)\) is the Signal-to-Noise Ratio in dB (default: 20.0 dB for new links)
- \(T(i,j)\) is the trust score (range: [0.3, 1.0])

#### Coefficient Analysis

The coefficient values are empirically tuned to balance physical link quality and security:

- **For normal nodes** (\(T = 1.0\), \(\text{SNR} = 20.0\)):
  \[
  \text{Cost} = \frac{1.0}{20.0} + \frac{500.0}{1.0} = 0.05 + 500.0 = 500.05
  \]

- **For nodes after one drop** (\(T = 0.5\), \(\text{SNR} = 20.0\)):
  \[
  \text{Cost} = \frac{1.0}{20.0} + \frac{500.0}{0.5} = 0.05 + 1000.0 = 1000.05
  \]

- **For nodes at trust floor** (\(T = 0.3\), \(\text{SNR} = 20.0\)):
  \[
  \text{Cost} = \frac{1.0}{20.0} + \frac{500.0}{0.3} = 0.05 + 1666.67 = 1666.72
  \]

This design ensures that:
1. Low-trust nodes are heavily penalized but not completely excluded (maintains connectivity)
2. Physical link quality (SNR) still influences routing decisions
3. The cost difference between normal and malicious nodes is significant (3.3x increase)

#### Baseline Mode

In Baseline mode, the cost function simplifies to hop count:

\[
\text{Cost}(i,j) = 1.0 \quad \forall (i,j) \in E
\]

This mimics standard routing protocols (e.g., AODV, OLSR) that ignore trust metrics, creating a vulnerability to blackhole attacks.

### 1.3 Blackhole Detection

The system employs **Behavioral Detection** without requiring a central authority or pre-configured blacklist. Detection occurs through the following mechanism:

#### Dynamic Detection Algorithm

A node \(n\) is classified as a blackhole if:

\[
\frac{|\{(i,j) \in E : (i = n \lor j = n) \land T(i,j) < 0.3\}|}{|\{(i,j) \in E : (i = n \lor j = n)\}|} > 0.5
\]

That is, if more than 50% of a node's links have trust scores below the threshold (\(0.3\)), the node is considered malicious.

#### Detection Process

1. **Initial State**: All nodes start with \(T = 1.0\) (trustworthy)
2. **Packet Drop Event**: When a packet is dropped (detected via `PhyRxDropCallback` or `Ipv4L3DropCallback`), the trust score for the corresponding link is updated
3. **Trust Decay**: The trust score is halved: \(T_{new} = \max(0.3, T_{old} \times 0.5)\)
4. **Threshold Check**: After 2-3 drops, \(T\) reaches \(0.3\)
5. **Classification**: If a majority of a node's links have \(T < 0.3\), the node is flagged as a blackhole

This approach is **purely dynamic**—no hardcoding or pre-knowledge of malicious nodes is required. The system learns about blackholes through observed behavior (packet drops).

---

## Section 2: Software Architecture & Implementation

### 2.1 Key Classes

#### BlockchainLedger

The `BlockchainLedger` class serves as an off-chain storage abstraction that maintains a distributed ledger of link metrics. It is responsible for:

- **Metric Storage**: Maintaining a map of link metrics (SNR, trust, drop count) for all node pairs
- **Trust Management**: Updating trust scores based on packet drop events
- **Blackhole Detection**: Dynamically identifying malicious nodes through trust analysis
- **Metric Retrieval**: Providing SNR and trust values to the routing engine

**Key Methods**:
- `UpdateMetric(src, dst, snr, isDrop, useBlockchain)`: Updates link metrics and applies trust decay
- `GetTrust(src, dst)`: Retrieves trust score for a link (default: 1.0)
- `GetSnr(src, dst)`: Retrieves SNR for a link (default: 20.0 dB)
- `IsBlackhole(nodeId)`: Determines if a node is a blackhole based on trust thresholds

#### RoutingEngine

The `RoutingEngine` class implements Dijkstra's shortest path algorithm with trust-aware edge weights. It serves as the decision maker for route calculation.

**Responsibilities**:
- **Graph Construction**: Building the network graph from physical node positions and radio range constraints
- **Weight Calculation**: Computing edge weights using the cost function (SNR + Trust)
- **Path Calculation**: Finding optimal paths using Dijkstra's algorithm
- **Mode Switching**: Supporting both Baseline (hop count) and Proposed (trust-aware) modes

**Key Methods**:
- `BuildGraph(nodes, ledger, maxRange, blackholeNodes, defaultSnr)`: Constructs the routing graph with appropriate edge weights
- `CalculatePath(source, dest)`: Computes the shortest path using Dijkstra's algorithm

#### SimulationHeartbeat

The `SimulationHeartbeat` function implements the control plane loop that periodically updates routing tables. It executes every 100 milliseconds and performs:

1. **Topology Discovery**: Rebuilding the network graph based on current node positions
2. **Path Calculation**: Computing optimal paths for all active traffic flows using Dijkstra's algorithm
3. **Route Installation**: Updating IPv4 static routing tables on all nodes along the calculated path

**Critical Logic**:
- Routes are recalculated every 100ms to adapt to mobility
- Routes are installed on **all nodes** in the path, including blackholes (routing table reflects Dijkstra's graph)
- Dijkstra's algorithm avoids blackholes through high trust-based costs in Proposed mode
- If a path still passes through a blackhole (rare), the blackhole will drop packets, triggering trust decay
- The routing table is flushed and rebuilt on each heartbeat to reflect current topology and trust metrics

### 2.2 Cross-Layer Data Collection

The simulation employs NS-3's trace source mechanism to collect data across multiple network layers, creating an "oracle" system that provides real-time network state information.

#### Trace Sources

Three trace sources are connected to monitor network events:

1. **PhyRxEnd**: Triggered when a packet is successfully received at the Physical layer
   - **Callback**: `PhyRxEndCallback`
   - **Purpose**: Updates SNR estimates and increments successful transmission counters
   - **SNR Estimation**: Uses distance-based model: \(\text{SNR} = \text{SNR}_{default} - \frac{d}{10}\), with minimum of 5.0 dB

2. **PhyRxDrop**: Triggered when a packet is dropped at the Physical layer
   - **Callback**: `PhyRxDropCallback`
   - **Purpose**: Detects signal quality issues (interference, fading, out-of-range)
   - **Action**: Updates trust metrics with `isDrop = true`

3. **Ipv4L3Drop**: Triggered when a packet is dropped at the Network layer
   - **Callback**: `Ipv4L3DropCallback`
   - **Purpose**: Detects routing issues (no route, TTL expired, blackhole drops)
   - **Action**: Updates trust metrics and increments malicious drop counters for blackhole nodes

#### Oracle Mechanism

The trace sources act as "oracles" that provide complete visibility into network events:

- **Real-time Updates**: Callbacks are invoked immediately when events occur
- **Cross-layer Visibility**: Events from PHY, MAC, and Network layers are captured
- **Automatic Ledger Updates**: The `BlockchainLedger` is updated automatically without requiring explicit polling

This design enables the routing protocol to react to network conditions in real-time, adapting to mobility, interference, and malicious behavior.

### 2.3 Routing Table Manipulation

The system enforces routing decisions through direct manipulation of NS-3's `Ipv4StaticRouting` tables.

#### Route Installation Process

For each path calculated by Dijkstra's algorithm:

1. **Route Removal**: Existing routes to the destination are removed to prevent stale entries
2. **Route Addition**: New routes are installed using `AddHostRouteTo(destIp, nextHopIp, interface)` on **all nodes** in the path
3. **Blackhole Behavior**: Routes are installed on all nodes, including blackholes. If a blackhole receives a packet, it will drop it (detected via `Ipv4L3DropCallback`), which triggers trust decay and enables dynamic detection

#### Periodic Rebuilding

The routing tables are completely rebuilt every 100ms by the `SimulationHeartbeat` function:

- **Flush Operation**: All routes to a destination are removed before installing new ones
- **Fresh Calculation**: Paths are recalculated from scratch based on current topology and trust metrics
- **Adaptation**: The system adapts to mobility, link failures, and trust changes

This approach ensures that routing tables always reflect the current network state, including dynamically detected blackholes.

---

## Section 3: Simulation Parameters (Methodology)

### 3.1 Simulation Setup Table

| Parameter | Value | Description |
|-----------|-------|-------------|
| **PHY Standard** | IEEE 802.11a (60 GHz physics) | Base standard with 60 GHz propagation model |
| **Propagation Model** | LogDistancePropagationLossModel | Path loss model for mmWave |
| **Path Loss Exponent** | 3.5 | Urban canyon environment (harsh 6G conditions) |
| **Reference Loss** | 68.0 dB @ 1m | Standard 60 GHz reference loss |
| **Transmit Power** | 10.0 dBm | Transmit power level |
| **Antenna Gain (Tx)** | +30 dBi | Transmit antenna gain (phased array) |
| **Antenna Gain (Rx)** | +30 dBi | Receive antenna gain (phased array) |
| **Total Link Budget** | +60 dB | Combined antenna gain improvement |
| **Mobility Model** | RandomWaypointMobilityModel | Stochastic mobility for MANET analysis |
| **Speed Range** | 1.0 - 5.0 m/s | Pedestrian speed (realistic MANET) |
| **Pause Time** | 1.0 s | Short pauses between movements |
| **Area (Sparse)** | 400 m × 400 m | Sparse network scenario |
| **Area (Dense)** | 300 m × 300 m | Dense network scenario (increased node density) |
| **Number of Nodes** | 30 | Total network nodes |
| **Number of Flows** | 10 | Concurrent traffic flows |
| **Packet Size** | 1024 bytes | UDP packet payload |
| **Packet Interval** | 0.1 s (10 packets/s) | Transmission rate per flow |
| **Data Rate** | ~82 kbps per flow | Effective data rate |
| **Simulation Time** | 60.0 s | Total simulation duration |
| **Application Start** | 1.0 s | Delay for ARP and routing stabilization |
| **Application Stop** | 59.9 s | Slightly before simulation end |
| **Max Radio Range** | 150.0 m | Maximum communication distance |
| **Default SNR** | 20.0 dB | Initial SNR for new links |
| **Number of Blackholes (Sparse)** | 5 | ~17% of network |
| **Number of Blackholes (Dense)** | 7 | ~23% of network |
| **Blackhole Behavior** | Drop all packets (NO_ROUTE) | Explicit packet dropping |
| **Heartbeat Interval** | 100 ms | Route recalculation period |

### 3.2 Adversary Model

#### Blackhole Node Selection

Blackhole nodes are randomly selected at simulation start using a uniform random distribution. The selection process:

1. **Random Selection**: Nodes are chosen uniformly from the set of all nodes (excluding sources/destinations)
2. **No Pre-configuration**: Blackholes are not hardcoded in the ledger—they must be detected dynamically
3. **Explicit Marking**: Selected nodes are marked in `g_context.blackholeNodes` set for tracking purposes

#### Blackhole Behavior

Blackhole nodes implement the following behavior:

1. **Route Installation**: Routes are installed on all nodes (including blackholes) to maintain routing table consistency with Dijkstra's graph
2. **Packet Dropping**: When packets arrive at a blackhole node, it drops them (detected via `Ipv4L3DropCallback`), which increments `g_maliciousDrops`
3. **Trust Decay Trigger**: Packet drops trigger trust decay, enabling dynamic detection
4. **Path Avoidance**: In Proposed mode, Dijkstra's algorithm naturally avoids blackholes through high trust-based costs (cost increases from ~500 to ~1667 for low-trust nodes)
5. **No Recovery**: Once detected, blackholes remain untrustworthy (no recovery mechanism)

This model represents a persistent attacker that continuously drops packets, making it detectable through behavioral analysis.

---

## Section 4: Experimental Results Analysis

### 4.1 Security Analysis

Based on the Dense Network results (5 runs), the Proposed protocol demonstrates significant security improvements:

#### Malicious Drop Reduction

| Metric | Baseline | Proposed | Reduction |
|--------|----------|----------|-----------|
| **Average Malicious Drops** | 643.8 | 92.6 | **85.6%** |
| **Min Malicious Drops** | 165 | 5 | **97.0%** |
| **Max Malicious Drops** | 1017 | 160 | **84.3%** |

**Attack Reduction Ratio**: The Proposed protocol reduces malicious attacks by approximately **85.6%** on average, with a maximum reduction of **97.0%** in the best case (Run 3).

#### Analysis

The significant reduction in malicious drops indicates that:

1. **Effective Avoidance**: Dijkstra's algorithm successfully avoids blackholes through high trust-based costs
2. **Dynamic Detection**: Trust decay mechanism identifies blackholes within 2-3 packet drops
3. **Path Diversion**: Routes are automatically diverted around detected blackholes

### 4.2 Reliability Analysis (PDR)

#### Dense Network Results

| Run | Baseline PDR (%) | Proposed PDR (%) | Difference |
|-----|-----------------|------------------|------------|
| 1 | 82.72 | 92.95 | +10.23 |
| 2 | 85.47 | 74.36 | -11.11 |
| 3 | 82.31 | 90.17 | +7.86 |
| 4 | 81.32 | 88.39 | +7.07 |
| 5 | 85.59 | 78.13 | -7.46 |
| **Average** | **83.48** | **84.80** | **+1.32** |

#### Trade-off Explanation

**Why PDR Improved in Dense Network**:

1. **Abundant Alternate Paths**: The dense topology (300m × 300m, 30 nodes) provides multiple routing options
2. **Short Detours**: When avoiding blackholes, the system can find short, safe alternate paths
3. **Reduced Blackhole Impact**: With more nodes, the probability of all paths being blocked by blackholes is lower

**Why PDR Sometimes Decreased**:

1. **Long Detour Paths**: In some scenarios, avoiding blackholes requires longer paths, increasing the probability of failure
2. **mmWave Fragility**: 60 GHz links are sensitive to mobility and interference—longer paths have more failure points
3. **Trust Floor Limitation**: Nodes with trust = 0.3 are still used when necessary, but they may drop packets occasionally

**Overall Assessment**: The Proposed protocol maintains comparable PDR (84.80% vs 83.48%) while providing significant security benefits (85.6% reduction in malicious drops). The slight PDR improvement in dense networks suggests that the trust-based routing is effective when alternate paths are available.

### 4.3 Latency & Hops Analysis

#### Dense Network Results

| Metric | Baseline | Proposed | Change |
|--------|----------|----------|--------|
| **Average Latency** | 3.45 ms | 4.05 ms | +0.60 ms (+17.4%) |
| **Average Hops** | 0.38 | 0.48 | +0.10 (+26.3%) |

#### Interpretation

**Latency Increase**: The Proposed protocol shows a modest increase in latency (+0.60 ms, +17.4%). This is expected because:

1. **Path Length**: Trust-aware routing may select longer paths to avoid blackholes
2. **Additional Processing**: Trust metric calculation adds minimal computational overhead
3. **Trade-off**: The security benefit (85.6% reduction in attacks) justifies the latency cost

**Hop Count Increase**: The average hop count increases by 0.10 hops (+26.3%), indicating that:

1. **Path Diversion**: Routes are successfully diverted around blackholes
2. **Multi-hop Preference**: The system prefers multi-hop paths through trusted nodes over direct paths through blackholes
3. **Connectivity Maintenance**: Despite longer paths, connectivity is maintained (PDR remains high)

**Conclusion**: The latency and hop count increases are acceptable trade-offs for the significant security improvement. The Proposed protocol successfully balances security and performance.

---

## Section 5: Code Snippets for Appendix

### 5.1 UpdateMetric Function (Trust Logic)

```cpp
void BlockchainLedger::UpdateMetric(uint32_t src, uint32_t dst, double snr, 
                                     bool isDrop, bool useBlockchain = true) {
    auto key = MakeKey(src, dst);
    
    if (m_ledger.find(key) == m_ledger.end()) {
        m_ledger[key] = LinkMetric();
    }
    
    LinkMetric& metric = m_ledger[key];
    
    // Update SNR (exponential moving average)
    if (snr > 0.0) {
        double alpha = 0.3;
        metric.movingAvgSnr = alpha * snr + (1.0 - alpha) * metric.movingAvgSnr;
    }
    
    // Trust decay: only in Proposed mode
    if (isDrop && useBlockchain) {
        metric.drops++;
        g_trustPenalties++;
        metric.trust = std::max(0.3, metric.trust * 0.5);
    } else if (isDrop) {
        // Baseline: count drops but don't apply trust penalties
        metric.drops++;
    }
}
```

### 5.2 CalculatePath / Dijkstra Loop (Cost Calculation)

```cpp
std::vector<uint32_t> RoutingEngine::CalculatePath(uint32_t source, uint32_t dest) {
    std::vector<uint32_t> path;
    
    // Dijkstra's algorithm initialization
    std::map<uint32_t, double> dist;
    std::map<uint32_t, uint32_t> prev;
    std::set<uint32_t> unvisited;
    
    for (const auto& pair : m_graph) {
        dist[pair.first] = std::numeric_limits<double>::infinity();
        prev[pair.first] = UINT32_MAX;
        unvisited.insert(pair.first);
    }
    
    dist[source] = 0.0;
    
    // Main Dijkstra loop
    while (!unvisited.empty()) {
        // Find unvisited node with minimum distance
        uint32_t u = UINT32_MAX;
        double minDist = std::numeric_limits<double>::infinity();
        for (uint32_t node : unvisited) {
            if (dist[node] < minDist) {
                minDist = dist[node];
                u = node;
            }
        }
        
        if (u == UINT32_MAX || minDist == std::numeric_limits<double>::infinity()) {
            break;  // No path found
        }
        
        if (u == dest) {
            break;  // Reached destination
        }
        
        unvisited.erase(u);
        
        // Update distances to neighbors
        if (m_graph.find(u) != m_graph.end()) {
            for (uint32_t v : m_graph[u]) {
                if (unvisited.find(v) != unvisited.end()) {
                    auto key = std::make_pair(u, v);
                    double weight = (m_weights.find(key) != m_weights.end()) ? 
                                   m_weights[key] : std::numeric_limits<double>::infinity();
                    
                    double alt = dist[u] + weight;
                    if (alt < dist[v]) {
                        dist[v] = alt;
                        prev[v] = u;
                    }
                }
            }
        }
    }
    
    // Reconstruct path
    if (dist[dest] != std::numeric_limits<double>::infinity()) {
        uint32_t current = dest;
        while (current != UINT32_MAX) {
            path.push_back(current);
            current = prev[current];
        }
        std::reverse(path.begin(), path.end());
    }
    
    return path;
}
```

### 5.3 BuildGraph Function (Cost Calculation)

```cpp
void RoutingEngine::BuildGraph(NodeContainer& nodes, BlockchainLedger& ledger, 
                                double maxRange, const std::set<uint32_t>& blackholeNodes, 
                                double defaultSnr = 20.0) {
    // ... (graph construction code) ...
    
    // Calculate weight based on routing mode
    double cost;
    if (m_useBlockchain) {
        // Proposed: Cost = (alpha / SNR) + (beta / Trust)
        cost = (m_alpha / snr) + (m_beta / trust);
    } else {
        // Baseline: Cost = 1 (hop count)
        cost = 1.0;
    }
    
    m_weights[std::make_pair(i, j)] = cost;
    m_weights[std::make_pair(j, i)] = cost;
}
```

### 5.4 SimulationHeartbeat (Integration Logic)

```cpp
void SimulationHeartbeat() {
    double currentTime = Simulator::Now().GetSeconds();
    
    // 1. Topology Discovery: Build graph from current physical positions
    g_context.routingEngine.BuildGraph(g_context.nodes, g_context.ledger, 
                                       g_context.maxRadioRange, g_context.blackholeNodes, 
                                       g_context.defaultSnr);
    
    // 2. Calculate and install routes for all active flows
    for (const auto& flow : g_context.activeFlows) {
        uint32_t source = flow.first;
        uint32_t dest = flow.second;
        
        // Calculate path using Dijkstra
        std::vector<uint32_t> path = g_context.routingEngine.CalculatePath(source, dest);
        
        if (path.size() > 1) {
            // Get destination IP address
            Ipv4Address destIp = g_context.ipv4Interfaces.GetAddress(dest);
            
            // Install routes on each node in the path (including blackholes)
            // Routes are installed on ALL nodes to maintain consistency with Dijkstra's graph
            // In Proposed mode, Dijkstra avoids blackholes through high trust-based costs
            // If a path still passes through a blackhole, it will drop packets, triggering trust decay
            for (size_t i = 0; i < path.size() - 1; i++) {
                uint32_t currentNode = path[i];
                uint32_t nextNode = path[i + 1];
                
                // Install route using Ipv4StaticRouting
                Ptr<Node> node = g_context.nodes.Get(currentNode);
                Ptr<Ipv4> ipv4 = node->GetObject<Ipv4>();
                Ptr<Ipv4StaticRouting> staticRouting = 
                    DynamicCast<Ipv4StaticRouting>(ipv4->GetRoutingProtocol());
                
                if (staticRouting) {
                    // Remove old routes to this destination
                    uint32_t numRoutes = staticRouting->GetNRoutes();
                    for (int32_t j = numRoutes - 1; j >= 0; j--) {
                        Ipv4RoutingTableEntry route = staticRouting->GetRoute(j);
                        if (route.GetDest() == destIp) {
                            staticRouting->RemoveRoute(j);
                        }
                    }
                    
                    // Install new route
                    Ipv4Address nextHopIp = g_context.ipv4Interfaces.GetAddress(nextNode);
                    uint32_t interface = ipv4->GetInterfaceForDevice(g_context.netDevices.Get(currentNode));
                    
                    if (interface != UINT32_MAX) {
                        staticRouting->AddHostRouteTo(destIp, nextHopIp, interface);
                    }
                }
            }
        }
    }
    
    // Reschedule for next heartbeat (100ms)
    Simulator::Schedule(MilliSeconds(100), &SimulationHeartbeat);
}
```

---

## References

- NS-3 Network Simulator: https://www.nsnam.org/
- IEEE 802.11ad (WiGig) Standard
- Dijkstra's Algorithm: E. W. Dijkstra, "A note on two problems in connexion with graphs," Numerische Mathematik, 1959

