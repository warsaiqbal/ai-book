import rclpy
from rclpy.node import Node
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup


class BaseROSNode(Node):
    """
    Base class for all ROS nodes in the nervous system.
    Provides common functionality for node lifecycle management,
    parameter handling, and logging.
    """
    
    def __init__(self, node_name):
        super().__init__(node_name)
        self.get_logger().info(f"Initializing {node_name}...")
        self._node_initialized = False
        self._node_active = False
        
    def setup_node(self):
        """
        Override this method to perform node-specific setup
        like creating publishers, subscribers, services, etc.
        """
        self.get_logger().info(f"{self.get_name()} setup complete")
        self._node_initialized = True
        
    def start_node(self):
        """
        Override this method to start any processing activities
        """
        self._node_active = True
        self.get_logger().info(f"{self.get_name()} started")
        
    def stop_node(self):
        """
        Override this method to stop any processing activities
        """
        self._node_active = False
        self.get_logger().info(f"{self.get_name()} stopped")


class LifecycleROSNode(LifecycleNode):
    """
    Base class for lifecycle-managed ROS nodes in the nervous system.
    Provides full lifecycle management (configure, activate, deactivate, cleanup, shutdown).
    """
    
    def __init__(self, node_name):
        super().__init__(node_name)
        self.get_logger().info(f"Initializing Lifecycle Node {node_name}...")
        
    def setup_node(self):
        """
        Override this method to perform node-specific setup during configuring state
        like creating publishers, subscribers, services, etc.
        """
        self.get_logger().info(f"{self.get_name()} setup complete during configuring state")
        return TransitionCallbackReturn.SUCCESS
        
    def on_configure(self, state):
        """
        Called when the node enters the configuring state
        """
        self.get_logger().info(f"{self.get_name()} is configuring")
        result = self.setup_node()
        return result

    def on_activate(self, state):
        """
        Called when the node enters the activating state
        """
        self.get_logger().info(f"{self.get_name()} is activating")
        return super().on_activate(state)

    def on_deactivate(self, state):
        """
        Called when the node enters the deactivating state
        """
        self.get_logger().info(f"{self.get_name()} is deactivating")
        return super().on_deactivate(state)

    def on_cleanup(self, state):
        """
        Called when the node enters the cleaningup state
        """
        self.get_logger().info(f"{self.get_name()} is cleaning up")
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state):
        """
        Called when the node enters the shuttingdown state
        """
        self.get_logger().info(f"{self.get_name()} is shutting down")
        return TransitionCallbackReturn.SUCCESS


def create_multithreaded_executor():
    """
    Creates a multi-threaded executor suitable for ROS nodes with multiple callback groups
    """
    return MultiThreadedExecutor()