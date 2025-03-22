# Blockchain System at the Junction of 6G and MANET Networks - Project Structure

This document provides a comprehensive overview of the project structure to help AI agents understand the organization and purpose of different components in the codebase.

## 1. Project Overview

This project implements a simulation of a blockchain system operating at the junction of 6G and MANET networks. It integrates NS-3 (Network Simulator 3) with custom blockchain simulation components to model the behavior of a decentralized network with mobile nodes.

## 2. Repository Structure

```
/
├── .git/                      # Git repository metadata
├── .vscode/                   # VSCode configuration
├── results/                   # Top-level simulation results directory
├── output/                    # Output files from simulations
├── test_ns3_blocksim/         # Main simulation framework
│   ├── config/                # Configuration files for simulation scenarios
│   ├── models/                # Core models for the simulation
│   │   ├── blockchain/        # Blockchain simulation models
│   │   │   ├── consensus/     # Consensus mechanisms implementations
│   │   │   ├── core/          # Core blockchain components
│   │   │   ├── network/       # Network-related blockchain components
│   │   │   └── security/      # Security mechanisms for blockchain
│   │   ├── manet/             # MANET network simulation models
│   │   ├── integration/       # Integration between blockchain and NS-3
│   │   ├── ns3_adapter.py     # Adapter for NS-3 functionality
│   │   ├── blocksim_adapter.py # Adapter for blockchain simulation
│   │   └── paths_manager.py   # Manages paths for project files and folders
│   ├── scripts/               # Scripts for running simulations
│   ├── visualization/         # Tools for visualizing simulation results
│   ├── results/               # Directory for storing simulation results
│   ├── external/              # External dependencies (NS-3)
│   ├── tests/                 # Test cases for the framework
│   ├── examples/              # Example simulations
│   ├── code_quality_venv/     # Virtual environment for code quality tools
│   ├── venv/                  # Main virtual environment
│   ├── README.md              # Technical documentation
│   ├── README_EN.md           # English technical documentation
│   ├── README_IMPLEMENTATION_STATUS_EN.md  # Current implementation status
│   ├── README_QUALITY_TOOLS.md             # Documentation on code quality tools
│   ├── requirements.txt       # Python dependencies
│   └── various script files   # Various utility scripts for code analysis, fixes, etc.
├── omnet++/                   # OMNeT++ simulation files (alternative to NS-3)
└── Various Python scripts and documentation files
```

## 3. Key Components

### 3.1 NS-3 Integration (test_ns3_blocksim/models)

NS-3 (Network Simulator 3) is used as the foundation for simulating network behavior. The project includes:

#### 3.1.1 NS-3 Adapter (`ns3_adapter.py`)
- Provides an interface to NS-3 functionality
- Manages node creation, positioning, and movement
- Handles wireless channel setup and configuration
- Implements AODV routing protocol integration
- Synchronizes network events with the simulation timeline

#### 3.1.2 MANET Models (`models/manet/`)
- Mobile Ad-hoc Network specific components
- Node mobility models
- Wireless communication implementations
- Topology management

### 3.2 Blockchain Simulation (test_ns3_blocksim/models/blockchain)

The blockchain component is organized into several subdirectories:

#### 3.2.1 Core (`blockchain/core/`)
- Block and transaction data structures
- Blockchain state management
- Ledger implementation
- Data serialization and storage

#### 3.2.2 Consensus (`blockchain/consensus/`)
- Proof of Authority (PoA) implementation
- Partial Practical Byzantine Fault Tolerance (PBFT) implementation
- Hybrid consensus mechanisms
- Validator selection and management

#### 3.2.3 Network (`blockchain/network/`)
- Block and transaction propagation
- Node discovery and communication
- Network state synchronization
- Handling of network partitions and merges

#### 3.2.4 Security (`blockchain/security/`)
- Cryptographic operations for transaction signing
- Node authentication and verification
- Trust rating system
- Protection against various attack vectors

#### 3.2.5 BlockSim Adapter (`blocksim_adapter.py`)
- Interface between blockchain components and the simulation framework
- Manages blockchain events and timeline
- Connects blockchain operations with network events

### 3.3 Integration Layer (test_ns3_blocksim/models/integration)

