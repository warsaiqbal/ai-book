"""
Specialized RobotModel data model for the simulation environment based on the 
base model defined in utils.data_models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from src.utils.data_models import (
    BaseEntity, Vector3, Quaternion, RobotModel as BaseRobotModel,
    Sensor, SensorType
)


@dataclass
class JointModel:
    """Represents a joint in the robot model."""
    name: str
    joint_type: str  # 'revolute', 'prismatic', 'fixed', 'continuous', etc.
    parent_link: str
    child_link: str
    axis: Vector3 = field(default_factory=lambda: Vector3(1.0, 0.0, 0.0))  # Joint axis in parent frame
    origin_position: Vector3 = field(default_factory=Vector3)  # Position offset from parent
    origin_rotation: Quaternion = field(default_factory=Quaternion)  # Rotation offset from parent
    limits_lower: Optional[float] = None  # Lower joint limit in radians or meters
    limits_upper: Optional[float] = None  # Upper joint limit in radians or meters
    limits_effort: float = 100.0  # Maximum joint effort
    limits_velocity: float = 1.0  # Maximum joint velocity
    dynamics_damping: float = 0.1  # Joint damping coefficient
    dynamics_friction: float = 0.0  # Joint friction coefficient

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'name': self.name,
            'joint_type': self.joint_type,
            'parent_link': self.parent_link,
            'child_link': self.child_link,
            'axis': {'x': self.axis.x, 'y': self.axis.y, 'z': self.axis.z},
            'origin_position': {'x': self.origin_position.x, 'y': self.origin_position.y, 'z': self.origin_position.z},
            'origin_rotation': {'x': self.origin_rotation.x, 'y': self.origin_rotation.y, 'z': self.origin_rotation.z, 'w': self.origin_rotation.w},
            'limits_lower': self.limits_lower,
            'limits_upper': self.limits_upper,
            'limits_effort': self.limits_effort,
            'limits_velocity': self.limits_velocity,
            'dynamics_damping': self.dynamics_damping,
            'dynamics_friction': self.dynamics_friction
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        axis_data = data.get('axis', {'x': 1.0, 'y': 0.0, 'z': 0.0})
        axis = Vector3(axis_data['x'], axis_data['y'], axis_data['z'])
        
        pos_data = data.get('origin_position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        origin_position = Vector3(pos_data['x'], pos_data['y'], pos_data['z'])
        
        rot_data = data.get('origin_rotation', {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})
        origin_rotation = Quaternion(rot_data['x'], rot_data['y'], rot_data['z'], rot_data['w'])
        
        return cls(
            name=data['name'],
            joint_type=data['joint_type'],
            parent_link=data['parent_link'],
            child_link=data['child_link'],
            axis=axis,
            origin_position=origin_position,
            origin_rotation=origin_rotation,
            limits_lower=data.get('limits_lower'),
            limits_upper=data.get('limits_upper'),
            limits_effort=data.get('limits_effort', 100.0),
            limits_velocity=data.get('limits_velocity', 1.0),
            dynamics_damping=data.get('dynamics_damping', 0.1),
            dynamics_friction=data.get('dynamics_friction', 0.0)
        )


@dataclass
class LinkModel:
    """Represents a link in the robot model."""
    name: str
    mass: float = 1.0
    inertia: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))  # Ixx, Iyy, Izz (Ixy, Ixz, Iyz assumed 0)
    visual_mesh_path: Optional[str] = None
    collision_mesh_path: Optional[str] = None
    visual_origin_position: Vector3 = field(default_factory=Vector3)
    visual_origin_rotation: Quaternion = field(default_factory=Quaternion)
    collision_origin_position: Vector3 = field(default_factory=Vector3)
    collision_origin_rotation: Quaternion = field(default_factory=Quaternion)
    color_rgba: List[float] = field(default_factory=lambda: [0.5, 0.5, 0.5, 1.0])  # RGBA values 0-1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'name': self.name,
            'mass': self.mass,
            'inertia': {'x': self.inertia.x, 'y': self.inertia.y, 'z': self.inertia.z},
            'visual_mesh_path': self.visual_mesh_path,
            'collision_mesh_path': self.collision_mesh_path,
            'visual_origin_position': {'x': self.visual_origin_position.x, 'y': self.visual_origin_position.y, 'z': self.visual_origin_position.z},
            'visual_origin_rotation': {'x': self.visual_origin_rotation.x, 'y': self.visual_origin_rotation.y, 'z': self.visual_origin_rotation.z, 'w': self.visual_origin_rotation.w},
            'collision_origin_position': {'x': self.collision_origin_position.x, 'y': self.collision_origin_position.y, 'z': self.collision_origin_position.z},
            'collision_origin_rotation': {'x': self.collision_origin_rotation.x, 'y': self.collision_origin_rotation.y, 'z': self.collision_origin_rotation.z, 'w': self.collision_origin_rotation.w},
            'color_rgba': self.color_rgba
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        inertia_data = data.get('inertia', {'x': 1.0, 'y': 1.0, 'z': 1.0})
        inertia = Vector3(inertia_data['x'], inertia_data['y'], inertia_data['z'])
        
        vis_pos_data = data.get('visual_origin_position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        visual_origin_position = Vector3(vis_pos_data['x'], vis_pos_data['y'], vis_pos_data['z'])
        
        vis_rot_data = data.get('visual_origin_rotation', {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})
        visual_origin_rotation = Quaternion(vis_rot_data['x'], vis_rot_data['y'], vis_rot_data['z'], vis_rot_data['w'])
        
        col_pos_data = data.get('collision_origin_position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        collision_origin_position = Vector3(col_pos_data['x'], col_pos_data['y'], col_pos_data['z'])
        
        col_rot_data = data.get('collision_origin_rotation', {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})
        collision_origin_rotation = Quaternion(col_rot_data['x'], col_rot_data['y'], col_rot_data['z'], col_rot_data['w'])
        
        return cls(
            name=data['name'],
            mass=data.get('mass', 1.0),
            inertia=inertia,
            visual_mesh_path=data.get('visual_mesh_path'),
            collision_mesh_path=data.get('collision_mesh_path'),
            visual_origin_position=visual_origin_position,
            visual_origin_rotation=visual_origin_rotation,
            collision_origin_position=collision_origin_position,
            collision_origin_rotation=collision_origin_rotation,
            color_rgba=data.get('color_rgba', [0.5, 0.5, 0.5, 1.0])
        )


@dataclass
class LocomotionConfiguration:
    """Configuration for bipedal locomotion."""
    controller_type: str = "mpc"  # Model Predictive Control
    gait_type: str = "walking"  # walking, running, standing, etc.
    step_height: float = 0.1  # meters
    step_length: float = 0.4  # meters
    walking_speed: float = 0.5  # m/s
    balance_threshold: float = 0.05  # meters
    control_rate: float = 100.0  # Hz
    com_height: float = 0.8  # Center of mass height
    foot_separation: float = 0.3  # Distance between feet
    zmp_margin: float = 0.05  # Zero moment point safety margin

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'controller_type': self.controller_type,
            'gait_type': self.gait_type,
            'step_height': self.step_height,
            'step_length': self.step_length,
            'walking_speed': self.walking_speed,
            'balance_threshold': self.balance_threshold,
            'control_rate': self.control_rate,
            'com_height': self.com_height,
            'foot_separation': self.foot_separation,
            'zmp_margin': self.zmp_margin
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        return cls(
            controller_type=data.get('controller_type', 'mpc'),
            gait_type=data.get('gait_type', 'walking'),
            step_height=data.get('step_height', 0.1),
            step_length=data.get('step_length', 0.4),
            walking_speed=data.get('walking_speed', 0.5),
            balance_threshold=data.get('balance_threshold', 0.05),
            control_rate=data.get('control_rate', 100.0),
            com_height=data.get('com_height', 0.8),
            foot_separation=data.get('foot_separation', 0.3),
            zmp_margin=data.get('zmp_margin', 0.05)
        )


@dataclass
class SensorMount:
    """Specification for where a sensor is mounted on the robot."""
    name: str
    sensor_type: SensorType
    link_name: str  # The link this sensor is attached to
    position: Vector3 = field(default_factory=Vector3)  # Position relative to link frame
    orientation: Quaternion = field(default_factory=Quaternion)  # Orientation relative to link frame
    parameters: Dict[str, Any] = field(default_factory=dict)  # Type-specific parameters

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'name': self.name,
            'sensor_type': self.sensor_type.value,
            'link_name': self.link_name,
            'position': {'x': self.position.x, 'y': self.position.y, 'z': self.position.z},
            'orientation': {'x': self.orientation.x, 'y': self.orientation.y, 'z': self.orientation.z, 'w': self.orientation.w},
            'parameters': self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        pos_data = data.get('position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        position = Vector3(pos_data['x'], pos_data['y'], pos_data['z'])
        
        rot_data = data.get('orientation', {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})
        orientation = Quaternion(rot_data['x'], rot_data['y'], rot_data['z'], rot_data['w'])
        
        sensor_type = SensorType(data['sensor_type'])
        
        return cls(
            name=data['name'],
            sensor_type=sensor_type,
            link_name=data['link_name'],
            position=position,
            orientation=orientation,
            parameters=data.get('parameters', {})
        )


@dataclass
class RobotModel(BaseRobotModel):
    """
    Specialized robot model for simulation with additional fields specific to Isaac Sim.
    
    Extends the base RobotModel with Isaac Sim specific properties.
    """
    # Additional Isaac Sim specific properties
    isaac_robot_path: Optional[str] = None
    enable_self_collision: bool = True
    enable_gravity: bool = True
    joint_damping: float = 0.1
    joint_friction: float = 0.0
    articulation_props: Dict[str, Any] = field(default_factory=dict)
    
    # Detailed robot structure
    links_obj: List[LinkModel] = field(default_factory=list)
    joints_obj: List[JointModel] = field(default_factory=list)
    locomotion_config_obj: Optional[LocomotionConfiguration] = None
    
    # Convert sensor_mounts to objects
    sensor_mounts_obj: List[SensorMount] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize objects if not provided."""
        super().__post_init__()  # Call parent __post_init__
        
        if not self.links_obj:
            # If links were provided in base format, convert them
            pass  # Links would typically be loaded separately
        
        if not self.joints_obj:
            # If joints were provided in base format, convert them
            pass  # Joints would typically be loaded separately
        
        if self.locomotion_config_obj is None:
            # Create default locomotion configuration
            self.locomotion_config_obj = LocomotionConfiguration()
        
        if not self.sensor_mounts_obj and self.sensor_mounts:
            # Convert sensor_mounts from base format
            for mount_data in self.sensor_mounts:
                if isinstance(mount_data, dict):
                    self.sensor_mounts_obj.append(SensorMount.from_dict(mount_data))
    
    def add_link(self, link: LinkModel):
        """Add a link to the robot model."""
        self.links_obj.append(link)
    
    def add_joint(self, joint: JointModel):
        """Add a joint to the robot model."""
        self.joints_obj.append(joint)
    
    def add_sensor_mount(self, mount: SensorMount):
        """Add a sensor mount to the robot model."""
        self.sensor_mounts_obj.append(mount)
        # Also update the base sensor_mounts list for compatibility
        self.sensor_mounts.append(mount.to_dict())
    
    def get_link_by_name(self, name: str) -> Optional[LinkModel]:
        """Get a link by its name."""
        for link in self.links_obj:
            if link.name == name:
                return link
        return None
    
    def get_joint_by_name(self, name: str) -> Optional[JointModel]:
        """Get a joint by its name."""
        for joint in self.joints_obj:
            if joint.name == name:
                return joint
        return None
    
    def get_sensor_mount_by_name(self, name: str) -> Optional[SensorMount]:
        """Get a sensor mount by its name."""
        for mount in self.sensor_mounts_obj:
            if mount.name == name:
                return mount
        return None
    
    def to_urdf(self) -> str:
        """Generate a URDF string for this robot model."""
        urdf = f'<?xml version="1.0"?>\n<robot name="{self.name}">\n'
        
        # Add links
        for link in self.links_obj:
            urdf += f'  <link name="{link.name}">\n'
            
            # Visual
            urdf += '    <visual>\n'
            if link.visual_mesh_path:
                urdf += f'      <geometry>\n        <mesh filename="{link.visual_mesh_path}"/>\n      </geometry>\n'
            else:
                urdf += '      <geometry>\n        <box size="0.1 0.1 0.1"/>\n      </geometry>\n'
            urdf += f'      <material name="{link.name}_material">\n        <color rgba="{link.color_rgba[0]} {link.color_rgba[1]} {link.color_rgba[2]} {link.color_rgba[3]}"/>\n      </material>\n'
            urdf += '    </visual>\n'
            
            # Collision
            urdf += '    <collision>\n'
            if link.collision_mesh_path:
                urdf += f'      <geometry>\n        <mesh filename="{link.collision_mesh_path}"/>\n      </geometry>\n'
            else:
                urdf += '      <geometry>\n        <box size="0.1 0.1 0.1"/>\n      </geometry>\n'
            urdf += '    </collision>\n'
            
            # Inertial
            urdf += '    <inertial>\n'
            urdf += f'      <mass value="{link.mass}"/>\n'
            urdf += f'      <inertia ixx="{link.inertia.x}" ixy="0.0" ixz="0.0" iyy="{link.inertia.y}" iyz="0.0" izz="{link.inertia.z}"/>\n'
            urdf += '    </inertial>\n'
            
            urdf += '  </link>\n'
        
        # Add joints
        for joint in self.joints_obj:
            urdf += f'  <joint name="{joint.name}" type="{joint.joint_type}">\n'
            urdf += f'    <parent link="{joint.parent_link}"/>\n'
            urdf += f'    <child link="{joint.child_link}"/>\n'
            urdf += f'    <origin xyz="{joint.origin_position.x} {joint.origin_position.y} {joint.origin_position.z}" rpy="0 0 0"/>\n'  # Simplified
            if joint.joint_type in ['revolute', 'prismatic']:
                urdf += f'    <limit lower="{joint.limits_lower or -3.14}" upper="{joint.limits_upper or 3.14}" effort="{joint.limits_effort}" velocity="{joint.limits_velocity}"/>\n'
            urdf += '  </joint>\n'
        
        # Add sensors as additional links and joints
        for mount in self.sensor_mounts_obj:
            # Create a sensor link
            sensor_link_name = f"{mount.name}_link"
            urdf += f'  <link name="{sensor_link_name}"/>\n'
            
            # Create a fixed joint to attach the sensor
            urdf += f'  <joint name="{mount.name}_joint" type="fixed">\n'
            urdf += f'    <parent link="{mount.link_name}"/>\n'
            urdf += f'    <child link="{sensor_link_name}"/>\n'
            urdf += f'    <origin xyz="{mount.position.x} {mount.position.y} {mount.position.z}" rpy="0 0 0"/>\n'  # Simplified rotation
            urdf += '  </joint>\n'
        
        urdf += '</robot>\n'
        return urdf
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert the robot model to a configuration dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'urdf_path': self.urdf_path,
            'sdf_path': self.sdf_path,
            'base_link': self.base_link,
            'joint_count': self.joint_count,
            'link_count': self.link_count,
            'dimensions': {
                'x': self.dimensions.x,
                'y': self.dimensions.y,
                'z': self.dimensions.z
            },
            'mass': self.mass,
            'max_joint_velocity': self.max_joint_velocity,
            'locomotion_config': self.locomotion_config_obj.to_dict() if self.locomotion_config_obj else {},
            'links': [link.to_dict() for link in self.links_obj],
            'joints': [joint.to_dict() for joint in self.joints_obj],
            'sensor_mounts': [mount.to_dict() for mount in self.sensor_mounts_obj],
            'isaac_robot_path': self.isaac_robot_path,
            'enable_self_collision': self.enable_self_collision,
            'enable_gravity': self.enable_gravity,
            'joint_damping': self.joint_damping,
            'joint_friction': self.joint_friction,
            'articulation_props': self.articulation_props
        }
    
    @classmethod
    def from_config_dict(cls, config_data: Dict[str, Any]):
        """Create a robot model from a configuration dictionary."""
        # Extract base properties
        robot_id = config_data.get('id', f'robot_{hash(str(config_data)) % 10000}')
        name = config_data.get('name', 'unnamed_robot')
        description = config_data.get('description', '')
        
        # Create dimensions
        dims_data = config_data.get('dimensions', {'x': 0.5, 'y': 0.3, 'z': 0.6})
        dimensions = Vector3(dims_data['x'], dims_data['y'], dims_data['z'])
        
        # Create instance
        robot = cls(
            id=robot_id,
            name=name,
            description=description,
            dimensions=dimensions,
            urdf_path=config_data.get('urdf_path', ''),
            sdf_path=config_data.get('sdf_path', ''),
            base_link=config_data.get('base_link', 'base_link'),
            joint_count=config_data.get('joint_count', 0),
            link_count=config_data.get('link_count', 0),
            mass=config_data.get('mass', 10.0),
            max_joint_velocity=config_data.get('max_joint_velocity', 1.0)
        )
        
        # Set Isaac-specific properties
        robot.isaac_robot_path = config_data.get('isaac_robot_path')
        robot.enable_self_collision = config_data.get('enable_self_collision', True)
        robot.enable_gravity = config_data.get('enable_gravity', True)
        robot.joint_damping = config_data.get('joint_damping', 0.1)
        robot.joint_friction = config_data.get('joint_friction', 0.0)
        robot.articulation_props = config_data.get('articulation_props', {})
        
        # Set locomotion configuration
        if 'locomotion_config' in config_data:
            robot.locomotion_config_obj = LocomotionConfiguration.from_dict(config_data['locomotion_config'])
        
        # Set links
        if 'links' in config_data:
            for link_data in config_data['links']:
                robot.links_obj.append(LinkModel.from_dict(link_data))
        
        # Set joints
        if 'joints' in config_data:
            for joint_data in config_data['joints']:
                robot.joints_obj.append(JointModel.from_dict(joint_data))
                
        # Set sensor mounts
        if 'sensor_mounts' in config_data:
            for mount_data in config_data['sensor_mounts']:
                robot.sensor_mounts_obj.append(SensorMount.from_dict(mount_data))
        
        return robot
    
    def save_to_file(self, file_path: str):
        """Save the robot model configuration to a file."""
        config = self.to_config_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the robot model configuration from a file."""
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        return cls.from_config_dict(config)


@dataclass
class RobotState:
    """Represents the current state of a robot in simulation."""
    robot_id: str
    timestamp: float
    joint_positions: Dict[str, float]  # joint_name -> position
    joint_velocities: Dict[str, float]  # joint_name -> velocity
    joint_efforts: Dict[str, float]  # joint_name -> effort
    base_position: Vector3 = field(default_factory=Vector3)
    base_orientation: Quaternion = field(default_factory=Quaternion)
    base_linear_velocity: Vector3 = field(default_factory=Vector3)
    base_angular_velocity: Vector3 = field(default_factory=Vector3)
    center_of_mass: Vector3 = field(default_factory=Vector3)
    external_forces: Dict[str, Vector3] = field(default_factory=dict)  # link_name -> force
    contact_points: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'robot_id': self.robot_id,
            'timestamp': self.timestamp,
            'joint_positions': self.joint_positions,
            'joint_velocities': self.joint_velocities,
            'joint_efforts': self.joint_efforts,
            'base_position': {'x': self.base_position.x, 'y': self.base_position.y, 'z': self.base_position.z},
            'base_orientation': {'x': self.base_orientation.x, 'y': self.base_orientation.y, 'z': self.base_orientation.z, 'w': self.base_orientation.w},
            'base_linear_velocity': {'x': self.base_linear_velocity.x, 'y': self.base_linear_velocity.y, 'z': self.base_linear_velocity.z},
            'base_angular_velocity': {'x': self.base_angular_velocity.x, 'y': self.base_angular_velocity.y, 'z': self.base_angular_velocity.z},
            'center_of_mass': {'x': self.center_of_mass.x, 'y': self.center_of_mass.y, 'z': self.center_of_mass.z},
            'external_forces': {link: {'x': force.x, 'y': force.y, 'z': force.z} 
                                for link, force in self.external_forces.items()},
            'contact_points': self.contact_points
        }

@dataclass
class RobotCommand:
    """Command to control a robot in simulation."""
    robot_id: str
    timestamp: float
    joint_commands: Dict[str, float]  # joint_name -> target position/effort
    base_command: Optional[Dict[str, float]] = None  # Base movement command if applicable
    gripper_commands: Dict[str, float] = field(default_factory=dict)  # gripper_name -> position
    control_mode: str = "position"  # position, velocity, or effort
    duration: Optional[float] = None  # Command duration in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'robot_id': self.robot_id,
            'timestamp': self.timestamp,
            'joint_commands': self.joint_commands,
            'base_command': self.base_command,
            'gripper_commands': self.gripper_commands,
            'control_mode': self.control_mode,
            'duration': self.duration
        }