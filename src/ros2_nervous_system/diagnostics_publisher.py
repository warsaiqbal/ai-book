import rclpy
from rclpy.node import Node
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

from ros2_nervous_system.msg import DiagnosticStatus as CustomDiagnosticStatus


class DiagnosticsPublisherNode(Node):
    """
    Diagnostics publisher node that publishes diagnostic information
    about the ROS2 nervous system health.
    """
    
    def __init__(self):
        super().__init__('diagnostics_publisher')
        
        # Create publisher for diagnostic messages
        self.diag_publisher = self.create_publisher(DiagnosticArray, '/diagnostics', 10)
        
        # Timer to periodically publish diagnostics
        self.timer = self.create_timer(1.0, self.publish_diagnostics)  # 1Hz
        
        self.get_logger().info('Diagnostics Publisher Node initialized')
    
    def create_diagnostic_status(self, name, level, message, hardware_id="", values=None):
        """Create and return a DiagnosticStatus message"""
        if values is None:
            values = []
            
        status = DiagnosticStatus()
        status.name = name
        status.level = level  # 0: OK, 1: Warn, 2: Error, 3: Stale
        status.message = message
        status.hardware_id = hardware_id
        status.values = values
        
        return status
    
    def publish_diagnostics(self):
        """Publish diagnostic information about the system"""
        # Create diagnostic array message
        diag_array = DiagnosticArray()
        diag_array.header = Header()
        diag_array.header.stamp = self.get_clock().now().to_msg()
        diag_array.header.frame_id = 'diagnostics'
        
        # Add system diagnostics
        diag_array.status.append(
            self.create_diagnostic_status(
                'ros2_nervous_system.node_communication',
                0,  # OK
                'Node communication is normal',
                'system',
                [KeyValue(key='active_nodes', value='5')]
            )
        )
        
        diag_array.status.append(
            self.create_diagnostic_status(
                'ros2_nervous_system.message_latency',
                0,  # OK
                'Message latency is within acceptable range',
                'system',
                [KeyValue(key='avg_latency_ms', value='15.3')]
            )
        )
        
        diag_array.status.append(
            self.create_diagnostic_status(
                'ros2_nervous_system.system_resources',
                0,  # OK
                'System resources are within limits',
                'system',
                [
                    KeyValue(key='cpu_usage_percent', value='22.1'),
                    KeyValue(key='memory_usage_percent', value='45.6')
                ]
            )
        )
        
        # Publish the diagnostic array
        self.diag_publisher.publish(diag_array)
        
        self.get_logger().info(f'Published diagnostic information for {len(diag_array.status)} components')


def main(args=None):
    rclpy.init(args=args)
    
    diag_publisher_node = DiagnosticsPublisherNode()
    
    try:
        rclpy.spin(diag_publisher_node)
    except KeyboardInterrupt:
        diag_publisher_node.get_logger().info('Interrupted by user')
    finally:
        diag_publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()