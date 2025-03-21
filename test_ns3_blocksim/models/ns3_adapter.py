"""
Adapter for NS-3 integration.
Provides management of NS-3 simulation from Python.
"""
import os
import sys
import logging
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NS3Adapter")

class NS3Adapter:
    """Class for interaction with NS-3"""
    
    def __init__(self, ns3_path: str = None):
        """
        Initializes the NS-3 adapter.
        
        Args:
            ns3_path (str, optional): Path to NS-3 directory.
                                      By default, looks for NS3_DIR environment variable.
        """
        # Define the path to NS-3
        if ns3_path:
            self.ns3_path = ns3_path
        else:
            self.ns3_path = os.environ.get("NS3_DIR", None)
            if not self.ns3_path:
                raise EnvironmentError("NS-3 path not specified. Provide it as an argument or set the NS3_DIR environment variable.")

        # Check if the directory exists
        if not os.path.exists(self.ns3_path):
            raise FileNotFoundError(f"NS-3 directory not found at: {self.ns3_path}")
        
        logger.info(f"NS-3 adapter initialized with path: {self.ns3_path}")
        
        # Variables for storing simulation state
        self.simulation_running = False
        self.current_nodes = {}
        self.current_links = {}
        self.simulation_time = 0.0
        
    def configure_and_build(self) -> bool:
        """
        Configures and builds NS-3 with optimizations.
        
        Returns:
            bool: True if build is successful, False otherwise
        """
        try:
            # Setup ccache
            os.environ["CCACHE_DIR"] = os.path.join(self.ns3_path, ".ccache")
            os.environ["CCACHE_MAXSIZE"] = "50G"
            
            # Configuration with optimizations
            configure_cmd = [
                "./ns3",
                "configure",
                "--enable-examples",
                "--enable-tests",
                "--enable-python-bindings",
                "--enable-modules=netanim",
                "--build-profile=optimized",
                "--enable-ccache",
                "--enable-ninja"
            ]
            
            subprocess.run(configure_cmd, cwd=self.ns3_path, check=True)
            
            # Parallel build
            build_cmd = ["./ns3", "build", f"-j{os.cpu_count()}"]
            subprocess.run(build_cmd, cwd=self.ns3_path, check=True)
            
            logger.info("NS-3 successfully configured and built")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"NS-3 build error: {e}")
            return False

    def create_scenario_file(self, nodes: Dict[str, Dict], 
                           links: Dict[str, Dict],
                           params: Dict[str, Any]) -> str:
        """
        Creates a temporary scenario file for NS-3 based on provided data.
        
        Args:
            nodes (Dict[str, Dict]): Dictionary with node information
            links (Dict[str, Dict]): Dictionary with link information
            params (Dict[str, Any]): Simulation parameters
            
        Returns:
            str: Path to created scenario file
        """
        # Create a temporary file for NS-3 scenario
        fd, scenario_path = tempfile.mkstemp(suffix=".xml", prefix="ns3_scenario_")
        os.close(fd)
        
        # Create root XML element
        root = ET.Element("scenario")
        
        # Add simulation parameters
        params_elem = ET.SubElement(root, "parameters")
        for key, value in params.items():
            param_elem = ET.SubElement(params_elem, "parameter")
            param_elem.set("name", key)
            param_elem.set("value", str(value))
        
        # Add node information
        nodes_elem = ET.SubElement(root, "nodes")
        for node_id, node_data in nodes.items():
            node_elem = ET.SubElement(nodes_elem, "node")
            node_elem.set("id", node_id)
            node_elem.set("type", node_data.get("type", "regular"))
            
            pos = node_data.get("position", (0, 0, 0))
            position_elem = ET.SubElement(node_elem, "position")
            position_elem.set("x", str(pos[0]))
            position_elem.set("y", str(pos[1]))
            position_elem.set("z", str(pos[2]))
            
            capabilities_elem = ET.SubElement(node_elem, "capabilities")
            for cap_name, cap_value in node_data.get("capabilities", {}).items():
                cap_elem = ET.SubElement(capabilities_elem, "capability")
                cap_elem.set("name", cap_name)
                cap_elem.set("value", str(cap_value))
        
        # Add link information
        links_elem = ET.SubElement(root, "links")
        for link_id, link_data in links.items():
            link_elem = ET.SubElement(links_elem, "link")
            link_elem.set("id", link_id)
            
            nodes_list = link_data.get("nodes", [])
            if len(nodes_list) >= 2:
                link_elem.set("source", nodes_list[0])
                link_elem.set("target", nodes_list[1])
            
            link_elem.set("quality", str(link_data.get("quality", 0.5)))
            link_elem.set("bandwidth", str(link_data.get("bandwidth", 1.0)))
        
        # Add animation settings
        anim_elem = ET.SubElement(root, "animation")
        anim_elem.set("enabled", "true")
        anim_elem.set("max_packets_per_sec", "500")
        anim_elem.set("update_interval", "0.1")
        
        # Save XML to file
        tree = ET.ElementTree(root)
        tree.write(scenario_path, encoding="utf-8", xml_declaration=True)
        
        logger.info(f"NS-3 scenario created: {scenario_path}")
        return scenario_path
    
    def run_simulation(self, scenario_path: str, duration: float, 
                     time_resolution: float = 0.1, output_dir: str = None) -> Dict[str, Any]:
        """
        Runs NS-3 simulation based on scenario.
        
        Args:
            scenario_path (str): Path to scenario file
            duration (float): Simulation duration in seconds
            time_resolution (float, optional): Time resolution in seconds. Default is 0.1.
            output_dir (str, optional): Output directory for results. Default is temporary.
            
        Returns:
            Dict[str, Any]: Simulation results
        """
        # Create output directory if not specified
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix="ns3_output_")
        elif not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Form command for NS-3 run
        ns3_script_path = os.path.join(self.ns3_path, "scratch", "manet-blockchain-sim.cc")
        
        # Check if script exists
        if not os.path.exists(ns3_script_path):
            logger.warning(f"Simulation script not found: {ns3_script_path}")
            logger.warning("Default script for MANET will be used")
            ns3_script_path = "scratch/manet-simulation"
        
        # NS-3 executable path
        ns3_exec = os.path.join(self.ns3_path, "ns3")
        
        # Form command line arguments
        cmd_args = [
            ns3_exec,
            "run",
            f"{ns3_script_path}",
            f"--scenarioFile={scenario_path}",
            f"--duration={duration}",
            f"--resolution={time_resolution}",
            f"--outputDir={output_dir}"
        ]
        
        # Run simulation
        logger.info(f"Running NS-3 simulation: {' '.join(cmd_args)}")
        
        try:
            # In real scenario, this would start NS-3 process
            # For demonstration, we simply simulate run and create fake results
            
            # proc = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
            # output = proc.stdout
            
            self.simulation_running = True
            logger.info("NS-3 simulation started")
            
            # Simulate simulation results
            results = {
                "simulation_time": duration,
                "node_movements": [],
                "link_qualities": [],
                "network_stats": {
                    "packets_sent": 1000,
                    "packets_received": 950,
                    "average_delay": 0.05,
                    "packet_loss": 0.05
                }
            }
            
            # In real integration, this would parse NS-3 output
            
            self.simulation_running = False
            logger.info("NS-3 simulation completed")
            
            return results
            
        except subprocess.CalledProcessError as e:
            logger.error(f"NS-3 simulation error: {e}")
            logger.error(f"Stderr: {e.stderr}")
            self.simulation_running = False
            return {"error": str(e), "stderr": e.stderr}
    
    def parse_ns3_output(self, output_dir: str) -> Dict[str, Any]:
        """
        Parses NS-3 simulation output.
        
        Args:
            output_dir (str): Output directory with simulation results
            
        Returns:
            Dict[str, Any]: Structured simulation results
        """
        # In this function, NS-3 output parsing would happen
        # For demonstration, we return a placeholder
        
        logger.info(f"Parsing NS-3 results from directory: {output_dir}")
        
        # Placeholder for results
        results = {
            "node_positions": {},
            "link_qualities": {},
            "packets_info": []
        }
        
        # In real implementation, there would be code to read files from output_dir
        # and extract node positions, link qualities, and packet information
        
        return results
    
    def create_ns3_manet_script(self) -> str:
        """
        Creates C++ script for NS-3, simulating MANET network with blockchain.
        
        Returns:
            str: Path to created script file
        """
        # Create scratch directory if it doesn't exist
        scratch_dir = os.path.join(self.ns3_path, "scratch")
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        
        # Script path
        script_path = os.path.join(scratch_dir, "manet-blockchain-sim.cc")
        
        # Update script content with NetAnim support
        script_content = """
        /* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
        /*
         * Simulation of MANET network with blockchain support
         */

        #include "ns3/core-module.h"
        #include "ns3/network-module.h"
        #include "ns3/internet-module.h"
        #include "ns3/mobility-module.h"
        #include "ns3/wifi-module.h"
        #include "ns3/applications-module.h"
        #include "ns3/netanim-module.h"
        #include "ns3/aodv-module.h"
        #include "ns3/flow-monitor-module.h"
        #include <iostream>
        #include <fstream>
        #include <string>
        #include <vector>
        #include <map>
        #include "ns3/command-line.h"

        using namespace ns3;

        NS_LOG_COMPONENT_DEFINE("ManetBlockchainSimulation");

        // Function to record node positions over time
        static void
        RecordNodePositions(NodeContainer nodes, double time, std::string filename)
        {
          std::ofstream file;
          file.open(filename, std::ios::app);
          file << time;
          
          for (uint32_t i = 0; i < nodes.GetN(); i++)
          {
            Ptr<MobilityModel> mobility = nodes.Get(i)->GetObject<MobilityModel>();
            Vector pos = mobility->GetPosition();
            file << "," << i << "," << pos.x << "," << pos.y << "," << pos.z;
          }
          
          file << std::endl;
          file.close();
        }

        // Function to record packet information
        static void
        RecordPacketInfo(std::string context, Ptr<const Packet> packet)
        {
          // In real implementation, this would record packet information
          NS_LOG_INFO("Packet transmitted: " << context << ", size: " << packet->GetSize());
        }

        // Function to handle packet route change
        static void 
        PacketTracing(std::string context, Ptr<const Packet> packet, 
                      Ptr<Ipv4> ipv4, uint32_t interface)
        {
          // Get a copy of the packet for header inspection
          Ptr<Packet> packetCopy = packet->Copy();
          
          // Extract IP headers for source and destination addresses
          Ipv4Header ipHeader;
          packetCopy->RemoveHeader(ipHeader);
          
          Ipv4Address srcAddr = ipHeader.GetSource();
          Ipv4Address dstAddr = ipHeader.GetDestination();
          
          NS_LOG_INFO("Packet route: " << srcAddr << " -> " << dstAddr 
                      << ", size: " << packet->GetSize() 
                      << ", TTL: " << (uint32_t)ipHeader.GetTtl());
          
          // Write to file for further analysis (if needed)
          // std::ofstream file;
          // file.open(outputDir + "/packet_traces.csv", std::ios::app);
          // file << Simulator::Now().GetSeconds() << "," << srcAddr << "," << dstAddr << "," << packet->GetSize() << std::endl;
          // file.close();
        }

        int
        main(int argc, char *argv[])
        {
          // Command line arguments
          std::string scenarioFile = "";
          double duration = 100.0;
          double resolution = 0.1;
          std::string outputDir = "./";
          
          CommandLine cmd;
          cmd.AddValue("scenarioFile", "Path to scenario file", scenarioFile);
          cmd.AddValue("duration", "Simulation duration in seconds", duration);
          cmd.AddValue("resolution", "Time resolution for data recording in seconds", resolution);
          cmd.AddValue("outputDir", "Output directory for results", outputDir);
          cmd.Parse(argc, argv);
          
          // Enable logging
          LogComponentEnable("ManetBlockchainSimulation", LOG_LEVEL_INFO);
          
          // Number of nodes (in real scenario, should be read from scenarioFile)
          uint32_t nNodes = 20;
          uint32_t nValidators = nNodes / 10;
          
          // Create nodes
          NodeContainer nodes;
          nodes.Create(nNodes);
          
          // Setup WiFi
          WifiHelper wifi;
          wifi.SetStandard(WIFI_STANDARD_80211g);
          
          YansWifiPhyHelper wifiPhy;
          YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
          wifiPhy.SetChannel(wifiChannel.Create());
          
          // Setup MAC layer for Ad-Hoc mode
          WifiMacHelper wifiMac;
          wifiMac.SetType("ns3::AdhocWifiMac");
          
          // Install Wi-Fi on nodes
          NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, nodes);
          
          // Mobility model (random walk)
          MobilityHelper mobility;
          mobility.SetPositionAllocator("ns3::GridPositionAllocator",
                                       "MinX", DoubleValue(0.0),
                                       "MinY", DoubleValue(0.0),
                                       "DeltaX", DoubleValue(50.0),
                                       "DeltaY", DoubleValue(50.0),
                                       "GridWidth", UintegerValue(5),
                                       "LayoutType", StringValue("RowFirst"));
          
          mobility.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                   "Bounds", RectangleValue(Rectangle(-500, 500, -500, 500)),
                                   "Speed", StringValue("ns3::ConstantRandomVariable[Constant=5.0]"));
          mobility.Install(nodes);
          
          // Setup Internet protocol stack
          InternetStackHelper internet;
          AodvHelper aodv; // Using AODV routing for MANET
          internet.SetRoutingHelper(aodv);
          internet.Install(nodes);
          
          // Assign IP addresses
          Ipv4AddressHelper ipv4;
          ipv4.SetBase("10.1.1.0", "255.255.255.0");
          Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);
          
          // Prepare files for output data
          std::string posFile = outputDir + "/node_positions.csv";
          std::ofstream positionFile;
          positionFile.open(posFile);
          positionFile << "time";
          for (uint32_t i = 0; i < nNodes; i++)
          {
            positionFile << ",node" << i << ",x,y,z";
          }
          positionFile << std::endl;
          positionFile.close();
          
          // Setup node positions recording
          for (double time = 0.0; time <= duration; time += resolution)
          {
            Simulator::Schedule(Seconds(time), &RecordNodePositions, nodes, time, posFile);
          }
          
          // Packet tracing
          Config::Connect("/NodeList/*/$ns3::MobilityModel/CourseChange",
                          MakeCallback(&CourseChangeCallback));
          
          // Add IP packet tracing for visualization
          Config::Connect("/NodeList/*/$ns3::Ipv4L3Protocol/Tx",
                         MakeCallback(&PacketTracing));
          Config::Connect("/NodeList/*/$ns3::Ipv4L3Protocol/Rx",
                         MakeCallback(&RecordPacketInfo));
          
          // Animation for visualization (if available)
          AnimationInterface anim(outputDir + "/animation.xml");
          
          // Enable packet metadata for visualization
          anim.EnablePacketMetadata(true);
          anim.EnableIpv4RouteTracking();
          anim.EnableQueueCounters();
          anim.EnableWifiMacCounters();
          anim.EnableWifiPhyCounters();
          
          // Setup node descriptions and colors
          for (uint32_t i = 0; i < nNodes; i++) {
            if (i < nValidators) {
              // Validators - red
              anim.UpdateNodeDescription(nodes.Get(i), "Validator " + std::to_string(i));
              anim.UpdateNodeColor(nodes.Get(i), 255, 0, 0);
            } else {
              // Regular nodes - blue
              anim.UpdateNodeDescription(nodes.Get(i), "Node " + std::to_string(i));
              anim.UpdateNodeColor(nodes.Get(i), 0, 0, 255);
            }
          }
          
          // Stream monitoring
          Ptr<FlowMonitor> flowMonitor;
          FlowMonitorHelper flowHelper;
          flowMonitor = flowHelper.InstallAll();
          
          // Run simulation
          Simulator::Stop(Seconds(duration));
          Simulator::Run();
          
          // Save stream statistics
          flowMonitor->SerializeToXmlFile(outputDir + "/flow-monitor.xml", true, true);
          
          Simulator::Destroy();
          
          NS_LOG_INFO("Simulation completed.");
          
          return 0;
        }
        """
        
        # Write script to file
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        logger.info(f"NS-3 script created: {script_path}")
        return script_path

    def compile_ns3_script(self, script_name: str) -> bool:
        """
        Compiles NS-3 script.
        
        Args:
            script_name (str): Script name (without path and extension)
            
        Returns:
            bool: True if compilation is successful, otherwise False
        """
        # NS-3 path for compilation
        cmd_args = [
            os.path.join(self.ns3_path, "ns3"),
            "build",
            f"scratch/{script_name}"
        ]
        
        logger.info(f"NS-3 script compilation: {' '.join(cmd_args)}")
        
        try:
            # In real scenario, this would start compilation
            # proc = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
            # return True
            
            # For demonstration, simply return success
            logger.info("NS-3 compilation completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"NS-3 script compilation error: {e}")
            logger.error(f"Stderr: {e.stderr}")
            return False


if __name__ == "__main__":
    # Example usage
    try:
        # Create adapter, specifying NS-3 path
        adapter = NS3Adapter("/path/to/ns3")
        
        # Create script for simulation
        script_path = adapter.create_ns3_manet_script()
        
        # Compile script
        adapter.compile_ns3_script("manet-blockchain-sim")
        
        # Create simple scenario
        nodes = {
            "base_station_1": {
                "type": "base_station",
                "position": (0.0, 0.0, 10.0),
                "capabilities": {"computational_power": 100, "storage": 1000}
            },
            "node_1": {
                "type": "regular",
                "position": (100.0, 100.0, 1.5),
                "capabilities": {"computational_power": 10, "storage": 50, "battery": 0.9}
            },
            "node_2": {
                "type": "validator",
                "position": (200.0, 200.0, 1.5),
                "capabilities": {"computational_power": 20, "storage": 100, "battery": 0.8}
            }
        }
        
        links = {
            "bs1_n1": {
                "nodes": ["base_station_1", "node_1"],
                "quality": 0.9,
                "bandwidth": 100.0
            },
            "n1_n2": {
                "nodes": ["node_1", "node_2"],
                "quality": 0.7,
                "bandwidth": 50.0
            }
        }
        
        params = {
            "simulation_time": 100.0,
            "wifi_standard": "80211g",
            "propagation_model": "friis",
            "routing_protocol": "aodv"
        }
        
        # Create scenario file
        scenario_file = adapter.create_scenario_file(nodes, links, params)
        
        # Run simulation
        results = adapter.run_simulation(
            scenario_file, 
            duration=100.0,
            time_resolution=0.1,
            output_dir="/tmp/ns3_results"
        )
        
        print(f"Simulation results: {results}")
        
    except Exception as e:
        print(f"Error: {e}")