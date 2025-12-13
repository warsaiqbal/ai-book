"""
Base data models for the Vision-Language-Action (VLA) robotics project.

This module defines foundational data structures that are used across
multiple components of the VLA system. These models are based on the
data-model.md specification but kept simple for cross-module use.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import math


# Basic geometric types
@dataclass
class Vector3:
    """Represents a 3D vector with x, y, z coordinates."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def magnitude(self) -> float:
        """Calculate the magnitude of the vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        """Normalize the vector to unit length."""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag


@dataclass
class Quaternion:
    """Represents a quaternion with x, y, z, w components."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0
    
    def normalize(self):
        """Normalize the quaternion."""
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if magnitude > 0:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
            self.w /= magnitude


@dataclass
class Pose:
    """Represents a 3D pose with position and orientation."""
    position: Vector3
    orientation: Quaternion
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.position is None:
            self.position = Vector3()
        if self.orientation is None:
            self.orientation = Quaternion()


@dataclass
class BoundingBox:
    """Represents a 2D or 3D bounding box."""
    x: float  # X coordinate of top-left corner (2D) or center (3D)
    y: float  # Y coordinate of top-left corner (2D) or center (3D)
    width: float  # Width of the box
    height: float  # Height of the box
    z: Optional[float] = None  # Z coordinate for 3D (optional)
    depth: Optional[float] = None  # Depth for 3D (optional)


# Enumerations based on the data model
class SensorType(Enum):
    """Enumeration of sensor types."""
    RGB_CAMERA = "rgb_camera"
    DEPTH_CAMERA = "depth_camera"
    LIDAR = "lidar"
    IMU = "imu"
    FORCE_TORQUE = "force_torque"
    GPS = "gps"
    ODOMETER = "odometer"


class ModelType(Enum):
    """Enumeration of model types."""
    OBJECT_DETECTION = "object_detection"
    SEGMENTATION = "segmentation"
    CLASSIFICATION = "classification"
    VSLAM = "vslam"
    POSE_ESTIMATION = "pose_estimation"


class ModelFramework(Enum):
    """Enumeration of model frameworks."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    TENSORRT = "tensorrt"
    ONNX = "onnx"


class ControllerType(Enum):
    """Enumeration of controller types."""
    MPC = "mpc"  # Model Predictive Control
    CPG = "cpg"  # Central Pattern Generator
    ZMP = "zmp"  # Zero Moment Point
    PID = "pid"  # Proportional-Integral-Derivative
    LQR = "lqr"  # Linear Quadratic Regulator


class GaitType(Enum):
    """Enumeration of gait types."""
    WALK = "walk"
    STAND = "stand"
    RUN = "run"
    STAIR_CLIMB = "stair_climb"
    TERRAIN_ADAPTIVE = "terrain_adaptive"


class PlannerType(Enum):
    """Enumeration of planner types."""
    A_STAR = "a_star"
    DIJKSTRA = "dijkstra"
    RRT_STAR = "rrt_star"
    TEB = "teb"  # Timed Elastic Band
    DWA = "dwa"  # Dynamic Window Approach


class PathStatus(Enum):
    """Enumeration of path planning statuses."""
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataType(Enum):
    """Enumeration of data types."""
    IMAGE = "image"
    POINT_CLOUD = "point_cloud"
    IMU = "imu"
    JOINT_STATE = "joint_state"
    LASER_SCAN = "laser_scan"
    ODOMETRY = "odometry"


class DetectionType(Enum):
    """Enumeration of detection types."""
    OBJECT = "object"
    PERSON = "person"
    OBSTACLE = "obstacle"
    LANDMARK = "landmark"
    SIGN = "sign"


class ValidationStatus(Enum):
    """Enumeration of validation statuses."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"


# Base data models based on the data-model.md specification
@dataclass
class BaseEntity:
    """Base class for all entities in the system."""
    id: str
    name: str
    description: Optional[str] = None


