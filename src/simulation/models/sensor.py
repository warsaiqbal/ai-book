"""
Specialized Sensor data model for the simulation environment based on the 
base model defined in utils.data_models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
from src.utils.data_models import (
    BaseEntity, Vector3, Quaternion, Sensor as BaseSensor,
    SensorType
)


@dataclass
class SensorParameters:
    """Detailed parameters for different sensor types."""
    # Camera-specific parameters
    width: int = 640
    height: int = 480
    fov: float = 1.047  # Field of view in radians (60 degrees)
    near_clip: float = 0.1  # Near clipping distance in meters
    far_clip: float = 10.0   # Far clipping distance in meters
    fps: int = 30  # Frame rate
    
    # LIDAR-specific parameters
    horizontal_resolution: int = 640  # Number of horizontal points
    vertical_resolution: int = 32   # Number of vertical points
    horizontal_fov: float = 3.14159  # Horizontal field of view in radians (180 degrees)
    vertical_fov: float = 0.523       # Vertical field of view in radians (30 degrees)
    min_range: float = 0.1          # Minimum range in meters
    max_range: float = 25.0         # Maximum range in meters
    
    # IMU-specific parameters
    noise_density: float = 1.0e-3    # Noise density (continuous density)
    random_walk: float = 1.0e-4      # Random walk (continuous density)
    
    # General sensor parameters
    update_rate: float = 30.0  # Hz
    latency: float = 0.01      # seconds
    resolution: float = 0.001  # sensor resolution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'width': self.width,
            'height': self.height,
            'fov': self.fov,
            'near_clip': self.near_clip,
            'far_clip': self.far_clip,
            'fps': self.fps,
            'horizontal_resolution': self.horizontal_resolution,
            'vertical_resolution': self.vertical_resolution,
            'horizontal_fov': self.horizontal_fov,
            'vertical_fov': self.vertical_fov,
            'min_range': self.min_range,
            'max_range': self.max_range,
            'noise_density': self.noise_density,
            'random_walk': self.random_walk,
            'update_rate': self.update_rate,
            'latency': self.latency,
            'resolution': self.resolution
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        return cls(
            width=data.get('width', 640),
            height=data.get('height', 480),
            fov=data.get('fov', 1.047),
            near_clip=data.get('near_clip', 0.1),
            far_clip=data.get('far_clip', 10.0),
            fps=data.get('fps', 30),
            horizontal_resolution=data.get('horizontal_resolution', 640),
            vertical_resolution=data.get('vertical_resolution', 32),
            horizontal_fov=data.get('horizontal_fov', 3.14159),
            vertical_fov=data.get('vertical_fov', 0.523),
            min_range=data.get('min_range', 0.1),
            max_range=data.get('max_range', 25.0),
            noise_density=data.get('noise_density', 1.0e-3),
            random_walk=data.get('random_walk', 1.0e-4),
            update_rate=data.get('update_rate', 30.0),
            latency=data.get('latency', 0.01),
            resolution=data.get('resolution', 0.001)
        )


@dataclass
class SensorDataBuffer:
    """Buffer to store sensor data."""
    max_size: int = 100  # Maximum number of data entries to store
    data: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_data(self, data_entry: Dict[str, Any]):
        """Add a data entry to the buffer."""
        self.data.append(data_entry)
        # Keep only the most recent entries
        if len(self.data) > self.max_size:
            self.data = self.data[-self.max_size:]
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """Get the most recent data entry."""
        if self.data:
            return self.data[-1]
        return None
    
    def clear(self):
        """Clear the buffer."""
        self.data = []


@dataclass
class Sensor(BaseSensor):
    """
    Specialized sensor model for simulation with additional fields specific to Isaac Sim.
    
    Extends the base Sensor with Isaac Sim specific properties.
    """
    # Isaac Sim specific properties
    isaac_sensor_path: Optional[str] = None
    sensor_type_name: Optional[str] = None  # Isaac Sim specific sensor type name
    render_product_path: Optional[str] = None  # Path to the render product for the sensor
    
    # Detailed parameters
    params_obj: Optional[SensorParameters] = None
    
    # Simulation-specific properties
    sensor_noise: float = 0.0  # Noise level for the sensor
    update_frequency: float = 30.0  # How often the sensor updates in Hz
    data_buffer: Optional[SensorDataBuffer] = None  # Buffer to store sensor data
    
    def __post_init__(self):
        """Initialize objects if not provided."""
        super().__post_init__()  # Call parent __post_init__
        
        if self.params_obj is None:
            # Convert dict to object if parameters exist, otherwise create default
            if self.parameters:
                self.params_obj = SensorParameters.from_dict(self.parameters)
            else:
                self.params_obj = SensorParameters()
        
        if self.data_buffer is None:
            # Create default data buffer
            self.data_buffer = SensorDataBuffer()
    
    def set_parameters(self, params: SensorParameters):
        """Set the sensor parameters."""
        self.params_obj = params
        # Also update the base parameters dict for compatibility
        self.parameters = params.to_dict()
    
    def get_parameters(self) -> SensorParameters:
        """Get the sensor parameters."""
        return self.params_obj
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert the sensor to a configuration dictionary suitable for Isaac Sim."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sensor_type': self.sensor_type.value,
            'frame_id': self.frame_id,
            'position': {'x': self.position.x, 'y': self.position.y, 'z': self.position.z},
            'orientation': {'x': self.orientation.x, 'y': self.orientation.y, 'z': self.orientation.z, 'w': self.orientation.w},
            'connected': self.connected,
            'parameters': self.params_obj.to_dict() if self.params_obj else {},
            'sensor_data_path': self.sensor_data_path,
            'isaac_sensor_path': self.isaac_sensor_path,
            'sensor_type_name': self.sensor_type_name,
            'render_product_path': self.render_product_path,
            'sensor_noise': self.sensor_noise,
            'update_frequency': self.update_frequency
        }
    
    @classmethod
    def from_config_dict(cls, config_data: Dict[str, Any]):
        """Create a sensor from a configuration dictionary."""
        # Extract base properties
        sensor_id = config_data.get('id', f'sensor_{hash(str(config_data)) % 10000}')
        name = config_data.get('name', 'unnamed_sensor')
        description = config_data.get('description', '')
        sensor_type = SensorType(config_data.get('sensor_type', 'rgb_camera'))
        
        # Create position
        pos_data = config_data.get('position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        position = Vector3(pos_data['x'], pos_data['y'], pos_data['z'])
        
        # Create orientation
        rot_data = config_data.get('orientation', {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})
        orientation = Quaternion(rot_data['x'], rot_data['y'], rot_data['z'], rot_data['w'])
        
        # Create instance
        sensor = cls(
            id=sensor_id,
            name=name,
            description=description,
            sensor_type=sensor_type,
            frame_id=config_data.get('frame_id', 'sensor_link'),
            position=position,
            orientation=orientation,
            connected=config_data.get('connected', True),
            sensor_data_path=config_data.get('sensor_data_path', ''),
        )
        
        # Set Isaac-specific properties
        sensor.isaac_sensor_path = config_data.get('isaac_sensor_path')
        sensor.sensor_type_name = config_data.get('sensor_type_name')
        sensor.render_product_path = config_data.get('render_product_path')
        sensor.sensor_noise = config_data.get('sensor_noise', 0.0)
        sensor.update_frequency = config_data.get('update_frequency', 30.0)
        
        # Set parameters
        if 'parameters' in config_data:
            sensor.params_obj = SensorParameters.from_dict(config_data['parameters'])
        
        return sensor
    
    def save_to_file(self, file_path: str):
        """Save the sensor configuration to a file."""
        config = self.to_config_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the sensor configuration from a file."""
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        return cls.from_config_dict(config)
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample sensor data based on the sensor type."""
        import time
        import random
        
        sample_data = {
            'timestamp': time.time(),
            'sensor_id': self.id,
            'sensor_type': self.sensor_type.value
        }
        
        # Generate different data based on sensor type
        if self.sensor_type == SensorType.RGB_CAMERA:
            sample_data['data_type'] = 'image'
            sample_data['width'] = self.params_obj.width
            sample_data['height'] = self.params_obj.height
            sample_data['format'] = 'rgb'
            sample_data['data'] = f"simulated_rgb_image_{int(time.time())}.png"
            
        elif self.sensor_type == SensorType.DEPTH_CAMERA:
            sample_data['data_type'] = 'depth_image'
            sample_data['width'] = self.params_obj.width
            sample_data['height'] = self.params_obj.height
            sample_data['format'] = 'depth'
            sample_data['data'] = f"simulated_depth_image_{int(time.time())}.png"
            sample_data['min_depth'] = self.params_obj.near_clip
            sample_data['max_depth'] = self.params_obj.far_clip
            
        elif self.sensor_type == SensorType.LIDAR:
            sample_data['data_type'] = 'pointcloud'
            sample_data['points'] = self.params_obj.horizontal_resolution * self.params_obj.vertical_resolution
            sample_data['min_range'] = self.params_obj.min_range
            sample_data['max_range'] = self.params_obj.max_range
            sample_data['data'] = f"simulated_lidar_{int(time.time())}.pcd"
            
        elif self.sensor_type == SensorType.IMU:
            sample_data['data_type'] = 'imu'
            sample_data['linear_acceleration'] = [
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(-9.81, self.params_obj.noise_density)
            ]
            sample_data['angular_velocity'] = [
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density)
            ]
            sample_data['orientation'] = [0, 0, 0, 1]  # [x, y, z, w]
            
        elif self.sensor_type == SensorType.FORCE_TORQUE:
            sample_data['data_type'] = 'force_torque'
            sample_data['force'] = [
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density)
            ]
            sample_data['torque'] = [
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density),
                random.gauss(0, self.params_obj.noise_density)
            ]
        
        # Add noise based on sensor noise parameter
        if self.sensor_noise > 0:
            # Apply noise to relevant fields based on sensor type
            if self.sensor_type in [SensorType.IMU, SensorType.FORCE_TORQUE]:
                for field in ['linear_acceleration', 'angular_velocity', 'force', 'torque']:
                    if field in sample_data:
                        for i in range(len(sample_data[field])):
                            sample_data[field][i] += random.gauss(0, self.sensor_noise)
        
        return sample_data


@dataclass
class SensorTransform:
    """Represents the transformation of a sensor in the robot frame."""
    sensor_id: str
    parent_frame: str  # The frame to which the sensor is attached
    child_frame: str   # The sensor's own frame
    translation: Vector3 = field(default_factory=Vector3)  # Position offset
    rotation: Quaternion = field(default_factory=Quaternion)  # Rotation offset
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'sensor_id': self.sensor_id,
            'parent_frame': self.parent_frame,
            'child_frame': self.child_frame,
            'translation': {'x': self.translation.x, 'y': self.translation.y, 'z': self.translation.z},
            'rotation': {'x': self.rotation.x, 'y': self.rotation.y, 'z': self.rotation.z, 'w': self.rotation.w},
            'timestamp': self.timestamp
        }


@dataclass
class SensorReading:
    """Represents a single reading from a sensor."""
    sensor_id: str
    timestamp: float
    data: Any  # The actual sensor data
    frame_id: str = ""  # The frame in which the data is expressed
    coordinate_system: str = "sensor"  # "sensor", "world", or other coordinate systems
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp,
            'frame_id': self.frame_id,
            'coordinate_system': self.coordinate_system
        }
        
        # Handle different data types appropriately
        if isinstance(self.data, (list, tuple)):
            result['data'] = list(self.data)
        elif isinstance(self.data, dict):
            result['data'] = self.data
        elif hasattr(self.data, 'to_dict'):
            result['data'] = self.data.to_dict()
        else:
            result['data'] = str(self.data)  # Convert to string representation
            
        return result


@dataclass
class SensorCalibration:
    """Calibration data for a sensor."""
    sensor_id: str
    calibration_date: str  # ISO date string
    calibration_data: Dict[str, Any]  # Calibration parameters specific to sensor type
    calibration_error: float = 0.0  # Average calibration error
    temperature: Optional[float] = None  # Temperature during calibration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'sensor_id': self.sensor_id,
            'calibration_date': self.calibration_date,
            'calibration_data': self.calibration_data,
            'calibration_error': self.calibration_error,
            'temperature': self.temperature
        }
    
    @classmethod
    def from_intrinsics_matrix(cls, sensor_id: str, intrinsics: List[float], 
                              distortion_coeffs: List[float]) -> 'SensorCalibration':
        """
        Create a calibration object from intrinsics matrix and distortion coefficients.
        
        Args:
            sensor_id: ID of the sensor
            intrinsics: 9-element list representing the 3x3 intrinsics matrix [fx, 0, cx, 0, fy, cy, 0, 0, 1]
            distortion_coeffs: List of distortion coefficients [k1, k2, p1, p2, k3, ...]
        """
        calibration_data = {
            'intrinsics': intrinsics,
            'distortion_coefficients': distortion_coeffs,
            'model': 'pinhole'  # Default camera model
        }
        
        return cls(
            sensor_id=sensor_id,
            calibration_date='2025-12-12',  # Current date
            calibration_data=calibration_data
        )