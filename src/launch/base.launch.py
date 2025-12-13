"""
Base ROS2 launch file template for the AI-Robot Brain project.

This module provides a base launch file that can be extended for
specific robot configurations and simulation scenarios.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate the launch description for the base robot system."""
    
    # Declare launch arguments
    namespace_launch_arg = DeclareLaunchArgument(
        'namespace',
        default_value='robot',
        description='Namespace for the robot nodes'
    )
    
    use_sim_time_launch_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    # Get launch configurations
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Path to robot description (URDF/SDF)
    robot_description_path = PathJoinSubstitution([
        FindPackageShare('your_robot_description'),
        'urdf',
        'bipedal_robot.urdf'
    ])
    
    # Set parameters globally
    set_use_sim_time = SetParameter(
        name='use_sim_time',
        value=use_sim_time
    )
    
    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=namespace,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': robot_description_path}
        ],
        output='screen'
    )
    
    # Joint State Publisher node (for simulation)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Perception pipeline node
    perception_node = Node(
        package='perception',
        executable='perception_node',
        name='perception_node',
        namespace=namespace,
        parameters=[
            {'use_sim_time': use_sim_time},
            # Additional parameters would be loaded from config file
        ],
        output='screen'
    )
    
    # Navigation node
    navigation_node = Node(
        package='navigation',
        executable='navigation_node',
        name='navigation_node',
        namespace=namespace,
        parameters=[
            {'use_sim_time': use_sim_time},
            # Additional parameters would be loaded from config file
        ],
        output='screen'
    )
    
    # Isaac Sim bridge node
    isaac_sim_bridge = Node(
        package='simulation',
        executable='isaac_sim_bridge',
        name='isaac_sim_bridge',
        namespace=namespace,
        parameters=[
            {'use_sim_time': use_sim_time},
            # Additional parameters would be loaded from config file
        ],
        output='screen'
    )
    
    # Create launch description
    ld = LaunchDescription()
    
    # Add launch arguments
    ld.add_action(namespace_launch_arg)
    ld.add_action(use_sim_time_launch_arg)
    
    # Add global parameters
    ld.add_action(set_use_sim_time)
    
    # Add nodes
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(perception_node)
    ld.add_action(navigation_node)
    ld.add_action(isaac_sim_bridge)
    
    return ld


# Additional launch utilities
def create_perception_launch():
    """Create launch description specifically for perception components."""
    # This would contain just the perception-related nodes
    pass


def create_navigation_launch():
    """Create launch description specifically for navigation components."""
    # This would contain just the navigation-related nodes
    pass


def create_simulation_launch():
    """Create launch description specifically for simulation components."""
    # This would contain just the simulation-related nodes
    pass