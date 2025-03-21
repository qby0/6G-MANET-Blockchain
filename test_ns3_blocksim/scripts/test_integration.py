#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify the integration with paths_manager
"""

import json
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.ns3_adapter import NS3Adapter
from models.paths_manager import get_all_paths, get_config_dir, get_ns3_dir


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("test_integration")


def main():
    """Main test function"""
    logger = setup_logging()
    logger.info("=== Integration Test with paths_manager ===")

    # Get paths from paths_manager
    logger.info("Retrieving paths from paths_manager...")
    all_paths = get_all_paths()

    # Print all paths
    logger.info("All configured paths:")
    for name, path in all_paths.items():
        logger.info("%s: %(path)s", name)
        if not os.path.exists(path):
            logger.warning(
                "WARNING: Path %s does not exist: %s", (name, path),
            )

    # Test NS-3 path
    ns3_path = get_ns3_dir()
    if ns3_path:
        logger.info("NS-3 path found: %s", ns3_path)

        # Check if NS-3 path exists
        if os.path.exists(ns3_path):
            logger.info("NS-3 directory exists at: %s", ns3_path)

            # Test NS3Adapter with the path
            try:
                logger.info("Testing NS3Adapter initialization...")
                adapter = NS3Adapter(ns3_path)
                logger.info("NS3Adapter initialized successfully!")

                # Get NS-3 version
                logger.info("Checking NS-3 version...")
                version = adapter.get_ns3_version()
                logger.info("NS-3 version: %s", version)

                # Check if NS-3 is properly configured
                logger.info("Checking if NS-3 is properly configured...")
                ns3_configured = os.path.exists(os.path.join(ns3_path, "ns3"))
                if ns3_configured:
                    logger.info("NS-3 appears to be properly configured.")
                else:
                    logger.warning(
                        "NS-3 may not be properly configured. Could not find 'ns3' script."
                    )

                logger.info("NS3Adapter test completed!")

            except Exception as e:
                logger.error("Error initializing NS3Adapter: %s", e)
                return 1

        else:
            logger.error(
                "NS-3 directory does not exist at: %s", ns3_path
            )
            logger.info("Please update the NS3_DIR path in env_paths.json")
            return 1
    else:
        logger.error("NS-3 path not found in paths_manager or environment variables")
        logger.info(
            "Please set NS3_DIR in env_paths.json or as an environment variable"
        )
        return 1

    # Test config path
    config_dir = get_config_dir()
    if config_dir:
        logger.info("Config directory found: %s", config_dir)

        # Check if integrated.json exists
        integrated_config = os.path.join(config_dir, "integrated.json")
        if os.path.exists(integrated_config):
            logger.info(
                "Integrated config file found: %s", integrated_config,
            )

            # Read the config file
            try:
                with open(integrated_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
                logger.info(
                    f"Successfully loaded integrated.json with {len(config)} keys"
                )

                # Check essential configuration
                if "simulation_name" in config:
                    logger.info(
                        "Simulation name: %(config['simulation_name'])s",
                        {config["simulation_name"]: config["simulation_name"]},
                    )
                else:
                    logger.warning("Missing 'simulation_name' in config")

                if "simulation_time" in config:
                    logger.info(
                        "Simulation time: %(config['simulation_time'])s seconds",
                        {config["simulation_time"]: config["simulation_time"]},
                    )
                else:
                    logger.warning("Missing 'simulation_time' in config")

                if "network" in config:
                    logger.info(
                        "Network config: %(len(config['network']))s parameters",
                        {len(config["network"]): len(config["network"])},
                    )
                else:
                    logger.warning("Missing 'network' section in config")

                if "blockchain" in config:
                    logger.info(
                        f"Blockchain config: {len(config['blockchain'])} parameters"
                    )
                else:
                    logger.warning("Missing 'blockchain' section in config")

            except Exception as e:
                logger.error("Error reading integrated.json: %s", e)
        else:
            logger.warning(
                "Integrated config file not found: %s", integrated_config,
            )
    else:
        logger.warning("Config directory not found")

    logger.info("=== Integration Test Completed Successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
