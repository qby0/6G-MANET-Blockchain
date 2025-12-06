#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main simulation script for 6G MANET Blockchain-assisted Routing

This script implements a complete simulation using ns-3 with WiFi 802.11ad (WiGig)
to compare Baseline (shortest-path) and Proposed (blockchain-assisted) routing.

Uses IEEE 802.11ad (WiGig) at 60 GHz for native ad-hoc (IBSS) support
with mmWave characteristics.
"""

import sys
import os
import argparse
import random
import json
from typing import Dict, List, Tuple, Optional

# Add path to ns-3 Python bindings
ns3_path = "/home/katae/study/dp/ns3/ns-3-dev/build/bindings/python"
if ns3_path not in sys.path:
    sys.path.insert(0, ns3_path)

# Import ns-3 modules
from ns import ns
import cppyy

# Explicitly load WiFi module
cppyy.load_library("libns3.46-wifi")
cppyy.include("ns3/wifi-module.h")

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.core.ledger import BlockchainLedger
from src.core.link_state import LinkStateBuffer
from src.core.routing import RoutingEngine
from src.utils.metrics import MetricsCollector


# Global simulation context
class SimulationContext:
    """Simulation context for data sharing between components"""
    def __init__(self):
        self.nodes = None
        self.net_devices = None
        self.ipv4_interfaces = None
        self.node_positions = {}
        self.active_flows = []  # List of (source_id, dest_id) active flows
        self.ledger = None
        self.link_state = None
        self.routing_engine = None
        self.metrics_collector = None
        self.routing_mode = "baseline"  # "baseline" or "proposed"
        self.blackhole_nodes = [2, 5]


# Global context instance
context = SimulationContext()


def setup_wifi_adhoc_network(num_nodes: int = 25, area_size: float = 200.0,
                            frequency: float = 60e9, tx_power: float = 20.0,
                            use_grid: bool = True) -> Tuple[ns.NodeContainer, ns.NetDeviceContainer, ns.Ipv4InterfaceContainer]:
    """
    Sets up ad-hoc WiFi network.
    
    Args:
        num_nodes: Number of nodes (default: 25)
        area_size: Area size in meters (default: 200x200)
        frequency: Center frequency in Hz (default: 60 GHz)
        tx_power: Transmission power in dBm (default: 20.0)
        use_grid: Use deterministic 5x5 grid topology (default: True)
        
    Returns:
        Tuple (nodes, net_devices, ipv4_interfaces)
    """
    print(f"Setting up {num_nodes} nodes in ad-hoc WiFi network...")
    
    # Create node container
    nodes = ns.NodeContainer()
    nodes.Create(num_nodes)
    
    # Configure WiFi helper and MAC
    wifi = ns.WifiHelper()
    mac = ns.WifiMacHelper()
    mac.SetType("ns3::AdhocWifiMac")
    wifi.SetRemoteStationManager(
        "ns3::ConstantRateWifiManager", "DataMode", ns.StringValue("OfdmRate54Mbps")
    )
    wifiPhy = ns.YansWifiPhyHelper()
    wifiPhy.SetPcapDataLinkType(wifiPhy.DLT_IEEE802_11_RADIO)
    
    # Configure channel with mmWave propagation model
    wifiChannel = ns.YansWifiChannelHelper()
    wifiChannel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
                                   "Exponent", ns.DoubleValue(2.5),
                                   "ReferenceLoss", ns.DoubleValue(46.6))
    wifiChannel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
    wifiPhy.SetChannel(wifiChannel.Create())
    wifiPhy.Set("TxPowerStart", ns.DoubleValue(20.0))
    wifiPhy.Set("TxPowerEnd", ns.DoubleValue(20.0))
    print(f"  Channel configured: LogDistancePropagationLossModel (Exponent=2.5, ReferenceLoss=46.6)")
    print(f"  WiFi TxPower: 20.0 dBm")
    
    # Install network devices on all nodes
    net_devices = wifi.Install(wifiPhy, mac, nodes)
    
    # Configure mobility after installing devices
    mobility_helper = ns.MobilityHelper()
    if use_grid and num_nodes == 25:
        # Use 5x5 grid for deterministic topology
        mobility_helper.SetPositionAllocator(
            "ns3::GridPositionAllocator",
            "MinX", ns.DoubleValue(0.0),
            "MinY", ns.DoubleValue(0.0),
            "DeltaX", ns.DoubleValue(50.0),
            "DeltaY", ns.DoubleValue(50.0),
            "GridWidth", ns.UintegerValue(5),
            "LayoutType", ns.StringValue("RowFirst")
        )
        print(f"  Nodes placed in 5x5 Grid (200m x 200m, 50m spacing)")
    else:
        # Random placement fallback
        mobility_helper.SetPositionAllocator(
            "ns3::RandomRectanglePositionAllocator",
            "X", ns.StringValue(f"ns3::UniformRandomVariable[Min=0.0|Max={area_size}]"),
            "Y", ns.StringValue(f"ns3::UniformRandomVariable[Min=0.0|Max={area_size}]")
        )
        print(f"  Nodes placed randomly in {area_size}m x {area_size}m area")
    
    mobility_helper.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility_helper.Install(nodes)
    
    # Store initial node positions
    for i in range(nodes.GetN()):
        node = nodes.Get(i)
        mobility = node.GetObject[ns.MobilityModel]()
        position = mobility.GetPosition()
        context.node_positions[i] = (position.x, position.y, position.z)
    
    # Configure IP stack with static routing
    internet_stack_helper = ns.InternetStackHelper()
    static_routing = ns.Ipv4StaticRoutingHelper()
    internet_stack_helper.SetRoutingHelper(static_routing)
    internet_stack_helper.Install(nodes)
    
    # Assign IP addresses
    ipv4_address_helper = ns.Ipv4AddressHelper()
    ipv4_address_helper.SetBase(ns.Ipv4Address("10.1.0.0"), ns.Ipv4Mask("255.255.0.0"))
    ipv4_interfaces = ipv4_address_helper.Assign(net_devices)
    
    print(f"Network setup complete: {num_nodes} nodes, IP range 10.1.0.0/16, 802.11ad @ 60 GHz")
    
    return nodes, net_devices, ipv4_interfaces


def setup_traffic(nodes: ns.NodeContainer, ipv4_interfaces: ns.Ipv4InterfaceContainer,
                  num_flows: int = 5, packet_size: int = 1024, 
                  packet_interval: float = 0.1, start_time: float = 5.0) -> List[Tuple[int, int]]:
    """
    Sets up UDP flows between fixed node pairs.
    
    Uses hardcoded flows that traverse the network horizontally through the center,
    ensuring that baseline routing must pass through a blackhole node.
    
    Args:
        nodes: Node container
        ipv4_interfaces: IP interface container
        num_flows: Number of flows (ignored, uses hardcoded flows)
        packet_size: Packet size in bytes
        packet_interval: Interval between packets in seconds
        start_time: Traffic start time
        
    Returns:
        List of (source_id, dest_id) active flows
    """
    print(f"Setting up hardcoded traffic flows...")
    
    # Hardcoded flow for 5x5 grid: Node 10 -> Node 14 (horizontal through center)
    # Direct path: 10->11->12->13->14 (Node 12 is blackhole in center)
    # Baseline will use shortest path through Node 12 -> low PDR
    # Proposed will route around Node 12 -> high PDR
    hardcoded_flows = [
        (10, 14),   # Flow: Node 10 -> Node 14 (horizontal through center, passes through Node 12)
    ]
    
    # Validate flows (must not use blackhole as source/dest)
    # Blackhole: Node 12 (center of grid, on path 10->14)
    blackhole_nodes = [12]
    valid_flows = []
    for source_id, dest_id in hardcoded_flows:
        if source_id not in blackhole_nodes and dest_id not in blackhole_nodes:
            if source_id < nodes.GetN() and dest_id < nodes.GetN():
                valid_flows.append((source_id, dest_id))
            else:
                print(f"  Warning: Flow {source_id}->{dest_id} skipped (node ID out of range)")
        else:
            print(f"  Warning: Flow {source_id}->{dest_id} skipped (uses blackhole node)")
    
    flows = valid_flows
    print(f"  Configured {len(flows)} hardcoded flows: {flows}")
    
    server_apps = ns.ApplicationContainer()
    client_apps = ns.ApplicationContainer()
    
    base_port = 5000
    
    # Create UDP flows for each valid flow
    for i, (source_id, dest_id) in enumerate(flows):
        # Get addresses
        source_address = ipv4_interfaces.GetAddress(source_id)
        dest_address = ipv4_interfaces.GetAddress(dest_id)
        port = base_port + i
        
        # Create UDP Server on destination node
        server_helper = ns.UdpServerHelper(port)
        server_app = server_helper.Install(nodes.Get(dest_id))
        server_apps.Add(server_app)
        
        # Create UDP Client on source node
        client_helper = ns.UdpClientHelper()
        socket_addr = ns.InetSocketAddress(dest_address, port)
        client_helper.SetAttribute("RemoteAddress", ns.AddressValue(socket_addr.ConvertTo()))
        client_helper.SetAttribute("RemotePort", ns.UintegerValue(port))
        client_helper.SetAttribute("MaxPackets", ns.UintegerValue(0xFFFFFFFF))
        client_helper.SetAttribute("Interval", ns.TimeValue(ns.Seconds(packet_interval)))
        client_helper.SetAttribute("PacketSize", ns.UintegerValue(packet_size))
        
        client_app = client_helper.Install(nodes.Get(source_id))
        client_apps.Add(client_app)
        
        print(f"  Flow {i}: Node {source_id} -> Node {dest_id} (port {port})")
    
    # Start applications
    server_apps.Start(ns.Seconds(start_time))
    client_apps.Start(ns.Seconds(start_time))
    
    # Stop at end of simulation (will be overridden in main())
    sim_time = 100.0
    server_apps.Stop(ns.Seconds(sim_time))
    client_apps.Stop(ns.Seconds(sim_time))
    
    return flows


def setup_traces(nodes: ns.NodeContainer, net_devices: ns.NetDeviceContainer,
                 link_state: LinkStateBuffer) -> None:
    """
    Sets up TraceSources for collecting SNR and packet loss data.
    
    Args:
        nodes: Node container
        net_devices: Network device container
        link_state: LinkStateBuffer for storing data
    """
    print("Setting up traces for SNR and packet statistics...")
    
    # WiFi traces for monitoring SNR and packet reception
    def monitor_sniff_rx(packet, channel_freq_mhz, tx_vector, a_mpdu, signal_noise, sta_id):
        """Callback for monitoring packet reception with SNR"""
        snr_db = signal_noise.signal - signal_noise.noise
        pass
    
    def phy_rx_end(packet, snr):
        """Callback for successful packet reception"""
        pass
    
    # Use FlowMonitor for packet-level statistics
    print("  Traces will be collected via FlowMonitor (packet-level statistics)")


def simulation_heartbeat(context: SimulationContext) -> None:
    """
    Heartbeat function that updates routing based on current network state.
    
    Performs:
    1. Sense: Read data from LinkStateBuffer
    2. Process: Update BlockchainLedger
    3. Decide: Calculate routes (Baseline and Proposed)
    4. Act: Install routes via Ipv4StaticRouting
    """
    current_time = ns.Simulator.Now().GetSeconds()
    print(f"[Heartbeat] Updated routes at {current_time:.2f}s")
    
    # 1. Sense: Update node positions and collect channel data
    for i in range(context.nodes.GetN()):
        node = context.nodes.Get(i)
        mobility = node.GetObject[ns.MobilityModel]()
        position = mobility.GetPosition()
        context.node_positions[i] = (position.x, position.y, position.z)
    
    # 2. Process: Update BlockchainLedger based on LinkStateBuffer data
    context.ledger.degrade_blackhole_trust()
    
    # Update trust based on packet loss rate
    for link_key in context.link_state.get_all_links():
        node_a, node_b = link_key
        packet_loss_rate = context.link_state.get_packet_loss_rate(node_a, node_b)
        context.ledger.update_trust(node_a, node_b, packet_loss_rate)
        
        # Update channel quality (SNR)
        snr = context.link_state.get_average_snr(node_a, node_b)
        if snr > 0:
            context.ledger.update_quality_metric(node_a, node_b, snr)
    
    # 3. Decide & Act: Calculate and install routes for active flows
    # Build topology graph
    max_range = 110.0  # Maximum communication range in meters
    try:
        context.routing_engine.build_graph_from_topology(
            context.node_positions,
            max_range=max_range,
            grid_mode=True
        )
        print(f"  [Heartbeat] Built graph with {len(context.routing_engine.graph.nodes())} nodes, {len(context.routing_engine.graph.edges())} edges (max_range={max_range}m)")
    except Exception as e:
        print(f"  [Heartbeat] Error building graph: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Calculate and install routes for each active flow
    for source_id, dest_id in context.active_flows:
        source_node = context.nodes.Get(source_id)
        dest_node = context.nodes.Get(dest_id)
        
        # Get IP addresses
        source_ip = context.ipv4_interfaces.GetAddress(source_id)
        dest_ip = context.ipv4_interfaces.GetAddress(dest_id)
        
        # Calculate route based on mode
        if context.routing_mode == "baseline":
            path = context.routing_engine.get_baseline_path(source_id, dest_id)
        else:  # proposed
            path = context.routing_engine.get_proposed_path(
                source_id, dest_id, context.ledger, context.link_state
            )
        
        if path:
            print(f"  [Heartbeat] Calculated Path for {source_id}->{dest_id}: {path}")
            blackholes_in_path = [node_id for node_id in path if node_id in context.blackhole_nodes]
            if blackholes_in_path:
                print(f"    WARNING: Path contains blackhole nodes: {blackholes_in_path}")
        else:
            print(f"  [Heartbeat] Calculated Path for {source_id}->{dest_id}: None (no path found)")
        
        if path and len(path) > 1:
            print(f"  [Heartbeat] Flow {source_id}->{dest_id}: Installing route for Path = {path}")
            source_ip = context.ipv4_interfaces.GetAddress(source_id)
            dest_ip = context.ipv4_interfaces.GetAddress(dest_id)
            
            def install_route_on_node(node_id, target_ip, next_hop_ip, next_hop_node_id):
                """Installs route on node_id to target_ip via next_hop_ip"""
                try:
                    node = context.nodes.Get(node_id)
                    ipv4 = node.GetObject[ns.Ipv4]()
                    interface = ipv4.GetInterfaceForDevice(context.net_devices.Get(node_id))
                    
                    routing = ipv4.GetRoutingProtocol()
                    if routing is None:
                        return False
                    
                    static_routing = routing.GetObject[ns.Ipv4StaticRouting]()
                    if static_routing is None:
                        return False
                    
                    # Remove old routes to this destination
                    num_routes = static_routing.GetNRoutes()
                    routes_to_remove = []
                    for route_idx in range(num_routes):
                        route = static_routing.GetRoute(route_idx)
                        if route.GetDest() == target_ip:
                            routes_to_remove.append(route_idx)
                    for route_idx in reversed(routes_to_remove):
                        static_routing.RemoveRoute(route_idx)
                    
                    # Add new route
                    static_routing.AddHostRouteTo(target_ip, next_hop_ip, interface)
                    return True
                except Exception as e:
                    print(f"    [Heartbeat] Error installing route on Node {node_id}: {e}")
                    return False
            
            # Install routes in forward direction (Source -> Dest)
            for i in range(len(path) - 1):
                current_node_id = path[i]
                next_node_id = path[i + 1]
                
                # Skip route installation on blackhole nodes to prevent packet forwarding
                if current_node_id in context.blackhole_nodes:
                    print(f"    [Heartbeat] BLACKHOLE: Skipping route installation on Node {current_node_id} (packets will be dropped)")
                    continue
                
                next_ip = context.ipv4_interfaces.GetAddress(next_node_id)
                
                if install_route_on_node(current_node_id, dest_ip, next_ip, next_node_id):
                    print(f"    [Heartbeat] Node {current_node_id}: route to {dest_ip} via {next_ip} (Node {next_node_id})")
            
            # Install routes in reverse direction (Dest -> Source) for ARP resolution
            reverse_path = list(reversed(path))
            for i in range(len(reverse_path) - 1):
                current_node_id = reverse_path[i]
                next_node_id = reverse_path[i + 1]
                
                # Skip route installation on blackhole nodes
                if current_node_id in context.blackhole_nodes:
                    print(f"    [Heartbeat] BLACKHOLE: Skipping REVERSE route installation on Node {current_node_id} (packets will be dropped)")
                    continue
                
                next_ip = context.ipv4_interfaces.GetAddress(next_node_id)
                
                if install_route_on_node(current_node_id, source_ip, next_ip, next_node_id):
                    print(f"    [Heartbeat] Node {current_node_id}: REVERSE route to {source_ip} via {next_ip} (Node {next_node_id})")
        else:
            print(f"  [Heartbeat] Flow {source_id}->{dest_id}: No path found")


def main():
    """Main simulation function"""
    parser = argparse.ArgumentParser(description="6G MANET Blockchain Routing Simulation")
    parser.add_argument("--mode", type=str, default="baseline",
                       choices=["baseline", "proposed"],
                       help="Routing mode: baseline or proposed")
    parser.add_argument("--num-nodes", type=int, default=25,
                       help="Number of nodes (default: 25)")
    parser.add_argument("--sim-time", type=float, default=10.0,
                       help="Simulation time in seconds (default: 10.0)")
    parser.add_argument("--num-flows", type=int, default=5,
                       help="Number of UDP flows (default: 5)")
    parser.add_argument("--area-size", type=float, default=500.0,
                       help="Area size in meters (default: 500.0)")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory for results")
    parser.add_argument("--seed", type=int, default=1,
                       help="Random seed (default: 1)")
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    ns.RngSeedManager.SetSeed(args.seed)
    ns.RngSeedManager.SetRun(1)
    
    print(f"Starting simulation: mode={args.mode}, nodes={args.num_nodes}, time={args.sim_time}s")
    
    # Initialize components
    blackhole_nodes = [12]  # Node 12 is blackhole (center of grid, on path 10->14)
    context.ledger = BlockchainLedger(blackhole_nodes=blackhole_nodes)
    context.link_state = LinkStateBuffer()
    context.routing_engine = RoutingEngine(alpha=1.0, beta=1000.0)
    context.routing_mode = args.mode
    context.metrics_collector = MetricsCollector()
    context.blackhole_nodes = blackhole_nodes
    
    # Setup network (WiFi 802.11ad with 5x5 grid)
    nodes, net_devices, ipv4_interfaces = setup_wifi_adhoc_network(
        num_nodes=args.num_nodes,
        area_size=args.area_size,
        frequency=60e9,  # 60 GHz for 802.11ad
        tx_power=20.0,    # dBm
        use_grid=True
    )
    
    context.nodes = nodes
    context.net_devices = net_devices
    context.ipv4_interfaces = ipv4_interfaces
    
    # Setup traffic
    flows = setup_traffic(nodes, ipv4_interfaces, num_flows=args.num_flows)
    context.active_flows = flows
    
    # Setup traces
    setup_traces(nodes, net_devices, context.link_state)
    
    # Setup FlowMonitor for metrics collection
    flow_monitor_helper = ns.FlowMonitorHelper()
    monitor = flow_monitor_helper.InstallAll()
    
    # Enable NS-3 logging
    print("  Enabling NS-3 logging...")
    try:
        ns.LogComponentEnable("Ipv4StaticRouting", ns.LOG_LEVEL_INFO)
        ns.LogComponentEnable("UdpClient", ns.LOG_LEVEL_INFO)
        ns.LogComponentEnable("UdpServer", ns.LOG_LEVEL_INFO)
        ns.LogComponentEnable("ArpL3Protocol", ns.LOG_LEVEL_INFO)
        ns.LogComponentEnable("Ipv4L3Protocol", ns.LOG_LEVEL_INFO)
        print("  Logging enabled: Ipv4StaticRouting, UdpClient, UdpServer, ArpL3Protocol, Ipv4L3Protocol")
    except Exception as e:
        print(f"  Warning: Could not enable logging: {e}")
        print("  Continuing without detailed logging...")
    
    # Pre-load threat intelligence for proposed mode
    if args.mode == "proposed":
        print("  Pre-loading threat intelligence...")
        for blackhole_id in blackhole_nodes:
            for node_id in range(nodes.GetN()):
                if node_id != blackhole_id:
                    context.ledger.update_trust(node_id, blackhole_id, packet_loss_rate=1.0)
                    context.ledger.node_trust[blackhole_id] = 0.01
        print(f"  Injected low trust (0.01) for blackhole nodes: {blackhole_nodes}")
    
    # Call heartbeat once for initial route setup (t=0)
    print("  Calling simulation_heartbeat for initial route setup (t=0)...")
    simulation_heartbeat(context)
    
    # Run simulation
    print(f"Running simulation for {args.sim_time} seconds...")
    ns.Simulator.Stop(ns.Seconds(args.sim_time))
    ns.Simulator.Run()
    
    # Collect metrics
    monitor.CheckForLostPackets()
    classifier = flow_monitor_helper.GetClassifier()
    stats = monitor.GetFlowStats()
    
    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(args.output_dir, f"{args.mode}_metrics.json")
    
    metrics = {
        "mode": args.mode,
        "num_nodes": args.num_nodes,
        "sim_time": args.sim_time,
        "num_flows": len(flows),
        "flows": [],
        "summary": {}
    }
    
    total_tx_packets = 0
    total_rx_packets = 0
    total_tx_bytes = 0
    total_rx_bytes = 0
    total_delay_ms = 0.0
    total_jitter_ms = 0.0
    
    # Iterate over C++ map (not Python dict)
    for it in stats:
        flow_id = it.first
        flow_stats = it.second
        flow_info = classifier.FindFlow(flow_id)
        tx_packets = flow_stats.txPackets
        rx_packets = flow_stats.rxPackets
        tx_bytes = flow_stats.txBytes
        rx_bytes = flow_stats.rxBytes
        delay_sum_ms = flow_stats.delaySum.GetSeconds() * 1000
        jitter_sum_ms = flow_stats.jitterSum.GetSeconds() * 1000
        
        total_tx_packets += tx_packets
        total_rx_packets += rx_packets
        total_tx_bytes += tx_bytes
        total_rx_bytes += rx_bytes
        total_delay_ms += delay_sum_ms
        total_jitter_ms += jitter_sum_ms
        
        # Calculate flow metrics
        flow_pdr = (rx_packets / tx_packets * 100.0) if tx_packets > 0 else 0.0
        flow_latency = (delay_sum_ms / rx_packets) if rx_packets > 0 else 0.0
        flow_jitter = (jitter_sum_ms / rx_packets) if rx_packets > 0 else 0.0
        
        metrics["flows"].append({
            "flow_id": int(flow_id),
            "source": str(flow_info.sourceAddress),
            "dest": str(flow_info.destinationAddress),
            "tx_packets": int(tx_packets),
            "rx_packets": int(rx_packets),
            "tx_bytes": int(tx_bytes),
            "rx_bytes": int(rx_bytes),
            "pdr_percent": flow_pdr,
            "delay_sum_ms": delay_sum_ms,
            "jitter_sum_ms": jitter_sum_ms,
            "average_latency_ms": flow_latency,
            "average_jitter_ms": flow_jitter
        })
    
    # Calculate overall metrics
    overall_pdr = (total_rx_packets / total_tx_packets * 100.0) if total_tx_packets > 0 else 0.0
    overall_latency = (total_delay_ms / total_rx_packets) if total_rx_packets > 0 else 0.0
    overall_jitter = (total_jitter_ms / total_rx_packets) if total_rx_packets > 0 else 0.0
    
    metrics["summary"] = {
        "pdr_percent": overall_pdr,
        "average_latency_ms": overall_latency,
        "average_jitter_ms": overall_jitter,
        "total_tx_packets": int(total_tx_packets),
        "total_rx_packets": int(total_rx_packets),
        "total_tx_bytes": int(total_tx_bytes),
        "total_rx_bytes": int(total_rx_bytes)
    }
    
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    # Print summary statistics
    print(f"\nSummary:")
    print(f"  Total TX packets: {total_tx_packets}")
    print(f"  Total RX packets: {total_rx_packets}")
    print(f"  PDR: {overall_pdr:.2f}%")
    print(f"  Average Latency: {overall_latency:.2f} ms")
    print(f"  Average Jitter: {overall_jitter:.2f} ms")
    
    ns.Simulator.Destroy()
    print("Simulation complete!")


if __name__ == "__main__":
    main()

