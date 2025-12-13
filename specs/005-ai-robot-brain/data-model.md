# Data Model: AI-Robot Brain (NVIDIA Isaac™)

## Overview
This document defines the data models for the AI-Robot Brain system using NVIDIA Isaac technology. It covers entities related to simulation environments, robot models, perception systems, navigation, and sensor data.

## Core Entities

### 1. SimulatedEnvironment
Represents a 3D environment in Isaac Sim with physics properties and assets

**Fields:**
- id (string): Unique identifier for the environment
- name (string): Display name of the environment
- description (string): Brief description of the environment
- dimensions (Vector3): Width, height, depth of the environment in meters
- gravity (Vector3): Gravity vector in m/s² (typically [0, 0, -9.81])
- lightingConditions (LightingConfig): Configuration for lighting, shadows, etc.
- assets (Array<EnvironmentAsset>): List of static and dynamic objects in the environment
- physicsProperties (PhysicsConfig): Configuration for physics engine parameters

**Relationships:**
- Contains many RobotModel instances
- Contains many Sensor instances

### 2. RobotModel
Digital twin of the physical robot with kinematic properties and sensors

**Fields:**
- id (string): Unique identifier for the robot model
- name (string): Name of the robot model (e.g., "Atlas-like Bipedal Robot")
- urdfPath (string): Path to URDF file describing robot kinematics
- sdfPath (string): Path to SDF file for simulation
- baseLink (string): Name of the robot's base link/frame
- jointCount (integer): Number of joints in the robot
- linkCount (integer): Number of links in the robot
- dimensions (Vector3): Physical dimensions of the robot in meters
- mass (float): Total mass of the robot in kg
- maxJointVelocity (float): Maximum joint velocity in rad/s
- sensorMounts (Array<SensorMount>): Locations where sensors are mounted
- locomotionCapabilities (LocomotionConfig): Configuration for bipedal movement

**Relationships:**
- Belongs to one SimulatedEnvironment
- Has many Sensor instances
- Has one PerceptionPipeline

### 3. Sensor
Virtual sensor mounted on the robot to collect data from the environment

**Fields:**
- id (string): Unique identifier for the sensor
- name (string): Name of the sensor (e.g., "Front RGB Camera")
- type (SensorType): Enum (RGB_CAMERA, DEPTH_CAMERA, LIDAR, IMU, FORCE_TORQUE, etc.)
- frameId (string): TF frame ID where the sensor is mounted
- position (Vector3): Position relative to parent link in meters
- orientation (Quaternion): Orientation relative to parent link
- connected (boolean): Whether sensor is currently active
- parameters (JSON): Type-specific parameters (resolution, range, etc.)
- sensorDataPath (string): Path where sensor data is logged

**Relationships:**
- Belongs to one RobotModel
- Generates many SensorData instances

### 4. PerceptionPipeline
Collection of AI models that process sensor data to understand the environment

**Fields:**
- id (string): Unique identifier for the pipeline
- name (string): Name of the pipeline configuration
- description (string): Description of what the pipeline does
- models (Array<PerceptionModel>): List of models in the pipeline
- inputSensors (Array<SensorType>): Types of sensors required
- detectionThreshold (float): Confidence threshold for detections (0.0-1.0)
- boundingBoxFormat (BoundingBoxFormat): Format of bounding box outputs
- processingRate (float): Max rate at which the pipeline processes data (Hz)

**Relationships:**
- Belongs to one RobotModel
- Processes many SensorData instances
- Produces many PerceptionResult instances

### 5. PerceptionModel
Individual AI model within a perception pipeline

**Fields:**
- id (string): Unique identifier for the model
- name (string): Name of the model (e.g., "Object Detection Model")
- modelType (ModelType): Enum (OBJECT_DETECTION, SEGMENTATION, CLASSIFICATION, VSLAM, etc.)
- framework (ModelFramework): Enum (PYTORCH, TENSORFLOW, TENSORRT, etc.)
- weightsPath (string): Path to model weights file
- inputChannels (integer): Number of input channels
- inputResolution (Vector2): Required input resolution [width, height]
- outputFormat (JSON): Expected output format of the model
- accuracy (float): Model accuracy metric
- latency (float): Processing latency in milliseconds

**Relationships:**
- Belongs to one PerceptionPipeline

### 6. NavigationPlan
Path planning and execution module for directing robot movement

**Fields:**
- id (string): Unique identifier for the navigation plan
- name (string): Name of the navigation configuration
- startPose (Pose): Starting position and orientation
- goalPose (Pose): Target position and orientation
- globalPath (Array<Pose>): Waypoints of the global path
- localPath (Array<Pose>): Waypoints of the local path (with obstacles considered)
- pathStatus (PathStatus): Current status (PLANNING, EXECUTING, COMPLETED, FAILED)
- plannerType (PlannerType): Enum (A_STAR, Dijkstra, RRT_STAR, etc.)
- parameters (JSON): Planner-specific parameters

