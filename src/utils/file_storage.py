"""
File-based data storage system for simulation scenes and robot models.

This module provides file-based storage for simulation environments,
robot models, and associated data in the AI-Robot Brain system.
"""

import os
import json
import yaml
import pickle
import gzip
import shutil
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import hashlib
from datetime import datetime


class FileStorageManager:
    """
    Manages file-based storage for simulation scenes, robot models, and sensor data.
    Provides methods for saving, loading, and organizing data files.
    """
    
    def __init__(self, base_path: str = "./data"):
        """
        Initialize the file storage manager.
        
        Args:
            base_path: Base directory for all data storage
        """
        self.base_path = Path(base_path)
        self.scenes_path = self.base_path / "simulation_scenes"
        self.models_path = self.base_path / "robot_models"
        self.sensor_data_path = self.base_path / "sensor_data"
        self.logs_path = self.base_path / "logs"
        
        # Create directories if they don't exist
        self.scenes_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.sensor_data_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
    
    def save_scene(self, scene_name: str, scene_data: Dict[str, Any]) -> str:
        """
        Save a simulation scene to disk.
        
        Args:
            scene_name: Name of the scene (used for filename)
            scene_data: Dictionary containing scene configuration and assets
            
        Returns:
            Path to the saved file
        """
        # Create scene directory
        scene_dir = self.scenes_path / scene_name
        scene_dir.mkdir(exist_ok=True)
        
        # Save scene configuration
        config_path = scene_dir / "scene_config.json"
        with open(config_path, 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        return str(config_path)
    
    def load_scene(self, scene_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a simulation scene from disk.
        
        Args:
            scene_name: Name of the scene to load
            
        Returns:
            Dictionary containing scene configuration, or None if not found
        """
        config_path = self.scenes_path / scene_name / "scene_config.json"
        
        if not config_path.exists():
            return None
            
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def save_robot_model(self, model_name: str, model_data: Union[Dict[str, Any], str]) -> str:
        """
        Save a robot model to disk.
        
        Args:
            model_name: Name of the robot model
            model_data: Either a path to the URDF/SDF file or a dictionary with model data
            
        Returns:
            Path to the saved file
        """
        model_dir = self.models_path / model_name
        model_dir.mkdir(exist_ok=True)
        
        if isinstance(model_data, str):
            # If model_data is a path, copy the file to our storage
            source_path = Path(model_data)
            if source_path.exists():
                target_path = model_dir / source_path.name
                shutil.copy2(source_path, target_path)
                return str(target_path)
            else:
                raise FileNotFoundError(f"Model file not found: {model_data}")
        else:
            # If model_data is a dict, save as JSON
            model_path = model_dir / "model_config.json"
            with open(model_path, 'w') as f:
                json.dump(model_data, f, indent=2)
            return str(model_path)
    
    def load_robot_model(self, model_name: str, file_type: str = "any") -> Optional[Union[Dict[str, Any], str]]:
        """
        Load a robot model from disk.
        
        Args:
            model_name: Name of the robot model to load
            file_type: Type of file to load ('urdf', 'sdf', 'json', or 'any')
            
        Returns:
            Either the path to the model file (for URDF/SDF) or the model config dict, or None if not found
        """
        model_dir = self.models_path / model_name
        if not model_dir.exists():
            return None
        
        # Look for different file types based on the file_type parameter
        if file_type in ["urdf", "any"]:
            urdf_path = model_dir / f"{model_name}.urdf"
            if urdf_path.exists():
                return str(urdf_path)
        
        if file_type in ["sdf", "any"]:
            sdf_path = model_dir / f"{model_name}.sdf"
            if sdf_path.exists():
                return str(sdf_path)
        
        if file_type in ["json", "any"]:
            config_path = model_dir / "model_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        
        return None
    
    def save_sensor_data(self, data_id: str, sensor_data: Any, data_format: str = "pickle") -> str:
        """
        Save sensor data to disk with metadata.
        
        Args:
            data_id: Unique identifier for the sensor data
            sensor_data: The actual sensor data to save
            data_format: Format to save in ('pickle', 'json', 'numpy', etc.)
            
        Returns:
            Path to the saved file
        """
        # Create timestamp-based subdirectory for organization
        timestamp_dir = self.sensor_data_path / datetime.now().strftime("%Y-%m-%d")
        timestamp_dir.mkdir(exist_ok=True)
        
        if data_format == "pickle":
            file_path = timestamp_dir / f"{data_id}.pkl.gz"
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(sensor_data, f)
        elif data_format == "json":
            file_path = timestamp_dir / f"{data_id}.json"
            with open(file_path, 'w') as f:
                json.dump(sensor_data, f, indent=2, default=str)  # default=str handles datetime objects
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
        
        # Save metadata
        metadata = {
            "id": data_id,
            "timestamp": datetime.now().isoformat(),
            "format": data_format,
            "size": os.path.getsize(file_path),
            "checksum": self._calculate_checksum(file_path)
        }
        
        metadata_path = timestamp_dir / f"{data_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    def load_sensor_data(self, data_id: str, date: Optional[str] = None) -> Optional[Any]:
        """
        Load sensor data from disk.
        
        Args:
            data_id: Unique identifier for the sensor data
            date: Date in YYYY-MM-DD format to look for the data
            
        Returns:
            The loaded sensor data, or None if not found
        """
        # Use provided date or today's date
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        date_dir = self.sensor_data_path / date
        
        # Try different formats
        for ext in [".pkl.gz", ".json"]:
            file_path = date_dir / f"{data_id}{ext}"
            if file_path.exists():
                if ext == ".pkl.gz":
                    with gzip.open(file_path, 'rb') as f:
                        return pickle.load(f)
                elif ext == ".json":
                    with open(file_path, 'r') as f:
                        return json.load(f)
        
        return None
    
    def save_robot_state(self, robot_id: str, state_data: Dict[str, Any]) -> str:
        """
        Save the current state of a robot.
        
        Args:
            robot_id: Identifier for the robot
            state_data: Dictionary containing the robot's state
            
        Returns:
            Path to the saved state file
        """
        states_dir = self.models_path / robot_id / "states"
        states_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        state_path = states_dir / f"state_{timestamp}.json"
        
        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
        
        return str(state_path)
    
    def load_latest_robot_state(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """
        Load the most recent state of a robot.
        
        Args:
            robot_id: Identifier for the robot
            
        Returns:
            Dictionary containing the robot's state, or None if no state found
        """
        states_dir = self.models_path / robot_id / "states"
        if not states_dir.exists():
            return None
        
        # Find the most recent state file
        state_files = list(states_dir.glob("state_*.json"))
        if not state_files:
            return None
        
        # Sort by filename to get the most recent (assumes timestamp in filename)
        latest_file = sorted(state_files)[-1]
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def list_scenes(self) -> List[str]:
        """List all available simulation scenes."""
        return [d.name for d in self.scenes_path.iterdir() if d.is_dir()]
    
    def list_robot_models(self) -> List[str]:
        """List all available robot models."""
        return [d.name for d in self.models_path.iterdir() if d.is_dir()]
    
    def delete_scene(self, scene_name: str) -> bool:
        """Delete a simulation scene."""
        scene_dir = self.scenes_path / scene_name
        if scene_dir.exists():
            shutil.rmtree(scene_dir)
            return True
        return False
    
    def delete_robot_model(self, model_name: str) -> bool:
        """Delete a robot model."""
        model_dir = self.models_path / model_name
        if model_dir.exists():
            shutil.rmtree(model_dir)
            return True
        return False
    
    def _calculate_checksum(self, file_path: Union[str, Path]) -> str:
        """
        Calculate MD5 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 checksum as a hex string
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        stat = path.stat()
        
        return {
            "name": path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "checksum": self._calculate_checksum(path)
        }


class SimulationSceneManager(FileStorageManager):
    """
    Specialized storage manager for simulation scenes with additional functionality.
    """
    
    def __init__(self, base_path: str = "./data"):
        super().__init__(base_path)
        self.scenes_metadata_path = self.base_path / "scenes_metadata.json"
    
    def create_scene_from_template(self, scene_name: str, template_name: str = "basic_indoor") -> str:
        """
        Create a new scene based on a template.
        
        Args:
            scene_name: Name for the new scene
            template_name: Name of the template to use
            
        Returns:
            Path to the created scene
        """
        # Define basic templates
        templates = {
            "basic_indoor": {
                "name": scene_name,
                "type": "indoor",
                "environment": {
                    "gravity": [0, 0, -9.81],
                    "lighting": {"intensity": 1000, "color": [1, 1, 1]},
                    "objects": []
                },
                "physics": {
                    "solver": "pgs",
                    "iterations": 128
                }
            },
            "outdoor_park": {
                "name": scene_name,
                "type": "outdoor",
                "environment": {
                    "gravity": [0, 0, -9.81],
                    "lighting": {"intensity": 5000, "color": [1, 0.95, 0.9]},
                    "objects": [
                        {"type": "ground_plane", "size": [100, 100], "position": [0, 0, 0]},
                        {"type": "tree", "count": 10, "distribution": "random"}
                    ]
                },
                "physics": {
                    "solver": "pgs",
                    "iterations": 64
                }
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        scene_data = templates[template_name]
        return self.save_scene(scene_name, scene_data)
    
    def update_scene_metadata(self, scene_name: str, metadata: Dict[str, Any]):
        """
        Update metadata for a specific scene.
        
        Args:
            scene_name: Name of the scene
            metadata: Metadata to add/modify
        """
        all_metadata = self._load_all_scenes_metadata()
        
        if scene_name in all_metadata:
            all_metadata[scene_name].update(metadata)
        else:
            all_metadata[scene_name] = metadata
        
        self._save_all_scenes_metadata(all_metadata)
    
    def get_scene_metadata(self, scene_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific scene.
        
        Args:
            scene_name: Name of the scene
            
        Returns:
            Metadata dictionary or None if not found
        """
        all_metadata = self._load_all_scenes_metadata()
        return all_metadata.get(scene_name)
    
    def _load_all_scenes_metadata(self) -> Dict[str, Any]:
        """Load all scenes metadata."""
        if self.scenes_metadata_path.exists():
            with open(self.scenes_metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_all_scenes_metadata(self, metadata: Dict[str, Any]):
        """Save all scenes metadata."""
        with open(self.scenes_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)


class RobotModelManager(FileStorageManager):
    """
    Specialized storage manager for robot models with additional functionality.
    """
    
    def __init__(self, base_path: str = "./data"):
        super().__init__(base_path)
        self.models_metadata_path = self.base_path / "models_metadata.json"
    
    def create_robot_template(self, model_name: str, robot_type: str = "bipedal") -> str:
        """
        Create a basic robot model template.
        
        Args:
            model_name: Name for the new robot model
            robot_type: Type of robot ('bipedal', 'quadruped', 'wheeled', etc.)
            
        Returns:
            Path to the created model
        """
        templates = {
            "bipedal": {
                "name": model_name,
                "type": "bipedal",
                "links": [
                    {"name": "base_link", "mass": 10.0, "inertia": [1, 0, 0, 1, 0, 1]},
                    {"name": "left_leg", "mass": 5.0, "inertia": [0.5, 0, 0, 0.5, 0, 0.5]},
                    {"name": "right_leg", "mass": 5.0, "inertia": [0.5, 0, 0, 0.5, 0, 0.5]},
                    {"name": "left_arm", "mass": 2.0, "inertia": [0.2, 0, 0, 0.2, 0, 0.2]},
                    {"name": "right_arm", "mass": 2.0, "inertia": [0.2, 0, 0, 0.2, 0, 0.2]},
                    {"name": "head", "mass": 1.0, "inertia": [0.1, 0, 0, 0.1, 0, 0.1]}
                ],
                "joints": [
                    {"name": "left_hip", "type": "revolute", "parent": "base_link", "child": "left_leg"},
                    {"name": "right_hip", "type": "revolute", "parent": "base_link", "child": "right_leg"},
                    {"name": "left_shoulder", "type": "revolute", "parent": "base_link", "child": "left_arm"},
                    {"name": "right_shoulder", "type": "revolute", "parent": "base_link", "child": "right_arm"}
                ],
                "sensors": [
                    {"name": "rgb_camera", "type": "camera", "position": [0.2, 0, 0.5]},
                    {"name": "imu", "type": "imu", "position": [0, 0, 0.3]},
                    {"name": "lidar", "type": "lidar", "position": [0.1, 0, 0.4]}
                ],
                "actuators": [
                    {"name": "left_hip_actuator", "joint": "left_hip"},
                    {"name": "right_hip_actuator", "joint": "right_hip"},
                    {"name": "left_knee_actuator", "joint": "left_knee"}
                ]
            },
            "wheeled": {
                "name": model_name,
                "type": "wheeled",
                "links": [
                    {"name": "base_link", "mass": 15.0, "inertia": [2, 0, 0, 2, 0, 2]},
                    {"name": "left_wheel", "mass": 2.0, "inertia": [0.5, 0, 0, 0.5, 0, 1.0]},
                    {"name": "right_wheel", "mass": 2.0, "inertia": [0.5, 0, 0, 0.5, 0, 1.0]},
                ],
                "joints": [
                    {"name": "left_wheel_joint", "type": "continuous", "parent": "base_link", "child": "left_wheel"},
                    {"name": "right_wheel_joint", "type": "continuous", "parent": "base_link", "child": "right_wheel"}
                ],
                "sensors": [
                    {"name": "front_camera", "type": "camera", "position": [0.3, 0, 0.2]},
                    {"name": "lidar", "type": "lidar", "position": [0, 0, 0.3]}
                ],
                "actuators": [
                    {"name": "left_wheel_actuator", "joint": "left_wheel_joint"},
                    {"name": "right_wheel_actuator", "joint": "right_wheel_joint"}
                ]
            }
        }
        
        if robot_type not in templates:
            raise ValueError(f"Unknown robot type: {robot_type}")
        
        model_data = templates[robot_type]
        return self.save_robot_model(model_name, model_data)
    
    def validate_robot_model(self, model_name: str) -> Dict[str, Any]:
        """
        Validate a robot model for completeness and correctness.
        
        Args:
            model_name: Name of the robot model to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        model_data = self.load_robot_model(model_name, "json")
        if not model_data:
            result["valid"] = False
            result["issues"].append(f"Model {model_name} not found or not in JSON format")
            return result
        
        # Check required fields
        required_fields = ["name", "type", "links", "joints"]
        for field in required_fields:
            if field not in model_data:
                result["valid"] = False
                result["issues"].append(f"Missing required field: {field}")
        
        # Check links
        if "links" in model_data:
            for i, link in enumerate(model_data["links"]):
                if not isinstance(link, dict) or "name" not in link:
                    result["valid"] = False
                    result["issues"].append(f"Link {i} is invalid or missing name")
        
        # Check joints
        if "joints" in model_data:
            for i, joint in enumerate(model_data["joints"]):
                if not isinstance(joint, dict) or "name" not in joint:
                    result["valid"] = False
                    result["issues"].append(f"Joint {i} is invalid or missing name")
        
        # Check for sensors
        if "sensors" not in model_data:
            result["warnings"].append("No sensors defined in the robot model")
        
        # Check for actuators
        if "actuators" not in model_data:
            result["warnings"].append("No actuators defined in the robot model")
        
        return result


# Global storage manager instance
_storage_manager = None


def get_storage_manager(base_path: str = "./data") -> FileStorageManager:
    """
    Get the global storage manager instance.
    
    Args:
        base_path: Base path for storage (only used if creating the first instance)
        
    Returns:
        The storage manager instance
    """
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = FileStorageManager(base_path)
    return _storage_manager


def initialize_storage(base_path: str = "./data") -> FileStorageManager:
    """
    Initialize and return a storage manager.
    
    Args:
        base_path: Base path for storage
        
    Returns:
        Initialized storage manager
    """
    global _storage_manager
    _storage_manager = FileStorageManager(base_path)
    return _storage_manager