#### 3.3.1 Integration Interface (`integration_interface.py`)
- Connects NS-3 network events with blockchain operations
- Synchronizes simulation timelines between components
- Manages cross-component communication
- Provides unified API for the simulation framework

#### 3.3.2 Paths Manager (`paths_manager.py`)
- Manages file paths for configuration, results, and resources
- Ensures consistent access to project files across different components
- Supports platform-independent path handling

### 3.4 Simulation Framework

Provides tools for setting up and running simulations:
- Configuration management through config files
- Dynamic parameter adjustment during simulation
- Metrics collection and analysis
- Visualization tools for simulation results
- State tracking and logging

## 4. Implementation Status

The project is under active development with varying levels of implementation for different features:

### Fully Implemented (✅)
- Basic MANET network using NS-3
- Integration between NS-3 and blockchain simulation
- Node types (base station, validators, regular nodes)
- Base station simulation with AODV routing
- Blockchain structure with blocks and transactions
- Node registration mechanism
- Basic consensus (PoA)
- Tracking of node activity and movement
- Dynamic topology updates
- Animation and visualization support

### Partially Implemented (⚠️)
- Integration of 6G network with MANET
- Comprehensive credential verification
- Hybrid consensus (PoA + PBFT)
- Security mechanisms (authentication, Sybil attack protection)
- Route verification by validators
- Adaptive resource management
- Recovery after network failures

### Not Implemented (❌)
- Session key rotation
- Zero-knowledge proof for identity verification
- Blockchain sharding
- Advanced conflict resolution
- Prediction of topology changes
- System update distribution via blockchain

See `test_ns3_blocksim/README_IMPLEMENTATION_STATUS_EN.md` for detailed status information.

## 5. Virtual Environments

The project uses multiple Python virtual environments:
- Main virtual environment: `/test_ns3_blocksim/venv/`
- Code quality tools environment: `/test_ns3_blocksim/code_quality_venv/`

Activate the appropriate environment before running different parts of the code.

## 6. Python Dependencies

Main dependencies include:
- NS-3 Python bindings
- Cryptography libraries
- Visualization tools
- Test frameworks

See `test_ns3_blocksim/requirements.txt` for a complete list.

## 7. Running Simulations

Simulations can be run using scripts in `test_ns3_blocksim/scripts/` with various configuration parameters set in `test_ns3_blocksim/config/`.

## 8. Development Workflow

The project follows a standard Git workflow with code quality checks implemented through:
- Pre-commit hooks (.pre-commit-config.yaml)
- Pylint (.pylintrc)
- Mypy for type checking
- Various code quality analysis scripts

## 9. Documentation

Documentation is available in multiple files:
- `README.md` - Main project documentation
- `test_ns3_blocksim/README.md` - Technical details
- `test_ns3_blocksim/README_IMPLEMENTATION_STATUS_EN.md` - Implementation status
- `test_ns3_blocksim/README_QUALITY_TOOLS.md` - Code quality tools documentation
- `SIMULATION_DETAILS.md` - Simulation details
- `BASESTATION_SIMULATION.md` - Base station simulation specifics

## 10. Languages

The project documentation is available in both English and Russian in various files.

## 11. Code Diagrams

```
                  +------------------------+
                  |   Simulation Manager   |
                  +------------------------+
                            |
                            v
        +--------------------------------------------+
        |                                            |
        v                                            v
+----------------+                         +-------------------+
| NS-3 Adapter   |<----- Integration ----->| BlockSim Adapter  |
+----------------+      Interface          +-------------------+
        |                                            |
        v                                            v
+----------------+                         +-------------------+
| MANET Models   |                         | Blockchain Models |
+----------------+                         +-------------------+
                                                   |
                             +--------------------+--------------------+
                             |                    |                    |
                             v                    v                    v
                     +-------------+     +----------------+    +--------------+
                     | Core        |     | Consensus      |    | Security     |
                     +-------------+     +----------------+    +--------------+
                                                |
                                                v
                                         +----------------+
                                         | Network        |
                                         +----------------+
```

This diagram illustrates the high-level architecture of the system, showing how the different components interact with each other through the integration interface.