**Relationships:**
- Belongs to one RobotModel
- References one SimulatedEnvironment

### 7. LocomotionController
Control system for bipedal humanoid movement

**Fields:**
- id (string): Unique identifier for the controller
- name (string): Name of the controller (e.g., "MPC Bipedal Controller")
- controllerType (ControllerType): Enum (MPC, CPG, ZMP, PID, etc.)
- gaitType (GaitType): Enum (WALK, STAND, RUN, STAIR_CLIMB, etc.)
- stepHeight (float): Maximum step height in meters
- stepLength (float): Maximum step length in meters
- walkingSpeed (float): Preferred walking speed in m/s
- balanceThreshold (float): Balance stability threshold
- controlRate (float): Rate at which controller updates (Hz)

**Relationships:**
- Belongs to one RobotModel
- Uses one NavigationPlan for movement goals

### 8. SensorData
Real-time data captured by sensors from the environment

**Fields:**
- id (string): Unique identifier for the data instance
- sensorId (string): Reference to the sensor that generated the data
- timestamp (DateTime): Time when the data was captured
- dataType (DataType): Enum (IMAGE, POINT_CLOUD, IMU, JOINT_STATE, etc.)
- dataPath (string): Path where the raw data is stored
- format (string): Format of the data (PNG, JPEG, PCD, etc.)
- frameId (string): TF frame ID where the data was captured
- width (integer): Width of image data (if applicable)
- height (integer): Height of image data (if applicable)
- metadata (JSON): Additional metadata about the data capture

**Relationships:**
- Generated by one Sensor instance
- Processed by one PerceptionPipeline
- Associated with one SimulatedEnvironment state

### 9. PerceptionResult
Output from the perception pipeline containing understanding of the environment

**Fields:**
- id (string): Unique identifier for the result
- pipelineId (string): Reference to the pipeline that generated the result
- sensorDataId (string): Reference to the input sensor data
- timestamp (DateTime): Time when the result was generated
- detectionType (DetectionType): Enum (OBJECT, PERSON, OBSTACLE, LANDMARK, etc.)
- confidence (float): Confidence score of the detection (0.0-1.0)
- boundingBox (BoundingBox): 2D or 3D bounding box of detection
- classification (string): Classification label for the detected object
- position (Vector3): 3D position of the detection in world coordinates
- attributes (JSON): Additional attributes specific to the detection
- validationStatus (ValidationStatus): VALID, INVALID, PENDING

**Relationships:**
- Generated by one PerceptionPipeline
- Based on one SensorData instance

## State Transitions

### RobotModelState
- IDLE → INITIALIZING (when robot model is loaded)
- INITIALIZING → READY (when all sensors are initialized)
- READY → OPERATING (when robot is executing tasks)
- OPERATING → EMERGENCY_STOP (when safety limits are exceeded)
- EMERGENCY_STOP → READY (after manual reset)
- READY → IDLE (when robot is shutdown)

### NavigationState
- IDLE → PLANNING (when a new goal is received)
- PLANNING → NAVIGATING (when path is found and execution starts)
- NAVIGATING → AVOIDING_OBSTACLE (when obstacle is detected in path)
- AVOIDING_OBSTACLE → NAVIGATING (when obstacle is cleared)
- NAVIGATING → COMPLETED (when goal is reached)
- NAVIGATING → FAILED (when navigation fails)
- COMPLETED → IDLE (when goal is achieved)

## Validation Rules

### From Requirements
- FR-004: Sensor data (camera, LIDAR, IMU) must match real-world characteristics
  - Validation: SensorData entities must have parameters within specified ranges of real sensors
- FR-005: Interfaces must support training and evaluation of perception algorithms
  - Validation: PerceptionPipeline entities must have proper data interfaces with SensorData and PerceptionResult
- FR-006: Physics-based simulation must include gravity, friction, and collision detection
  - Validation: SimulatedEnvironment entities must have physics properties defined
- FR-009: Transfer learning must have minimal domain gap
  - Validation: PerceptionModel entities must support domain randomization parameters

## Indexes and Performance Considerations

### Critical Indexes
- SimulatedEnvironment.id (primary key)
- RobotModel.id (primary key)
- Sensor.id (primary key) and Sensor.robotId (foreign key)
- SensorData.timestamp (for temporal queries)
- SensorData.sensorId (for sensor-specific queries)
- PerceptionResult.pipelineId (for pipeline-specific queries)
- PerceptionResult.timestamp (for temporal queries)

### Performance Optimizations
- Use efficient data formats (e.g., HDF5) for sensor data storage
- Implement data streaming for real-time processing
- Cache frequently accessed simulation states
- Use spatial indexing for environment assets and robot positions