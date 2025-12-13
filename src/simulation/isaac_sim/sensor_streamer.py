"""
Real-time sensor data streaming system for Isaac Sim environments in the AI-Robot Brain project.

This module provides functionality to stream sensor data in real-time from the simulation
to other components of the system, such as perception modules and external systems.
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.sensor import Sensor as IsaacSensor
from omni.isaac.core.utils.prims import is_prim_path_valid
from typing import Dict, Any, Optional, List, Callable, Union
import asyncio
import numpy as np
from datetime import datetime
import json
from dataclasses import dataclass
from threading import Thread, Event
from queue import Queue, Empty
import time
from src.simulation.models.sensor import Sensor, SensorType
from src.simulation.models.robot import RobotModel
from src.utils.data_models import Vector3, Quaternion


@dataclass
class SensorDataPacket:
    """Structure for sensor data packets."""
    sensor_id: str
    timestamp: float
    data_type: str  # 'image', 'pointcloud', 'imu', etc.
    data: Any
    frame_id: str
    robot_id: str
    sequence_number: int = 0


class SensorStreamer:
    """
    Class responsible for streaming sensor data in real-time from Isaac Sim.
    """
    
    def __init__(self, world: Optional[World] = None):
        """
        Initialize the sensor streamer.
        
        Args:
            world: Isaac Sim World instance (optional, can be set later)
        """
        self.world = world
        self.is_streaming = False
        self.streaming_thread: Optional[Thread] = None
        self.shutdown_event = Event()
        self.data_queue = Queue()
        
        # Callback storage for sensor data hooks
        self.sensor_callbacks: Dict[str, List[Callable]] = {}
        
        # Storage for current sensor data
        self.current_data: Dict[str, SensorDataPacket] = {}
        
        # Sequence numbers for each sensor
        self.sequence_numbers: Dict[str, int] = {}
    
    def set_world(self, world: World):
        """
        Set the Isaac Sim World instance.
        
        Args:
            world: Isaac Sim World instance
        """
        self.world = world
    
    def start_streaming(self, sensor_ids: List[str] = None) -> bool:
        """
        Start streaming sensor data in real-time.
        
        Args:
            sensor_ids: List of sensor IDs to stream (None for all configured sensors)
            
        Returns:
            True if successfully started, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        if self.is_streaming:
            carb.log_warn("Sensor streaming is already active.")
            return True
        
        try:
            self.is_streaming = True
            self.shutdown_event.clear()
            
            # Start the streaming thread
            self.streaming_thread = Thread(target=self._streaming_loop, args=(sensor_ids,))
            self.streaming_thread.start()
            
            carb.log_info("Sensor streaming started successfully")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to start sensor streaming: {str(e)}")
            self.is_streaming = False
            return False
    
    def stop_streaming(self):
        """Stop streaming sensor data."""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        self.shutdown_event.set()
        
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=2.0)  # Wait up to 2 seconds for thread to finish
        
        carb.log_info("Sensor streaming stopped")
    
    def _streaming_loop(self, sensor_ids: List[str] = None):
        """
        Main streaming loop running in a separate thread.
        
        Args:
            sensor_ids: List of sensor IDs to stream
        """
        while not self.shutdown_event.is_set() and self.is_streaming:
            try:
                # Process one world step to update sensor data
                if self.world:
                    self.world.step(render=False)
                
                # Get sensor data for all requested sensors
                if sensor_ids:
                    for sensor_id in sensor_ids:
                        self._get_sensor_data(sensor_id)
                else:
                    # Get data for all sensors (implement based on your sensor tracking)
                    # This would require maintaining a list of active sensors
                    pass
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1.0/60.0)  # ~60 FPS
                
            except Exception as e:
                carb.log_error(f"Error in streaming loop: {str(e)}")
                break
    
    def _get_sensor_data(self, sensor_id: str):
        """
        Get data from a specific sensor.
        
        Args:
            sensor_id: ID of the sensor to get data from
        """
        # In a real implementation, this would get data from Isaac Sim sensors
        # For this example, we'll simulate data based on the sensor type
        
        # Create a mock sensor data packet
        timestamp = time.time()
        sequence_num = self.sequence_numbers.get(sensor_id, 0) + 1
        self.sequence_numbers[sensor_id] = sequence_num
        
        # Mock data based on sensor type
        mock_data = self._generate_mock_data(sensor_id)
        
        if mock_data:
            data_packet = SensorDataPacket(
                sensor_id=sensor_id,
                timestamp=timestamp,
                data_type=mock_data['type'],
                data=mock_data['data'],
                frame_id=mock_data.get('frame_id', 'base_link'),
                robot_id=mock_data.get('robot_id', 'unknown'),
                sequence_number=sequence_num
            )
            
            # Store current data
            self.current_data[sensor_id] = data_packet
            
            # Add to queue for potential consumers
            self.data_queue.put(data_packet)
            
            # Call registered callbacks
            self._trigger_callbacks(sensor_id, data_packet)
    
    def _generate_mock_data(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate mock sensor data for a sensor (in a real implementation, this would get data from Isaac Sim).
        
        Args:
            sensor_id: ID of the sensor to generate mock data for
            
        Returns:
            Dictionary with sensor data and metadata
        """
        # In a real implementation, this would query Isaac Sim for actual sensor data
        # For example:
        # - Camera: Get image data from Camera object
        # - LIDAR: Get point cloud data from LIDAR object
        # - IMU: Get acceleration and angular velocity from IMU object
        
        # For this example, we'll return mock data based on sensor type inference
        # In a real scenario, we'd have access to sensor specifications
        if "camera" in sensor_id.lower():
            # Mock camera data
            width, height = 640, 480
            # Generate a simple mock image (grayscale for simplicity)
            image_data = np.random.rand(height, width).astype(np.float32)
            
            return {
                'type': 'image',
                'data': image_data,
                'frame_id': 'camera_link',
                'robot_id': 'mock_robot',
                'width': width,
                'height': height
            }
        elif "lidar" in sensor_id.lower():
            # Mock LIDAR data
            num_points = 1000
            # Generate mock point cloud (x, y, z coordinates)
            points = np.random.rand(num_points, 3).astype(np.float32) * 10.0 - 5.0  # Range from -5 to 5 meters
            
            return {
                'type': 'pointcloud',
                'data': points,
                'frame_id': 'lidar_link',
                'robot_id': 'mock_robot',
                'num_points': num_points
            }
        elif "imu" in sensor_id.lower():
            # Mock IMU data
            linear_acceleration = [np.random.normal(0, 0.1), np.random.normal(0, 0.1), np.random.normal(-9.81, 0.1)]
            angular_velocity = [np.random.normal(0, 0.01), np.random.normal(0, 0.01), np.random.normal(0, 0.01)]
            
            return {
                'type': 'imu',
                'data': {
                    'linear_acceleration': linear_acceleration,
                    'angular_velocity': angular_velocity
                },
                'frame_id': 'imu_link',
                'robot_id': 'mock_robot'
            }
        else:
            # Default: return some generic sensor data
            return {
                'type': 'generic',
                'data': f"Mock data for sensor {sensor_id}",
                'frame_id': 'sensor_link',
                'robot_id': 'mock_robot'
            }
    
    def _trigger_callbacks(self, sensor_id: str, data_packet: SensorDataPacket):
        """
        Trigger registered callbacks for a sensor data update.
        
        Args:
            sensor_id: ID of the sensor that generated the data
            data_packet: The sensor data packet
        """
        if sensor_id in self.sensor_callbacks:
            for callback in self.sensor_callbacks[sensor_id]:
                try:
                    callback(data_packet)
                except Exception as e:
                    carb.log_error(f"Error in sensor callback for {sensor_id}: {str(e)}")
    
    def subscribe_to_sensor(self, sensor_id: str, callback: Callable[[SensorDataPacket], None]) -> bool:
        """
        Subscribe to data from a specific sensor.
        
        Args:
            sensor_id: ID of the sensor to subscribe to
            callback: Function to call when new data is received
            
        Returns:
            True if successfully subscribed, False otherwise
        """
        if sensor_id not in self.sensor_callbacks:
            self.sensor_callbacks[sensor_id] = []
        
        self.sensor_callbacks[sensor_id].append(callback)
        carb.log_info(f"Subscribed to sensor {sensor_id}")
        return True
    
    def unsubscribe_from_sensor(self, sensor_id: str, callback: Callable[[SensorDataPacket], None]) -> bool:
        """
        Unsubscribe from data from a specific sensor.
        
        Args:
            sensor_id: ID of the sensor to unsubscribe from
            callback: Function that was registered for callbacks
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        if sensor_id in self.sensor_callbacks and callback in self.sensor_callbacks[sensor_id]:
            self.sensor_callbacks[sensor_id].remove(callback)
            
            if not self.sensor_callbacks[sensor_id]:
                del self.sensor_callbacks[sensor_id]
            
            carb.log_info(f"Unsubscribed from sensor {sensor_id}")
            return True
        
        return False
    
    def get_latest_sensor_data(self, sensor_id: str) -> Optional[SensorDataPacket]:
        """
        Get the latest data from a specific sensor.
        
        Args:
            sensor_id: ID of the sensor to get data from
            
        Returns:
            Latest SensorDataPacket if available, None otherwise
        """
        return self.current_data.get(sensor_id)
    
    def get_data_from_queue(self, timeout: float = 0.1) -> Optional[SensorDataPacket]:
        """
        Get sensor data from the internal queue.
        
        Args:
            timeout: Maximum time to wait for data in seconds
            
        Returns:
            SensorDataPacket if available, None if queue is empty
        """
        try:
            return self.data_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_all_available_data(self) -> List[SensorDataPacket]:
        """
        Get all available sensor data from the internal queue.
        
        Returns:
            List of all available SensorDataPacket instances
        """
        data_list = []
        while not self.data_queue.empty():
            try:
                data_packet = self.data_queue.get_nowait()
                data_list.append(data_packet)
            except Empty:
                break
        return data_list


class ROSTranslator:
    """
    Translates sensor data from Isaac Sim format to ROS format.
    """
    
    def __init__(self):
        """Initialize the ROS translator."""
        pass
    
    def sensor_data_to_ros_message(self, data_packet: SensorDataPacket) -> Optional[Any]:
        """
        Convert a SensorDataPacket to a ROS message.
        
        Args:
            data_packet: The sensor data packet to convert
            
        Returns:
            ROS message if conversion is possible, None otherwise
        """
        try:
            if data_packet.data_type == 'image':
                return self._convert_image_to_ros(data_packet)
            elif data_packet.data_type == 'pointcloud':
                return self._convert_pointcloud_to_ros(data_packet)
            elif data_packet.data_type == 'imu':
                return self._convert_imu_to_ros(data_packet)
            else:
                # For other data types, return the raw data
                return data_packet.data
        except Exception as e:
            carb.log_error(f"Failed to convert sensor data to ROS message: {str(e)}")
            return None
    
    def _convert_image_to_ros(self, data_packet: SensorDataPacket):
        """Convert image data to ROS Image message."""
        # In a real implementation, this would create a ROS Image message
        # For now, return mock data
        mock_ros_image = {
            'header': {
                'stamp': data_packet.timestamp,
                'frame_id': data_packet.frame_id
            },
            'height': data_packet.data.get('height', 480),
            'width': data_packet.data.get('width', 640),
            'encoding': 'rgb8',
            'is_bigendian': False,
            'step': data_packet.data.get('width', 640) * 3,  # 3 bytes per pixel for RGB
            'data': data_packet.data['data'].tobytes() if isinstance(data_packet.data, np.ndarray) else b'mock_image_data'
        }
        return mock_ros_image
    
    def _convert_pointcloud_to_ros(self, data_packet: SensorDataPacket):
        """Convert pointcloud data to ROS PointCloud2 message."""
        # In a real implementation, this would create a ROS PointCloud2 message
        # For now, return mock data
        mock_ros_pointcloud = {
            'header': {
                'stamp': data_packet.timestamp,
                'frame_id': data_packet.frame_id
            },
            'height': 1,
            'width': data_packet.data.get('num_points', 1000),
            'fields': [
                {'name': 'x', 'offset': 0, 'datatype': 7, 'count': 1},  # FLOAT32
                {'name': 'y', 'offset': 4, 'datatype': 7, 'count': 1},
                {'name': 'z', 'offset': 8, 'datatype': 7, 'count': 1}
            ],
            'is_bigendian': False,
            'point_step': 12,  # 3 * 4 bytes per float
            'row_step': data_packet.data.get('num_points', 1000) * 12,
            'data': data_packet.data['data'].tobytes() if isinstance(data_packet.data, np.ndarray) else b'mock_pointcloud_data',
            'is_dense': True
        }
        return mock_ros_pointcloud
    
    def _convert_imu_to_ros(self, data_packet: SensorDataPacket):
        """Convert IMU data to ROS IMU message."""
        # In a real implementation, this would create a ROS IMU message
        # For now, return mock data
        imu_data = data_packet.data
        mock_ros_imu = {
            'header': {
                'stamp': data_packet.timestamp,
                'frame_id': data_packet.frame_id
            },
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
            'orientation_covariance': [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'angular_velocity': {
                'x': imu_data['angular_velocity'][0],
                'y': imu_data['angular_velocity'][1],
                'z': imu_data['angular_velocity'][2]
            },
            'angular_velocity_covariance': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'linear_acceleration': {
                'x': imu_data['linear_acceleration'][0],
                'y': imu_data['linear_acceleration'][1],
                'z': imu_data['linear_acceleration'][2]
            },
            'linear_acceleration_covariance': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }
        return mock_ros_imu


class DataLogger:
    """
    Logs sensor data to files for later analysis.
    """
    
    def __init__(self, log_directory: str = "./sensor_logs"):
        """
        Initialize the data logger.
        
        Args:
            log_directory: Directory to store log files
        """
        import os
        self.log_directory = log_directory
        os.makedirs(log_directory, exist_ok=True)
        self.log_files: Dict[str, TextIO] = {}
    
    def log_sensor_data(self, data_packet: SensorDataPacket):
        """
        Log sensor data to the appropriate file.
        
        Args:
            data_packet: The sensor data packet to log
        """
        try:
            # Create or get the log file for this sensor
            log_file_path = f"{self.log_directory}/{data_packet.sensor_id}_log.jsonl"
            
            if data_packet.sensor_id not in self.log_files:
                self.log_files[data_packet.sensor_id] = open(log_file_path, 'a')
            
            # Prepare the data for logging
            log_entry = {
                'timestamp': data_packet.timestamp,
                'sensor_id': data_packet.sensor_id,
                'data_type': data_packet.data_type,
                'frame_id': data_packet.frame_id,
                'robot_id': data_packet.robot_id,
                'sequence_number': data_packet.sequence_number,
                # Only serialize numpy arrays to lists to make them JSON serializable
                'data': self._serialize_data(data_packet.data)
            }
            
            # Write the entry as a JSON line
            self.log_files[data_packet.sensor_id].write(json.dumps(log_entry) + '\n')
            self.log_files[data_packet.sensor_id].flush()
            
        except Exception as e:
            carb.log_error(f"Failed to log sensor data: {str(e)}")
    
    def _serialize_data(self, data: Any) -> Any:
        """
        Serialize data to make it JSON-compatible (e.g., convert numpy arrays to lists).
        
        Args:
            data: The data to serialize
            
        Returns:
            JSON-compatible version of the data
        """
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        else:
            return data
    
    def close_all_logs(self):
        """Close all open log files."""
        for file in self.log_files.values():
            file.close()
        self.log_files.clear()


# Example usage function
def example_usage():
    """
    Example of how to use the SensorStreamer.
    """
    # Initialize streamer
    streamer = SensorStreamer()  # We'll set the world later
    
    # Define a callback to handle sensor data
    def sensor_callback(data_packet: SensorDataPacket):
        carb.log_info(f"Received data from sensor {data_packet.sensor_id}: {data_packet.data_type}")
        # Process the sensor data here based on your application needs
    
    # Subscribe to sensor data
    streamer.subscribe_to_sensor("test_camera", sensor_callback)
    
    # In a real scenario, after setting up the world:
    # streamer.set_world(world)
    # streamer.start_streaming(["test_camera"])
    # 
    # # Do other work...
    # # Get latest data
    # latest_data = streamer.get_latest_sensor_data("test_camera")
    # 
    # # Stop streaming when done
    # streamer.stop_streaming()
    
    carb.log_info("Sensor streamer example completed")
    
    return streamer