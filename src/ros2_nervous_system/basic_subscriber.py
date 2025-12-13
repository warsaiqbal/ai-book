import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState

from ros2_nervous_system.msg import RobotCommand, RobotState, SensorData
from ros2_nervous_system.qos_profiles import CRITICAL_CONTROL_QOS, SENSOR_DATA_QOS, DEFAULT_QOS


class BasicSubscriberNode(Node):
    """
    Basic ROS subscriber node that subscribes to various types of messages
    to demonstrate communication in the nervous system.
    """

    def __init__(self):
        super().__init__('basic_subscriber')

        # Create subscribers with appropriate QoS profiles
        self.robot_command_subscriber = self.create_subscription(
            RobotCommand,
            '/robot_command',
            self.robot_command_callback,
            CRITICAL_CONTROL_QOS
        )

        self.robot_state_subscriber = self.create_subscription(
            RobotState,
            '/robot_state',
            self.robot_state_callback,
            CRITICAL_CONTROL_QOS
        )

        self.sensor_data_subscriber = self.create_subscription(
            SensorData,
            '/sensor_data',
            self.sensor_data_callback,
            SENSOR_DATA_QOS
        )

        self.joint_state_subscriber = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            DEFAULT_QOS
        )

        self.get_logger().info('Basic Subscriber Node initialized')

    def robot_state_callback(self, msg):
        """Callback for robot state messages"""
        self.get_logger().info(
            f'Received RobotState: robot={msg.robot_name}, '
            f'joints={len(msg.joint_names)}, '
            f'pos=[{", ".join(f"{p:.2f}" for p in msg.joint_positions[:3])}...]'
        )

        # Process robot state if needed
        # For example, use the state for control decisions

    def robot_command_callback(self, msg):
        """Callback for robot command messages"""
        self.get_logger().info(
            f'Received RobotCommand: type={msg.command_type}, '
            f'pos=[{", ".join(f"{p:.2f}" for p in msg.target_positions)}], '
            f'timeout={msg.timeout}'
        )
        
        # In a real system, we would process the command here
        # For now, just log the received command

    def sensor_data_callback(self, msg):
        """Callback for sensor data messages"""
        self.get_logger().info(
            f'Received SensorData: type={msg.sensor_type}, '
            f'name={msg.sensor_name}, '
            f'data=[{", ".join(f"{d:.2f}" for d in msg.data)}]'
        )
        
        # Process sensor data if needed
        # For example, use IMU data for state estimation

    def joint_state_callback(self, msg):
        """Callback for joint state messages"""
        if len(msg.position) > 0:
            self.get_logger().info(
                f'Received JointState: joints={len(msg.name)}, '
                f'pos=[{", ".join(f"{p:.2f}" for p in msg.position[:3])}...]'
            )
        else:
            self.get_logger().info('Received JointState: no position data')


def main(args=None):
    rclpy.init(args=args)
    
    subscriber_node = BasicSubscriberNode()
    
    try:
        rclpy.spin(subscriber_node)
    except KeyboardInterrupt:
        subscriber_node.get_logger().info('Interrupted by user')
    finally:
        subscriber_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()