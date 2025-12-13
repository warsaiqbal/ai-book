"""
Test suite for real-time sensor data streaming functionality in the AI-Robot Brain project.

This module provides tests to validate that sensor data is streamed correctly in real-time
from the simulation environment to various consumers.
"""

import unittest
import numpy as np
from unittest.mock import Mock, MagicMock, patch, call
import time
from threading import Thread
import queue
from src.simulation.isaac_sim.sensor_streamer import SensorStreamer, SensorDataPacket, ROSTranslator, DataLogger
from src.simulation.models.sensor import Sensor, SensorType, SensorParameters
from src.simulation.models.robot import RobotModel
from src.utils.data_models import Vector3, Quaternion


class TestSensorStreaming(unittest.TestCase):
    """
    Test cases for sensor data streaming functionality.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.streamer = SensorStreamer()
        
        # Create test sensors
        self.camera_sensor = Sensor(
            id="test_camera_1",
            name="Test Camera",
            sensor_type=SensorType.RGB_CAMERA,
            frame_id="camera_frame"
        )
        
        self.lidar_sensor = Sensor(
            id="test_lidar_1",
            name="Test LIDAR",
            sensor_type=SensorType.LIDAR,
            frame_id="lidar_frame"
        )
        
        self.imu_sensor = Sensor(
            id="test_imu_1",
            name="Test IMU",
            sensor_type=SensorType.IMU,
            frame_id="imu_frame"
        )
    
    @patch('omni.isaac.core.World')
    def test_streamer_initialization(self, mock_world):
        """Test that sensor streamer initializes properly."""
        # Verify initial state
        self.assertFalse(self.streamer.is_streaming)
        self.assertIsNone(self.streamer.world)
        self.assertEqual(len(self.streamer.current_data), 0)
        self.assertTrue(self.streamer.data_queue.empty())
    
    @patch('omni.isaac.core.World')
    def test_sensor_subscription(self, mock_world):
        """Test subscribing and unsubscribing to sensor data."""
        # Define a simple callback function to collect data
        received_data = []
        def callback(data_packet):
            received_data.append(data_packet)
        
        # Subscribe to a sensor
        result = self.streamer.subscribe_to_sensor("test_camera_1", callback)
        self.assertTrue(result)
        
        # Verify the callback is registered
        self.assertIn("test_camera_1", self.streamer.sensor_callbacks)
        self.assertIn(callback, self.streamer.sensor_callbacks["test_camera_1"])
        
        # Subscribe another callback
        def callback2(data_packet):
            received_data.append(data_packet)
        
        self.streamer.subscribe_to_sensor("test_camera_1", callback2)
        self.assertEqual(len(self.streamer.sensor_callbacks["test_camera_1"]), 2)
        
        # Unsubscribe one callback
        result = self.streamer.unsubscribe_from_sensor("test_camera_1", callback)
        self.assertTrue(result)
        self.assertEqual(len(self.streamer.sensor_callbacks["test_camera_1"]), 1)
        
        # Unsubscribe last callback
        result = self.streamer.unsubscribe_from_sensor("test_camera_1", callback2)
        self.assertTrue(result)
        self.assertNotIn("test_camera_1", self.streamer.sensor_callbacks)
    
    def test_data_packet_creation(self):
        """Test creation and properties of sensor data packets."""
        # Create a test data packet
        packet = SensorDataPacket(
            sensor_id="test_sensor_1",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(480, 640, 3).astype(np.float32),
            frame_id="camera_frame",
            robot_id="test_robot_1",
            sequence_number=5
        )
        
        # Verify packet properties
        self.assertEqual(packet.sensor_id, "test_sensor_1")
        self.assertEqual(packet.data_type, "image")
        self.assertEqual(packet.frame_id, "camera_frame")
        self.assertEqual(packet.robot_id, "test_robot_1")
        self.assertEqual(packet.sequence_number, 5)
        self.assertEqual(packet.data.shape, (480, 640, 3))
    
    def test_data_queue_operations(self):
        """Test operations on the data queue."""
        # Create test packets
        packet1 = SensorDataPacket(
            sensor_id="sensor1",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="frame1",
            robot_id="robot1"
        )
        
        packet2 = SensorDataPacket(
            sensor_id="sensor2",
            timestamp=time.time(),
            data_type="pointcloud",
            data=np.random.rand(100, 3),
            frame_id="frame2",
            robot_id="robot2"
        )
        
        # Add packets to queue
        self.streamer.data_queue.put(packet1)
        self.streamer.data_queue.put(packet2)
        
        # Get packets from queue
        retrieved_packet1 = self.streamer.get_data_from_queue()
        retrieved_packet2 = self.streamer.get_data_from_queue()
        
        # Verify packets are retrieved in correct order
        self.assertEqual(retrieved_packet1.sensor_id, "sensor1")
        self.assertEqual(retrieved_packet2.sensor_id, "sensor2")
        
        # Verify queue is now empty
        self.assertIsNone(self.streamer.get_data_from_queue(timeout=0.1))
        
        # Test getting all available data
        self.streamer.data_queue.put(packet1)
        self.streamer.data_queue.put(packet2)
        all_data = self.streamer.get_all_available_data()
        self.assertEqual(len(all_data), 2)
    
    def test_latest_data_retrieval(self):
        """Test retrieval of latest sensor data."""
        # Create test packets with different timestamps
        packet1 = SensorDataPacket(
            sensor_id="test_sensor",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="frame1",
            robot_id="robot1",
            sequence_number=1
        )
        
        packet2 = SensorDataPacket(
            sensor_id="test_sensor",
            timestamp=time.time() + 1,  # Later timestamp
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="frame1",
            robot_id="robot1",
            sequence_number=2
        )
        
        # Store both packets (the second should overwrite the first)
        self.streamer.current_data["test_sensor"] = packet1
        self.streamer.current_data["test_sensor"] = packet2
        
        # Get latest data
        latest = self.streamer.get_latest_sensor_data("test_sensor")
        self.assertEqual(latest.sequence_number, 2)
        
        # Try to get non-existent sensor data
        non_existent = self.streamer.get_latest_sensor_data("non_existent_sensor")
        self.assertIsNone(non_existent)


class TestROSIntegration(unittest.TestCase):
    """
    Test cases for ROS data conversion and integration.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ros_translator = ROSTranslator()
    
    def test_image_to_ros_conversion(self):
        """Test conversion of image data to ROS format."""
        # Create a test image packet
        image_data = np.random.rand(480, 640, 3).astype(np.uint8)
        packet = SensorDataPacket(
            sensor_id="camera_1",
            timestamp=time.time(),
            data_type="image",
            data={
                'height': 480,
                'width': 640,
                'encoding': 'rgb8',
                'data': image_data
            },
            frame_id="camera_link",
            robot_id="test_robot"
        )
        
        # Convert to ROS message
        ros_msg = self.ros_translator.sensor_data_to_ros_message(packet)
        
        # Verify the conversion
        self.assertIsNotNone(ros_msg)
        self.assertEqual(ros_msg['header']['frame_id'], 'camera_link')
        self.assertEqual(ros_msg['height'], 480)
        self.assertEqual(ros_msg['width'], 640)
        self.assertEqual(ros_msg['encoding'], 'rgb8')
    
    def test_pointcloud_to_ros_conversion(self):
        """Test conversion of pointcloud data to ROS format."""
        # Create a test pointcloud packet
        points = np.random.rand(1000, 3).astype(np.float32)
        packet = SensorDataPacket(
            sensor_id="lidar_1",
            timestamp=time.time(),
            data_type="pointcloud",
            data={
                'num_points': 1000,
                'data': points
            },
            frame_id="lidar_link",
            robot_id="test_robot"
        )
        
        # Convert to ROS message
        ros_msg = self.ros_translator.sensor_data_to_ros_message(packet)
        
        # Verify the conversion
        self.assertIsNotNone(ros_msg)
        self.assertEqual(ros_msg['header']['frame_id'], 'lidar_link')
        self.assertEqual(ros_msg['width'], 1000)
        self.assertEqual(len(ros_msg['fields']), 3)  # x, y, z
    
    def test_imu_to_ros_conversion(self):
        """Test conversion of IMU data to ROS format."""
        # Create a test IMU packet
        imu_data = {
            'linear_acceleration': [0.1, 0.2, -9.7],
            'angular_velocity': [0.01, 0.02, 0.03]
        }
        packet = SensorDataPacket(
            sensor_id="imu_1",
            timestamp=time.time(),
            data_type="imu",
            data=imu_data,
            frame_id="imu_link",
            robot_id="test_robot"
        )
        
        # Convert to ROS message
        ros_msg = self.ros_translator.sensor_data_to_ros_message(packet)
        
        # Verify the conversion
        self.assertIsNotNone(ros_msg)
        self.assertEqual(ros_msg['header']['frame_id'], 'imu_link')
        self.assertEqual(ros_msg['linear_acceleration']['x'], 0.1)
        self.assertEqual(ros_msg['angular_velocity']['z'], 0.03)


