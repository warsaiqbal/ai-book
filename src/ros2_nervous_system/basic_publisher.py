import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Time
import math
import random

from ros2_nervous_system.msg import RobotCommand, RobotState, SensorData
from ros2_nervous_system.qos_profiles import CRITICAL_CONTROL_QOS, SENSOR_DATA_QOS, DEFAULT_QOS


class BasicPublisherNode(Node):
    """
    Basic ROS publisher node that publishes various types of messages
    to demonstrate communication in the nervous system.
    """

    def __init__(self):
        super().__init__('basic_publisher')

        # Create publishers with appropriate QoS profiles
        self.robot_command_publisher = self.create_publisher(RobotCommand, '/robot_command', CRITICAL_CONTROL_QOS)
        self.robot_state_publisher = self.create_publisher(RobotState, '/robot_state', CRITICAL_CONTROL_QOS)
        self.sensor_data_publisher = self.create_publisher(SensorData, '/sensor_data', SENSOR_DATA_QOS)
        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', DEFAULT_QOS)

        # Timer to periodically publish messages
        self.timer = self.create_timer(0.5, self.publish_messages)  # 2Hz

        self.get_logger().info('Basic Publisher Node initialized')

        # Counter for message sequencing
        self.message_count = 0

    def publish_messages(self):
        """Publish various types of messages"""
        # Publish a robot command
        cmd_msg = RobotCommand()
        cmd_msg.command_type = 'move_to'
        cmd_msg.target_positions = [math.sin(self.get_clock().now().nanoseconds * 1e-9),
                                    math.cos(self.get_clock().now().nanoseconds * 1e-9)]
        cmd_msg.timeout = 5.0
        cmd_msg.joints = ['joint1', 'joint2']

        self.robot_command_publisher.publish(cmd_msg)

        # Publish robot state
        state_msg = RobotState()
        state_msg.robot_name = 'test_robot'
        state_msg.joint_positions = [math.sin(self.get_clock().now().nanoseconds * 1e-9),
                                     math.cos(self.get_clock().now().nanoseconds * 1e-9)]
        state_msg.joint_velocities = [math.cos(self.get_clock().now().nanoseconds * 1e-9),
                                      -math.sin(self.get_clock().now().nanoseconds * 1e-9)]
        state_msg.joint_effort = [0.1, 0.2]
        state_msg.joint_names = ['joint1', 'joint2']
        state_msg.cartesian_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Placeholder
        state_msg.timestamp = self.get_clock().now().to_msg()

        self.robot_state_publisher.publish(state_msg)

        # Publish sensor data
        sensor_msg = SensorData()
        sensor_msg.sensor_type = 'imu'
        sensor_msg.sensor_name = 'imu_link'
        sensor_msg.data = [random.uniform(-1.0, 1.0) for _ in range(3)]  # Simulated IMU data
        sensor_msg.frame_rate = 100.0
        sensor_msg.frame_id = 'imu_link'
        sensor_msg.timestamp = self.get_clock().now().to_msg()

        self.sensor_data_publisher.publish(sensor_msg)

        # Publish joint states
        joint_msg = JointState()
        joint_msg.name = ['joint1', 'joint2']
        joint_msg.position = [math.sin(self.get_clock().now().nanoseconds * 1e-9),
                              math.cos(self.get_clock().now().nanoseconds * 1e-9)]
        joint_msg.velocity = [math.cos(self.get_clock().now().nanoseconds * 1e-9),
                              -math.sin(self.get_clock().now().nanoseconds * 1e-9)]
        joint_msg.effort = [0.1, 0.2]
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.header.frame_id = 'base_link'

        self.joint_state_publisher.publish(joint_msg)

        self.message_count += 1
        self.get_logger().info(f'Published message #{self.message_count}')


def main(args=None):
    rclpy.init(args=args)
    
    publisher_node = BasicPublisherNode()
    
    try:
        rclpy.spin(publisher_node)
    except KeyboardInterrupt:
        publisher_node.get_logger().info('Interrupted by user')
    finally:
        publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()