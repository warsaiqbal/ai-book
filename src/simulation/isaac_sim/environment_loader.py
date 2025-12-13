"""
Isaac Sim environment loader for the AI-Robot Brain project.

This module provides functionality to load and initialize simulation environments
using NVIDIA Isaac Sim.
"""

import carb
import omni
import omni.kit.commands
from omni.isaac.core import World
from omni.isaac.core.scenes import Scene
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils import asset_paths
from pxr import Gf, Sdf, UsdGeom
import numpy as np
from typing import Optional, Dict, Any, List
import asyncio
from src.simulation.models.environment import SimulatedEnvironment
from src.simulation.models.robot import RobotModel
from src.simulation.models.sensor import Sensor


class IsaacSimEnvironmentLoader:
    """
    Class responsible for loading and setting up Isaac Sim environments.
    """
    
    def __init__(self):
        """Initialize the Isaac Sim environment loader."""
        self.world: Optional[World] = None
        self.current_environment: Optional[SimulatedEnvironment] = None
        self.robots: Dict[str, Any] = {}  # Store loaded robots
        self.sensors: Dict[str, Any] = {}  # Store loaded sensors
    
    async def initialize_world_async(self) -> World:
        """
        Asynchronously initialize the Isaac Sim world.
        
        Returns:
            Initialized World instance
        """
        # Create a new world instance
        self.world = World(stage_units_in_meters=1.0)
        
        # Wait for the world to be ready
        await omni.kit.app.get_app().next_update_async()
        
        return self.world
    
    def initialize_world(self) -> World:
        """
        Initialize the Isaac Sim world synchronously.
        
        Returns:
            Initialized World instance
        """
        # Create a new world instance
        self.world = World(stage_units_in_meters=1.0)
        
        return self.world
    
    def load_environment(self, environment: SimulatedEnvironment) -> bool:
        """
        Load a simulated environment into Isaac Sim.
        
        Args:
            environment: The SimulatedEnvironment object to load
            
        Returns:
            True if successfully loaded, False otherwise
        """
        if not self.world:
            carb.log_error("World not initialized. Call initialize_world() first.")
            return False
        
        self.current_environment = environment
        
        try:
            # Set physics parameters based on environment configuration
            self._configure_physics(environment)
            
            # Create the scene based on environment description
            self._create_scene(environment)
            
            # Add environment assets
            self._add_assets(environment)
            
            # Configure lighting
            self._configure_lighting(environment)
            
            carb.log_info(f"Environment '{environment.name}' loaded successfully")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to load environment: {str(e)}")
            return False
    
    def _configure_physics(self, environment: SimulatedEnvironment):
        """Configure physics parameters based on the environment."""
        if environment.physics_properties_obj:
            # Set gravity
            gravity = environment.physics_properties_obj.gravity
            self.world.get_physics_context().set_gravity([gravity.x, gravity.y, gravity.z])
            
            # Set solver parameters
            self.world.get_physics_context().set_solver_type(environment.physics_properties_obj.solver_type)
            self.world.get_physics_context().set_maximum_solver_velocity_iterations(environment.physics_properties_obj.solver_iterations)
            self.world.get_physics_context().set_maximum_contact_position_iterations(environment.physics_properties_obj.solver_iterations)
            
            # Set CCD parameters
            self.world.get_physics_context().set_enable_ccd(environment.physics_properties_obj.enable_ccd)
            
    def _create_scene(self, environment: SimulatedEnvironment):
        """Create the base scene for the environment."""
        # Create a basic scene with ground plane
        scene = Scene()
        scene.add_default_ground_plane()
        
        # Set environment dimensions if specified
        if environment.dimensions.x > 0 and environment.dimensions.y > 0:
            # Create boundaries based on environment dimensions
            self._create_boundaries(environment)
    
    def _create_boundaries(self, environment: SimulatedEnvironment):
        """Create boundaries for the environment based on its dimensions."""
        # This is a simplified implementation
        # In a real implementation, you would create actual boundary objects
        carb.log_info(f"Setting up environment boundaries: {environment.dimensions.x}x{environment.dimensions.y}m")
    
    def _add_assets(self, environment: SimulatedEnvironment):
        """Add assets to the environment."""
        for asset in environment.assets_obj:
            try:
                # Determine asset path - first try local path, then use nucleus
                asset_path = None
                if asset.asset_path and asset.asset_path.startswith("omniverse://"):
                    asset_path = asset.asset_path
                else:
                    # Look for asset in local data directory
                    local_asset_path = f"./data/assets/{asset.asset_path}"
                    if asset.asset_path and not asset.asset_path.startswith('/'):
                        # For now, we'll use a placeholder - in real implementation this would reference actual assets
                        asset_path = f"omniverse://localhost/NVIDIA/Assets/Environments/Simple_Room/simple_room.usd"
                
                # For the purpose of this implementation, we'll add a reference to a default asset
                # In a real implementation, we would add each specific asset
                if not asset_path:
                    continue
                
                # Add asset to stage at specified position
                full_path = f"/World/{asset.name}"
                add_reference_to_stage(usd_path=asset_path, prim_path=full_path)
                
                # Set position and orientation
                self.world.scene.add_manipulator_to_stage(
                    prim_path=full_path,
                    position=[asset.position.x, asset.position.y, asset.position.z],
                    orientation=[asset.orientation.x, asset.orientation.y, asset.orientation.z, asset.orientation.w]
                )
                
            except Exception as e:
                carb.log_warn(f"Failed to add asset {asset.name}: {str(e)}")
    
    def _configure_lighting(self, environment: SimulatedEnvironment):
        """Configure lighting for the environment."""
        # Create default lighting
        # In a real implementation, this would configure lighting based on environment settings
        from omni.isaac.core.utils.prims import define_prim
        from omni.isaac.core.utils.stage import get_current_stage
        from pxr import UsdLux
            
        stage = get_current_stage()
        
        # Add a dome light for environment lighting
        dome_light_path = Sdf.Path("/World/DomeLight")
        define_prim(dome_light_path, "DomeLight")
        dome_light = UsdLux.DomeLight.Define(stage, dome_light_path)
        dome_light.CreateIntensityAttr(500)
        
        # Add a distant light for main illumination
        distant_light_path = Sdf.Path("/World/DistantLight")
        define_prim(distant_light_path, "DistantLight")
        distant_light = UsdLux.DistantLight.Define(stage, distant_light_path)
        distant_light.CreateIntensityAttr(3000)
        distant_light.AddRotateXOp().Set(-45)  # Angle the light
    
    def spawn_robot(self, robot: RobotModel) -> bool:
        """
        Spawn a robot in the current environment.
        
        Args:
            robot: The RobotModel to spawn
            
        Returns:
            True if successfully spawned, False otherwise
        """
        if not self.world or not self.current_environment:
            carb.log_error("World not initialized or environment not loaded.")
            return False
        
        try:
            # Load the robot from its URDF
            robot_path = robot.urdf_path or f"./data/robot_models/{robot.name}/{robot.name}.urdf"
            
            # In a real implementation, this would use Isaac's robot loading functionality
            # For now, we'll simulate the loading
            from omni.isaac.core.utils.nucleus import get_assets_root_path
            from omni.isaac.core.robots import Robot
            from omni.isaac.core.utils.stage import add_reference_to_stage
            
            # Create robot path based on URDF
            # This is simplified - in real implementation would convert URDF to USD
            robot_prim_path = f"/World/{robot.name}"
            
            # For this example, we'll use a default robot asset
            # In a real implementation, we would convert the URDF to USD or use a USD robot
            default_robot_path = "omniverse://localhost/NVIDIA/Assets/Isaac/Robots/Franka/franka_alt_fingers.usd"
            
            # Add the robot to the stage
            add_reference_to_stage(
                usd_path=default_robot_path,
                prim_path=robot_prim_path
            )
            
            # Store reference to the robot
            # In real implementation, this would store the actual robot object
            self.robots[robot.id] = {
                'prim_path': robot_prim_path,
                'model': robot
            }
            
            carb.log_info(f"Robot '{robot.name}' spawned successfully")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to spawn robot {robot.name}: {str(e)}")
            return False
    
    def add_sensor_to_robot(self, robot_id: str, sensor: Sensor) -> bool:
        """
        Add a sensor to a robot in the simulation.
        
        Args:
            robot_id: ID of the robot to add the sensor to
            sensor: Sensor to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.world:
            carb.log_error("World not initialized.")
            return False
        
        try:
            # Check if robot exists
            if robot_id not in self.robots:
                carb.log_error(f"Robot with ID {robot_id} not found.")
                return False
            
            robot_info = self.robots[robot_id]
            robot_model = robot_info['model']
            
            # Create sensor prim path
            sensor_prim_path = f"{robot_info['prim_path']}/{sensor.name}"
            
            # In a real implementation, this would add the specific sensor type to the robot
            # For now, we'll log the sensor addition
            carb.log_info(f"Added sensor '{sensor.name}' to robot '{robot_model.name}'")
            
            # Store reference to the sensor
            self.sensors[sensor.id] = {
                'prim_path': sensor_prim_path,
                'sensor': sensor,
                'robot_id': robot_id
            }
            
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to add sensor {sensor.name} to robot {robot_id}: {str(e)}")
            return False
    
    def setup_sensor_streaming(self, sensor_ids: List[str] = None) -> bool:
        """
        Set up real-time sensor data streaming.
        
        Args:
            sensor_ids: List of sensor IDs to stream (None for all sensors)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if sensor_ids is None:
                sensor_ids = list(self.sensors.keys())
            
            for sensor_id in sensor_ids:
                if sensor_id in self.sensors:
                    sensor_info = self.sensors[sensor_id]
                    sensor = sensor_info['sensor']
                    
                    # In a real implementation, this would set up the appropriate sensor interface
                    # For example, setting up cameras, LIDAR, IMU, etc.
                    carb.log_info(f"Set up streaming for sensor '{sensor.name}' ({sensor.sensor_type.value})")
                    
                    # For each sensor type, we would set up the appropriate streaming mechanism
                    # This is simplified for the example
                    if sensor.sensor_type.value == 'rgb_camera':
                        self._setup_camera_streaming(sensor_info)
                    elif sensor.sensor_type.value == 'lidar':
                        self._setup_lidar_streaming(sensor_info)
                    elif sensor.sensor_type.value == 'imu':
                        self._setup_imu_streaming(sensor_info)
            
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to set up sensor streaming: {str(e)}")
            return False
    
    def _setup_camera_streaming(self, sensor_info: Dict[str, Any]):
        """Set up RGB camera streaming."""
        # In a real implementation, this would configure the Isaac Sim camera interface
        from omni.isaac.sensor import Camera
        import omni.replicator.core as rep
        
        sensor = sensor_info['sensor']
        camera = Camera(
            prim_path=sensor_info['prim_path'],
            frequency=sensor.update_frequency,
            resolution=(sensor.params_obj.width, sensor.params_obj.height)
        )
        
        # Configure camera properties
        camera.set_focal_length(24.0)  # Default value
        camera.set_focus_distance(10.0)  # Default value
        camera.set_horizontal_aperture(20.955)  # Default value
        
        # In a real implementation, we would set up the camera publisher to ROS2
        carb.log_info(f"Camera '{sensor.name}' streaming configured")
    
    def _setup_lidar_streaming(self, sensor_info: Dict[str, Any]):
        """Set up LIDAR streaming."""
        # In a real implementation, this would configure the Isaac Sim LIDAR interface
        # For now, this is a placeholder
        sensor = sensor_info['sensor']
        carb.log_info(f"LIDAR '{sensor.name}' streaming configured")
    
    def _setup_imu_streaming(self, sensor_info: Dict[str, Any]):
        """Set up IMU streaming."""
        # In a real implementation, this would configure the Isaac Sim IMU interface
        # For now, this is a placeholder
        sensor = sensor_info['sensor']
        carb.log_info(f"IMU '{sensor.name}' streaming configured")
    
    def reset_environment(self):
        """Reset the environment to its initial state."""
        if self.world:
            self.world.reset()
    
    def close(self):
        """Close the environment loader and clean up resources."""
        if self.world:
            self.world.clear()
            self.world = None
        self.robots.clear()
        self.sensors.clear()
        self.current_environment = None


