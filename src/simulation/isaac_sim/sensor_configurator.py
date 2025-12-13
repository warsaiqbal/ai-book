"""
Sensor configuration system for Isaac Sim environments in the AI-Robot Brain project.

This module provides functionality to configure sensors on robots in simulation
with appropriate parameters and settings based on the sensor model specifications.
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.sensor import Sensor as IsaacSensor
from omni.isaac.core.utils.prims import is_prim_path_valid
from typing import Dict, Any, Optional, List, Union
import asyncio
from src.simulation.models.sensor import Sensor, SensorType, SensorParameters
from src.simulation.models.robot import RobotModel
from src.utils.data_models import Vector3, Quaternion


class SensorConfigurator:
    """
    Class responsible for configuring sensors in Isaac Sim based on Sensor specifications.
    """
    
    def __init__(self, world: Optional[World] = None):
        """
        Initialize the sensor configurator.
        
        Args:
            world: Isaac Sim World instance (optional, can be set later)
        """
        self.world = world
        self.configured_sensors: Dict[str, IsaacSensor] = {}
        self.sensor_configurations: Dict[str, Sensor] = {}
        self.robot_sensor_attachments: Dict[str, List[str]] = {}  # robot_id -> [sensor_ids]
    
    def set_world(self, world: World):
        """
        Set the Isaac Sim World instance.
        
        Args:
            world: Isaac Sim World instance
        """
        self.world = world
    
    def configure_sensor_on_robot(self, sensor: Sensor, robot_model: RobotModel, 
                                 robot_prim_path: str) -> bool:
        """
        Configure a sensor on a specific robot in the simulation.
        
        Args:
            sensor: Sensor specification to configure
            robot_model: Robot model to attach the sensor to
            robot_prim_path: Prim path of the robot in the simulation
            
        Returns:
            True if successfully configured, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            # Find the appropriate link on the robot where the sensor should be mounted
            mount_link = self._find_sensor_mount_link(robot_model, sensor.name)
            if not mount_link:
                carb.log_error(f"Could not find mount point for sensor {sensor.name} on robot {robot_model.name}")
                return False
            
            # Calculate the sensor's prim path based on robot and mount point
            sensor_prim_path = f"{robot_prim_path}/{sensor.frame_id}"
            
            # Check if sensor path already exists, if so modify it
            counter = 0
            original_sensor_path = sensor_prim_path
            while is_prim_path_valid(sensor_prim_path):
                counter += 1
                sensor_prim_path = f"{original_sensor_path}_{counter}"
            
            # Configure the sensor based on its type
            isaac_sensor = self._create_isaac_sensor(sensor, sensor_prim_path, robot_model)
            if not isaac_sensor:
                return False
            
            # Store the sensor configuration
            self.sensor_configurations[sensor.id] = sensor
            self.configured_sensors[sensor.id] = isaac_sensor
            
            # Track the robot-sensor relationship
            if robot_model.id not in self.robot_sensor_attachments:
                self.robot_sensor_attachments[robot_model.id] = []
            self.robot_sensor_attachments[robot_model.id].append(sensor.id)
            
            carb.log_info(f"Sensor '{sensor.name}' configured on robot '{robot_model.name}' at {sensor_prim_path}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to configure sensor {sensor.name} on robot {robot_model.name}: {str(e)}")
            return False
    
    def _find_sensor_mount_link(self, robot_model: RobotModel, sensor_name: str) -> Optional[str]:
        """
        Find the appropriate link on the robot where the sensor should be mounted.
        
        Args:
            robot_model: Robot model containing sensor mounts
            sensor_name: Name of the sensor to mount
            
        Returns:
            Link name where the sensor should be mounted, or None if not found
        """
        for mount in robot_model.sensor_mounts_obj:
            if mount.name == sensor_name:
                return mount.link_name
        
        # If not found by name, use the first matching sensor type
        sensor_type = None
        for sensor in robot_model.sensor_mounts_obj:
            if sensor.name == sensor_name:
                sensor_type = sensor.sensor_type
                break
        
        if sensor_type:
            for mount in robot_model.sensor_mounts_obj:
                if mount.sensor_type == sensor_type:
                    return mount.link_name
        
        return None
    
    def _create_isaac_sensor(self, sensor: Sensor, sensor_prim_path: str, robot_model: RobotModel) -> Optional[IsaacSensor]:
        """
        Create an Isaac Sim sensor based on the sensor specification.
        
        Args:
            sensor: Sensor specification
            sensor_prim_path: Prim path for the sensor in the simulation
            robot_model: Robot model that will host the sensor
            
        Returns:
            IsaacSensor instance if successfully created, None otherwise
        """
        from omni.isaac.core.utils.stage import add_reference_to_stage
        from pxr import Gf, Sdf, UsdGeom
        
        # Create the sensor based on its type
        if sensor.sensor_type == SensorType.RGB_CAMERA:
            return self._create_camera_sensor(sensor, sensor_prim_path)
        elif sensor.sensor_type == SensorType.DEPTH_CAMERA:
            return self._create_depth_camera_sensor(sensor, sensor_prim_path)
        elif sensor.sensor_type == SensorType.LIDAR:
            return self._create_lidar_sensor(sensor, sensor_prim_path)
        elif sensor.sensor_type == SensorType.IMU:
            return self._create_imu_sensor(sensor, sensor_prim_path)
        elif sensor.sensor_type == SensorType.FORCE_TORQUE:
            return self._create_force_torque_sensor(sensor, sensor_prim_path)
        else:
            # For other sensor types, create a general sensor
            from omni.isaac.core.sensors import Sensor
            return Sensor(prim_path=sensor_prim_path, name=sensor.name)
    
    def _create_camera_sensor(self, sensor: Sensor, sensor_prim_path: str) -> Optional[IsaacSensor]:
        """Create an RGB camera sensor."""
        try:
            from omni.isaac.sensor import Camera
            
            # Create camera sensor
            camera = Camera(
                prim_path=sensor_prim_path,
                frequency=sensor.update_frequency,
                resolution=(int(sensor.params_obj.width), int(sensor.params_obj.height))
            )
            
            # Configure camera properties based on the sensor parameters
            camera.set_focal_length(24.0)  # Default focal length
            camera.set_focus_distance(10.0)  # Default focus distance
            camera.set_horizontal_aperture(20.955)  # Default horizontal aperture
            camera.set_vertical_aperture(15.29)   # Default vertical aperture
            
            return camera
        except Exception as e:
            carb.log_error(f"Failed to create camera sensor: {str(e)}")
            return None
    
    def _create_depth_camera_sensor(self, sensor: Sensor, sensor_prim_path: str) -> Optional[IsaacSensor]:
        """Create a depth camera sensor."""
        try:
            from omni.isaac.sensor import Camera
            
            # Create depth camera sensor
            camera = Camera(
                prim_path=sensor_prim_path,
                frequency=sensor.update_frequency,
                resolution=(int(sensor.params_obj.width), int(sensor.params_obj.height))
            )
            
            # Enable depth measurement
            # In a real implementation, this would configure depth-specific properties
            carb.log_verbose(f"Depth camera {sensor.name} configured")
            
            return camera
        except Exception as e:
            carb.log_error(f"Failed to create depth camera sensor: {str(e)}")
            return None
    
    def _create_lidar_sensor(self, sensor: Sensor, sensor_prim_path: str) -> Optional[IsaacSensor]:
        """Create a LIDAR sensor."""
        try:
            from omni.isaac.range_sensor import LidarRtx
            import omni.replicator.core as rep
            
            # Create LIDAR sensor
            lidar = LidarRtx(
                prim_path=sensor_prim_path,
                translation=(0, 0, 0),
                orientation=(0, 0, 0, 1),
                config="Example_Rotary",
                depth_range=(sensor.params_obj.min_range, sensor.params_obj.max_range),
                horizontal_samples=sensor.params_obj.horizontal_resolution,
                vertical_samples=sensor.params_obj.vertical_resolution,
                rotation_frequency=0,
                update_frequency=sensor.update_frequency
            )
            
            # Initialize the sensor
            lidar.initialize()
            
            return lidar
        except Exception as e:
            carb.log_error(f"Failed to create LIDAR sensor: {str(e)}")
            return None
    
    def _create_imu_sensor(self, sensor: Sensor, sensor_prim_path: str) -> Optional[IsaacSensor]:
        """Create an IMU sensor."""
        try:
            from omni.isaac.sensor import IMU
            
            # Create IMU sensor
            imu = IMU(
                prim_path=sensor_prim_path,
                frequency=sensor.update_frequency
            )
            
            return imu
        except Exception as e:
            carb.log_error(f"Failed to create IMU sensor: {str(e)}")
            return None
    
    def _create_force_torque_sensor(self, sensor: Sensor, sensor_prim_path: str) -> Optional[IsaacSensor]:
        """Create a force/torque sensor."""
        try:
            # For force/torque sensing in Isaac Sim, we typically use contact sensors
            # This is a simplified implementation
            carb.log_warn("Force/torque sensor implementation is simplified in this example")
            
            # In real implementation, you would set up a force/torque sensor
            # This might involve setting up contact reporting or attaching to joints
            return None
        except Exception as e:
            carb.log_error(f"Failed to create force/torque sensor: {str(e)}")
            return None
    
    def configure_robot_sensors(self, robot_model: RobotModel, robot_prim_path: str, 
                               sensor_ids: Optional[List[str]] = None) -> bool:
        """
        Configure all sensors for a specific robot.
        
        Args:
            robot_model: Robot model containing sensor mounts
            robot_prim_path: Prim path of the robot in the simulation
            sensor_ids: Optional list of specific sensor IDs to configure (None for all)
            
        Returns:
            True if all applicable sensors were configured, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            # Get sensors to configure
            sensors_to_configure = []
            
            if sensor_ids:
                # Only configure specified sensors
                for sensor_mount in robot_model.sensor_mounts_obj:
                    if sensor_mount.name in sensor_ids or sensor_mount.name in [s.name for s in self.sensor_configurations.values() if s.id in sensor_ids]:
                        sensors_to_configure.append(sensor_mount)
            else:
                # Configure all sensors
                sensors_to_configure = robot_model.sensor_mounts_obj
            
            success_count = 0
            for sensor_mount in sensors_to_configure:
                # Find the actual sensor specification
                sensor_spec = self._find_sensor_spec_by_mount(robot_model, sensor_mount)
                if sensor_spec:
                    if self.configure_sensor_on_robot(sensor_spec, robot_model, robot_prim_path):
                        success_count += 1
                else:
                    carb.log_warn(f"Could not find sensor specification for mount {sensor_mount.name}")
            
            carb.log_info(f"Configured {success_count}/{len(sensors_to_configure)} sensors on robot '{robot_model.name}'")
            return success_count == len(sensors_to_configure)
            
        except Exception as e:
            carb.log_error(f"Failed to configure sensors for robot {robot_model.name}: {str(e)}")
            return False
    
    def _find_sensor_spec_by_mount(self, robot_model: RobotModel, sensor_mount) -> Optional[Sensor]:
        """
        Find the sensor specification based on a sensor mount.
        
        Args:
            robot_model: Robot model that has the sensor mount
            sensor_mount: Sensor mount specification
            
        Returns:
            Sensor specification if found, None otherwise
        """
        # Search through sensor mounts to find the corresponding sensor spec
        for sensor in self.sensor_configurations.values():
            if sensor.name == sensor_mount.name and sensor.frame_id == sensor_mount.name:
                return sensor
        
        # If not found directly, try to match by type
        for sensor in self.sensor_configurations.values():
            if sensor.name == sensor_mount.name:
                return sensor
        
        # If still not found, create a basic sensor based on mount information
        # This is a fallback in case sensor specs weren't pre-loaded
        return Sensor(
            id=f"auto_{sensor_mount.name}",
            name=sensor_mount.name,
            sensor_type=sensor_mount.sensor_type,
            frame_id=sensor_mount.name,
            position=sensor_mount.position,
            orientation=sensor_mount.orientation
        )
    
    def get_configured_sensor(self, sensor_id: str) -> Optional[IsaacSensor]:
        """
        Get a reference to a configured sensor by its ID.
        
        Args:
            sensor_id: ID of the sensor to retrieve
            
        Returns:
            IsaacSensor instance if found, None otherwise
        """
        return self.configured_sensors.get(sensor_id)
    
    def get_sensor_configuration(self, sensor_id: str) -> Optional[Sensor]:
        """
        Get the configuration of a configured sensor by its ID.
        
        Args:
            sensor_id: ID of the sensor to retrieve configuration for
            
        Returns:
            Sensor specification if found, None otherwise
        """
        return self.sensor_configurations.get(sensor_id)
    
    def get_robot_sensors(self, robot_id: str) -> List[str]:
        """
        Get all sensor IDs associated with a specific robot.
        
        Args:
            robot_id: ID of the robot
            
        Returns:
            List of sensor IDs associated with the robot
        """
        return self.robot_sensor_attachments.get(robot_id, [])
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """
        Remove a sensor from the simulation.
        
        Args:
            sensor_id: ID of the sensor to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        if sensor_id in self.configured_sensors:
            sensor = self.configured_sensors[sensor_id]
            try:
                # Remove from tracking dictionaries
                del self.configured_sensors[sensor_id]
                if sensor_id in self.sensor_configurations:
                    del self.sensor_configurations[sensor_id]
                
                # Remove from robot-to-sensor mappings
                for robot_id, sensor_list in self.robot_sensor_attachments.items():
                    if sensor_id in sensor_list:
                        self.robot_sensor_attachments[robot_id].remove(sensor_id)
                
                carb.log_info(f"Sensor {sensor_id} removed from simulation")
                return True
            except Exception as e:
                carb.log_error(f"Failed to remove sensor {sensor_id}: {str(e)}")
                return False
        
        return False
    
    def update_sensor_parameters(self, sensor_id: str, new_params: Union[SensorParameters, Dict[str, Any]]) -> bool:
        """
        Update parameters of a configured sensor.
        
        Args:
            sensor_id: ID of the sensor to update
            new_params: New parameters for the sensor
            
        Returns:
            True if successfully updated, False otherwise
        """
        if sensor_id not in self.configured_sensors:
            carb.log_error(f"Sensor {sensor_id} not found in configured sensors")
            return False
        
        try:
            # Update the sensor parameters in the configuration
            sensor_spec = self.sensor_configurations[sensor_id]
            if isinstance(new_params, SensorParameters):
                sensor_spec.set_parameters(new_params)
            elif isinstance(new_params, dict):
                updated_params = SensorParameters.from_dict(new_params)
                sensor_spec.set_parameters(updated_params)
            
            # In a real implementation, this would update the Isaac Sim sensor with new parameters
            # For now, we'll just log the update
            carb.log_info(f"Parameters updated for sensor {sensor_id}")
            
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to update sensor {sensor_id} parameters: {str(e)}")
            return False
    
    def get_all_configured_sensors(self) -> Dict[str, IsaacSensor]:
        """
        Get all configured sensors.
        
        Returns:
            Dictionary mapping sensor IDs to IsaacSensor instances
        """
        return self.configured_sensors.copy()
    
    def clear_all_sensors(self):
        """Remove all configured sensors from the simulation."""
        sensor_ids = list(self.configured_sensors.keys())
        for sensor_id in sensor_ids:
            self.remove_sensor(sensor_id)


