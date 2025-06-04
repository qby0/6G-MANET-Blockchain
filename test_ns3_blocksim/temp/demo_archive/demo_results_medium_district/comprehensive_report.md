# Cross-Zone Blockchain Simulation Report

## Executive Summary

This report presents the results of an advanced realistic cross-zone blockchain simulation 
that models real-world device parameters, energy consumption, and network dynamics.

### Key Findings

- **Total Devices**: 344
- **Simulation Duration**: 599 seconds (10.0 minutes)
- **Total Transactions**: 23,105
- **Confirmed Transactions**: 5,990
- **Success Rate**: 25.9%
- **Total Blocks**: 120
- **Device Uptime**: 100.0%

## Energy Analysis

### Overall Energy Consumption
- **Total Energy Consumed**: 913192171.4 mJ
- **Energy per Transaction**: 152452.8 mJ
- **Energy per Block**: 7609934.8 mJ

### Device Type Energy Breakdown
- **Smartphone**: 12253832.0 mJ across 200/200 devices
- **Iot Sensor**: 384813.0 mJ across 100/100 devices
- **Vehicle**: 900104936.4 mJ across 30/30 devices
- **Base Station 5G**: 92010.0 mJ across 3/3 devices
- **Small Cell**: 326340.0 mJ across 10/10 devices
- **Edge Server**: 30240.0 mJ across 1/1 devices

## Network Performance

### Zone Distribution
- **BRIDGE Zone**: 89 devices (25.9%)
- **5G Zone**: 201 devices (58.4%)
- **MANET Zone**: 54 devices (15.7%)

### Transaction Performance
- **Transaction Rate**: 2314.4 tx/min
- **Confirmed Rate**: 600.0 tx/min
- **Block Rate**: 12.0 blocks/min

### Consensus Performance
- **Average Consensus Time**: 1.20 seconds
- **Total Consensus Rounds**: 120

## Device Performance Analysis

### Mobile Device Battery Analysis
- **Smartphone**: Avg 95.5%, Min 95.2%
- **Iot Sensor**: Avg 99.7%, Min 99.7%

### Zone Transition Analysis
- **BRIDGE → TO → 5G**: 242 transitions
- **5G → TO → BRIDGE**: 233 transitions
- **MANET → TO → BRIDGE**: 28 transitions
- **MANET → TO → 5G**: 48 transitions
- **5G → TO → MANET**: 1 transitions
- **BRIDGE → TO → MANET**: 1 transitions

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
- **CPU Performance**: 9.127096851879127 GFLOPS
- **Memory**: 8 GB
- **Mobility**: pedestrian

#### Iot Sensor
- **Count**: 100
- **CPU Performance**: 0.5153573506449751 GFLOPS
- **Memory**: 0.5 GB
- **Mobility**: static

#### Vehicle
- **Count**: 30
- **CPU Performance**: 27.66670627978021 GFLOPS
- **Memory**: 8 GB
- **Mobility**: vehicular

#### Base Station 5G
- **Count**: 3
- **CPU Performance**: 1184.9413610715983 GFLOPS
- **Memory**: 64 GB
- **Mobility**: fixed

#### Small Cell
- **Count**: 10
- **CPU Performance**: 156.14190877384152 GFLOPS
- **Memory**: 8 GB
- **Mobility**: fixed

#### Edge Server
- **Count**: 1
- **CPU Performance**: 2468.4336310883964 GFLOPS
- **Memory**: 256 GB
- **Mobility**: fixed

## Conclusions

1. **Energy Efficiency**: The system achieved 152452.8 mJ per confirmed transaction
2. **Network Stability**: 100.0% device uptime demonstrates robust network operation
3. **Transaction Throughput**: 600.0 confirmed transactions per minute
4. **Consensus Performance**: Average consensus time of 1.20 seconds

## Recommendations

1. **Energy Optimization**: Focus on optimizing smartphone devices for better energy efficiency
2. **Zone Balancing**: Consider load balancing strategies for zone distribution
3. **Consensus Tuning**: Evaluate consensus parameters for optimal performance vs. security trade-offs

---
*Report generated on 2025-05-28 23:56:20*
