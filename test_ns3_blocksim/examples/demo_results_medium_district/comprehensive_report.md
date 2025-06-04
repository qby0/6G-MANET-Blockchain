# Cross-Zone Blockchain Simulation Report

## Executive Summary

This report presents the results of an advanced realistic cross-zone blockchain simulation 
that models real-world device parameters, energy consumption, and network dynamics.

### Key Findings

- **Total Devices**: 344
- **Simulation Duration**: 599 seconds (10.0 minutes)
- **Total Transactions**: 21,847
- **Confirmed Transactions**: 5,992
- **Success Rate**: 27.4%
- **Total Blocks**: 120
- **Device Uptime**: 100.0%

## Energy Analysis

### Overall Energy Consumption
- **Total Energy Consumed**: 913155190.4 mJ
- **Energy per Transaction**: 152395.7 mJ
- **Energy per Block**: 7609626.6 mJ

### Device Type Energy Breakdown
- **Smartphone**: 12239625.0 mJ across 200/200 devices
- **Iot Sensor**: 384303.0 mJ across 100/100 devices
- **Vehicle**: 900082372.4 mJ across 30/30 devices
- **Base Station 5G**: 91470.0 mJ across 3/3 devices
- **Small Cell**: 327240.0 mJ across 10/10 devices
- **Edge Server**: 30180.0 mJ across 1/1 devices

## Network Performance

### Zone Distribution
- **MANET Zone**: 58 devices (16.9%)
- **5G Zone**: 170 devices (49.4%)
- **BRIDGE Zone**: 116 devices (33.7%)

### Transaction Performance
- **Transaction Rate**: 2188.3 tx/min
- **Confirmed Rate**: 600.2 tx/min
- **Block Rate**: 12.0 blocks/min

### Consensus Performance
- **Average Consensus Time**: 1.24 seconds
- **Total Consensus Rounds**: 120

## Device Performance Analysis

### Mobile Device Battery Analysis
- **Smartphone**: Avg 95.5%, Min 95.2%
- **Iot Sensor**: Avg 99.7%, Min 99.7%

### Zone Transition Analysis
- **BRIDGE → TO → MANET**: 70 transitions
- **BRIDGE → TO → 5G**: 79 transitions
- **5G → TO → BRIDGE**: 90 transitions
- **MANET → TO → BRIDGE**: 96 transitions
- **MANET → TO → 5G**: 41 transitions
- **5G → TO → MANET**: 3 transitions

## Methodology

### Simulation Parameters
- **Scenario**: medium_district
- **Area**: 9 km²
- **Time Step**: 1 second
- **Consensus Interval**: 5 seconds
- **Maximum Block Size**: 50 transactions

### Device Models
The simulation uses realistic device parameters based on current technology:

#### Smartphone
- **Count**: 200
- **CPU Performance**: 9.860119427124546 GFLOPS
- **Memory**: 8 GB
- **Mobility**: pedestrian

#### Iot Sensor
- **Count**: 100
- **CPU Performance**: 0.4864955012041205 GFLOPS
- **Memory**: 0.5 GB
- **Mobility**: static

#### Vehicle
- **Count**: 30
- **CPU Performance**: 31.86080759115695 GFLOPS
- **Memory**: 8 GB
- **Mobility**: vehicular

#### Base Station 5G
- **Count**: 3
- **CPU Performance**: 1212.3624059752512 GFLOPS
- **Memory**: 64 GB
- **Mobility**: fixed

#### Small Cell
- **Count**: 10
- **CPU Performance**: 136.55508783462582 GFLOPS
- **Memory**: 8 GB
- **Mobility**: fixed

#### Edge Server
- **Count**: 1
- **CPU Performance**: 2495.8586386962197 GFLOPS
- **Memory**: 256 GB
- **Mobility**: fixed

## Conclusions

1. **Energy Efficiency**: The system achieved 152395.7 mJ per confirmed transaction
2. **Network Stability**: 100.0% device uptime demonstrates robust network operation
3. **Transaction Throughput**: 600.2 confirmed transactions per minute
4. **Consensus Performance**: Average consensus time of 1.24 seconds

## Recommendations

1. **Energy Optimization**: Focus on optimizing smartphone devices for better energy efficiency
2. **Zone Balancing**: Consider load balancing strategies for zone distribution
3. **Consensus Tuning**: Evaluate consensus parameters for optimal performance vs. security trade-offs

---
*Report generated on 2025-05-29 00:29:05*
