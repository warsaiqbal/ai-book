import rclpy
from rclpy.node import Node

from ros2_nervous_system.srv import GetRobotState
from ros2_nervous_system.msg import RobotState
from builtin_interfaces.msg import Time
import math


class BasicServiceServerNode(Node):
    """
    Basic ROS service server node that provides the GetRobotState service
    to demonstrate service communication in the nervous system.
    """
    
    def __init__(self):
        super().__init__('basic_service_server')
        
        # Create a service server for GetRobotState
        self.srv = self.create_service(
            GetRobotState, 
            'get_robot_state', 
            self.get_robot_state_callback
        )
        
        self.get_logger().info('Basic Service Server Node initialized')

    def get_robot_state_callback(self, request, response):
        """Callback for GetRobotState service requests"""
        self.get_logger().info(f'Received request for robot state: {request.robot_name}')
        
        # Create and populate the response
        response.success = True
        response.message = 'Successfully retrieved robot state'
        
        # Create a RobotState message
        response.state = RobotState()
        response.state.robot_name = request.robot_name
        # Simulate some joint positions based on time
        time_sec = self.get_clock().now().nanoseconds * 1e-9
        response.state.joint_positions = [
            math.sin(time_sec), 
            math.cos(time_sec), 
            math.sin(time_sec * 0.5)
        ]
        response.state.joint_velocities = [
            math.cos(time_sec), 
            -math.sin(time_sec), 
            0.5 * math.cos(time_sec * 0.5)
        ]
        response.state.joint_effort = [0.1, 0.2, 0.15]
        response.state.joint_names = ['joint1', 'joint2', 'joint3']
        response.state.cartesian_pose = [1.0, 0.0, 0.5, 0.0, 0.0, 0.0]  # Placeholder
        response.state.timestamp = self.get_clock().now().to_msg()
        
        self.get_logger().info(f'Returned state for robot: {request.robot_name}')
        return response


def main(args=None):
    rclpy.init(args=args)
    
    service_server_node = BasicServiceServerNode()
    
    try:
        rclpy.spin(service_server_node)
    except KeyboardInterrupt:
        service_server_node.get_logger().info('Interrupted by user')
    finally:
        service_server_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()