@dataclass
class SimulatedEnvironment(BaseEntity):
    """
    Represents a 3D environment in Isaac Sim with physics properties and assets.
    
    Fields:
    - id (string): Unique identifier for the environment
    - name (string): Display name of the environment
    - description (string): Brief description of the environment
    - dimensions (Vector3): Width, height, depth of the environment in meters
    - gravity (Vector3): Gravity vector in m/s² (typically [0, 0, -9.81])
    - lightingConditions (LightingConfig): Configuration for lighting, shadows, etc.
    - assets (Array<EnvironmentAsset>): List of static and dynamic objects in the environment
    - physicsProperties (PhysicsConfig): Configuration for physics engine parameters
    """
    dimensions: Vector3 = None
    gravity: Vector3 = None
    assets: List[Dict[str, Any]] = None
    physics_properties: Dict[str, Any] = None
    lighting_conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.dimensions is None:
            self.dimensions = Vector3()
        if self.gravity is None:
            # Default to Earth gravity
            self.gravity = Vector3(0.0, 0.0, -9.81)
        if self.assets is None:
            self.assets = []
        if self.physics_properties is None:
            self.physics_properties = {}
        if self.lighting_conditions is None:
            self.lighting_conditions = {}


@dataclass
class RobotModel(BaseEntity):
    """
    Digital twin of the physical robot with kinematic properties and sensors.
    
    Fields:
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
    """
    urdf_path: str = ""
    sdf_path: str = ""
    base_link: str = "base_link"
    joint_count: int = 0
    link_count: int = 0
    dimensions: Vector3 = None
    mass: float = 0.0
    max_joint_velocity: float = 0.0
    sensor_mounts: List[Dict[str, Any]] = None
    locomotion_capabilities: Dict[str, Any] = None
    perception_pipeline_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.dimensions is None:
            self.dimensions = Vector3()
        if self.sensor_mounts is None:
            self.sensor_mounts = []
        if self.locomotion_capabilities is None:
            self.locomotion_capabilities = {}


@dataclass
class Sensor(BaseEntity):
    """
    Virtual sensor mounted on the robot to collect data from the environment.
    
    Fields:
    - id (string): Unique identifier for the sensor
    - name (string): Name of the sensor (e.g., "Front RGB Camera")
    - type (SensorType): Enum (RGB_CAMERA, DEPTH_CAMERA, LIDAR, IMU, FORCE_TORQUE, etc.)
    - frameId (string): TF frame ID where the sensor is mounted
    - position (Vector3): Position relative to parent link in meters
    - orientation (Quaternion): Orientation relative to parent link
    - connected (boolean): Whether sensor is currently active
    - parameters (JSON): Type-specific parameters (resolution, range, etc.)
    - sensorDataPath (string): Path where sensor data is logged
    """
    sensor_type: SensorType = SensorType.RGB_CAMERA
    frame_id: str = "sensor_link"
    position: Vector3 = None
    orientation: Quaternion = None
    connected: bool = True
    parameters: Dict[str, Any] = None
    sensor_data_path: str = ""
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.position is None:
            self.position = Vector3()
        if self.orientation is None:
            self.orientation = Quaternion()
        if self.parameters is None:
            self.parameters = {}


@dataclass
class PerceptionPipeline(BaseEntity):
    """
    Collection of AI models that process sensor data to understand the environment.
    
    Fields:
    - id (string): Unique identifier for the pipeline
    - name (string): Name of the pipeline configuration
    - description (string): Description of what the pipeline does
    - models (Array<PerceptionModel>): List of models in the pipeline
    - inputSensors (Array<SensorType>): Types of sensors required
    - detectionThreshold (float): Confidence threshold for detections (0.0-1.0)
    - boundingBoxFormat (BoundingBoxFormat): Format of bounding box outputs
    - processingRate (float): Max rate at which the pipeline processes data (Hz)
    """
    models: List[str] = None  # IDs of PerceptionModel instances
    input_sensors: List[SensorType] = None
    detection_threshold: float = 0.7
    bounding_box_format: str = "xywh"  # Format: xywh (x, y, width, height) or xyxy (x1, y1, x2, y2)
    processing_rate: float = 30.0  # Hz
    robot_model_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.models is None:
            self.models = []
        if self.input_sensors is None:
            self.input_sensors = []


@dataclass
class PerceptionModel(BaseEntity):
    """
    Individual AI model within a perception pipeline.
    
    Fields:
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
    """
    model_type: ModelType = ModelType.OBJECT_DETECTION
    framework: ModelFramework = ModelFramework.PYTORCH
    weights_path: str = ""
    input_channels: int = 3
    input_resolution: tuple = (640, 480)  # width, height
    output_format: Dict[str, Any] = None
    accuracy: float = 0.0
    latency: float = 0.0  # in milliseconds
    pipeline_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.output_format is None:
            self.output_format = {}


