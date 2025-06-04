# Realistic Device Parameters for Cross-Zone Blockchain

## Overview
This document defines realistic technical parameters for devices in the 6G-MANET Cross-Zone Blockchain system, based on current and near-future technology specifications.

---

## 📱 **Mobile Devices (MANET Nodes)**

### **Smartphone Category (70% of devices)**
**Base Model: Modern Android/iPhone (2023-2025)**

#### **Hardware Specifications**
- **CPU**: Snapdragon 8 Gen 2 / Apple A16 Bionic
  - Processing Power: 8-12 GFLOPS
  - Cores: 8 (4 performance + 4 efficiency)
  - Clock Speed: 2.8-3.2 GHz (performance cores)
  - Cache: 6-8 MB L3
- **RAM**: 6-12 GB LPDDR5
- **Storage**: 128-512 GB UFS 4.0
- **GPU**: Adreno 740 / Apple GPU (5-6 cores)

#### **Network Capabilities**
- **5G**: Sub-6GHz and mmWave
  - Max Speed: 2-5 Gbps (mmWave), 100-400 Mbps (Sub-6)
  - Latency: 1-10ms
  - Range: 100-500m (Sub-6), 100-200m (mmWave)
- **WiFi**: 802.11ax (WiFi 6/6E)
  - Max Speed: 600-1200 Mbps
  - Range: 50-100m (indoor), 100-250m (outdoor)
  - Frequency: 2.4/5/6 GHz
- **Bluetooth**: 5.2/5.3
  - Range: 10-50m
  - Speed: 2-3 Mbps

#### **Battery & Power**
- **Capacity**: 3000-5000 mAh
- **Voltage**: 3.7V nominal
- **Energy**: 11-18.5 Wh
- **Idle Power**: 50-100 mW
- **Active Power**: 1-3W (normal), 5-8W (high load)
- **Radio Power**: 100-200 mW (WiFi), 200-500 mW (5G)
- **Battery Life**: 8-24 hours (usage dependent)

#### **Environmental Parameters**
- **Operating Temperature**: -10°C to +50°C
- **Humidity**: 5-95% RH
- **Altitude**: 0-3000m
- **Shock Resistance**: 1.5m drop
- **Water Resistance**: IP67/IP68

### **IoT Devices (20% of devices)**
**Base Model: ESP32/Raspberry Pi based sensors**

#### **Hardware Specifications**
- **CPU**: ARM Cortex-M4/A53
  - Processing Power: 0.1-1 GFLOPS
  - Cores: 1-4
  - Clock Speed: 240 MHz - 1.5 GHz
  - Cache: 512KB - 1MB
- **RAM**: 512KB - 4GB
- **Storage**: 4MB - 64GB
- **Power Management**: Deep sleep modes

#### **Network Capabilities**
- **WiFi**: 802.11n/ac
  - Max Speed: 150-300 Mbps
  - Range: 50-150m
- **Cellular**: LTE Cat-M1/NB-IoT
  - Speed: 1-10 Mbps
  - Range: 1-10 km
- **LoRa**: Long-range communication
  - Speed: 0.3-50 kbps
  - Range: 2-15 km

#### **Battery & Power**
- **Capacity**: 1000-5000 mAh
- **Energy**: 3.7-18.5 Wh
- **Idle Power**: 1-10 mW
- **Active Power**: 50-500 mW
- **Battery Life**: 1-10 years (depending on activity)

### **Vehicular Devices (10% of devices)**
**Base Model: Connected car units, drones**

#### **Hardware Specifications**
- **CPU**: ARM Cortex-A78/Intel Atom
  - Processing Power: 10-50 GFLOPS
  - Cores: 4-8
  - Clock Speed: 2.0-3.0 GHz
- **RAM**: 4-16 GB
- **Storage**: 32-500 GB SSD
- **GPU**: Integrated graphics

#### **Network Capabilities**
- **5G**: Full mmWave + Sub-6
  - Max Speed: 1-10 Gbps
  - Range: 200-1000m
- **V2X**: Dedicated Short Range Communications
  - Speed: 3-27 Mbps
  - Range: 300-1000m
- **Satellite**: Emergency backup
  - Speed: 1-100 Mbps
  - Global coverage

#### **Power Supply**
- **Vehicle**: 12V/24V DC (unlimited during operation)
- **Drone**: 7000-30000 mAh LiPo
  - Flight Time: 20-120 minutes
  - Power: 100-2000W

---

## 📡 **5G Base Stations**

### **Macro Cell Base Station**
**Model: Ericsson/Nokia/Huawei 5G gNodeB**

#### **Hardware Specifications**
- **Baseband Unit (BBU)**:
  - CPU: Intel Xeon Gold/ARM Neoverse
  - Cores: 16-32
  - Processing Power: 500-2000 GFLOPS
  - RAM: 32-128 GB DDR4/DDR5
  - Storage: 1-10 TB NVMe SSD
- **Remote Radio Head (RRH)**:
  - MIMO: 64T64R (massive MIMO)
  - Frequency: 3.5GHz, 28GHz, 39GHz
  - Power Output: 10-40W per channel

