import rclpy
from rclpy.node import Node

from ros2_nervous_system.srv import GetRobotState


class BasicServiceClientNode(Node):
    """
    Basic ROS service client node that calls the GetRobotState service
    to demonstrate service communication in the nervous system.
    """
    
    def __init__(self):
        super().__init__('basic_service_client')
        
        # Create a service client for GetRobotState
        self.cli = self.create_client(GetRobotState, 'get_robot_state')
        
        # Wait for the service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        
        self.get_logger().info('Basic Service Client Node initialized')
        
        # Create a timer to periodically call the service
        self.timer = self.create_timer(2.0, self.call_service)  # Every 2 seconds

    def call_service(self):
        """Call the GetRobotState service"""
        request = GetRobotState.Request()
        request.robot_name = 'test_robot'
        
        # Make an asynchronous service call
        self.future = self.cli.call_async(request)
        self.future.add_done_callback(self.service_callback)

    def service_callback(self, future):
        """Callback for service response"""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(
                    f'Service call successful: {response.message}, '
                    f'Robot: {response.state.robot_name}, '
                    f'Joints: {len(response.state.joint_names)}, '
                    f'Positions: [{", ".join(f"{p:.2f}" for p in response.state.joint_positions)}]'
                )
            else:
                self.get_logger().error(f'Service call failed: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Service call failed with exception: {e}')


def main(args=None):
    rclpy.init(args=args)
    
    service_client_node = BasicServiceClientNode()
    
    try:
        rclpy.spin(service_client_node)
    except KeyboardInterrupt:
        service_client_node.get_logger().info('Interrupted by user')
    finally:
        service_client_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()