@dataclass
class NavigationPlan(BaseEntity):
    """
    Path planning and execution module for directing robot movement.
    
    Fields:
    - id (string): Unique identifier for the navigation plan
    - name (string): Name of the navigation configuration
    - startPose (Pose): Starting position and orientation
    - goalPose (Pose): Target position and orientation
    - globalPath (Array<Pose>): Waypoints of the global path
    - localPath (Array<Pose>): Waypoints of the local path (with obstacles considered)
    - pathStatus (PathStatus): Current status (PLANNING, EXECUTING, COMPLETED, FAILED)
    - plannerType (PlannerType): Enum (A_STAR, Dijkstra, RRT_STAR, etc.)
    - parameters (JSON): Planner-specific parameters
    """
    start_pose: Pose = None
    goal_pose: Pose = None
    global_path: List[Pose] = None
    local_path: List[Pose] = None
    path_status: PathStatus = PathStatus.PLANNING
    planner_type: PlannerType = PlannerType.A_STAR
    parameters: Dict[str, Any] = None
    robot_model_id: Optional[str] = None
    simulated_environment_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.start_pose is None:
            self.start_pose = Pose(Vector3(), Quaternion())
        if self.goal_pose is None:
            self.goal_pose = Pose(Vector3(), Quaternion())
        if self.global_path is None:
            self.global_path = []
        if self.local_path is None:
            self.local_path = []
        if self.parameters is None:
            self.parameters = {}


@dataclass
class LocomotionController(BaseEntity):
    """
    Control system for bipedal humanoid movement.
    
    Fields:
    - id (string): Unique identifier for the controller
    - name (string): Name of the controller (e.g., "MPC Bipedal Controller")
    - controllerType (ControllerType): Enum (MPC, CPG, ZMP, PID, etc.)
    - gaitType (GaitType): Enum (WALK, STAND, RUN, STAIR_CLIMB, etc.)
    - stepHeight (float): Maximum step height in meters
    - stepLength (float): Maximum step length in meters
    - walkingSpeed (float): Preferred walking speed in m/s
    - balanceThreshold (float): Balance stability threshold
    - controlRate (float): Rate at which controller updates (Hz)
    """
    controller_type: ControllerType = ControllerType.MPC
    gait_type: GaitType = GaitType.WALK
    step_height: float = 0.1  # meters
    step_length: float = 0.5  # meters
    walking_speed: float = 0.5  # m/s
    balance_threshold: float = 0.05  # meters
    control_rate: float = 100.0  # Hz
    robot_model_id: Optional[str] = None
    navigation_plan_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        pass


@dataclass
class SensorData(BaseEntity):
    """
    Real-time data captured by sensors from the environment.
    
    Fields:
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
    """
    sensor_id: str = ""
    timestamp: float = 0.0  # Unix timestamp
    data_type: DataType = DataType.IMAGE
    data_path: str = ""
    format: str = "unknown"
    frame_id: str = "sensor_link"
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Dict[str, Any] = None
    simulated_environment_state: str = ""
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PerceptionResult(BaseEntity):
    """
    Output from the perception pipeline containing understanding of the environment.
    
    Fields:
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
    """
    pipeline_id: str = ""
    sensor_data_id: str = ""
    timestamp: float = 0.0  # Unix timestamp
    detection_type: DetectionType = DetectionType.OBJECT
    confidence: float = 0.0
    bounding_box: BoundingBox = None
    classification: str = ""
    position: Vector3 = None
    attributes: Dict[str, Any] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.bounding_box is None:
            self.bounding_box = BoundingBox(0.0, 0.0, 0.0, 0.0)
        if self.position is None:
            self.position = Vector3()
        if self.attributes is None:
            self.attributes = {}


# VLA-specific data models
class VoiceCommandStatus(Enum):
    """Enumeration of voice command statuses."""
    RECEIVED = "received"
    TRANSCRIBED = "transcribed"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(Enum):
    """Enumeration of action types."""
    NAVIGATION = "navigation"
    PERCEPTION = "perception"
    MANIPULATION = "manipulation"
    COMMUNICATION = "communication"
    WAIT = "wait"
    LOOP = "loop"