#### **Coverage & Performance**
- **Coverage Radius**: 1-35 km (frequency dependent)
  - Sub-6 GHz: 5-35 km
  - mmWave: 100-500m
- **Capacity**: 1000-10000 concurrent users
- **Throughput**: 1-20 Gbps aggregate
- **Latency**: 1-5ms
- **Backhaul**: 10-100 Gbps fiber

#### **Power Requirements**
- **Total Power**: 2-10 kW
- **Baseband**: 500-2000W
- **Radio**: 200-1000W per sector
- **Cooling**: 500-2000W
- **Backup**: 24-72 hours battery

### **Small Cell (Picocell/Femtocell)**
**Model: Dense urban deployment**

#### **Hardware Specifications**
- **CPU**: ARM Cortex-A78/Intel Atom
  - Cores: 4-8
  - Processing Power: 50-200 GFLOPS
  - RAM: 4-16 GB
  - Storage: 32-256 GB
- **Radio**: 2T2R/4T4R MIMO
  - Power Output: 1-10W

#### **Coverage & Performance**
- **Coverage Radius**: 10-200m
- **Capacity**: 10-200 concurrent users
- **Throughput**: 100 Mbps - 2 Gbps
- **Backhaul**: 1-10 Gbps

#### **Power Requirements**
- **Total Power**: 20-200W
- **PoE**: 30-90W typical
- **Backup**: 4-8 hours

---

## 🌐 **Edge Computing Nodes**

### **Multi-Access Edge Computing (MEC)**
**Model: Dell/HPE/Cisco edge servers**

#### **Hardware Specifications**
- **CPU**: Intel Xeon/AMD EPYC
  - Cores: 16-64
  - Processing Power: 1000-5000 GFLOPS
  - RAM: 64-512 GB DDR4/DDR5
  - Storage: 1-50 TB NVMe SSD
- **GPU**: NVIDIA T4/A100 (optional)
  - CUDA Cores: 2560-6912
  - AI Performance: 65-312 TOPS
- **Network**: 10/25/100 GbE

#### **Performance Metrics**
- **Latency**: 1-10ms to users
- **Throughput**: 10-100 Gbps
- **Concurrent VMs**: 50-500
- **Service Radius**: 1-10 km

#### **Power & Environment**
- **Power**: 500-5000W
- **Cooling**: Rack-mounted with active cooling
- **Reliability**: 99.99% uptime
- **Backup**: UPS + generator

---

## ⚡ **Blockchain-Specific Parameters**

### **Cryptographic Performance**
#### **Signature Generation/Verification (ECDSA P-256)**
- **Smartphone**: 100-500 signatures/sec, 200-1000 verifications/sec
- **IoT Device**: 10-50 signatures/sec, 20-100 verifications/sec
- **Base Station**: 5000-20000 signatures/sec, 10000-40000 verifications/sec
- **Edge Node**: 10000-50000 signatures/sec, 20000-100000 verifications/sec

#### **Hash Operations (SHA-256)**
- **Smartphone**: 50-200 MB/s
- **IoT Device**: 5-20 MB/s
- **Base Station**: 500-2000 MB/s
- **Edge Node**: 1000-5000 MB/s

### **Consensus Parameters**
#### **PBFT Consensus**
- **Message Complexity**: O(n²) per round
- **Round Time**: 100ms - 2s (network dependent)
- **Fault Tolerance**: f < n/3 Byzantine nodes
- **Memory per Node**: 1-10 MB per consensus round

#### **Validator Requirements**
- **Minimum Stake**: Device-dependent
  - Smartphone: Medium stake
  - IoT: Low stake
  - Vehicle: High stake
  - Base Station: Highest stake
- **Performance Scoring**: CPU + Network + Uptime + Battery

---

## 📊 **Mobility Parameters**

### **Movement Patterns**
#### **Pedestrian (Smartphone)**
- **Speed**: 0-7 km/h
- **Pattern**: Random walk, hotspot clustering
- **Pause Time**: 10s - 10min
- **Direction Change**: Every 30s - 5min

#### **Vehicular**
- **Speed**: 0-120 km/h
- **Pattern**: Road-constrained, highway/urban
- **Acceleration**: -5 to +3 m/s²
- **Turn Rate**: Max 30°/s

#### **Static IoT**
- **Movement**: 0 km/h (sensors, infrastructure)
- **Micro-mobility**: ±1m (environmental factors)

### **Zone Transition Thresholds**
#### **RSSI-based Zone Detection**
- **5G Zone**: RSSI > -90 dBm
- **Bridge Zone**: -110 dBm < RSSI < -90 dBm
- **MANET Zone**: RSSI < -110 dBm
- **Hysteresis**: ±5 dBm to prevent ping-ponging

#### **Handover Parameters**
- **Measurement Period**: 100-500ms
- **Decision Time**: 10-50ms
- **Execution Time**: 20-100ms
- **Total Handover Time**: 130-650ms

