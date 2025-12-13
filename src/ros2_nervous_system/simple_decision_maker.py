import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from typing import List, Dict, Any, Callable, Optional
import time
import threading
from datetime import datetime

from ros2_nervous_system.python_agent_model import PythonAgent
from ros2_nervous_system.msg import RobotCommand, RobotState, SensorData
from ros2_nervous_system.base_agent import BasePythonAgent
from ros2_nervous_system.ros_bridge import get_ros_bridge


class SimpleDecisionMakerAgent(BasePythonAgent):
    """
    Simple decision maker agent that provides basic AI decision-making
    capabilities with ROS integration using the ROSBridge.
    """

    def __init__(self, agent_name: str = "simple_decision_maker"):
        super().__init__(agent_name, algorithm_type="classical_control")

        # Get the ROS bridge instance
        self.bridge = get_ros_bridge(f"bridge_{agent_name}")

        # Register subscribers for various sensor data through the bridge
        self.bridge.register_subscriber('/robot_state', RobotState, self.robot_state_callback)
        self.bridge.register_subscriber('/sensor_data', SensorData, self.sensor_data_callback)

        # Register publisher for robot commands through the bridge
        self.bridge.register_publisher('/robot_command', RobotCommand)

        # Initialize internal state for decision making
        self.target_joint_position = 0.0
        self.last_command_time = 0.0
        self.sensor_data_buffer = []  # To store recent sensor readings

        self.get_logger().info('Simple Decision Maker Agent initialized using ROSBridge')

    def sensor_data_callback(self, msg):
        """Callback for sensor data messages"""
        # Add to buffer for processing
        self.sensor_data_buffer.append({
            'timestamp': self.get_clock().now().nanoseconds * 1e-9,
            'sensor_type': msg.sensor_type,
            'sensor_name': msg.sensor_name,
            'data': list(msg.data),
            'frame_id': msg.frame_id
        })

        # Keep only recent sensor data (last 10 readings)
        if len(self.sensor_data_buffer) > 10:
            self.sensor_data_buffer.pop(0)

        # Log sensor data for debugging
        self.get_logger().info(
            f'Received sensor data from {msg.sensor_name} ({msg.sensor_type}): '
            f'[{", ".join(f"{d:.2f}" for d in msg.data)}]'
        )

        # Process with the base class method
        super().sensor_data_callback(msg, '/sensor_data')

    def robot_state_callback(self, msg):
        """Callback for robot state messages"""
        self.get_logger().info(
            f'Received robot state: {msg.robot_name}, '
            f'joints={len(msg.joint_names)}, '
            f'pos=[{", ".join(f"{p:.2f}" for p in msg.joint_positions[:3])}...]'
        )

        # Process with the base class method
        super().sensor_data_callback(msg, '/robot_state')
    
    def make_decision(self, sensor_data: Dict[str, Any]) -> Optional[RobotCommand]:
        """
        Simple decision-making algorithm:
        - If robot state is available, move to a target position
        - If sensor data indicates an obstacle, avoid it
        """
        current_time = self.get_clock().now().nanoseconds * 1e-9

        # Only make a decision every 2 seconds to avoid spamming commands
        if current_time - self.last_command_time < 2.0:
            return None

        # Check if we have robot state data
        if '/robot_state' in sensor_data:
            robot_state = sensor_data['/robot_state']
            current_positions = robot_state.get('joint_positions', [])

            # Simple target-seeking behavior
            if current_positions:
                # Calculate target to oscillate around
                import math
                self.target_joint_position = math.sin(current_time * 0.5) * 1.5

                # Create a command to move toward target
                command = self.create_command(
                    command_type='move_to',
                    target_positions=[self.target_joint_position] + current_positions[1:] if len(current_positions) > 1 else [self.target_joint_position],
                    timeout=3.0,
                    joints=['joint1'] if len(current_positions) > 0 else []
                )

                self.last_command_time = current_time
                # Use the bridge to publish the command
                self.bridge.publish_message('/robot_command', command)
                return command

        # If no specific decision was made, return None
        return None


def main(args=None):
    rclpy.init(args=args)
    
    agent = SimpleDecisionMakerAgent()
    agent.activate()
    
    try:
        rclpy.spin(agent)
    except KeyboardInterrupt:
        agent.get_logger().info('Interrupted by user')
    finally:
        agent.deactivate()
        agent.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()