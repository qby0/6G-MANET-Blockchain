#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility to manage environment paths for the project.
Loads paths from env_paths.json and provides access to them.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional


class PathsManager:
    """
    Class to manage environment paths for the project.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(PathsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the paths manager if not already initialized"""
        if self._initialized:
            return

        self.logger = logging.getLogger("PathsManager")
        self.paths: Dict[str, Any] = {}
        self._load_paths()
        self._initialized = True

    def _load_paths(self) -> None:
        """Load paths from env_paths.json"""
        # Get the project root directory (parent of the directory containing this file)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Path to the env_paths.json file
        env_paths_file = os.path.join(project_root, "env_paths.json")

        # Load paths from the file
        if os.path.exists(env_paths_file):
            try:
                with open(env_paths_file, "r", encoding="utf-8") as f:
                    self.paths = json.load(f)
                self.logger.info(
                    "Loaded paths from %(env_paths_file)s",
                    {env_paths_file: env_paths_file},
                )

                # Ensure all paths exist
                for name, path in self.paths.items():
                    if not os.path.exists(path):
                        self.logger.warning(
                            "Path %(name)s = '%(path)s' does not exist",
                            {name: name, path: path},
                        )

            except Exception as e:
                self.logger.error(
                    "Error loading paths from %(env_paths_file)s: %(e)s",
                    {env_paths_file: env_paths_file, e: e},
                )
                # Initialize with empty paths
                self.paths: Dict[str, Any] = {}
        else:
            self.logger.warning(
                "Paths file not found: %(env_paths_file)s",
                {env_paths_file: env_paths_file},
            )
            # Initialize with empty paths
            self.paths: Dict[str, Any] = {}

        # Add project root to paths
        self.paths["PROJECT_ROOT"] = project_root

        # Create standard paths if not already in the file
        standard_paths = {
            "EXTERNAL_DIR": os.path.join(project_root, "external"),
            "RESULTS_DIR": os.path.join(project_root, "results"),
            "CONFIG_DIR": os.path.join(project_root, "config"),
            "MODELS_DIR": os.path.join(project_root, "models"),
            "SCRIPTS_DIR": os.path.join(project_root, "scripts"),
            "TESTS_DIR": os.path.join(project_root, "tests"),
        }

        # Add standard paths if they don't exist
        for name, path in standard_paths.items():
            if name not in self.paths:
                self.paths[name] = path

    def get_path(self, path_name: str) -> Optional[str]:
        """
        Get a path by name.

        Args:
            path_name (str): Name of the path to get

        Returns:
            Optional[str]: Path if found, None otherwise
        """
        return self.paths.get(path_name)

    def get_all_paths(self) -> Dict[str, str]:
        """
        Get all paths.

        Returns:
            Dict[str, str]: Dictionary of all paths
        """
        return dict(self.paths)

    def add_path(self, path_name: str, path_value: str) -> None:
        """
        Add a new path.

        Args:
            path_name (str): Name of the path to add
            path_value (str): Value of the path
        """
        self.paths[path_name] = path_value

    def save_paths(self) -> bool:
        """
        Save paths to env_paths.json.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the project root directory
            project_root = self.paths.get(
                "PROJECT_ROOT",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            )

            # Path to the env_paths.json file
            env_paths_file = os.path.join(project_root, "env_paths.json")

            # Filter out PROJECT_ROOT from saved paths
            save_paths = {k: v for k, v in self.paths.items() if k != "PROJECT_ROOT"}

            # Save paths to the file
            with open(env_paths_file, "w", encoding="utf-8") as f:
                json.dump(save_paths, f, indent=4)

            self.logger.info(
                "Saved paths to %(env_paths_file)s", {env_paths_file: env_paths_file}
            )
            return True

        except Exception as e:
            self.logger.error("Error saving paths: %(e)s", {e: e})
            return False

    def get_ns3_dir(self) -> Optional[str]:
        """
        Get the NS-3 directory.
        First tries to get from paths, then from environment variables.

        Returns:
            Optional[str]: NS-3 directory if found, None otherwise
        """
        # Try to get from paths
        ns3_dir = self.get_path("NS3_DIR")

        # If not found, try to get from environment variables
        if not ns3_dir:
            ns3_dir = os.environ.get("NS3_DIR")

            # If found in environment, add to paths
            if ns3_dir:
                self.add_path("NS3_DIR", ns3_dir)

        return ns3_dir

    def ensure_directory(self, dir_path: str) -> str:
        """
        Ensure a directory exists.

        Args:
            dir_path (str): Path to the directory

        Returns:
            str: Path to the directory
        """
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def get_results_dir(self) -> str:
        """
        Get the results directory.

        Returns:
            str: Path to the results directory
        """
        results_dir = self.get_path("RESULTS_DIR")
        return self.ensure_directory(results_dir)

    def get_config_dir(self) -> str:
        """
        Get the configuration directory.

        Returns:
            str: Path to the configuration directory
        """
        config_dir = self.get_path("CONFIG_DIR")
        return config_dir


# Create a singleton instance
paths_manager = PathsManager()

# Export methods at module level for convenience
get_path = paths_manager.get_path
get_all_paths = paths_manager.get_all_paths
add_path = paths_manager.add_path
save_paths = paths_manager.save_paths
get_ns3_dir = paths_manager.get_ns3_dir
get_results_dir = paths_manager.get_results_dir
get_config_dir = paths_manager.get_config_dir


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Test paths manager
    print("=== Paths Manager Test ===")
    print(f"All paths: {json.dumps(get_all_paths(), indent=2)}")
    print(f"NS-3 directory: {get_ns3_dir()}")
    print(f"Results directory: {get_results_dir()}")
    print(f"Config directory: {get_config_dir()}")