---

## 🔋 **Energy Consumption Models**

### **Power Consumption Breakdown**

#### **Smartphone (per operation)**
- **Idle**: 50-100 mW
- **CPU (blockchain)**: 500-1500 mW
- **WiFi Tx**: 200-400 mW
- **5G Tx**: 400-800 mW
- **Display**: 200-1000 mW
- **GPS**: 50-150 mW

#### **Transaction Energy Cost**
- **Signature**: 0.1-0.5 mJ
- **Hash**: 0.01-0.05 mJ
- **Network Tx**: 1-10 mJ
- **Storage Write**: 0.1-1 mJ
- **Total per Tx**: 2-20 mJ

### **Battery Life Estimation**
#### **Blockchain Participation Impact**
- **Light Node**: -5 to -15% battery life
- **Validator Node**: -15 to -30% battery life
- **Heavy Usage**: -30 to -50% battery life

---

## 🌍 **Environmental Conditions**

### **Urban Environment (60% scenarios)**
- **Building Density**: High (>500 buildings/km²)
- **Path Loss Exponent**: 3.5-4.5
- **Shadowing**: 8-12 dB std dev
- **Interference**: High (-80 to -60 dBm)
- **Node Density**: 1000-10000 nodes/km²

### **Suburban Environment (30% scenarios)**
- **Building Density**: Medium (100-500 buildings/km²)
- **Path Loss Exponent**: 3.0-3.8
- **Shadowing**: 6-10 dB std dev
- **Interference**: Medium (-90 to -70 dBm)
- **Node Density**: 100-1000 nodes/km²

### **Rural Environment (10% scenarios)**
- **Building Density**: Low (<100 buildings/km²)
- **Path Loss Exponent**: 2.5-3.2
- **Shadowing**: 4-8 dB std dev
- **Interference**: Low (-100 to -80 dBm)
- **Node Density**: 10-100 nodes/km²

---

## 🛠️ **Implementation Parameters**

### **Configuration Templates**

#### **Smartphone Config**
```json
{
  "device_type": "smartphone",
  "cpu_cores": 8,
  "cpu_freq_ghz": 2.8,
  "ram_gb": 8,
  "storage_gb": 256,
  "battery_mah": 4000,
  "radio_types": ["5g", "wifi", "bluetooth"],
  "max_tx_power_dbm": {
    "5g": 23,
    "wifi": 20,
    "bluetooth": 10
  },
  "energy_per_tx_mj": 5,
  "signatures_per_sec": 200,
  "movement": {
    "type": "pedestrian",
    "max_speed_kmh": 7,
    "pause_time_range": [10, 600]
  }
}
```

#### **Base Station Config**
```json
{
  "device_type": "base_station",
  "coverage_radius_m": 1000,
  "max_users": 5000,
  "throughput_gbps": 10,
  "power_consumption_w": 5000,
  "backup_hours": 48,
  "latency_ms": 2,
  "frequencies_ghz": [3.5, 28],
  "mimo_config": "64T64R",
  "processing_power_gflops": 1000
}
```

#### **IoT Device Config**
```json
{
  "device_type": "iot_sensor",
  "cpu_freq_mhz": 240,
  "ram_kb": 512,
  "battery_mah": 2000,
  "expected_lifetime_years": 5,
  "duty_cycle_percent": 1,
  "tx_interval_sec": 3600,
  "radio_types": ["wifi", "lora"],
  "movement": {
    "type": "static",
    "max_speed_kmh": 0
  }
}
```

### **Performance Benchmarks**
- **Transaction Throughput**: 100-10,000 tx/s (system-wide)
- **Block Time**: 1-10 seconds
- **Consensus Latency**: 0.5-2 seconds
- **Zone Handover**: <500ms
- **Energy per Transaction**: 1-50 mJ
- **Network Availability**: >99.9%

---

## 📈 **Scaling Parameters**

### **Network Size Scenarios**
- **Small**: 10-50 nodes, 1 base station
- **Medium**: 100-500 nodes, 3-5 base stations
- **Large**: 1000-5000 nodes, 10-20 base stations
- **Extra Large**: 10000+ nodes, 50+ base stations

### **Geographic Coverage**
- **Campus**: 1-4 km²
- **District**: 10-50 km²
- **City**: 100-1000 km²
- **Metropolitan**: 1000-10000 km²

### **Performance Scaling**
- **Linear Scaling**: Transaction throughput, storage
- **Logarithmic Scaling**: Consensus latency, routing overhead
- **Constant**: Individual device performance

---

## 💡 **Key Insights & Recommendations**

1. **Device Heterogeneity**: Wide range of capabilities requires adaptive protocols
2. **Energy Constraints**: Critical for IoT and mobile devices
3. **Network Dynamics**: High mobility requires fast handovers
4. **Performance Variance**: 1000x difference between IoT and edge nodes
5. **Realistic Expectations**: Balance functionality with device limitations

These parameters provide a realistic foundation for simulation, development, and performance evaluation of the cross-zone blockchain system. 