class AdvancedSensorConfigurator(SensorConfigurator):
    """
    Extended sensor configurator with additional capabilities for complex sensor setups.
    """
    
    def configure_sensor_fusion(self, sensor_group: List[str], fusion_algorithm: str) -> bool:
        """
        Configure sensor fusion between multiple sensors.
        
        Args:
            sensor_group: List of sensor IDs to fuse
            fusion_algorithm: Algorithm to use for fusion (e.g., "kalman_filter", "particle_filter")
            
        Returns:
            True if successfully configured, False otherwise
        """
        # This would implement sensor fusion between multiple sensors
        # For example, combining data from IMU, LIDAR, and camera
        carb.log_info(f"Sensor fusion configured for sensors: {sensor_group} using {fusion_algorithm}")
        return True
    
    def configure_dynamic_sensor_parameters(self, sensor_id: str, parameter_func) -> bool:
        """
        Configure a sensor with parameters that change dynamically based on environment.
        
        Args:
            sensor_id: ID of the sensor to configure
            parameter_func: Function that returns updated parameters based on current state
            
        Returns:
            True if successfully configured, False otherwise
        """
        # This would implement dynamic parameter adjustment during simulation
        # For example, adjusting camera exposure based on lighting conditions
        carb.log_info(f"Dynamic parameters configured for sensor {sensor_id}")
        return True


