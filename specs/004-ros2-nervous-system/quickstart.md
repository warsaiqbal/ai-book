# Quickstart Guide: ROS2 Nervous System

## Overview
This guide provides a quick setup process to get the ROS 2-based nervous system running for robot control, including node communication, Python agent integration, and URDF model loading.

## Prerequisites

### System Requirements
- Ubuntu 22.04 LTS (recommended)
- 8GB+ RAM (16GB+ recommended for complex humanoid robots)
- Multi-core processor (4+ cores recommended)
- 10GB+ free disk space

### Software Dependencies
1. **ROS 2 Humble Hawksbill** (with Python and C++ development tools)
2. **Python 3.11+** with pip
3. **Git** version control system
4. **Colcon** build system
5. **RViz2** for visualization (optional)
6. **Gazebo** for simulation (optional)

## Setup Process

### Step 1: Install ROS 2 Humble Hawksbill

1. Set locale to UTF-8:
   ```bash
   locale  # Check for UTF-8
   sudo apt update && sudo apt install locales
   sudo locale-gen en_US.UTF-8
   ```

2. Add ROS 2 apt repository:
   ```bash
   sudo apt update && sudo apt install curl gnupg lsb-release
   curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/rosKeyserver.pub.gpg | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
   ```

3. Install ROS 2 development packages:
   ```bash
   sudo apt update
   sudo apt install ros-humble-desktop
   sudo apt install python3-colcon-common-extensions
   sudo apt install python3-rosdep
   ```

4. Source ROS 2 environment:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```

### Step 2: Install Python Dependencies

1. Install additional Python packages:
   ```bash
   pip3 install rclpy transforms3d numpy
   ```

### Step 3: Clone and Setup Project

1. Create a workspace directory:
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws
   ```

2. Clone the project:
   ```bash
   git clone [repository-url] src/ros2_nervous_system
   ```

### Step 4: Build the Project

1. Source ROS 2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Build the project:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select ros2_nervous_system
   source install/setup.bash
   ```

## Basic Usage Examples

### Example 1: Create and Run a Simple Publisher Node

1. Create a simple publisher node:
   ```bash
   cd ~/ros2_ws/src/ros2_nervous_system
   ros2 run ros2_nervous_system simple_publisher_node
   ```

2. In another terminal, listen to the topic:
   ```bash
   source ~/ros2_ws/install/setup.bash
   ros2 topic echo /robot_command std_msgs/String
   ```

### Example 2: Run Python Agent with ROS Bridge

1. Source the environment:
   ```bash
   source ~/ros2_ws/install/setup.bash
   source /opt/ros/humble/setup.bash
   ```

2. Run the Python agent:
   ```bash
   cd ~/ros2_ws/src/ros2_nervous_system
   python3 python_agents/simple_decision_maker.py
   ```

### Example 3: Load and Visualize URDF Model

1. Source the environment:
   ```bash
   source ~/ros2_ws/install/setup.bash
   ```

2. Launch the robot state publisher with a URDF model:
   ```bash
   ros2 launch ros2_nervous_system load_humanoid.launch.py
   ```

3. Visualize the robot model in RViz2:
   ```bash
   ros2 run rviz2 rviz2
   # Then add a RobotModel display and set the robot description topic
   ```

## Running the Complete System

1. Source the ROS 2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   source ~/ros2_ws/install/setup.bash
   ```

2. Launch the complete nervous system:
   ```bash
   ros2 launch ros2_nervous_system complete_system.launch.py
   ```

3. This will start:
   - Basic robot state publisher
   - Control nodes
   - Python agent interfaces
   - Diagnostic tools

## Testing the System

1. Run the basic tests:
   ```bash
   source ~/ros2_ws/install/setup.bash
   colcon test --packages-select ros2_nervous_system
   colcon test-result --all
   ```

2. Verify node communication:
   ```bash
   ros2 node list
   ros2 topic list
   ros2 service list
   ```

## Troubleshooting

### Common Issues:

1. **Permission errors**: Ensure you've properly sourced the ROS environment
2. **Package not found**: Make sure to run `source ~/ros2_ws/install/setup.bash` in each new terminal
3. **URDF parsing errors**: Check that the URDF files are valid XML and all referenced resources exist
4. **Python agent not connecting**: Verify that rclpy is properly installed and the ROS environment is sourced

## Next Steps

After completing this quickstart:
- Review the detailed documentation on creating custom robot controllers
- Learn how to implement more sophisticated Python agents
- Explore advanced URDF features for complex humanoid robots
- Understand how to optimize performance for real-time control