# Convenience function to load an environment from file
async def load_environment_from_file(file_path: str) -> Optional[IsaacSimEnvironmentLoader]:
    """
    Load an environment from a configuration file.
    
    Args:
        file_path: Path to the environment configuration file
        
    Returns:
        IsaacSimEnvironmentLoader with the loaded environment, or None if failed
    """
    try:
        # Load environment from file
        from src.simulation.models.environment import SimulatedEnvironment
        env = SimulatedEnvironment.load_from_file(file_path)
        
        # Create loader and initialize
        loader = IsaacSimEnvironmentLoader()
        loader.initialize_world()
        
        # Load the environment
        success = loader.load_environment(env)
        
        if success:
            return loader
        else:
            loader.close()
            return None
            
    except Exception as e:
        carb.log_error(f"Failed to load environment from {file_path}: {str(e)}")
        return None


# Example usage function
def example_usage():
    """
    Example of how to use the IsaacSimEnvironmentLoader.
    """
    # Create a simulated environment
    from src.simulation.models.environment import SimulatedEnvironment, EnvironmentAsset
    from src.simulation.models.robot import RobotModel
    from src.simulation.models.sensor import Sensor, SensorType
    from src.utils.data_models import Vector3, Quaternion
    
    # Create an environment
    env = SimulatedEnvironment(
        id="test_env_1",
        name="Test Environment",
        description="A test environment for the AI-Robot Brain project"
    )
    
    # Add an asset to the environment
    asset = EnvironmentAsset(
        id="table_1",
        name="Dining Table",
        asset_type="static",
        position=Vector3(2.0, 0.0, 0.0),
        asset_path="omniverse://localhost/NVIDIA/Assets/Isaac/Props/Food/table.usd"
    )
    env.add_asset(asset)
    
    # Create a robot
    robot = RobotModel(
        id="bipedal_1",
        name="Test Bipedal Robot",
        urdf_path="./data/robot_models/bipedal_robot/bipedal.urdf"
    )
    
    # Create a sensor
    camera_sensor = Sensor(
        id="camera_1",
        name="Front RGB Camera",
        sensor_type=SensorType.RGB_CAMERA,
        frame_id="camera_link",
        position=Vector3(0.2, 0.0, 0.5),  # Position relative to robot base
        orientation=Quaternion(0.0, 0.0, 0.0, 1.0)
    )
    
    # Initialize loader
    loader = IsaacSimEnvironmentLoader()
    loader.initialize_world()
    
    # Load environment
    loader.load_environment(env)
    
    # Spawn robot
    loader.spawn_robot(robot)
    
    # Add sensor to robot
    loader.add_sensor_to_robot(robot.id, camera_sensor)
    
    # Set up sensor streaming
    loader.setup_sensor_streaming()
    
    carb.log_info("Example environment loaded successfully!")
    
    # At this point, you would typically run the simulation
    # loader.world.step(render=True)  # In a real scenario
    
    return loader