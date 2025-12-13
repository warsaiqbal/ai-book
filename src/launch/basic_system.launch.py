from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for the basic nervous system"""
    
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    # Define the basic publisher node
    basic_publisher_node = Node(
        package='ros2_nervous_system',
        executable='basic_publisher',
        name='basic_publisher',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )
    
    # Define the basic subscriber node
    basic_subscriber_node = Node(
        package='ros2_nervous_system',
        executable='basic_subscriber',
        name='basic_subscriber',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )
    
    # Define the simple decision maker node
    simple_decision_maker_node = Node(
        package='ros2_nervous_system',
        executable='simple_decision_maker',
        name='simple_decision_maker',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        basic_publisher_node,
        basic_subscriber_node,
        simple_decision_maker_node
    ])