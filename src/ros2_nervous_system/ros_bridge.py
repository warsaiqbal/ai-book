"""
ROS Bridge - Provides a clean interface between Python agents and ROS controllers using rclpy
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import String
from typing import Dict, List, Callable, Any, Optional
import threading
import time
from dataclasses import dataclass

from ros2_nervous_system.msg import RobotCommand, RobotState, SensorData
from ros2_nervous_system.srv import GetRobotState, ExecuteTrajectory, SetControlMode


@dataclass
class TopicSubscription:
    """Represents a topic subscription"""
    topic_name: str
    msg_type: Any
    callback: Callable
    qos_profile: QoSProfile


@dataclass
class ServiceClientInfo:
    """Represents a service client"""
    service_name: str
    srv_type: Any
    client: Any  # The actual client object


class ROSBridge(Node):
    """
    A bridge module that handles communication between Python agents and ROS controllers,
    managing serialization/deserialization and error handling.
    This creates a clean interface and allows for better debugging and monitoring.
    """
    
    def __init__(self, node_name: str = "ros_bridge"):
        super().__init__(node_name)
        
        # Store all publishers, subscribers, and service clients
        self.publishers: Dict[str, Any] = {}
        self.subscribers: Dict[str, Any] = {}
        self.service_clients: Dict[str, ServiceClientInfo] = {}
        self.service_servers: Dict[str, Any] = {}
        
        # Thread lock for safe access to shared resources
        self._lock = threading.Lock()
        
        self.get_logger().info("ROS Bridge initialized")
    
    def register_publisher(self, topic_name: str, msg_type: Any, qos_profile: QoSProfile = None):
        """Register a publisher for a specific topic"""
        if qos_profile is None:
            from ros2_nervous_system.qos_profiles import DEFAULT_QOS
            qos_profile = DEFAULT_QOS
            
        if topic_name not in self.publishers:
            publisher = self.create_publisher(msg_type, topic_name, qos_profile)
            self.publishers[topic_name] = publisher
            self.get_logger().info(f"Registered publisher for topic: {topic_name}")
            return publisher
        else:
            self.get_logger().warning(f"Publisher already exists for topic: {topic_name}")
            return self.publishers[topic_name]
    
    def register_subscriber(self, topic_name: str, msg_type: Any, callback: Callable, qos_profile: QoSProfile = None):
        """Register a subscriber for a specific topic"""
        if qos_profile is None:
            from ros2_nervous_system.qos_profiles import DEFAULT_QOS
            qos_profile = DEFAULT_QOS
            
        if topic_name not in self.subscribers:
            subscriber = self.create_subscription(
                msg_type,
                topic_name,
                callback,
                qos_profile
            )
            self.subscribers[topic_name] = subscriber
            self.get_logger().info(f"Registered subscriber for topic: {topic_name}")
            return subscriber
        else:
            self.get_logger().warning(f"Subscriber already exists for topic: {topic_name}")
            return self.subscribers[topic_name]
    
    def register_service_client(self, service_name: str, srv_type: Any):
        """Register a service client for a specific service"""
        if service_name not in self.service_clients:
            client = self.create_client(srv_type, service_name)
            client_info = ServiceClientInfo(
                service_name=service_name,
                srv_type=srv_type,
                client=client
            )
            self.service_clients[service_name] = client_info
            self.get_logger().info(f"Registered service client for: {service_name}")
            return client
        else:
            self.get_logger().warning(f"Service client already exists for: {service_name}")
            return self.service_clients[service_name].client
    
    def publish_message(self, topic_name: str, message: Any) -> bool:
        """Publish a message to a registered topic"""
        if topic_name in self.publishers:
            try:
                self.publishers[topic_name].publish(message)
                return True
            except Exception as e:
                self.get_logger().error(f"Failed to publish to {topic_name}: {e}")
                return False
        else:
            self.get_logger().error(f"No publisher registered for topic: {topic_name}")
            return False
    
    def call_service(self, service_name: str, request, timeout_sec: float = 5.0):
        """Call a registered service asynchronously"""
        if service_name in self.service_clients:
            client = self.service_clients[service_name].client
            
            # Wait for service to be available
            if not client.wait_for_service(timeout_sec=timeout_sec):
                self.get_logger().error(f"Service {service_name} not available")
                return None
            
            # Make the service call
            future = client.call_async(request)
            return future
        else:
            self.get_logger().error(f"No service client registered for: {service_name}")
            return None
    
    def get_robot_state_sync(self, robot_name: str, timeout_sec: float = 5.0) -> Optional[RobotState]:
        """Synchronous call to get robot state"""
        request = GetRobotState.Request()
        request.robot_name = robot_name
        
        future = self.call_service('get_robot_state', request, timeout_sec)
        if future:
            # Wait for the result (this will block)
            rclpy.spin_until_future_complete(self, future, timeout_sec=timeout_sec)
            return future.result()
        return None
    
    def send_robot_command(self, command: RobotCommand) -> bool:
        """Send a robot command to the default command topic"""
        return self.publish_message('/robot_command', command)
    
    def send_robot_command_to_topic(self, topic_name: str, command: RobotCommand) -> bool:
        """Send a robot command to a specific topic"""
        return self.publish_message(topic_name, command)


# Global bridge instance to be shared among agents
_ros_bridge_instance = None
_bridge_lock = threading.Lock()


def get_ros_bridge(node_name: str = "ros_bridge") -> ROSBridge:
    """Get or create the singleton ROS bridge instance"""
    global _ros_bridge_instance
    
    with _bridge_lock:
        if _ros_bridge_instance is None:
            # We need to initialize rclpy if it's not already
            if not rclpy.ok():
                rclpy.init()
            
            _ros_bridge_instance = ROSBridge(node_name)
            
            # Start the bridge in a separate thread to handle callbacks
            def spin_bridge():
                try:
                    rclpy.spin(_ros_bridge_instance)
                except KeyboardInterrupt:
                    pass
            
            bridge_thread = threading.Thread(target=spin_bridge, daemon=True)
            bridge_thread.start()
        
        return _ros_bridge_instance


def cleanup_ros_bridge():
    """Clean up the ROS bridge instance"""
    global _ros_bridge_instance
    
    with _bridge_lock:
        if _ros_bridge_instance is not None:
            _ros_bridge_instance.destroy_node()
            _ros_bridge_instance = None
            # rclpy.shutdown() is not called here as it may affect other nodes