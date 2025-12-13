# Quickstart Guide: Digital Twin Simulation (Gazebo & Unity)

## Overview
This guide provides a quick setup process to get the Digital Twin simulation system running with Gazebo for physics simulation and Unity for high-fidelity rendering.

## Prerequisites

### System Requirements
- Ubuntu 22.04 LTS (recommended) or Windows 10/11
- 8GB+ RAM (16GB+ recommended for complex simulations)
- Multi-core processor (4+ cores recommended)
- GPU with DirectX 11 or OpenGL 4.5+ support
- 10GB+ free disk space

### Software Dependencies
1. **Gazebo Garden** (or compatible version)
2. **Unity Hub + Unity 2022.3 LTS** (Linux version if available)
3. **ROS2 Humble Hawksbill** (on Ubuntu) or ROS2 Iron Irwini (on Windows)
4. **Python 3.11+** with pip
5. **Git** version control system

## Setup Process

### Step 1: Environment Preparation

1. Install Ubuntu 22.04 LTS (if not already installed)
2. Update system packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Step 2: Install ROS2

1. Add ROS2 repository:
   ```bash
   sudo apt update && sudo apt install curl gnupg lsb-release
   curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/rosSigning.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
   ```

2. Install ROS2 Humble:
   ```bash
   sudo apt update
   sudo apt install ros-humble-ros-base
   sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
   ```

3. Initialize rosdep:
   ```bash
   sudo rosdep init
   rosdep update
   ```

4. Source ROS2 environment:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```

### Step 3: Install Gazebo

1. Add Gazebo repository:
   ```bash
   sudo apt install wget lsb-release gnupg
   sudo wget -O - https://packages.osrfoundation.org/gazebo.gpg | sudo gpg --dearmor -o /usr/share/keyrings/gazebo-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo.list > /dev/null
   ```

2. Install Gazebo Garden:
   ```bash
   sudo apt update
   sudo apt install gazebo
   ```

### Step 4: Install Unity

1. Download and install Unity Hub from the Unity website
2. Through Unity Hub, install Unity 2022.3 LTS
3. Install the Linux Build Support module if available

### Step 5: Clone and Setup Project

1. Create a workspace directory:
   ```bash
   mkdir -p ~/digital_twin_ws/src
   cd ~/digital_twin_ws
   ```

2. Clone the project:
   ```bash
   git clone [repository-url] src/digital_twin
   ```

3. Install Python dependencies:
   ```bash
   pip3 install -r src/digital_twin/requirements.txt
   ```

### Step 6: Build and Run

1. Source ROS2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Build the project:
   ```bash
   cd ~/digital_twin_ws
   colcon build
   source install/setup.bash
   ```

### Step 7: Launch Basic Simulation

1. Run the digital twin simulation:
   ```bash
   ros2 launch digital_twin simulation.launch.py
   ```

2. Open Unity editor and load the Digital Twin scene to visualize the simulation

## Example Usage: Creating a Simple Environment

1. Launch Gazebo:
   ```bash
   gazebo --verbose
   ```

2. In Gazebo, create a new simulation environment with basic objects

3. Launch the Unity client to visualize the same environment

4. Use ROS2 commands to control a simulated robot:
   ```bash
   ros2 run digital_twin robot_controller --ros-args -p robot_name:=my_robot -p target_position:="1.0,2.0,0.0"
   ```

## Troubleshooting

### Common Issues:

1. **Gazebo won't start**: Ensure NVIDIA drivers are properly installed if using GPU acceleration
2. **Unity/ROS2 communication fails**: Check that both systems are on the same network and ROS2 environment is properly sourced
3. **Performance issues**: Reduce rendering quality in Unity or physics complexity in Gazebo

## Next Steps

After completing this quickstart:
- Review the detailed documentation on creating complex environments
- Learn how to add custom robot models
- Explore sensor simulation capabilities
- Understand how to synchronize states between Gazebo and Unity