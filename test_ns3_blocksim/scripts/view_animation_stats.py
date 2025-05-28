#!/usr/bin/env python3
"""
NetAnim XML Animation Statistics Viewer
Analyzes the generated NetAnim XML file and displays statistics
"""

import xml.etree.ElementTree as ET
import sys
import os
from datetime import datetime

def analyze_netanim_xml(xml_file):
    """Analyze NetAnim XML file and extract statistics"""
    
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found")
        return
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ Error parsing XML: {e}")
        return
    
    print("🎬 MANET Blockchain NetAnim Analysis")
    print("=" * 50)
    
    # Basic info
    print(f"📁 File: {xml_file}")
    print(f"📊 File size: {os.path.getsize(xml_file):,} bytes")
    print(f"⏰ Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Animation info
    anim_info = root.find('.//anim')
    if anim_info is not None:
        print("🎯 Animation Parameters:")
        version = anim_info.get('ver', 'Unknown')
        print(f"   • Version: {version}")
    
    # Topology info
    topology = root.find('.//topology')
    if topology is not None:
        print("🌐 Network Topology:")
        min_x = topology.get('minX', '0')
        min_y = topology.get('minY', '0')
        max_x = topology.get('maxX', '1000')
        max_y = topology.get('maxY', '1000')
        print(f"   • Area: {min_x},{min_y} to {max_x},{max_y} meters")
    print()
    
    # Node analysis
    nodes = root.findall('.//node')
    print(f"📡 Network Nodes: {len(nodes)} total")
    
    validators = 0
    regular_nodes = 0
    node_colors = {}
    
    for node in nodes:
        node_id = node.get('id', 'Unknown')
        
        # Check for color information (blue = validator, red = regular)
        color_updates = root.findall(f'.//nodeupdate[@id="{node_id}"][@t="0"][@r][@g][@b]')
        for color_update in color_updates:
            r = int(color_update.get('r', '0'))
            g = int(color_update.get('g', '0'))
            b = int(color_update.get('b', '0'))
            
            if r == 0 and g == 0 and b == 255:  # Blue
                validators += 1
                node_colors[node_id] = 'Validator'
            elif r == 255 and g == 0 and b == 0:  # Red
                regular_nodes += 1
                node_colors[node_id] = 'Regular'
    
    print(f"   • 🔵 Validators: {validators}")
    print(f"   • 🔴 Regular Nodes: {regular_nodes}")
    print()
    
    # Packet analysis
    packets = root.findall('.//packet')
    print(f"📦 Network Traffic: {len(packets)} packets")
    
    if packets:
        # Analyze packet timing
        first_time = float('inf')
        last_time = 0
        packet_sizes = []
        
        for packet in packets[:100]:  # Sample first 100 packets
            from_time = packet.get('ft')
            to_time = packet.get('lt')
            
            if from_time:
                first_time = min(first_time, float(from_time))
            if to_time:
                last_time = max(last_time, float(to_time))
        
        if first_time != float('inf'):
            duration = last_time - first_time
            print(f"   • Duration: {duration:.2f} seconds")
            print(f"   • First packet: {first_time:.2f}s")
            print(f"   • Last packet: {last_time:.2f}s")
            if duration > 0:
                pps = len(packets) / duration
                print(f"   • Rate: {pps:.1f} packets/second")
    print()
    
    # Mobility analysis
    position_updates = root.findall('.//nodeupdate[@x][@y]')
    print(f"🚶 Node Mobility: {len(position_updates)} position updates")
    
    if position_updates:
        # Find movement range
        x_positions = []
        y_positions = []
        
        for update in position_updates:
            try:
                x = float(update.get('x', '0'))
                y = float(update.get('y', '0'))
                x_positions.append(x)
                y_positions.append(y)
            except ValueError:
                continue
        
        if x_positions and y_positions:
            print(f"   • X range: {min(x_positions):.1f} to {max(x_positions):.1f} meters")
            print(f"   • Y range: {min(y_positions):.1f} to {max(y_positions):.1f} meters")
            
            # Calculate movement
            total_distance = 0
            for i in range(1, min(100, len(x_positions))):
                dx = x_positions[i] - x_positions[i-1]
                dy = y_positions[i] - y_positions[i-1]
                distance = (dx*dx + dy*dy)**0.5
                total_distance += distance
            
            if total_distance > 0:
                print(f"   • Sample movement: {total_distance:.1f} meters")
    print()
    
    # Show node details
    print("🎨 Node Details:")
    if node_colors:
        for node_id, node_type in sorted(node_colors.items(), key=lambda x: int(x[0]))[:10]:
            print(f"   • Node {node_id}: {node_type}")
        if len(node_colors) > 10:
            print(f"   • ... and {len(node_colors) - 10} more nodes")
    print()
    
    # Blockchain traffic analysis
    print("⛓️  Blockchain Traffic Analysis:")
    
    # Look for UDP traffic patterns
    udp_packets = []
    for packet in packets[:50]:  # Sample packets
        meta = packet.find('.//meta')
        if meta is not None:
            meta_info = meta.get('info', '')
            if 'UDP' in meta_info or '9000' in meta_info:
                udp_packets.append(packet)
    
    print(f"   • UDP packets (sample): {len(udp_packets)}")
    
    if udp_packets:
        # Analyze UDP traffic
        validator_traffic = 0
        regular_traffic = 0
        
        for packet in udp_packets:
            from_node = packet.get('fromId', '')
            to_node = packet.get('toId', '')
            
            if from_node in node_colors and to_node in node_colors:
                if node_colors[from_node] == 'Validator' or node_colors[to_node] == 'Validator':
                    validator_traffic += 1
                else:
                    regular_traffic += 1
        
        print(f"   • Validator traffic: {validator_traffic} packets")
        print(f"   • Inter-node traffic: {regular_traffic} packets")
    
    print()
    print("✅ Analysis Complete!")
    print()
    print("🎮 To view the full animation:")
    print("   1. Install NetAnim: ./scripts/setup_netanim.sh")
    print("   2. Launch: cd netanim-3.109 && ./NetAnim")
    print("   3. Open: manet-blockchain-visualization.xml")

def main():
    # Default file location
    xml_files = [
        'external/ns-3/manet-blockchain-visualization.xml',
        'manet-blockchain-visualization.xml',
        '../external/ns-3/manet-blockchain-visualization.xml'
    ]
    
    # Try command line argument first
    if len(sys.argv) > 1:
        xml_files.insert(0, sys.argv[1])
    
    # Find the XML file
    xml_file = None
    for file_path in xml_files:
        if os.path.exists(file_path):
            xml_file = file_path
            break
    
    if xml_file:
        analyze_netanim_xml(xml_file)
    else:
        print("❌ NetAnim XML file not found!")
        print("Searched for:")
        for file_path in xml_files:
            print(f"   • {file_path}")
        print()
        print("Usage: python view_animation_stats.py [xml_file]")

if __name__ == "__main__":
    main() 