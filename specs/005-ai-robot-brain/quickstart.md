# Quickstart Guide: AI-Robot Brain (NVIDIA Isaac™)

## Prerequisites

### Hardware Requirements
- NVIDIA GPU with compute capability 6.0 or higher (RTX 3080 recommended)
- 32GB+ RAM (64GB recommended)
- 1TB+ free storage for simulation assets and datasets
- Multi-core CPU (8+ cores recommended)

### Software Requirements
- Ubuntu 22.04 LTS
- NVIDIA GPU drivers (535 or later)
- CUDA 12.0+
- ROS2 Humble Hawksbill
- NVIDIA Isaac Sim 2023.1.0+
- Isaac ROS 3.1.0+
- Navigation2 (Nav2)
- Python 3.10+
- Docker (optional, for containerized deployment)

## Installation

### 1. Install NVIDIA Isaac Sim
```bash
# Download Isaac Sim from NVIDIA Developer website
# Extract and install in /opt/isaac-sim
# Verify installation
cd /opt/isaac-sim
./isaac-sim.launch.sh
```

### 2. Set up ROS2 Environment
```bash
# Install ROS2 Humble Hawksbill
sudo apt update
sudo apt install ros-humble-desktop ros-humble-ros-base

# Install Isaac ROS packages
sudo apt install ros-humble-isaac-ros-dev
sudo apt install ros-humble-isaac-ros-common
sudo apt install ros-humble-isaac-ros-perception
sudo apt install ros-humble-isaac-ros-navigation
```

### 3. Install Navigation2
```bash
# Clone and build Nav2 from source
source /opt/ros/humble/setup.bash
mkdir -p ~/robot_ws/src
cd ~/robot_ws

# Clone navigation2 repository
git clone -b humble https://github.com/ros-planning/navigation2.git
cd navigation2
git checkout 3.0.0

# Build the workspace
colcon build --symlink-install --packages-select navigation2 nav2_bringup
source install/setup.bash
```

## Quick Setup: Basic Simulation Environment

### 1. Create a Simulation Environment
```bash
# Navigate to your project workspace
cd ~/robot_ws

# Create a new environment configuration
mkdir -p src/simulation/environments/basic_world
cp -r /opt/isaac-sim/apps/omniverse.kit.examples.example-standalone/assets src/simulation/environments/basic_world/
```

### 2. Define a Robot Model
```bash
# Create a robot model directory
mkdir -p src/robot_models/bipedal_robot

# Create a basic URDF for the robot (simplified)
cat << EOF > src/robot_models/bipedal_robot/bipedal.urdf
<?xml version="1.0"?>
<robot name="bipedal_robot">
  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.6"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>

  <!-- Add sensors -->
  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.2" rpy="0 0 0"/>
  </joint>
  
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </visual>
  </link>
</robot>
EOF
```

### 3. Launch the Simulation
```bash
# Source ROS2 and Isaac packages
source /opt/ros/humble/setup.bash
source install/setup.bash
export ISAACSIM_PATH=/opt/isaac-sim

# Launch Isaac Sim with your environment
cd $ISAACSIM_PATH
./isaac-sim.launch.sh --ext-folder apps/omniverse.kit.examples.example-standalone --config my_simulation_config
```

## Quick Setup: Perception Pipeline

### 1. Configure a Basic Perception Node
```bash
# Create perception configuration
mkdir -p src/perception/config

cat << EOF > src/perception/config/basic_perception.yaml
perception_pipeline:
  nodes:
    - name: object_detection
      type: IsaacROSDetection
      parameters:
        model_path: "/path/to/trained/model"
        confidence_threshold: 0.7
        input_topic: "/camera/rgb/image_raw"
        output_topic: "/detections"
    - name: depth_segmentation
      type: IsaacROSDepthSegmentation
      parameters:
        input_topic: "/camera/depth/image_raw"
        output_topic: "/segmentation"
EOF
```

### 2. Run the Perception Pipeline
```bash
# Launch perception nodes
source install/setup.bash
ros2 launch perception basic_perception.launch.py
```

## Quick Setup: Navigation with Nav2

### 1. Prepare Navigation Configuration
```bash
# Create Nav2 configuration
mkdir -p src/navigation/config

cat << EOF > src/navigation/config/nav2_params.yaml
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    bt_xml_filename: "navigate_w_replanning_and_recovery.xml"
    default_server_timeout: 20
    enable_groot_monitoring: True
    interruptable_controllers: True
    controller_frequency: 20.0
    controller_server_name: controller_server
    recovery_server_name: recovery_server
    bt_loop_duration: 10
    max_loop_duration: 10
    enable_loop_backoff: True

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # DWB Controller configuration
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.5
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 0
      vtheta_samples: 40
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.15
      stateful: True
      shorten_transformed_plan: True
      utilize_cost_regulated_transitions: False
      use_dwa: False
      velocity_scaling_enabled: False
      scaling_speed: 0.25
      max_scaling_factor: 0.2
EOF
```

### 2. Launch Navigation
```bash
# Launch Nav2 stack in simulation
source install/setup.bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True
```

## Running the Complete System

### 1. Start Isaac Sim
```bash
cd /opt/isaac-sim
./isaac-sim.launch.sh
```

### 2. In a new terminal, start ROS2 nodes
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch robot control and perception
ros2 launch your_robot_bringup robot.launch.py
```

### 3. In another terminal, start navigation
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch navigation
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True
```

### 4. Send navigation commands
```bash
# In another terminal, send a goal to Nav2
source /opt/ros/humble/setup.bash

# Use RViz2 to set navigation goals, or send directly:
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{goal_pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

## Verification Steps

### 1. Check Simulation
- Verify Isaac Sim is running at 60+ FPS
- Confirm robot model appears in the environment
- Validate sensors are publishing data (check with `ros2 topic echo`)

### 2. Check Perception
- Verify perception nodes are running: `ros2 node list`
- Check that perception topics are publishing: `ros2 topic echo /detections`
- Use RViz2 to visualize perception results

### 3. Check Navigation
- Ensure Nav2 nodes are running: `ros2 node list`
- Verify TF tree is correct: `ros2 run tf2_tools view_frames`
- Test basic navigation commands and observe robot movement in simulation

## Troubleshooting

### Common Issues
- **Isaac Sim fails to start**: Verify NVIDIA drivers and CUDA installation
- **Sensor topics not publishing**: Check robot model URDF and sensor configuration
- **Navigation errors**: Verify TF tree and map availability
- **Performance issues**: Reduce simulation complexity or upgrade hardware

### Useful Commands
```bash
# Check ROS2 nodes
ros2 node list

# Check ROS2 topics
ros2 topic list

# Monitor simulation performance
ros2 topic echo /isaac_sim_performance_metrics

# Check TF tree
ros2 run tf2_tools view_frames
```

## Next Steps

1. Customize your robot model with detailed URDF
2. Train perception models on synthetic data generated by Isaac Sim
3. Implement bipedal-specific locomotion controllers
4. Extend navigation for bipedal movement patterns
5. Add more complex environments and scenarios