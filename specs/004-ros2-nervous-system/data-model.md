# Data Model: ROS2 Nervous System

## Entities Overview

This document describes the key data structures and entities for the ROS 2-based nervous system for robot control.

## ROS Node

**Description**: An executable process that communicates with other nodes to perform computation, representing either a sensor, controller, or AI agent.

**Fields**:
- id: Unique identifier for the node
- name: Name of the node within the ROS namespace
- type: Type of node (sensor, controller, AI agent, etc.)
- status: Current operational status (active, inactive, error)
- creation_time: Timestamp when the node was created
- last_heartbeat: Timestamp of the last successful communication
- subscribed_topics: List of topics this node subscribes to
- published_topics: List of topics this node publishes to
- provided_services: List of services this node provides
- required_services: List of services this node requires

**Relationships**:
- Publishes to multiple Topic entities
- Subscribes to multiple Topic entities
- Provides multiple Service entities
- Requires multiple Service entities

**Validation rules**:
- Node name must be unique within the namespace
- Status must be one of the defined status values
- Heartbeat must be updated regularly to maintain active status

## Topic

**Description**: A named bus over which nodes exchange messages, enabling publisher-subscriber communication patterns.

**Fields**:
- id: Unique identifier for the topic
- name: Name of the topic
- message_type: Type of messages published on this topic (e.g., std_msgs/String)
- publisher_count: Number of nodes publishing to this topic
- subscriber_count: Number of nodes subscribed to this topic
- bandwidth_usage: Current bandwidth usage in bytes/second
- qos_profile: Quality of Service settings for the topic

**Relationships**:
- Connected to multiple Node entities (publishers)
- Connected to multiple Node entities (subscribers)

**Validation rules**:
- Message type must be a valid ROS 2 message type
- QoS settings must be compatible between publishers and subscribers
- Topic name must follow ROS naming conventions

## Service

**Description**: A synchronous request-response communication pattern between nodes for direct interaction.

**Fields**:
- id: Unique identifier for the service
- name: Name of the service
- service_type: Type of the service (e.g., std_srvs/SetBool)
- node_id: ID of the node providing this service
- request_count: Number of requests handled
- success_rate: Percentage of successful requests
- average_response_time: Average time to respond to requests

**Relationships**:
- Provided by one Node entity
- Used by multiple Node entities (clients)

**Validation rules**:
- Service name must be unique within the namespace
- Service type must be a valid ROS 2 service type
- Response time should be within acceptable bounds

## Python Agent

**Description**: An AI-based component written in Python that uses rclpy to interface with ROS controllers.

**Fields**:
- id: Unique identifier for the agent
- name: Name of the agent
- algorithm_type: Type of AI algorithm (e.g., reinforcement_learning, classical_control)
- status: Current operational status (active, inactive, paused)
- last_decision_time: Timestamp of the last decision made
- subscribed_topics: List of ROS topics the agent subscribes to
- published_topics: List of ROS topics the agent publishes to
- connected_services: List of ROS services the agent can call
- performance_metrics: Dictionary of performance metrics

**Relationships**:
- Communicates with multiple Node entities through topics and services
- Interacts with multiple Topic entities
- Interacts with multiple Service entities

**Validation rules**:
- Algorithm type must be a supported AI approach
- Status must be one of the defined status values
- Performance metrics must be regularly updated

## URDF Model

**Description**: The Unified Robot Description Format representation of a robot's physical structure, including links, joints, and kinematic properties.

**Fields**:
- id: Unique identifier for the URDF model
- name: Name of the robot model
- robot_name: Name of the robot as defined in the URDF
- file_path: Path to the URDF file
- joint_count: Number of joints in the robot
- link_count: Number of links in the robot
- kinematic_chains: List of kinematic chains in the robot
- collision_meshes: List of collision mesh definitions
- visual_meshes: List of visual mesh definitions

**Relationships**:
- Associated with multiple Joint entities
- Associated with multiple Link entities
- Connected to Robot Controller entity

**Validation rules**:
- URDF must be syntactically correct XML
- All referenced mesh files must exist
- Joint limits must be physically plausible

## Joint

**Description**: A connection between two links in a robot that constrains their relative motion.

**Fields**:
- id: Unique identifier for the joint
- name: Name of the joint
- type: Type of joint (revolute, prismatic, fixed, etc.)
- parent_link: Name of the parent link
- child_link: Name of the child link
- origin_position: Position of the joint relative to parent
- origin_rotation: Rotation of the joint relative to parent
- axis: Axis of motion for the joint
- limits_lower: Lower limit for joint motion
- limits_upper: Upper limit for joint motion
- limits_effort: Maximum effort for the joint
- limits_velocity: Maximum velocity for the joint

**Relationships**:
- Belongs to one URDF Model entity
- Connected to one parent Link entity
- Connected to one child Link entity

**Validation rules**:
- Joint type must be a valid URDF joint type
- Joint limits must be physically feasible
- Parent and child links must exist in the URDF

## Link

**Description**: A rigid component of the robot that represents a physical part.

**Fields**:
- id: Unique identifier for the link
- name: Name of the link
- visual_geometry: Description of visual geometry
- collision_geometry: Description of collision geometry
- inertial_mass: Mass of the link
- inertial_inertia: Inertial properties of the link
- position: Current position in the robot's coordinate system
- orientation: Current orientation in the robot's coordinate system

**Relationships**:
- Belongs to one URDF Model entity
- Connected to multiple Joint entities as parent or child

**Validation rules**:
- Mass and inertial properties must be physically plausible
- Visual and collision geometry must be properly defined

## Robot Controller

**Description**: A ROS node responsible for translating high-level commands into low-level hardware actions.

**Fields**:
- id: Unique identifier for the controller
- name: Name of the controller
- controller_type: Type of controller (position, velocity, effort, etc.)
- controlled_joints: List of joint names controlled by this controller
- hardware_interface: Interface to the physical hardware
- status: Current operational status
- command_frequency: Frequency at which commands are sent
- last_command_time: Timestamp of the last command sent

**Relationships**:
- Connects to multiple Joint entities
- Associated with one URDF Model entity
- Communicates with Node entities (command publishers)

**Validation rules**:
- Controlled joints must exist in the associated URDF model
- Controller type must match the joint types it controls
- Status must reflect actual hardware state when possible