@dataclass
class VoiceCommand(BaseEntity):
    """
    Represents a spoken instruction from a human user to the robot.
    
    Fields:
    - id (string): Unique identifier for the voice command
    - audio_data_path (string): File path to the audio recording
    - transcribed_text (string): Text transcription of the spoken command
    - timestamp (datetime): When the command was issued
    - language (string): Language of the command (e.g., "en", "es", etc.)
    - confidence_score (float): Confidence score of the speech recognition (0.0-1.0)
    - raw_audio_format (string): Format of the raw audio (e.g., "wav", "mp3", "flac")
    - duration (float): Duration of the audio in seconds
    - user_id (string): Identifier for the user who issued the command
    - semantic_intent (string): Parsed semantic intent of the command
    - processed_status (enum): Status of command processing
    - error_message (string): Error message if processing failed
    """
    audio_data_path: str = ""
    transcribed_text: str = ""
    timestamp: float = 0.0  # Unix timestamp
    language: str = "en"
    confidence_score: float = 0.0
    raw_audio_format: str = "wav"
    duration: float = 0.0
    user_id: str = ""
    semantic_intent: str = ""
    processed_status: VoiceCommandStatus = VoiceCommandStatus.RECEIVED
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        pass


@dataclass
class ActionStep:
    """
    Individual action within an action plan.
    
    Fields:
    - id (string): Unique identifier for the action step
    - action_plan_id (string): Reference to the parent action plan
    - step_number (integer): Sequential number in the plan (0-indexed)
    - action_type (enum): Type of action
    - action_parameters (JSON): Parameters specific to the action type
    - description (string): Human-readable description of the action
    - estimated_duration (float): Estimated time to complete this action in seconds
    - success_threshold (float): Threshold for determining success (0.0-1.0)
    - dependencies (array of string): IDs of other ActionSteps this step depends on
    - priority (integer): Priority level (0-10)
    - status (enum): Current status
    - error_code (string): Error code if execution failed
    - robot_task_id (string): Task ID in the robot's execution system (if applicable)
    """
    id: str
    action_plan_id: str
    step_number: int = 0
    action_type: ActionType = ActionType.NAVIGATION
    action_parameters: Dict[str, Any] = None
    description: str = ""
    estimated_duration: float = 0.0
    success_threshold: float = 0.8
    dependencies: List[str] = None
    priority: int = 5
    status: str = "pending"
    error_code: Optional[str] = None
    robot_task_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.action_parameters is None:
            self.action_parameters = {}
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ActionPlan(BaseEntity):
    """
    Sequence of ROS 2 actions generated by the LLM to fulfill a command.
    
    Fields:
    - id (string): Unique identifier for the action plan
    - voice_command_id (string): Reference to the originating voice command
    - llm_response (string): Raw response from the LLM containing planned steps
    - action_sequence (array of ActionStep): Ordered list of actions to execute
    - priority (integer): Priority level of the plan (0-10, higher is more urgent)
    - estimated_duration (float): Estimated time to complete the plan in seconds
    - estimated_energy (float): Estimated energy consumption
    - plan_status (enum): Current status
    - created_at (datetime): Timestamp when plan was created
    - updated_at (datetime): Timestamp when plan was last updated
    - robot_constraints (array of string): Constraints specific to the robot executing the plan
    - environmental_context (JSON): Context about the environment relevant to the plan
    - success_criteria (array of string): Conditions that define success for this plan
    """
    voice_command_id: str = ""
    llm_response: str = ""
    action_sequence: List[ActionStep] = None
    priority: int = 5
    estimated_duration: float = 0.0
    estimated_energy: float = 0.0
    plan_status: str = "planning"
    created_at: float = 0.0  # Unix timestamp
    updated_at: float = 0.0  # Unix timestamp
    robot_constraints: List[str] = None
    environmental_context: Dict[str, Any] = None
    success_criteria: List[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.action_sequence is None:
            self.action_sequence = []
        if self.robot_constraints is None:
            self.robot_constraints = []
        if self.environmental_context is None:
            self.environmental_context = {}
        if self.success_criteria is None:
            self.success_criteria = []


@dataclass
class LLMQuery(BaseEntity):
    """
    Represents a query sent to a Large Language Model for cognitive planning.
    
    Fields:
    - id (string): Unique identifier for the query
    - query_type (enum): Purpose of query
    - input_context (string): Context provided to the LLM
    - prompt_template (string): Template used to format the query
    - raw_query (string): Full query sent to the LLM
    - response_format (string): Expected format of the response
    - model_used (string): Name of the LLM used
    - temperature (float): Temperature setting for the model (0.0-1.0)
    - max_tokens (integer): Maximum tokens in the response
    - response (string): Full response from the LLM
    - query_timestamp (datetime): When the query was sent
    - response_timestamp (datetime): When the response was received
    - query_duration (float): Time taken for the LLM to respond in seconds
    - tokens_used (integer): Number of tokens in the query and response
    - cost_estimate (float): Estimated cost of the query
    - success (boolean): Whether the query was successful
    - error_message (string): Error message if query failed
    """
    query_type: str = "action_planning"
    input_context: str = ""
    prompt_template: str = ""
    raw_query: str = ""
    response_format: str = "json"
    model_used: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    response: str = ""
    query_timestamp: float = 0.0  # Unix timestamp
    response_timestamp: float = 0.0  # Unix timestamp
    query_duration: float = 0.0
    tokens_used: int = 0
    cost_estimate: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        pass


@dataclass
class RobotState(BaseEntity):
    """
    Current configuration of the robot including position, orientation, and task progress.
    
    Fields:
    - id (string): Unique identifier for the robot state record
    - robot_id (string): Reference to the robot
    - position (Vector3): Current position in 3D space (x, y, z in meters)
    - orientation (Quaternion): Current orientation as quaternion (x, y, z, w)
    - joint_angles (array of float): Current angles of all joints in radians
    - battery_level (float): Current battery level as percentage (0.0-1.0)
    - task_progress (float): Current progress in the active task (0.0-1.0)
    - current_action_id (string): ID of the currently executing action
    - last_update (datetime): Timestamp of the last state update
    - operational_status (enum): Current status
    - current_gripper_status (enum): Status of end effector
    - active_sensors (array of string): List of currently active sensors
    - current_behavior (string): Current behavior pattern (for FSM/BT systems)
    """
    robot_id: str = ""
    position: Vector3 = None
    orientation: Quaternion = None
    joint_angles: List[float] = None
    battery_level: float = 1.0
    task_progress: float = 0.0
    current_action_id: str = ""
    last_update: float = 0.0  # Unix timestamp
    operational_status: str = "idle"
    current_gripper_status: str = "open"
    active_sensors: List[str] = None
    current_behavior: str = "idle"
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.position is None:
            self.position = Vector3()
        if self.orientation is None:
            self.orientation = Quaternion()
        if self.joint_angles is None:
            self.joint_angles = []
        if self.active_sensors is None:
            self.active_sensors = []


@dataclass
class EnvironmentalMap(BaseEntity):
    """
    Representation of the environment including obstacles, objects, and navigable areas.
    
    Fields:
    - id (string): Unique identifier for the environmental map
    - map_name (string): Name of the map
    - resolution (float): Resolution of the map in meters per cell
    - origin (Vector3): Origin point of the map in global coordinates
    - width (integer): Width of the map in cells
    - height (integer): Height of the map in cells
    - data (bytes): Binary data of the map (serialized occupancy grid)
    - occupied_threshold (float): Threshold above which areas are considered occupied (0.0-1.0)
    - free_threshold (float): Threshold below which areas are considered free (0.0-1.0)
    - update_timestamp (datetime): Last time the map was updated
    - map_type (enum): Type of map
    - semantic_objects (array of SemanticObject): Objects with semantic meaning in the map
    - frame_id (string): Coordinate frame of the map (e.g., "map", "odom")
    """
    map_name: str = ""
    resolution: float = 0.05
    origin: Vector3 = None
    width: int = 0
    height: int = 0
    data: bytes = b""
    occupied_threshold: float = 0.65
    free_threshold: float = 0.196
    update_timestamp: float = 0.0  # Unix timestamp
    map_type: str = "occupancy_grid"
    semantic_objects: List[Dict[str, Any]] = None
    frame_id: str = "map"
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.origin is None:
            self.origin = Vector3()
        if self.semantic_objects is None:
            self.semantic_objects = []


@dataclass
class DetectedObject(BaseEntity):
    """
    Identified item in the environment with properties relevant for manipulation.
    
    Fields:
    - id (string): Unique identifier for the detection
    - object_class (string): Class of the object (e.g., "cup", "chair", "person")
    - confidence (float): Confidence score of the detection (0.0-1.0)
    - bounding_box (BoundingBox): 2D bounding box in image coordinates
    - position_3d (Vector3): 3D position in world coordinates
    - orientation_3d (Quaternion): 3D orientation in world coordinates
    - dimensions (Vector3): Physical dimensions (width, height, depth) in meters
    - object_color (Vector3): RGB color values (0.0-1.0 for each channel)
    - affordances (array of string): Possible interactions
    - tracking_id (string): ID for tracking the object across frames
    - detection_source (enum): How the object was detected
    - age (float): Time in seconds since the object was first detected
    - mask (string): Path to segmentation mask if available
    - category (string): Broader category (e.g., "furniture", "food", "personal_item")
    """
    object_class: str = ""
    confidence: float = 0.0
    bounding_box: BoundingBox = None
    position_3d: Vector3 = None
    orientation_3d: Quaternion = None
    dimensions: Vector3 = None
    object_color: Vector3 = None
    affordances: List[str] = None
    tracking_id: str = ""
    detection_source: str = "vision"
    age: float = 0.0
    mask: str = ""
    category: str = ""
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.bounding_box is None:
            self.bounding_box = BoundingBox(0, 0, 0, 0)
        if self.position_3d is None:
            self.position_3d = Vector3()
        if self.orientation_3d is None:
            self.orientation_3d = Quaternion()
        if self.dimensions is None:
            self.dimensions = Vector3()
        if self.object_color is None:
            self.object_color = Vector3()
        if self.affordances is None:
            self.affordances = []


@dataclass
class Observation(BaseEntity):
    """
    Snapshot of sensor data and environmental perception at a specific time.
    
    Fields:
    - id (string): Unique identifier for the observation
    - timestamp (datetime): Time when the observation was made
    - sensor_data_paths (dictionary): Paths to different sensor data files
    - detected_objects (array of DetectedObject): Objects detected in this observation
    - environment_context (string): Descriptive text of the current environment
    - camera_image_path (string): Path to the primary camera image
    - depth_image_path (string): Path to the depth image (if available)
    - point_cloud_path (string): Path to the point cloud data (if available)
    - robot_state_id (string): Reference to the robot state at the time of observation
    - semantic_tags (array of string): Tags describing the scene semantics
    - activity_recognition (string): Detected activities in the scene
    - salient_regions (array of BoundingBox): Regions of interest in images
    """
    timestamp: float = 0.0  # Unix timestamp
    sensor_data_paths: Dict[str, str] = None
    detected_objects: List[DetectedObject] = None
    environment_context: str = ""
    camera_image_path: str = ""
    depth_image_path: str = ""
    point_cloud_path: str = ""
    robot_state_id: str = ""
    semantic_tags: List[str] = None
    activity_recognition: str = ""
    salient_regions: List[BoundingBox] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.sensor_data_paths is None:
            self.sensor_data_paths = {}
        if self.detected_objects is None:
            self.detected_objects = []
        if self.semantic_tags is None:
            self.semantic_tags = []
        if self.salient_regions is None:
            self.salient_regions = []


@dataclass
class RobotAction(BaseEntity):
    """
    Executable action in the ROS 2 system.
    
    Fields:
    - id (string): Unique identifier for the robot action
    - action_type (enum): ROS 2 action type
    - parameters (JSON): Action-specific parameters as ROS 2 message
    - goal_message (string): Serialized ROS 2 goal message
    - result_message (string): Serialized ROS 2 result message (when completed)
    - status (enum): Current status
    - created_at (datetime): When the action was created
    - started_at (datetime): When the action started execution
    - completed_at (datetime): When the action completed
    - execution_duration (float): Time taken to execute in seconds
    - action_step_id (string): Reference to the ActionStep that triggered this action
    - feedback_messages (array of JSON): Feedback messages received during execution
    """
    action_type: str = "move_base"  # Common default
    parameters: Dict[str, Any] = None
    goal_message: str = ""
    result_message: str = ""
    status: str = "pending"
    created_at: float = 0.0  # Unix timestamp
    started_at: float = 0.0  # Unix timestamp
    completed_at: float = 0.0  # Unix timestamp
    execution_duration: float = 0.0
    action_step_id: str = ""
    feedback_messages: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.parameters is None:
            self.parameters = {}
        if self.feedback_messages is None:
            self.feedback_messages = []


@dataclass
class User(BaseEntity):
    """
    Information about users interacting with the system.
    
    Fields:
    - id (string): Unique identifier for the user
    - name (string): Full name of the user
    - user_type (enum): Type of user
    - voice_profile_path (string): Path to the user's voice profile for recognition
    - preferences (JSON): User preferences for interaction
    - permissions (array of string): Permission levels granted to the user
    - last_active (datetime): Last time user interacted with the system
    - language_preference (string): Preferred language for interaction
    - accessibility_needs (array of string): Any accessibility requirements
    """
    name: str = ""
    user_type: str = "casual_user"
    voice_profile_path: str = ""
    preferences: Dict[str, Any] = None
    permissions: List[str] = None
    last_active: float = 0.0  # Unix timestamp
    language_preference: str = "en"
    accessibility_needs: List[str] = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.preferences is None:
            self.preferences = {}
        if self.permissions is None:
            self.permissions = []
        if self.accessibility_needs is None:
            self.accessibility_needs = []