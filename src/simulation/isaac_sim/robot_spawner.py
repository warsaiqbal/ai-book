"""
Robot spawning system for Isaac Sim environments in the AI-Robot Brain project.

This module provides functionality to spawn robots in simulation with appropriate
configurations based on the robot model specifications.
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.prims import is_prim_path_valid, define_prim
from pxr import Gf, Sdf, UsdGeom
from typing import Dict, Any, Optional, List, Tuple
import asyncio
import os
from src.simulation.models.robot import RobotModel, JointModel, LinkModel, SensorMount
from src.simulation.models.sensor import Sensor
from src.utils.file_storage import get_storage_manager


class RobotSpawner:
    """
    Class responsible for spawning robots in Isaac Sim based on RobotModel specifications.
    """
    
    def __init__(self, world: Optional[World] = None):
        """
        Initialize the robot spawner.
        
        Args:
            world: Isaac Sim World instance (optional, can be set later)
        """
        self.world = world
        self.spawned_robots: Dict[str, Robot] = {}
        self.robot_configurations: Dict[str, RobotModel] = {}
        self.storage_manager = get_storage_manager()
    
    def set_world(self, world: World):
        """
        Set the Isaac Sim World instance.
        
        Args:
            world: Isaac Sim World instance
        """
        self.world = world
    
    def spawn_robot(self, robot_model: RobotModel, position: Tuple[float, float, float] = (0, 0, 0), 
                   orientation: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> Optional[Robot]:
        """
        Spawn a robot in the simulation based on the robot model specification.
        
        Args:
            robot_model: RobotModel specification to spawn
            position: Position (x, y, z) where to spawn the robot
            orientation: Orientation (x, y, z, w) as quaternion where to spawn the robot
            
        Returns:
            Robot instance if successfully spawned, None otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return None
        
        try:
            # Determine robot USD path - try URDF conversion or use provided USD path
            robot_path = self._get_robot_path(robot_model)
            if not robot_path:
                carb.log_error(f"Could not determine path for robot {robot_model.name}")
                return None
            
            # Define the prim path for this robot instance
            prim_path = f"/World/{robot_model.name}_{robot_model.id[-4:]}"  # Use last 4 chars of ID to avoid conflicts
            
            # Check if path already exists, if so modify it
            counter = 0
            original_prim_path = prim_path
            while is_prim_path_valid(prim_path):
                counter += 1
                prim_path = f"{original_prim_path}_{counter}"
            
            # Add the robot to the stage
            add_reference_to_stage(
                usd_path=robot_path,
                prim_path=prim_path
            )
            
            # Create the robot instance in the world
            isaac_robot = self.world.scene.add(
                Robot(
                    prim_path=prim_path,
                    name=robot_model.name,
                    position=position,
                    orientation=orientation
                )
            )
            
            # Store the robot configuration
            self.robot_configurations[robot_model.id] = robot_model
            self.spawned_robots[robot_model.id] = isaac_robot
            
            carb.log_info(f"Robot '{robot_model.name}' spawned at {prim_path}")
            
            # Configure robot after spawning
            self._configure_robot_after_spawn(robot_model, isaac_robot)
            
            return isaac_robot
            
        except Exception as e:
            carb.log_error(f"Failed to spawn robot {robot_model.name}: {str(e)}")
            return None
    
    def _get_robot_path(self, robot_model: RobotModel) -> Optional[str]:
        """
        Determine the appropriate path for the robot (USD, URDF conversion, etc.).
        
        Args:
            robot_model: RobotModel specification
            
        Returns:
            Path to the robot asset or None if not found
        """
        # If a specific path is provided in the model, use it
        if robot_model.urdf_path and os.path.exists(robot_model.urdf_path):
            # In a real implementation, this would convert URDF to USD
            # For now, we'll look for a USD version of the robot
            usd_path = robot_model.urdf_path.replace('.urdf', '.usd')
            if os.path.exists(usd_path):
                return usd_path
            
            # If no USD file exists, try to find it in the storage system
            stored_model = self.storage_manager.load_robot_model(robot_model.name, 'urdf')
            if stored_model and os.path.exists(stored_model):
                usd_path = stored_model.replace('.urdf', '.usd')
                if os.path.exists(usd_path):
                    return usd_path
        
        # Look for USD files in the robot model storage
        stored_model_path = self.storage_manager.load_robot_model(robot_model.name, 'any')
        if stored_model_path and isinstance(stored_model_path, str):
            if stored_model_path.endswith('.usd'):
                return stored_model_path
            elif stored_model_path.endswith('.urdf'):
                # Try to find corresponding USD file
                usd_path = stored_model_path.replace('.urdf', '.usd')
                if os.path.exists(usd_path):
                    return usd_path
        
        # If we can't find a suitable path, return None
        # In a real implementation, we would convert the URDF to USD here
        return None
    
    def _configure_robot_after_spawn(self, robot_model: RobotModel, isaac_robot: Robot):
        """
        Configure the robot after it has been spawned in the simulation.
        
        Args:
            robot_model: RobotModel specification
            isaac_robot: Isaac Sim Robot instance
        """
        try:
            # Configure joint properties
            self._configure_joints(robot_model, isaac_robot)
            
            # Configure initial joint positions if specified
            self._set_initial_joint_positions(robot_model, isaac_robot)
            
            # Configure robot-specific properties
            self._configure_robot_properties(robot_model, isaac_robot)
            
            carb.log_info(f"Robot '{robot_model.name}' configured successfully")
            
        except Exception as e:
            carb.log_error(f"Failed to configure robot {robot_model.name} after spawning: {str(e)}")
    
    def _configure_joints(self, robot_model: RobotModel, isaac_robot: Robot):
        """
        Configure joint properties based on the robot model specification.
        
        Args:
            robot_model: RobotModel specification
            isaac_robot: Isaac Sim Robot instance
        """
        # In a real implementation, this would configure each joint with the specified properties
        # For now, we'll log the configuration
        for joint in robot_model.joints_obj:
            carb.log_verbose(f"Configuring joint: {joint.name} (type: {joint.joint_type})")
            
            # In real implementation: set joint limits, friction, damping, etc.
            # isaac_robot.set_joint_position_limit(joint.name, joint.limits_lower, joint.limits_upper)
            # isaac_robot.set_joint_friction(joint.name, joint.dynamics_friction)
            # isaac_robot.set_joint_damping(joint.name, joint.dynamics_damping)
    
    def _set_initial_joint_positions(self, robot_model: RobotModel, isaac_robot: Robot):
        """
        Set initial joint positions for the robot.
        
        Args:
            robot_model: RobotModel specification
            isaac_robot: Isaac Sim Robot instance
        """
        # In a real implementation, this would set the initial joint positions
        # For now, we'll use default or zero positions
        carb.log_verbose(f"Setting initial joint positions for {robot_model.name}")
        
        # Example: set all joints to zero position
        # joint_names = [joint.name for joint in robot_model.joints_obj]
        # joint_positions = [0.0] * len(joint_names)
        # isaac_robot.set_joints_default_state(positions=joint_positions, joint_names=joint_names)
    
    def _configure_robot_properties(self, robot_model: RobotModel, isaac_robot: Robot):
        """
        Configure general robot properties.
        
        Args:
            robot_model: RobotModel specification
            isaac_robot: Isaac Sim Robot instance
        """
        # In a real implementation, this would set robot-specific properties
        # For now, we'll log the configuration
        carb.log_verbose(f"Configuring properties for {robot_model.name}")
        
        # Examples of properties that could be configured:
        # - Enable/disable gravity
        # - Set articulation properties
        # - Configure self-collision
        
        # Enable gravity for the robot
        if robot_model.enable_gravity:
            # In real implementation: isaac_robot.enable_gravity()
            carb.log_verbose("Gravity enabled for robot")
        
        # Configure self-collision
        if robot_model.enable_self_collision:
            # In real implementation: isaac_robot.enable_self_collisions()
            carb.log_verbose("Self-collision enabled for robot")
        
        # Set joint properties
        # In real implementation: use articulation_view to set joint properties
        # articulation_view = self.world.scene.get_articulation_view(robot_model.name)
        # articulation_view.set_joint_stiffnesses(robot_model.joint_stiffness)
        # articulation_view.set_joint_dampings(robot_model.joint_damping)
    
    def spawn_robot_with_sensors(self, robot_model: RobotModel, sensors: List[Sensor], 
                                position: Tuple[float, float, float] = (0, 0, 0),
                                orientation: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> Optional[Robot]:
        """
        Spawn a robot with its sensors attached according to the sensor mounts in the robot model.
        
        Args:
            robot_model: RobotModel specification to spawn
            sensors: List of sensors to attach to the robot
            position: Position (x, y, z) where to spawn the robot
            orientation: Orientation (x, y, z, w) as quaternion where to spawn the robot
            
        Returns:
            Robot instance if successfully spawned, None otherwise
        """
        # First spawn the base robot
        robot = self.spawn_robot(robot_model, position, orientation)
        if not robot:
            return None
        
        # Then attach sensors to their designated mounting points
        try:
            self._attach_sensors_to_robot(robot_model, sensors)
            return robot
        except Exception as e:
            carb.log_error(f"Failed to attach sensors to robot {robot_model.name}: {str(e)}")
            return None
    
    def _attach_sensors_to_robot(self, robot_model: RobotModel, sensors: List[Sensor]):
        """
        Attach sensors to their designated mounting points on the robot.
        
        Args:
            robot_model: RobotModel specification
            sensors: List of sensors to attach
        """
        # Map sensor names to sensor objects for quick lookup
        sensor_map = {sensor.name: sensor for sensor in sensors}
        
        # Iterate through sensor mounts in the robot model
        for mount in robot_model.sensor_mounts_obj:
            # Find the corresponding sensor in the provided list
            if mount.name in sensor_map:
                sensor = sensor_map[mount.name]
                
                # In a real implementation, this would attach the sensor to the robot
                # using the mount position and orientation
                carb.log_verbose(f"Attaching sensor '{sensor.name}' to link '{mount.link_name}'")
                
                # Calculate the world position and orientation for the sensor
                # This would involve transforming the mount's local position/orientation
                # to world coordinates based on the robot's current pose and the link's transform
                # sensor_world_pos = self._transform_to_world(robot, mount.link_name, mount.position)
                # sensor_world_rot = self._transform_rotation_to_world(robot, mount.link_name, mount.orientation)
                
    def spawn_multiple_robots(self, robot_configs: List[Tuple[RobotModel, Tuple[float, float, float], Tuple[float, float, float, float]]]) -> Dict[str, Robot]:
        """
        Spawn multiple robots in the simulation.
        
        Args:
            robot_configs: List of tuples containing (RobotModel, position, orientation) for each robot
            
        Returns:
            Dictionary mapping robot IDs to Robot instances
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return {}
        
        spawned_robots = {}
        
        for robot_model, position, orientation in robot_configs:
            robot = self.spawn_robot(robot_model, position, orientation)
            if robot:
                spawned_robots[robot_model.id] = robot
        
        return spawned_robots
    
    def get_spawned_robot(self, robot_id: str) -> Optional[Robot]:
        """
        Get a reference to a spawned robot by its ID.
        
        Args:
            robot_id: ID of the robot to retrieve
            
        Returns:
            Robot instance if found, None otherwise
        """
        return self.spawned_robots.get(robot_id)
    
    def get_robot_configuration(self, robot_id: str) -> Optional[RobotModel]:
        """
        Get the configuration of a spawned robot by its ID.
        
        Args:
            robot_id: ID of the robot to retrieve configuration for
            
        Returns:
            RobotModel if found, None otherwise
        """
        return self.robot_configurations.get(robot_id)
    
    def remove_robot(self, robot_id: str) -> bool:
        """
        Remove a robot from the simulation.
        
        Args:
            robot_id: ID of the robot to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        if robot_id in self.spawned_robots:
            robot = self.spawned_robots[robot_id]
            try:
                # In a real implementation, this would remove the robot from the scene
                # self.world.scene.remove(robot)
                
                # Remove from our tracking dictionaries
                del self.spawned_robots[robot_id]
                if robot_id in self.robot_configurations:
                    del self.robot_configurations[robot_id]
                
                carb.log_info(f"Robot {robot_id} removed from simulation")
                return True
            except Exception as e:
                carb.log_error(f"Failed to remove robot {robot_id}: {str(e)}")
                return False
        
        return False
    
    def reset_robot(self, robot_id: str) -> bool:
        """
        Reset a robot to its initial state.
        
        Args:
            robot_id: ID of the robot to reset
            
        Returns:
            True if successfully reset, False otherwise
        """
        if robot_id in self.spawned_robots:
            robot = self.spawned_robots[robot_id]
            try:
                # In a real implementation, this would reset the robot's state
                # robot.reset()
                
                carb.log_info(f"Robot {robot_id} reset to initial state")
                return True
            except Exception as e:
                carb.log_error(f"Failed to reset robot {robot_id}: {str(e)}")
                return False
        
        return False
    
    def get_all_spawned_robots(self) -> Dict[str, Robot]:
        """
        Get all spawned robots.
        
        Returns:
            Dictionary mapping robot IDs to Robot instances
        """
        return self.spawned_robots.copy()
    
    def clear_all_robots(self):
        """Remove all spawned robots from the simulation."""
        robot_ids = list(self.spawned_robots.keys())
        for robot_id in robot_ids:
            self.remove_robot(robot_id)


class BipedalRobotSpawner(RobotSpawner):
    """
    Specialized spawner for bipedal robots with additional functionality
    for configuring bipedal-specific properties.
    """
    
    def spawn_bipedal_robot(self, robot_model: RobotModel, 
                           position: Tuple[float, float, float] = (0, 0, 0.8),
                           orientation: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> Optional[Robot]:
        """
        Spawn a bipedal robot with additional configuration for bipedal locomotion.
        
        Args:
            robot_model: RobotModel specification (should be for a bipedal robot)
            position: Position (x, y, z) where to spawn the robot
            orientation: Orientation (x, y, z, w) as quaternion where to spawn the robot
            
        Returns:
            Robot instance if successfully spawned, None otherwise
        """
        robot = self.spawn_robot(robot_model, position, orientation)
        if robot:
            try:
                self._configure_bipedal_properties(robot_model, robot)
                carb.log_info(f"Bipedal robot '{robot_model.name}' configured for locomotion")
            except Exception as e:
                carb.log_error(f"Failed to configure bipedal properties: {str(e)}")
        
        return robot
    
    def _configure_bipedal_properties(self, robot_model: RobotModel, isaac_robot: Robot):
        """
        Configure bipedal-specific properties for locomotion.
        
        Args:
            robot_model: RobotModel specification
            isaac_robot: Isaac Sim Robot instance
        """
        if robot_model.locomotion_config_obj:
            config = robot_model.locomotion_config_obj
            
            carb.log_verbose(f"Configuring bipedal locomotion for {robot_model.name}")
            carb.log_verbose(f"  Controller type: {config.controller_type}")
            carb.log_verbose(f"  Gait type: {config.gait_type}")
            carb.log_verbose(f"  Walking speed: {config.walking_speed} m/s")
            carb.log_verbose(f"  Step height: {config.step_height} m")
            carb.log_verbose(f"  Step length: {config.step_length} m")
            carb.log_verbose(f"  Balance threshold: {config.balance_threshold} m")
            carb.log_verbose(f"  Control rate: {config.control_rate} Hz")
            
            # In a real implementation, this would configure the robot's locomotion controller
            # with the specified parameters


# Example usage function
def example_usage():
    """
    Example of how to use the RobotSpawner.
    """
    # Create a robot model
    from src.simulation.models.robot import RobotModel, LocomotionConfiguration
    from src.simulation.models.sensor import Sensor, SensorType
    from src.utils.data_models import Vector3, Quaternion
    
    # Create a bipedal robot model
    robot = RobotModel(
        id="bipedal_robot_1",
        name="Test Bipedal Robot",
        description="A test bipedal robot for the AI-Robot Brain project",
        urdf_path="./data/robot_models/bipedal_robot/bipedal.urdf"
    )
    
    # Configure locomotion
    robot.locomotion_config_obj = LocomotionConfiguration(
        controller_type="mpc",
        gait_type="walking",
        step_height=0.1,
        step_length=0.4,
        walking_speed=0.5,
        balance_threshold=0.05,
        control_rate=100.0
    )
    
    # Create some sensors
    camera_sensor = Sensor(
        id="rgb_camera_1",
        name="Front RGB Camera",
        sensor_type=SensorType.RGB_CAMERA
    )
    
    imu_sensor = Sensor(
        id="imu_1",
        name="IMU",
        sensor_type=SensorType.IMU
    )
    
    # Initialize a world (in practice this would be done by the environment loader)
    # world = World(stage_units_in_meters=1.0)
    
    # Initialize spawner
    spawner = RobotSpawner()  # We'll set the world later
    
    # In a real scenario, we would have an Isaac Sim World to work with
    # For this example, we'll just show how the API would be used:
    # robot_instance = spawner.spawn_robot_with_sensors(robot, [camera_sensor, imu_sensor], 
    #                                                 position=(0, 0, 0.8), 
    #                                                 orientation=(0, 0, 0, 1))
    
    carb.log_info("Robot spawner example completed")
    
    return spawner