class TestDataLogging(unittest.TestCase):
    """
    Test cases for sensor data logging functionality.
    """
    
    def test_data_logger_initialization(self):
        """Test that data logger initializes properly."""
        import tempfile
        import os
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = DataLogger(log_directory=temp_dir)
            
            # Verify initial state
            self.assertEqual(logger.log_directory, temp_dir)
            self.assertEqual(len(logger.log_files), 0)
    
    def test_data_logging(self):
        """Test logging of sensor data to files."""
        import tempfile
        import os
        
        # Create a test packet
        packet = SensorDataPacket(
            sensor_id="test_sensor",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="camera_link",
            robot_id="test_robot",
            sequence_number=1
        )
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = DataLogger(log_directory=temp_dir)
            
            # Log the packet
            logger.log_sensor_data(packet)
            
            # Close the logger
            logger.close_all_logs()
            
            # Check that a log file was created
            log_file_path = os.path.join(temp_dir, "test_sensor_log.jsonl")
            self.assertTrue(os.path.exists(log_file_path))
            
            # Read the log file and verify content
            with open(log_file_path, 'r') as f:
                content = f.read().strip()
                self.assertTrue(len(content) > 0)  # Should have content
                # Verify it's valid JSON
                import json
                log_entry = json.loads(content)
                self.assertEqual(log_entry['sensor_id'], 'test_sensor')
                self.assertEqual(log_entry['sequence_number'], 1)
    
    def test_data_serialization(self):
        """Test that various data types are properly serialized."""
        logger = DataLogger()
        
        # Test numpy array serialization
        test_data = {
            'array': np.array([1, 2, 3]),
            'nested': {
                'array2': np.array([[1, 2], [3, 4]])
            },
            'normal': 'value'
        }
        
        serialized = logger._serialize_data(test_data)
        
        # Verify numpy arrays were converted to lists
        self.assertIsInstance(serialized['array'], list)
        self.assertEqual(serialized['array'], [1, 2, 3])
        self.assertIsInstance(serialized['nested']['array2'], list)
        self.assertEqual(serialized['nested']['array2'], [[1, 2], [3, 4]])
        self.assertEqual(serialized['normal'], 'value')