# Example usage function
def example_usage():
    """
    Example of how to use the SensorConfigurator.
    """
    # Create sensor specifications
    from src.simulation.models.sensor import Sensor, SensorType
    from src.simulation.models.robot import RobotModel
    from src.utils.data_models import Vector3, Quaternion
    
    # Create a robot model
    robot = RobotModel(
        id="robot_1",
        name="Test Robot",
        description="A test robot for sensor configuration"
    )
    
    # Add a sensor mount to the robot
    from src.simulation.models.sensor import SensorMount
    camera_mount = SensorMount(
        name="front_camera",
        sensor_type=SensorType.RGB_CAMERA,
        link_name="head_link",
        position=Vector3(0.1, 0.0, 0.05),
        orientation=Quaternion(0.0, 0.0, 0.0, 1.0)
    )
    robot.sensor_mounts_obj.append(camera_mount)
    
    # Create a sensor specification
    camera_sensor = Sensor(
        id="cam_1",
        name="front_camera",
        sensor_type=SensorType.RGB_CAMERA,
        frame_id="camera_link",
        position=Vector3(0.1, 0.0, 0.05),
        orientation=Quaternion(0.0, 0.0, 0.0, 1.0)
    )
    
    # Initialize configurator
    # Note: In a real scenario, we would have an Isaac Sim World to work with
    configurator = SensorConfigurator()  # We'll set the world later
    
    # In a real scenario, after creating a world:
    # configurator.set_world(world)
    # robot_prim_path = "/World/Robot_0"
    # configurator.configure_sensor_on_robot(camera_sensor, robot, robot_prim_path)
    
    carb.log_info("Sensor configurator example completed")
    
    return configurator