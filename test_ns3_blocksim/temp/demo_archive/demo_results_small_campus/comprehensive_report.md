# Cross-Zone Blockchain Simulation Report

## Executive Summary

This report presents the results of an advanced realistic cross-zone blockchain simulation 
that models real-world device parameters, energy consumption, and network dynamics.

### Key Findings

- **Total Devices**: 68
- **Simulation Duration**: 299 seconds (5.0 minutes)
- **Total Transactions**: 2,493
- **Confirmed Transactions**: 2,465
- **Success Rate**: 98.9%
- **Total Blocks**: 60
- **Device Uptime**: 100.0%

## Energy Analysis

### Overall Energy Consumption
- **Total Energy Consumed**: 77343718.5 mJ
- **Energy per Transaction**: 31376.8 mJ
- **Energy per Block**: 1289062.0 mJ

### Device Type Energy Breakdown
- **Smartphone**: 2250073.0 mJ across 40/40 devices
- **Iot Sensor**: 37165.5 mJ across 20/20 devices
- **Vehicle**: 75008990.0 mJ across 5/5 devices
- **Base Station 5G**: 15060.0 mJ across 1/1 devices
- **Small Cell**: 32430.0 mJ across 2/2 devices

## Network Performance

### Zone Distribution
- **5G Zone**: 55 devices (80.9%)
- **BRIDGE Zone**: 1 devices (1.5%)
- **MANET Zone**: 12 devices (17.6%)

### Transaction Performance
- **Transaction Rate**: 500.3 tx/min
- **Confirmed Rate**: 494.6 tx/min
- **Block Rate**: 12.0 blocks/min

### Consensus Performance
- **Average Consensus Time**: 1.30 seconds
- **Total Consensus Rounds**: 60

## Device Performance Analysis

### Mobile Device Battery Analysis
- **Smartphone**: Avg 97.7%, Min 97.6%
- **Iot Sensor**: Avg 99.8%, Min 99.8%

### Zone Transition Analysis
- **MANET → TO → 5G**: 16 transitions
- **BRIDGE → TO → 5G**: 22 transitions
- **MANET → TO → BRIDGE**: 1 transitions
- **5G → TO → BRIDGE**: 11 transitions

## Methodology

### Simulation Parameters
- **Scenario**: small_campus
- **Area**: 1 km²
- **Time Step**: 1 second
- **Consensus Interval**: 5 seconds
- **Maximum Block Size**: 50 transactions

### Device Models
The simulation uses realistic device parameters based on current technology:

#### Smartphone
- **Count**: 40
- **CPU Performance**: 10.317858399995 GFLOPS
- **Memory**: 8 GB
- **Mobility**: pedestrian

#### Iot Sensor
- **Count**: 20
- **CPU Performance**: 0.5144667933896792 GFLOPS
- **Memory**: 0.5 GB
- **Mobility**: static

#### Vehicle
- **Count**: 5
- **CPU Performance**: 29.806209375983997 GFLOPS
- **Memory**: 8 GB
- **Mobility**: vehicular

#### Base Station 5G
- **Count**: 1
- **CPU Performance**: 1205.4155397755812 GFLOPS
- **Memory**: 64 GB
- **Mobility**: fixed

#### Small Cell
- **Count**: 2
- **CPU Performance**: 161.1274321589187 GFLOPS
- **Memory**: 8 GB
- **Mobility**: fixed

## Conclusions

1. **Energy Efficiency**: The system achieved 31376.8 mJ per confirmed transaction
2. **Network Stability**: 100.0% device uptime demonstrates robust network operation
3. **Transaction Throughput**: 494.6 confirmed transactions per minute
4. **Consensus Performance**: Average consensus time of 1.30 seconds

## Recommendations

1. **Energy Optimization**: Focus on optimizing smartphone devices for better energy efficiency
2. **Zone Balancing**: Consider load balancing strategies for zone distribution
3. **Consensus Tuning**: Evaluate consensus parameters for optimal performance vs. security trade-offs

---
*Report generated on 2025-05-28 23:56:00*