class TestStreamingCallbacks(unittest.TestCase):
    """
    Test cases for sensor data callback functionality.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.streamer = SensorStreamer()
    
    def test_callback_execution(self):
        """Test that callbacks are executed when sensor data is available."""
        # Define a callback that will store the received data
        received_packets = []
        
        def test_callback(data_packet):
            received_packets.append(data_packet)
        
        # Subscribe to sensor data
        self.streamer.subscribe_to_sensor("test_sensor", test_callback)
        
        # Simulate receiving a data packet
        test_packet = SensorDataPacket(
            sensor_id="test_sensor",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="camera_link",
            robot_id="test_robot"
        )
        
        # Trigger callbacks manually (in real usage this would happen automatically)
        self.streamer._trigger_callbacks("test_sensor", test_packet)
        
        # Verify the callback was executed
        self.assertEqual(len(received_packets), 1)
        self.assertEqual(received_packets[0].sensor_id, "test_sensor")
    
    def test_callback_error_handling(self):
        """Test that errors in callbacks don't stop the system."""
        # Define a callback that raises an exception
        def error_callback(data_packet):
            raise Exception("Test error in callback")
        
        # Define a callback that works normally
        success_received = []
        def success_callback(data_packet):
            success_received.append(data_packet)
        
        # Subscribe both callbacks to the same sensor
        self.streamer.subscribe_to_sensor("test_sensor", error_callback)
        self.streamer.subscribe_to_sensor("test_sensor", success_callback)
        
        # Simulate receiving a data packet
        test_packet = SensorDataPacket(
            sensor_id="test_sensor",
            timestamp=time.time(),
            data_type="image",
            data=np.random.rand(10, 10),
            frame_id="camera_link",
            robot_id="test_robot"
        )
        
        # Trigger callbacks - the error should be caught and logged
        self.streamer._trigger_callbacks("test_sensor", test_packet)
        
        # Verify that the successful callback still executed
        self.assertEqual(len(success_received), 1)
        self.assertEqual(success_received[0].sensor_id, "test_sensor")


class TestStreamingPerformance(unittest.TestCase):
    """
    Test cases for sensor streaming performance.
    """
    
    def test_sequential_numbering(self):
        """Test that sequence numbers are properly maintained."""
        streamer = SensorStreamer()
        
        # Add several data points and verify sequence numbers increment
        for i in range(1, 6):
            streamer._get_sensor_data(f"sensor_{i}")
            self.assertEqual(streamer.sequence_numbers.get(f"sensor_{i}", 0), 1)
        
        # Simulate getting data multiple times for one sensor
        for i in range(3):
            streamer._get_sensor_data("sensor_multi")
        
        self.assertEqual(streamer.sequence_numbers.get("sensor_multi", 0), 3)


def suite():
    """Create a test suite combining all test cases."""
    suite = unittest.TestSuite()
    
    # Add tests for sensor streaming
    suite.addTest(unittest.makeSuite(TestSensorStreaming))
    
    # Add tests for ROS integration
    suite.addTest(unittest.makeSuite(TestROSIntegration))
    
    # Add tests for data logging
    suite.addTest(unittest.makeSuite(TestDataLogging))
    
    # Add tests for streaming callbacks
    suite.addTest(unittest.makeSuite(TestStreamingCallbacks))
    
    # Add tests for streaming performance
    suite.addTest(unittest.makeSuite(TestStreamingPerformance))
    
    return suite


if __name__ == '__main__':
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())