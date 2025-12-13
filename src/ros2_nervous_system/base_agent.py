import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from typing import List, Dict, Any, Callable, Optional
import time
import threading
from datetime import datetime

from ros2_nervous_system.python_agent_model import PythonAgent
from ros2_nervous_system.msg import RobotCommand, RobotState, SensorData


class BasePythonAgent(Node):
    """
    Base Python agent class that provides common functionality for 
    AI agents that interface with ROS controllers using rclpy.
    """
    
    def __init__(self, agent_name: str, agent_id: str = None, algorithm_type: str = "classical_control"):
        if agent_id is None:
            agent_id = agent_name.replace(" ", "_").lower()
        
        super().__init__(agent_name)
        
        # Initialize the Python Agent data model
        self.agent_data = PythonAgent(
            id=agent_id,
            name=agent_name,
            algorithm_type=algorithm_type
        )
        
        # Store references to publishers and subscribers
        self.publishers = {}
        self.subscribers = {}
        
        # Store callbacks and their conditions
        self.callbacks = {}
        
        # Agent state
        self.is_running = False
        self.decision_count = 0
        
        self.get_logger().info(f'Base Python Agent "{agent_name}" initialized')
    
    def activate(self):
        """Activate the agent"""
        self.agent_data.activate_agent()
        self.is_running = True
        self.get_logger().info(f'Agent {self.agent_data.name} activated')
    
    def deactivate(self):
        """Deactivate the agent"""
        self.agent_data.deactivate_agent()
        self.is_running = False
        self.get_logger().info(f'Agent {self.agent_data.name} deactivated')
    
    def register_publisher(self, topic_name: str, msg_type, qos_profile=None):
        """Register a publisher for the agent"""
        if qos_profile is None:
            from ros2_nervous_system.qos_profiles import DEFAULT_QOS
            qos_profile = DEFAULT_QOS
            
        publisher = self.create_publisher(msg_type, topic_name, qos_profile)
        self.publishers[topic_name] = publisher
        self.agent_data.publish_to_topic(topic_name)
        return publisher
    
    def register_subscriber(self, topic_name: str, msg_type, callback: Callable, qos_profile=None):
        """Register a subscriber for the agent"""
        if qos_profile is None:
            from ros2_nervous_system.qos_profiles import DEFAULT_QOS
            qos_profile = DEFAULT_QOS
            
        subscriber = self.create_subscription(
            msg_type,
            topic_name,
            callback,
            qos_profile
        )
        self.subscribers[topic_name] = subscriber
        self.agent_data.subscribe_to_topic(topic_name)
        return subscriber
    
    def create_command(self, command_type: str, target_positions: List[float], 
                      timeout: float = 5.0, joints: List[str] = None) -> RobotCommand:
        """Create a RobotCommand message"""
        cmd = RobotCommand()
        cmd.command_type = command_type
        cmd.target_positions = target_positions
        cmd.timeout = timeout
        cmd.joints = joints or []
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        
        return cmd
    
    def publish_command(self, topic_name: str, command: RobotCommand):
        """Publish a robot command"""
        if topic_name in self.publishers:
            self.publishers[topic_name].publish(command)
            self.decision_count += 1
            self.agent_data.last_decision_time = datetime.now()
        else:
            self.get_logger().error(f'No publisher registered for topic: {topic_name}')
    
    def update_performance_metric(self, metric_name: str, value: float):
        """Update a performance metric"""
        self.agent_data.update_performance_metric(metric_name, value)
    
    def make_decision(self, sensor_data: Dict[str, Any]) -> Optional[RobotCommand]:
        """
        Abstract method to be implemented by subclasses.
        Should process sensor_data and return a RobotCommand if appropriate.
        """
        raise NotImplementedError("Subclasses must implement make_decision method")
    
    def sensor_data_callback(self, msg, topic_name: str):
        """Generic callback for sensor data to be processed by the agent"""
        # Convert message to a dictionary that can be used by the agent decision-making
        sensor_dict = self.message_to_dict(msg)
        
        # Process the data and make a decision
        if self.is_running:
            command = self.make_decision({topic_name: sensor_dict})
            if command:
                # Publish the command (default to /robot_command if not specified)
                self.publish_command('/robot_command', command)
    
    def message_to_dict(self, msg) -> Dict[str, Any]:
        """Convert a ROS message to a dictionary representation"""
        result = {}
        for field_name in msg.get_fields_and_field_types():
            value = getattr(msg, field_name)
            if hasattr(value, '__dict__'):  # Nested message
                result[field_name] = self.message_to_dict(value)
            elif isinstance(value, list):  # Array field
                result[field_name] = [self.message_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
            else:
                result[field_name] = value
        return result


def main(args=None):
    rclpy.init(args=args)
    print("Base agent module - run specific agent implementations instead")
    rclpy.shutdown()

if __name__ == '__main__':
    main()